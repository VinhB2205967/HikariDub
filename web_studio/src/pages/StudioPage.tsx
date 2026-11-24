import React, { useState } from 'react';
import { useStudioStore } from '../store/useStudioStore';
import { Card, PrimaryButton, SecondaryButton, StatusBadge } from '../components/ui';

export const StudioPage: React.FC = () => {
  const store = useStudioStore();
  const [findStr, setFindStr] = useState('');
  const [replaceStr, setReplaceStr] = useState('');
  const [mobileTab, setMobileTab] = useState<'config' | 'preview' | 'subs'>('preview');

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files?.[0];
    if (f) store.simulateUploadVideo(f.name);
  };

  return (
    <div className="flex flex-col h-[calc(100vh-56px)]">
      {/* Mobile <768px Tab Switcher */}
      <div className="flex md:hidden border-b border-[#262B38] bg-[#171A23] px-3 py-1.5 gap-2">
        {(['config', 'preview', 'subs'] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setMobileTab(tab)}
            className={`flex-1 py-1.5 rounded-[8px] text-xs font-semibold ${
              mobileTab === tab ? 'bg-[#7C5CFF] text-white' : 'text-[#8B93A7]'
            }`}
          >
            {tab === 'config' ? '1. Cấu hình' : tab === 'preview' ? '2. Xem trước' : '3. Phụ đề'}
          </button>
        ))}
      </div>

      {/* Main 3-Column Responsive Workspace (>=1280px 3 cols, 768-1279px 2 cols, <768px 1 col) */}
      <div className="flex-1 min-h-0 grid grid-cols-1 md:grid-cols-12 gap-3 p-3 overflow-hidden">
        {/* LEFT COLUMN: Configuration Cards */}
        <aside
          className={`md:col-span-4 xl:col-span-3 overflow-y-auto space-y-3 pr-1 ${
            mobileTab !== 'config' ? 'hidden md:block' : ''
          }`}
        >
          <Card className="space-y-2.5">
            <div className="text-sm font-bold">1. Nguồn Video &amp; Tải lên</div>
            <label
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleDrop}
              className="block p-3 rounded-[10px] border border-dashed border-[#262B38] hover:border-[#7C5CFF] bg-[#0F1117] text-center cursor-pointer transition"
            >
              <div className="text-xs font-semibold text-[#E6E8EE] truncate" title={store.videoName}>
                🎬 {store.videoName}
              </div>
              <div className="text-[11px] text-[#8B93A7] mt-0.5">
                Kéo thả video hoặc bấm để chọn file mới ({store.uploadProgress}%)
              </div>
              <input
                type="file"
                accept="video/*"
                className="hidden"
                onChange={(e) => e.target.files?.[0] && store.simulateUploadVideo(e.target.files[0].name)}
              />
            </label>
          </Card>

          <Card className="space-y-2.5">
            <div className="text-sm font-bold">2. Mô hình Whisper &amp; Giọng AI</div>
            <div>
              <label className="text-xs text-[#8B93A7] block mb-1">Mô hình Whisper STT</label>
              <select
                aria-label="Mô hình Whisper"
                value={store.whisperModel}
                onChange={(e) => store.updateConfig({ whisperModel: e.target.value })}
                className="w-full px-2.5 py-1.5 rounded-[10px] bg-[#0F1117] border border-[#262B38] text-xs"
              >
                <option value="tiny">Tiny — Siêu tốc</option>
                <option value="base">Base — Nhanh</option>
                <option value="small">Small — Cân bằng (Khuyên dùng)</option>
                <option value="medium">Medium — Chính xác cao</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-[#8B93A7] block mb-1">Giọng đọc AI</label>
              <div className="flex gap-1.5">
                <select
                  aria-label="Giọng đọc AI"
                  value={store.selectedVoiceId}
                  onChange={(e) => store.updateConfig({ selectedVoiceId: e.target.value })}
                  className="flex-1 min-w-0 px-2.5 py-1.5 rounded-[10px] bg-[#0F1117] border border-[#262B38] text-xs"
                >
                  {store.voices.map((v) => (
                    <option key={v.id} value={v.id}>
                      {v.name} ({v.gender} · {v.engine})
                    </option>
                  ))}
                </select>
                <SecondaryButton
                  onClick={() => store.showToast('info', 'Đang phát mẫu giọng đọc AI...')}
                  className="px-2.5 py-1 text-xs shrink-0"
                  title="Nghe thử giọng"
                >
                  🔊 Thử
                </SecondaryButton>
              </div>
            </div>
          </Card>

          <Card className="space-y-2.5">
            <div className="text-sm font-bold">3. Dịch thuật &amp; Phong cách</div>
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-xs text-[#8B93A7] block mb-1">Ngôn ngữ đích</label>
                <select
                  value={store.targetLang}
                  onChange={(e) => store.updateConfig({ targetLang: e.target.value })}
                  className="w-full px-2 py-1.5 rounded-[10px] bg-[#0F1117] border border-[#262B38] text-xs"
                >
                  <option>Tiếng Việt</option>
                  <option>English</option>
                  <option>日本語</option>
                </select>
              </div>
              <div>
                <label className="text-xs text-[#8B93A7] block mb-1">Phong cách</label>
                <select
                  value={store.stylePreset}
                  onChange={(e) => store.updateConfig({ stylePreset: e.target.value })}
                  className="w-full px-2 py-1.5 rounded-[10px] bg-[#0F1117] border border-[#262B38] text-xs"
                >
                  <option>Tự nhiên / Đời thường</option>
                  <option>Review Phim / Anime</option>
                  <option>Hài hước / Giải trí</option>
                </select>
              </div>
            </div>
          </Card>

          <Card className="space-y-2.5">
            <div className="text-sm font-bold">4. Lọc giọng &amp; Trộn âm thanh</div>
            <label className="flex items-center gap-2 text-xs cursor-pointer">
              <input
                type="checkbox"
                checked={store.vocalSep}
                onChange={(e) => store.updateConfig({ vocalSep: e.target.checked })}
                className="accent-[#7C5CFF]"
              />
              <span>Tách lời thoại / Giữ nhạc nền BGM</span>
            </label>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between text-[#8B93A7]">
                <span>Âm gốc / BGM</span>
                <span className="text-[#4F8CFF] font-bold">{store.origVolume}%</span>
              </div>
              <input
                type="range"
                min={0}
                max={100}
                value={store.origVolume}
                onChange={(e) => store.updateConfig({ origVolume: Number(e.target.value) })}
                className="w-full accent-[#7C5CFF]"
              />
            </div>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between text-[#8B93A7]">
                <span>Giọng đọc AI</span>
                <span className="text-[#7C5CFF] font-bold">{store.voiceVolume}%</span>
              </div>
              <input
                type="range"
                min={50}
                max={200}
                value={store.voiceVolume}
                onChange={(e) => store.updateConfig({ voiceVolume: Number(e.target.value) })}
                className="w-full accent-[#7C5CFF]"
              />
            </div>
          </Card>
        </aside>

        {/* CENTER COLUMN: Video Player + Waveform Timeline + Overlays */}
        <main
          className={`md:col-span-8 xl:col-span-5 flex flex-col gap-3 min-h-0 ${
            mobileTab !== 'preview' ? 'hidden md:flex' : 'flex'
          }`}
        >
          <Card className="flex-1 min-h-[240px] flex flex-col justify-between relative overflow-hidden bg-[#0A0C10]">
            <div className="flex items-center justify-between text-xs z-10">
              <span className="px-2.5 py-1 rounded-md bg-black/60 border border-white/10 truncate max-w-[240px]" title={store.videoName}>
                {store.videoName} · 1080p 60fps
              </span>
              <span className="px-2.5 py-0.5 rounded-md bg-[#7C5CFF]/20 text-[#A594FF] border border-[#7C5CFF]/40 font-semibold">
                {store.watermarkText}
              </span>
            </div>

            <div className="my-auto text-center space-y-3 py-6">
              <div className="text-xs text-[#8B93A7]">Khung xem trước Canvas 16:9 (Kéo thả Vùng che / Logo / Watermark)</div>
              <div className="mx-auto max-w-md px-4 py-2 rounded-lg bg-black/75 border border-white/10 text-sm font-bold text-white shadow">
                {store.subtitles[0]?.translated || 'Chưa có phụ đề'}
              </div>
            </div>

            {/* Overlay Compact Tabs */}
            <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-[#262B38]">
              <div className="flex items-center gap-1.5">
                {(['mask', 'logo', 'watermark'] as const).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => store.updateConfig({ activeOverlayTab: tab })}
                    className={`px-2.5 py-1 rounded-[8px] text-xs font-medium transition ${
                      store.activeOverlayTab === tab
                        ? 'bg-[#7C5CFF]/25 text-white border border-[#7C5CFF]'
                        : 'bg-[#1E2230] text-[#8B93A7]'
                    }`}
                  >
                    {tab === 'mask' ? '▭ Vùng che' : tab === 'logo' ? '🖼️ Logo' : '✒️ Watermark'}
                  </button>
                ))}
              </div>
              <span className="text-xs font-mono text-[#8B93A7]">
                00:{String(store.currentTimeSec).padStart(2, '0')} / 00:{store.videoDurationSec}
              </span>
            </div>
          </Card>

          {/* Waveform Timeline */}
          <Card className="p-3 space-y-2">
            <div className="flex items-center justify-between text-xs text-[#8B93A7]">
              <span>Timeline Waveform &amp; Phân đoạn phụ đề</span>
              <span>Chạm để tua nhanh</span>
            </div>
            <div className="h-12 rounded-[8px] bg-[#0F1117] border border-[#262B38] p-2 flex items-end gap-1 overflow-hidden">
              {Array.from({ length: 48 }).map((_, idx) => {
                const h = 25 + Math.round(Math.abs(Math.sin(idx * 0.45) * 65));
                const active = idx / 48 <= store.currentTimeSec / store.videoDurationSec;
                return (
                  <div
                    key={idx}
                    onClick={() => store.updateConfig({ currentTimeSec: Math.round((idx / 48) * store.videoDurationSec) })}
                    style={{ height: `${h}%` }}
                    className={`flex-1 rounded-sm cursor-pointer transition ${
                      active ? 'bg-[#4F8CFF]' : 'bg-[#262B38] hover:bg-[#3A4258]'
                    }`}
                  />
                );
              })}
            </div>
          </Card>
        </main>

        {/* RIGHT COLUMN: Side-by-Side Editable Subtitle Editor */}
        <section
          className={`md:col-span-12 xl:col-span-4 flex flex-col min-h-0 ${
            mobileTab !== 'subs' ? 'hidden xl:flex' : 'flex'
          }`}
        >
          <Card className="flex-1 flex flex-col min-h-0 space-y-3">
            <div className="flex items-center justify-between gap-2">
              <div className="text-sm font-bold">Trình biên tập phụ đề (Gốc / Dịch)</div>
              <SecondaryButton
                onClick={() => store.showToast('success', 'Đã xuất file phụ đề .SRT!')}
                className="px-2.5 py-1 text-xs"
              >
                📤 Xuất SRT
              </SecondaryButton>
            </div>

            {/* Find & Replace */}
            <div className="flex gap-1.5">
              <input
                value={findStr}
                onChange={(e) => setFindStr(e.target.value)}
                placeholder="Tìm từ..."
                className="flex-1 min-w-0 px-2.5 py-1.5 rounded-[8px] bg-[#0F1117] border border-[#262B38] text-xs"
              />
              <input
                value={replaceStr}
                onChange={(e) => setReplaceStr(e.target.value)}
                placeholder="Thay bằng..."
                className="flex-1 min-w-0 px-2.5 py-1.5 rounded-[8px] bg-[#0F1117] border border-[#262B38] text-xs"
              />
              <SecondaryButton
                onClick={() => store.replaceAllSubtitles(findStr, replaceStr)}
                className="px-2.5 py-1.5 text-xs shrink-0"
              >
                Thay tất cả
              </SecondaryButton>
            </div>

            {/* Subtitle Rows */}
            <div className="flex-1 overflow-y-auto space-y-2 pr-1">
              {store.subtitles.map((sub) => (
                <div
                  key={sub.id}
                  onClick={() => store.updateConfig({ currentTimeSec: Math.round(sub.startMs / 1000) })}
                  className="p-2.5 rounded-[10px] bg-[#0F1117] border border-[#262B38] hover:border-[#4F8CFF]/60 space-y-1.5 transition"
                >
                  <div className="flex items-center justify-between text-[11px] font-mono text-[#8B93A7]">
                    <span>#{sub.id} · {sub.timeText}</span>
                    <span className="text-[#4F8CFF]">Chạm để nhảy tới</span>
                  </div>
                  <input
                    aria-label={`Phụ đề gốc câu ${sub.id}`}
                    value={sub.original}
                    onChange={(e) => store.updateSubtitle(sub.id, 'original', e.target.value)}
                    className="w-full px-2 py-1 rounded bg-[#171A23] border border-[#262B38] text-xs text-[#8B93A7]"
                  />
                  <input
                    aria-label={`Phụ đề dịch câu ${sub.id}`}
                    value={sub.translated}
                    onChange={(e) => store.updateSubtitle(sub.id, 'translated', e.target.value)}
                    className="w-full px-2 py-1 rounded bg-[#171A23] border border-[#262B38] focus:border-[#7C5CFF] text-xs font-medium text-[#E6E8EE]"
                  />
                </div>
              ))}
            </div>
          </Card>
        </section>
      </div>

      {/* BOTTOM BAR: 4-Step Stepper + Start CTA + Realtime Progress */}
      <footer className="px-4 py-2.5 bg-[#171A23] border-t border-[#262B38] flex flex-wrap items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-2">
          {['1. Bóc băng', '2. Dịch phụ đề', '3. Tạo giọng AI', '4. Xuất 1080p'].map((label, idx) => (
            <div key={label} className="flex items-center gap-1.5 px-2.5 py-1 rounded-[8px] bg-[#0F1117] border border-[#262B38] text-xs">
              <span className="font-semibold">{label}</span>
              <StatusBadge status={store.steps[idx]} />
            </div>
          ))}
        </div>

        <div className="flex items-center gap-3 flex-1 max-w-md">
          <div className="flex-1 h-2 rounded-full bg-[#0F1117] overflow-hidden border border-[#262B38]">
            <div
              className="h-full bg-gradient-to-r from-[#7C5CFF] to-[#4F8CFF] transition-all duration-300"
              style={{ width: `${store.overallProgress}%` }}
            />
          </div>
          <span className="text-xs text-[#8B93A7] whitespace-nowrap">{store.etaText}</span>
        </div>

        <div className="flex items-center gap-2">
          {store.isProcessing && (
            <SecondaryButton onClick={store.cancelPipelineMock} className="text-[#FF5C5C] border-[#FF5C5C]/40">
              ⏹ Hủy
            </SecondaryButton>
          )}
          <PrimaryButton onClick={store.startPipelineMock} disabled={store.isProcessing}>
            {store.isProcessing ? '⟳ Đang xử lý...' : '▶ Bắt đầu xử lý'}
          </PrimaryButton>
        </div>
      </footer>
    </div>
  );
};
