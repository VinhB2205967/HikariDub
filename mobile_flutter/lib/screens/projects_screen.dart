import 'package:flutter/material.dart';
import '../state/studio_controller.dart';
import '../theme/app_tokens.dart';
import '../widgets/shared_widgets.dart';

class ProjectsScreen extends StatefulWidget {
  final StudioController controller;
  const ProjectsScreen({super.key, required this.controller});

  @override
  State<ProjectsScreen> createState() => _ProjectsScreenState();
}

class _ProjectsScreenState extends State<ProjectsScreen> {
  String _filter = 'all'; // 'all' | 'processing' | 'done' | 'error'
  String _query = '';

  @override
  Widget build(BuildContext context) {
    final items = widget.controller.projects.where((p) {
      final matchFilter = _filter == 'all' || p.status == _filter;
      final matchQuery = p.title.toLowerCase().contains(_query.toLowerCase());
      return matchFilter && matchQuery;
    }).toList();

    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 92),
      children: [
        const Text('Quản lý Dự án', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800)),
        const SizedBox(height: 12),
        TextField(
          onChanged: (v) => setState(() => _query = v),
          decoration: InputDecoration(
            hintText: 'Tìm kiếm dự án video...',
            prefixIcon: const Icon(Icons.search_rounded),
            filled: true,
            fillColor: AppTokens.card,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(AppTokens.radius),
              borderSide: const BorderSide(color: AppTokens.border),
            ),
          ),
        ),
        const SizedBox(height: 12),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              for (final (id, lbl) in [
                ('all', 'Tất cả'),
                ('processing', 'Đang xử lý'),
                ('done', 'Xong'),
                ('error', 'Lỗi'),
              ])
                Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(lbl),
                    selected: _filter == id,
                    onSelected: (_) => setState(() => _filter = id),
                  ),
                ),
            ],
          ),
        ),
        const SizedBox(height: 14),
        if (items.isEmpty)
          const EmptyStateIllustration(
            icon: Icons.video_collection_outlined,
            title: 'Không tìm thấy dự án nào',
            subtitle: 'Thử đổi bộ lọc hoặc bấm nút "+" ở giữa thanh dưới để tạo dự án mới.',
          )
        else
          GridView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: items.length,
            gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
              maxCrossAxisExtent: 220,
              mainAxisExtent: 196,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
            ),
            itemBuilder: (_, idx) {
              final p = items[idx];
              return StudioCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Container(
                      height: 74,
                      decoration: BoxDecoration(
                        color: AppTokens.bg,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      alignment: Alignment.center,
                      child: const Icon(Icons.movie_rounded, color: AppTokens.purple, size: 30),
                    ),
                    Text(
                      p.title,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
                    ),
                    if (p.status == 'error')
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const StatusChip(status: 'error'),
                          TextButton(
                            onPressed: () {
                              widget.controller.retryProject(p.id);
                              setState(() {});
                            },
                            child: const Text('Thử lại', style: TextStyle(fontSize: 12, color: AppTokens.error)),
                          ),
                        ],
                      )
                    else
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(p.duration, style: const TextStyle(fontSize: 11, color: AppTokens.textSecondary)),
                          StatusChip(status: p.status),
                        ],
                      ),
                  ],
                ),
              );
            },
          ),
      ],
    );
  }
}
