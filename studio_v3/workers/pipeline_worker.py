"""
Background QThread Worker for the 4-Step Pipeline State Machine.
Communicates strictly via Qt Signals/Slots and supports real cooperative cancellation.
"""

import time
import threading
from app.qt_compat import QThread, Signal
from core.pipeline_engine import PipelineContext, PipelineEngine


class PipelineWorker(QThread):
    stepStateChanged = Signal(int, str)       # (step_index, 'waiting'|'running'|'done'|'error')
    progressUpdated = Signal(int, str)        # (percent 0..100, eta_text)
    logMessage = Signal(str, str)             # (level 'INFO'|'SUCCESS'|'WARN'|'ERROR', message)
    subtitlesReady = Signal(str, str)         # (kind 'orig'|'trans', srt_path)
    pipelineFinished = Signal(bool, str)      # (success, result_message_or_path)

    def __init__(self, ctx: PipelineContext, single_step: int = None, parent=None):
        super().__init__(parent)
        self.ctx = ctx
        self.single_step = single_step
        self._cancel_ev = threading.Event()

    def cancel(self):
        self._cancel_ev.set()
        self.logMessage.emit("WARN", "Đang hủy tiến trình theo yêu cầu...")

    def run(self):
        t_start = time.time()
        try:
            PipelineEngine.validate_inputs(self.ctx, self.single_step)
        except Exception as e:
            if self.single_step is not None:
                self.stepStateChanged.emit(self.single_step, "error")
            self.logMessage.emit("ERROR", str(e))
            self.pipelineFinished.emit(False, str(e))
            return

        steps = [self.single_step] if self.single_step is not None else [0, 1, 2, 3]
        total = len(steps)

        for idx, step in enumerate(steps):
            if self._cancel_ev.is_set():
                self.stepStateChanged.emit(step, "waiting")
                self.pipelineFinished.emit(False, "Đã hủy tiến trình.")
                return

            self.stepStateChanged.emit(step, "running")
            base_pct = int((idx / total) * 100)
            self.progressUpdated.emit(max(5, base_pct), f"Đang xử lý bước {step + 1}/4...")

            def _log(msg: str):
                lvl = "SUCCESS" if "✓" in msg or "hoàn tất" in msg.lower() else ("WARN" if "⚠️" in msg else "INFO")
                self.logMessage.emit(lvl, str(msg))

            try:
                if step == 0:
                    srt = PipelineEngine.run_step_0_transcribe(self.ctx, _log, self._cancel_ev)
                    self.subtitlesReady.emit("orig", srt)
                elif step == 1:
                    srt = PipelineEngine.run_step_1_translate(self.ctx, _log, self._cancel_ev)
                    self.subtitlesReady.emit("trans", srt)
                elif step == 2:
                    PipelineEngine.run_step_2_tts(self.ctx, _log, self._cancel_ev)
                elif step == 3:
                    PipelineEngine.run_step_3_render(self.ctx, _log, self._cancel_ev)

                self.stepStateChanged.emit(step, "done")
                elapsed = max(0.5, time.time() - t_start)
                done_count = idx + 1
                rem_steps = total - done_count
                eta_s = int((elapsed / done_count) * rem_steps)
                pct = int((done_count / total) * 100)
                eta_txt = f"Còn khoảng ~{eta_s}s" if rem_steps > 0 else f"Hoàn tất trong {int(elapsed)}s"
                self.progressUpdated.emit(pct, eta_txt)

            except InterruptedError as ie:
                self.stepStateChanged.emit(step, "waiting")
                self.logMessage.emit("WARN", str(ie))
                self.pipelineFinished.emit(False, str(ie))
                return
            except Exception as err:
                self.stepStateChanged.emit(step, "error")
                self.logMessage.emit("ERROR", f"Lỗi ở bước {step + 1}: {err}")
                self.pipelineFinished.emit(False, str(err))
                return

        res_msg = self.ctx.final_mp4 or "Đã hoàn tất xử lý!"
        self.logMessage.emit("SUCCESS", f"Hoàn tất quy trình: {res_msg}")
        self.pipelineFinished.emit(True, res_msg)
