import 'package:flutter/material.dart';
import '../state/studio_controller.dart';
import '../theme/app_tokens.dart';
import '../widgets/shared_widgets.dart';
import 'subtitle_editor_screen.dart';

class HomeScreen extends StatelessWidget {
  final StudioController controller;
  final VoidCallback onStartWizard;
  const HomeScreen({
    super.key,
    required this.controller,
    required this.onStartWizard,
  });

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 92),
      children: [
        // Push Notification Banner when a background job completes
        if (controller.pushBannerMessage != null)
          Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: AppTokens.success.withOpacity(0.16),
              borderRadius: BorderRadius.circular(AppTokens.radius),
              border: Border.all(color: AppTokens.success),
            ),
            child: Row(
              children: [
                const Icon(Icons.notifications_active_rounded, color: AppTokens.success, size: 20),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    controller.pushBannerMessage!,
                    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                  ),
                ),
                IconButton(
                  constraints: const BoxConstraints(minWidth: 44, minHeight: 44),
                  icon: const Icon(Icons.close_rounded, size: 18),
                  onPressed: controller.clearPushBanner,
                ),
              ],
            ),
          ),

        // Edge-case Alert Banner (Offline / Video too long / Low storage)
        if (controller.isOffline || controller.lowStorageWarning || controller.videoTooLongWarning)
          Container(
            margin: const EdgeInsets.only(bottom: 12),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTokens.warning.withOpacity(0.15),
              borderRadius: BorderRadius.circular(AppTokens.radius),
              border: Border.all(color: AppTokens.warning),
            ),
            child: Row(
              children: [
                const Icon(Icons.warning_amber_rounded, color: AppTokens.warning),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    controller.isOffline
                        ? 'Đang ngoại tuyến: Tự động dùng giọng Piper Local Offline.'
                        : controller.lowStorageWarning
                            ? 'Bộ nhớ máy sắp đầy (<500MB). Hãy dọn bộ nhớ đệm trước khi xuất 1080p.'
                            : 'Video dài >30 phút: Hệ thống sẽ tự chia đoạn để xử lý ổn định.',
                    style: const TextStyle(fontSize: 12, color: AppTokens.textPrimary),
                  ),
                ),
              ],
            ),
          ),

        const Text(
          'Xin chào, Creator 👋',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800),
        ),
        const SizedBox(height: 4),
        const Text(
          'Phòng thu lồng tiếng AI bỏ túi — tối ưu thao tác một tay.',
          style: TextStyle(fontSize: 13, color: AppTokens.textSecondary),
        ),
        const SizedBox(height: 18),

        // Recent Projects Horizontal Carousel
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Dự án gần đây', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            TextButton(
              onPressed: () {
                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => SubtitleEditorScreen(controller: controller),
                  ),
                );
              },
              child: const Text('Sửa phụ đề nhanh →', style: TextStyle(fontSize: 13)),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SizedBox(
          height: 136,
          child: controller.isLoadingSkeleton
              ? ListView(
                  scrollDirection: Axis.horizontal,
                  children: const [
                    SizedBox(width: 220, child: SkeletonCard(height: 130)),
                    SizedBox(width: 12),
                    SizedBox(width: 220, child: SkeletonCard(height: 130)),
                  ],
                )
              : ListView.separated(
                  scrollDirection: Axis.horizontal,
                  itemCount: controller.projects.length,
                  separatorBuilder: (_, __) => const SizedBox(width: 12),
                  itemBuilder: (_, idx) {
                    final p = controller.projects[idx];
                    return SizedBox(
                      width: 230,
                      child: StudioCard(
                        onTap: onStartWizard,
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              p.title,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                              style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14),
                            ),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Text(
                                  '⏱ ${p.duration}',
                                  style: const TextStyle(fontSize: 12, color: AppTokens.textSecondary),
                                ),
                                StatusChip(status: p.status),
                              ],
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),
        ),
        const SizedBox(height: 18),

        // Quick Tips Card
        const StudioCard(
          child: Row(
            children: [
              Icon(Icons.lightbulb_rounded, color: AppTokens.warning, size: 24),
              SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Mẹo nhanh: Trong trình sửa phụ đề, vuốt sang trái để xóa câu hoặc bấm biểu tượng gộp để nối 2 câu ngắn.',
                  style: TextStyle(fontSize: 13, height: 1.4),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // Quick Edge-case Simulator Bar for QA testing
        StudioCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Kiểm thử trạng thái hệ thống (QA):',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: AppTokens.textSecondary)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: [
                  FilterChip(
                    label: const Text('Mất mạng', style: TextStyle(fontSize: 12)),
                    selected: controller.isOffline,
                    onSelected: (v) => controller.toggleEdgeCase(offline: v),
                  ),
                  FilterChip(
                    label: const Text('Video quá dài', style: TextStyle(fontSize: 12)),
                    selected: controller.videoTooLongWarning,
                    onSelected: (v) => controller.toggleEdgeCase(longVideo: v),
                  ),
                  FilterChip(
                    label: const Text('Hết dung lượng', style: TextStyle(fontSize: 12)),
                    selected: controller.lowStorageWarning,
                    onSelected: (v) => controller.toggleEdgeCase(lowStorage: v),
                  ),
                  ActionChip(
                    label: const Text('Bắn thông báo xong', style: TextStyle(fontSize: 12)),
                    onPressed: () => controller.triggerPushNotification('🎉 Dự án "Review Anime Tập 12" đã xuất 1080p xong!'),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 20),

        // Thumb-zone Primary Action Button
        GradientButton(
          label: 'Tạo lồng tiếng mới',
          icon: Icons.add_circle_outline_rounded,
          onPressed: onStartWizard,
        ),
      ],
    );
  }
}
