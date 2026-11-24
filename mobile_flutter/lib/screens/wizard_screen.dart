import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../state/studio_controller.dart';
import '../theme/app_tokens.dart';
import '../widgets/shared_widgets.dart';

class WizardScreen extends StatefulWidget {
  final StudioController controller;
  const WizardScreen({super.key, required this.controller});

  @override
  State<WizardScreen> createState() => _WizardScreenState();
}

class _WizardScreenState extends State<WizardScreen> {
  int _step = 0; // 0: Chọn video, 1: Cấu hình, 2: Xử lý, 3: Kết quả
  String _subTab = 'trans'; // 'orig' | 'trans'

  @override
  Widget build(BuildContext context) {
    final c = widget.controller;
    return Scaffold(
      appBar: AppBar(
        title: Text('Tạo dự án · Bước ${_step + 1}/4'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(6),
          child: LinearProgressIndicator(
            value: (_step + 1) / 4.0,
            backgroundColor: AppTokens.card,
            color: AppTokens.purple,
          ),
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(child: _buildStepContent(c)),
            // One-handed Bottom Thumb Zone Action Bar (>=48pt)
            Container(
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 14),
              decoration: const BoxDecoration(
                color: AppTokens.card,
                border: Border(top: BorderSide(color: AppTokens.border)),
              ),
              child: Row(
                children: [
                  if (_step > 0) ...[
                    Expanded(
                      child: SizedBox(
                        height: AppTokens.minTouch,
                        child: OutlinedButton(
                          onPressed: () => setState(() => _step--),
                          child: const Text('Quay lại'),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],
                  Expanded(
                    flex: 2,
                    child: GradientButton(
                      label: _step == 3 ? 'Xuất 1080p & Lưu' : 'Tiếp tục',
                      icon: _step == 3 ? Icons.check_circle_rounded : Icons.arrow_forward_rounded,
                      onPressed: () {
                        if (_step < 3) {
                          setState(() => _step++);
                        } else {
                          c.triggerPushNotification('🎉 Đã xuất video 1080p và lưu vào thư viện!');
                          Navigator.of(context).pop();
                        }
                      },
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStepContent(StudioController c) {
    if (_step == 0) {
      return ListView(
        padding: const EdgeInsets.all(16),
        children: [
          StudioCard(
            child: Column(
              children: [
                Container(
                  height: 170,
                  decoration: BoxDecoration(
                    color: AppTokens.bg,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  alignment: Alignment.center,
                  child: const Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.play_circle_fill_rounded, size: 52, color: AppTokens.purple),
                      SizedBox(height: 8),
                      Text('snaptik_review_clip.mp4', style: TextStyle(fontWeight: FontWeight.w700)),
                      Text('Thời lượng: 00:36 · 1920×1080', style: TextStyle(fontSize: 12, color: AppTokens.textSecondary)),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          _pickOption(Icons.photo_library_rounded, 'Chọn video từ Thư viện'),
          const SizedBox(height: 10),
          _pickOption(Icons.videocam_rounded, 'Quay video mới bằng Camera'),
          const SizedBox(height: 10),
          _pickOption(Icons.link_rounded, 'Dán link TikTok / Douyin / YouTube'),
        ],
      );
    }

    if (_step == 1) {
      final curVoice = c.voices.firstWhere((v) => v.id == c.selectedVoiceId, orElse: () => c.voices.first);
      return ListView(
        padding: const EdgeInsets.all(16),
        children: [
          StudioCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Ngôn ngữ & Phong cách dịch', style: TextStyle(fontWeight: FontWeight.w700)),
                const SizedBox(height: 8),
                Text('${c.sourceLang} → ${c.targetLang} · Phong cách: ${c.translateStyle}',
                    style: const TextStyle(fontSize: 13, color: AppTokens.textSecondary)),
              ],
            ),
          ),
          const SizedBox(height: 12),
          StudioCard(
            onTap: () => _openVoiceBottomSheet(c),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Giọng đọc AI (Chạm để đổi & nghe thử)',
                          style: TextStyle(fontSize: 12, color: AppTokens.textSecondary)),
                      const SizedBox(height: 4),
                      Text('${curVoice.name} · ${curVoice.engine}',
                          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15)),
                    ],
                  ),
                ),
                const Icon(Icons.expand_less_rounded, color: AppTokens.blue),
              ],
            ),
          ),
          const SizedBox(height: 12),
          StudioCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Tốc độ giọng: ${(c.voiceSpeed * 100).round()}%'),
                Slider(
                  value: c.voiceSpeed,
                  min: 0.7,
                  max: 1.5,
                  onChanged: (v) => setState(() => c.voiceSpeed = v),
                ),
                Text('Âm gốc / Nhạc nền BGM: ${(c.origVolume * 100).round()}%'),
                Slider(
                  value: c.origVolume,
                  min: 0.0,
                  max: 1.0,
                  onChanged: (v) => setState(() => c.origVolume = v),
                ),
                Text('Âm lượng giọng AI: ${(c.voiceVolume * 100).round()}%'),
                Slider(
                  value: c.voiceVolume,
                  min: 0.5,
                  max: 2.0,
                  onChanged: (v) => setState(() => c.voiceVolume = v),
                ),
              ],
            ),
          ),
        ],
      );
    }

    if (_step == 2) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const SizedBox(
                width: 104,
                height: 104,
                child: CircularProgressIndicator(value: 0.76, strokeWidth: 8, color: AppTokens.purple),
              ),
              const SizedBox(height: 20),
              const Text('76% · Bước 3/4: Đang tổng hợp giọng đọc AI',
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
              const SizedBox(height: 8),
              const Text('Thời gian còn lại: ~8 giây',
                  style: TextStyle(color: AppTokens.textSecondary, fontSize: 13)),
              const SizedBox(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  OutlinedButton.icon(
                    onPressed: () => setState(() => _step = 1),
                    icon: const Icon(Icons.cancel_outlined, color: AppTokens.error),
                    label: const Text('Hủy', style: TextStyle(color: AppTokens.error)),
                  ),
                  const SizedBox(width: 12),
                  OutlinedButton.icon(
                    onPressed: () {
                      c.triggerPushNotification('⏳ Đang xử lý ngầm dự án của bạn...');
                      Navigator.of(context).pop();
                    },
                    icon: const Icon(Icons.minimize_rounded),
                    label: const Text('Chạy nền'),
                  ),
                ],
              ),
            ],
          ),
        ),
      );
    }

    // Step 3: Result Player + Subtitle Tabs + Export/Share/Save
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        StudioCard(
          child: Column(
            children: [
              Container(
                height: 150,
                decoration: BoxDecoration(
                  color: AppTokens.bg,
                  borderRadius: BorderRadius.circular(12),
                ),
                alignment: Alignment.center,
                child: const Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.check_circle_rounded, size: 42, color: AppTokens.success),
                    SizedBox(height: 6),
                    Text('Xem trước bản lồng tiếng 1080p 60fps', style: TextStyle(fontWeight: FontWeight.w700)),
                  ],
                ),
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => HapticFeedback.lightImpact(),
                      icon: const Icon(Icons.share_rounded, size: 18),
                      label: const Text('Chia sẻ'),
                    ),
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () => HapticFeedback.lightImpact(),
                      icon: const Icon(Icons.download_rounded, size: 18),
                      label: const Text('Lưu thư viện'),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: ChoiceChip(
                label: const Text('Phụ đề dịch (Sửa trực tiếp)'),
                selected: _subTab == 'trans',
                onSelected: (_) => setState(() => _subTab = 'trans'),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: ChoiceChip(
                label: const Text('Phụ đề gốc'),
                selected: _subTab == 'orig',
                onSelected: (_) => setState(() => _subTab = 'orig'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),
        ...c.subtitles.map(
          (s) => Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: StudioCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('#${s.id} · ${s.timeRange}', style: const TextStyle(fontSize: 11, color: AppTokens.textSecondary)),
                  const SizedBox(height: 4),
                  TextFormField(
                    key: ValueKey('${s.id}_$_subTab'),
                    initialValue: _subTab == 'trans' ? s.translated : s.original,
                    onChanged: (v) {
                      if (_subTab == 'trans') {
                        s.translated = v;
                      } else {
                        s.original = v;
                      }
                    },
                    style: const TextStyle(fontSize: 14),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _pickOption(IconData icon, String title) {
    return StudioCard(
      onTap: () => HapticFeedback.selectionClick(),
      child: Row(
        children: [
          Icon(icon, color: AppTokens.blue),
          const SizedBox(width: 12),
          Expanded(child: Text(title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14))),
          const Icon(Icons.chevron_right_rounded, color: AppTokens.textSecondary),
        ],
      ),
    );
  }

  void _openVoiceBottomSheet(StudioController c) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTokens.card,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) {
        return ListView(
          shrinkWrap: true,
          padding: const EdgeInsets.all(16),
          children: [
            const Text('Chọn giọng đọc AI', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800)),
            const SizedBox(height: 10),
            ...c.voices.map(
              (v) => ListTile(
                contentPadding: const EdgeInsets.symmetric(horizontal: 8),
                title: Text(v.name, style: const TextStyle(fontWeight: FontWeight.w700)),
                subtitle: Text('${v.langGroup} · ${v.engine}'),
                trailing: IconButton(
                  constraints: const BoxConstraints(minWidth: 44, minHeight: 44),
                  icon: const Icon(Icons.volume_up_rounded, color: AppTokens.blue),
                  onPressed: () => HapticFeedback.lightImpact(),
                ),
                onTap: () {
                  c.selectVoice(v.id);
                  setState(() {});
                  Navigator.pop(context);
                },
              ),
            ),
          ],
        );
      },
    );
  }
}
