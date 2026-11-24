import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../state/studio_controller.dart';
import '../theme/app_tokens.dart';
import '../widgets/shared_widgets.dart';

class VoiceLibraryScreen extends StatelessWidget {
  final StudioController controller;
  const VoiceLibraryScreen({super.key, required this.controller});

  @override
  Widget build(BuildContext context) {
    final groups = <String, List<VoiceModel>>{};
    for (final v in controller.voices) {
      groups.putIfAbsent(v.langGroup, () => []).add(v);
    }

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 92),
      children: [
        const Text('Thư viện Giọng đọc AI', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800)),
        const SizedBox(height: 4),
        const Text('Nhóm theo ngôn ngữ · Chạm để nghe thử hoặc đánh dấu yêu thích.',
            style: TextStyle(fontSize: 13, color: AppTokens.textSecondary)),
        const SizedBox(height: 16),
        for (final entry in groups.entries) ...[
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 6),
            child: Text(
              entry.key,
              style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: AppTokens.blue),
            ),
          ),
          ...entry.value.map(
            (v) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: StudioCard(
                child: Row(
                  children: [
                    IconButton(
                      constraints: const BoxConstraints(minWidth: 44, minHeight: 44),
                      icon: const Icon(Icons.play_circle_fill_rounded, color: AppTokens.purple, size: 30),
                      onPressed: () {
                        HapticFeedback.lightImpact();
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(content: Text('Đang phát mẫu giọng ${v.name}...')),
                        );
                      },
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(v.name, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                          Text(v.engine, style: const TextStyle(fontSize: 12, color: AppTokens.textSecondary)),
                        ],
                      ),
                    ),
                    IconButton(
                      constraints: const BoxConstraints(minWidth: 44, minHeight: 44),
                      icon: Icon(
                        v.isFavorite ? Icons.favorite_rounded : Icons.favorite_border_rounded,
                        color: v.isFavorite ? AppTokens.error : AppTokens.textSecondary,
                      ),
                      onPressed: () => controller.toggleFavoriteVoice(v.id),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ],
    );
  }
}
