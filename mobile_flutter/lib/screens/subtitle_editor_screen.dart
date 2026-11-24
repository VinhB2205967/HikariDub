import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../state/studio_controller.dart';
import '../theme/app_tokens.dart';
import '../widgets/shared_widgets.dart';

class SubtitleEditorScreen extends StatefulWidget {
  final StudioController controller;
  const SubtitleEditorScreen({super.key, required this.controller});

  @override
  State<SubtitleEditorScreen> createState() => _SubtitleEditorScreenState();
}

class _SubtitleEditorScreenState extends State<SubtitleEditorScreen> {
  final TextEditingController _findCtrl = TextEditingController();
  final TextEditingController _repCtrl = TextEditingController();
  int? _playingId;

  @override
  void dispose() {
    _findCtrl.dispose();
    _repCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final subs = widget.controller.subtitles;
    return Scaffold(
      appBar: AppBar(
        title: const Text('Trình sửa phụ đề'),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Find & Replace Toolbar
            Container(
              padding: const EdgeInsets.all(12),
              decoration: const BoxDecoration(
                color: AppTokens.card,
                border: Border(bottom: BorderSide(color: AppTokens.border)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _findCtrl,
                      decoration: const InputDecoration(
                        hintText: 'Tìm từ...',
                        isDense: true,
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller: _repCtrl,
                      decoration: const InputDecoration(
                        hintText: 'Thay bằng...',
                        isDense: true,
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  SizedBox(
                    height: AppTokens.minTouch,
                    child: ElevatedButton(
                      onPressed: () {
                        final count = widget.controller.replaceAllSubtitles(
                          _findCtrl.text,
                          _repCtrl.text,
                        );
                        setState(() {});
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Đã thay thế $count dòng phụ đề.')),
                        );
                      },
                      style: ElevatedButton.styleFrom(backgroundColor: AppTokens.purple),
                      child: const Text('Thay', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w700)),
                    ),
                  ),
                ],
              ),
            ),

            // Subtitle List (Tap to play segment, Swipe left to delete, Button to merge)
            Expanded(
              child: subs.isEmpty
                  ? const EmptyStateIllustration(
                      icon: Icons.subtitles_off_rounded,
                      title: 'Danh sách phụ đề trống',
                      subtitle: 'Hãy bóc băng video hoặc nạp file SRT để chỉnh sửa.',
                    )
                  : ListView.builder(
                      padding: const EdgeInsets.all(14),
                      itemCount: subs.length,
                      itemBuilder: (_, idx) {
                        final s = subs[idx];
                        final isPlaying = _playingId == s.id;
                        return Dismissible(
                          key: ValueKey(s.id),
                          direction: DismissDirection.endToStart,
                          onDismissed: (_) => setState(() => widget.controller.deleteSubtitle(idx)),
                          background: Container(
                            margin: const EdgeInsets.only(bottom: 10),
                            padding: const EdgeInsets.only(right: 20),
                            alignment: Alignment.centerRight,
                            decoration: BoxDecoration(
                              color: AppTokens.error.withOpacity(0.25),
                              borderRadius: BorderRadius.circular(AppTokens.radius),
                            ),
                            child: const Icon(Icons.delete_forever_rounded, color: AppTokens.error),
                          ),
                          child: Padding(
                            padding: const EdgeInsets.only(bottom: 10),
                            child: StudioCard(
                              onTap: () {
                                HapticFeedback.selectionClick();
                                setState(() => _playingId = s.id);
                              },
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      Row(
                                        children: [
                                          Icon(
                                            isPlaying ? Icons.pause_circle_filled_rounded : Icons.play_circle_fill_rounded,
                                            color: isPlaying ? AppTokens.success : AppTokens.blue,
                                            size: 20,
                                          ),
                                          const SizedBox(width: 6),
                                          Text(
                                            '#${s.id} · ${s.timeRange}',
                                            style: const TextStyle(fontSize: 12, color: AppTokens.textSecondary),
                                          ),
                                        ],
                                      ),
                                      if (idx + 1 < subs.length)
                                        TextButton.icon(
                                          onPressed: () => setState(() => widget.controller.mergeSubtitleWithNext(idx)),
                                          icon: const Icon(Icons.merge_type_rounded, size: 16),
                                          label: const Text('Gộp dòng dưới', style: TextStyle(fontSize: 11)),
                                        ),
                                    ],
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    s.original,
                                    style: const TextStyle(fontSize: 12, color: AppTokens.textSecondary),
                                  ),
                                  const SizedBox(height: 6),
                                  TextFormField(
                                    initialValue: s.translated,
                                    onChanged: (val) => s.translated = val,
                                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                                    decoration: const InputDecoration(
                                      isDense: true,
                                      contentPadding: EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                                      border: OutlineInputBorder(),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
