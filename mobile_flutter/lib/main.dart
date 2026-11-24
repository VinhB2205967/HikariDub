// Hikari Tsukimi – AI Dubbing Studio (Mobile-First Flutter Application for iOS & Android)
// One-handed ergonomic UX, 44x44pt touch targets, #0F1117 dark theme, #171A23 cards,
// 4-step Creation Wizard, Swipeable Subtitle Editor, Voice Library & Settings.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));
  runApp(const HikariMobileApp());
}

class AppTokens {
  static const Color bg = Color(0xFF0F1117);
  static const Color card = Color(0xFF171A23);
  static const Color border = Color(0xFF262B38);
  static const Color textPrimary = Color(0xFFE6E8EE);
  static const Color textSecondary = Color(0xFF8B93A7);
  static const Color purple = Color(0xFF7C5CFF);
  static const Color blue = Color(0xFF4F8CFF);
  static const Color success = Color(0xFF2ECC71);
  static const Color warning = Color(0xFFF5A524);
  static const Color error = Color(0xFFFF5C5C);
  static const double radius = 14.0;

  static const LinearGradient brandGradient = LinearGradient(
    colors: [purple, blue],
    begin: Alignment.centerLeft,
    end: Alignment.centerRight,
  );
}

class SubtitleItem {
  int index;
  String timeRange;
  String original;
  String translated;
  SubtitleItem(this.index, this.timeRange, this.original, this.translated);
}

class ProjectItem {
  final String title;
  final String duration;
  final String status; // 'processing' | 'done' | 'error'
  final double progress;
  const ProjectItem(this.title, this.duration, this.status, this.progress);
}

class HikariMobileApp extends StatelessWidget {
  const HikariMobileApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Hikari Tsukimi Mobile',
      debugShowCheckedModeBanner: false,
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: AppTokens.bg,
        cardColor: AppTokens.card,
        colorScheme: const ColorScheme.dark(
          primary: AppTokens.purple,
          secondary: AppTokens.blue,
          surface: AppTokens.card,
          error: AppTokens.error,
        ),
      ),
      home: const MobileShell(),
    );
  }
}

class MobileShell extends StatefulWidget {
  const MobileShell({super.key});

  @override
  State<MobileShell> createState() => _MobileShellState();
}

class _MobileShellState extends State<MobileShell> {
  int _tabIndex = 0;

  final List<ProjectItem> _projects = const [
    ProjectItem('Review Anime Tập 12.mp4', '02:15', 'done', 1.0),
    ProjectItem('Vlog Du Lịch Nhật Bản.mp4', '04:40', 'processing', 0.64),
    ProjectItem('Highlight Game Chung Kết.mp4', '01:08', 'error', 0.35),
  ];

  void _openCreateWizard() {
    HapticFeedback.lightImpact();
    Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const CreateProjectWizardScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      HomeScreen(projects: _projects, onCreateNew: _openCreateWizard),
      ProjectsScreen(projects: _projects),
      const VoiceLibraryScreen(),
      const SettingsScreen(),
    ];

    return Scaffold(
      body: SafeArea(child: pages[_tabIndex]),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      floatingActionButton: SizedBox(
        width: 56,
        height: 56,
        child: FloatingActionButton(
          onPressed: _openCreateWizard,
          backgroundColor: AppTokens.purple,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
          child: const Icon(Icons.add_rounded, size: 30, color: Colors.white),
        ),
      ),
      bottomNavigationBar: BottomAppBar(
        color: AppTokens.card,
        shape: const CircularNotchedRectangle(),
        notchMargin: 8,
        child: SizedBox(
          height: 62,
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _navBtn(0, Icons.home_rounded, 'Trang chủ'),
              _navBtn(1, Icons.video_library_rounded, 'Dự án'),
              const SizedBox(width: 44),
              _navBtn(2, Icons.record_voice_over_rounded, 'Giọng'),
              _navBtn(3, Icons.settings_rounded, 'Cài đặt'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _navBtn(int idx, IconData icon, String label) {
    final active = _tabIndex == idx;
    return InkWell(
      onTap: () {
        HapticFeedback.selectionClick();
        setState(() => _tabIndex = idx);
      },
      borderRadius: BorderRadius.circular(12),
      child: ConstrainedBox(
        constraints: const BoxConstraints(minWidth: 64, minHeight: 48),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 22, color: active ? AppTokens.purple : AppTokens.textSecondary),
            const SizedBox(height: 2),
            Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 11,
                fontWeight: active ? FontWeight.w700 : FontWeight.w500,
                color: active ? AppTokens.textPrimary : AppTokens.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class HomeScreen extends StatelessWidget {
  final List<ProjectItem> projects;
  final VoidCallback onCreateNew;
  const HomeScreen({super.key, required this.projects, required this.onCreateNew});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('Xin chào, Creator 👋', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800)),
        const SizedBox(height: 4),
        const Text('Biến mọi video thành bản lồng tiếng chuẩn 1080p chỉ với 1 chạm.',
            style: TextStyle(color: AppTokens.textSecondary, fontSize: 13)),
        const SizedBox(height: 16),
        const Text('Dự án gần đây', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
        const SizedBox(height: 10),
        SizedBox(
          height: 128,
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: projects.length,
            separatorBuilder: (_, __) => const SizedBox(width: 12),
            itemBuilder: (_, i) {
              final p = projects[i];
              return Container(
                width: 220,
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppTokens.card,
                  borderRadius: BorderRadius.circular(AppTokens.radius),
                  border: Border.all(color: AppTokens.border),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(p.title, maxLines: 2, overflow: TextOverflow.ellipsis,
                        style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 14)),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(p.duration, style: const TextStyle(color: AppTokens.textSecondary, fontSize: 12)),
                        _statusBadge(p.status),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
        ),
        const SizedBox(height: 20),
        Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppTokens.card,
            borderRadius: BorderRadius.circular(AppTokens.radius),
            border: Border.all(color: AppTokens.border),
          ),
          child: const Row(
            children: [
              Icon(Icons.tips_and_updates_rounded, color: AppTokens.warning),
              SizedBox(width: 12),
              Expanded(
                child: Text(
                  'Mẹo nhanh: Bật "Lọc giọng BGM" ở Bước 2 để giữ nguyên nhạc nền gốc khi lồng tiếng.',
                  style: TextStyle(fontSize: 13, color: AppTokens.textPrimary),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 28),
        // Bottom thumb-zone primary CTA
        InkWell(
          onTap: onCreateNew,
          borderRadius: BorderRadius.circular(AppTokens.radius),
          child: Container(
            height: 54,
            decoration: BoxDecoration(
              gradient: AppTokens.brandGradient,
              borderRadius: BorderRadius.circular(AppTokens.radius),
            ),
            alignment: Alignment.center,
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.auto_awesome_rounded, color: Colors.white),
                SizedBox(width: 8),
                Text('Tạo lồng tiếng mới', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w800, color: Colors.white)),
              ],
            ),
          ),
        ),
      ],
    );
  }

  static Widget _statusBadge(String st) {
    final map = {
      'done': ('Hoàn tất', AppTokens.success),
      'processing': ('Đang xử lý', AppTokens.blue),
      'error': ('Lỗi', AppTokens.error),
    };
    final item = map[st] ?? ('Chờ', AppTokens.textSecondary);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: item.$2.withOpacity(0.16),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(item.$1, style: TextStyle(color: item.$2, fontSize: 11, fontWeight: FontWeight.w700)),
    );
  }
}

class CreateProjectWizardScreen extends StatefulWidget {
  const CreateProjectWizardScreen({super.key});

  @override
  State<CreateProjectWizardScreen> createState() => _CreateProjectWizardScreenState();
}

class _CreateProjectWizardScreenState extends State<CreateProjectWizardScreen> {
  int _step = 0; // 0: Chọn video, 1: Cấu hình, 2: Xử lý, 3: Kết quả & Sửa phụ đề
  String _selectedVoice = 'Ban Mai (Nữ · Local)';
  double _speed = 1.0;
  double _origVol = 0.35;
  double _voiceVol = 1.0;

  final List<SubtitleItem> _subs = [
    SubtitleItem(1, '00:01 → 00:04', 'Welcome to Hikari AI Studio.', 'Chào mừng đến với Hikari AI Studio.'),
    SubtitleItem(2, '00:04 → 00:08', 'Dub videos on mobile with one hand.', 'Lồng tiếng video trên điện thoại chỉ bằng một tay.'),
    SubtitleItem(3, '00:08 → 00:12', 'Export crisp 1080p 60fps output.', 'Xuất video 1080p 60fps sắc nét.'),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: AppTokens.bg,
        title: Text('Tạo dự án · Bước ${_step + 1}/4', style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
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
            Expanded(child: _buildStepBody()),
            // Ergonomic bottom action bar (48pt+ touch target)
            Container(
              padding: const EdgeInsets.fromLTRB(16, 10, 16, 14),
              decoration: const BoxDecoration(
                color: AppTokens.card,
                border: Border(top: BorderSide(color: AppTokens.border)),
              ),
              child: Row(
                children: [
                  if (_step > 0)
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => setState(() => _step--),
                        style: OutlinedButton.styleFrom(minimumSize: const Size(0, 48)),
                        child: const Text('Quay lại'),
                      ),
                    ),
                  if (_step > 0) const SizedBox(width: 12),
                  Expanded(
                    flex: 2,
                    child: ElevatedButton(
                      onPressed: () {
                        HapticFeedback.mediumImpact();
                        if (_step < 3) {
                          setState(() => _step++);
                        } else {
                          Navigator.of(context).pop();
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppTokens.purple,
                        minimumSize: const Size(0, 48),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                      child: Text(
                        _step == 3 ? 'Xuất 1080p & Lưu' : 'Tiếp tục',
                        style: const TextStyle(fontWeight: FontWeight.w700, color: Colors.white),
                      ),
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

  Widget _buildStepBody() {
    if (_step == 0) {
      return ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            height: 190,
            decoration: BoxDecoration(
              color: AppTokens.card,
              borderRadius: BorderRadius.circular(AppTokens.radius),
              border: Border.all(color: AppTokens.border),
            ),
            alignment: Alignment.center,
            child: const Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.play_circle_fill_rounded, size: 48, color: AppTokens.purple),
                SizedBox(height: 8),
                Text('snaptik_demo_clip.mp4 · 00:36 · 1080p', style: TextStyle(fontWeight: FontWeight.w600)),
              ],
            ),
          ),
          const SizedBox(height: 16),
          _sourceBtn(Icons.photo_library_rounded, 'Chọn từ Thư viện máy'),
          const SizedBox(height: 10),
          _sourceBtn(Icons.videocam_rounded, 'Quay video mới'),
          const SizedBox(height: 10),
          _sourceBtn(Icons.link_rounded, 'Dán link TikTok / Douyin / YouTube'),
        ],
      );
    }
    if (_step == 1) {
      return ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Ngôn ngữ: Tự động → Tiếng Việt', style: TextStyle(fontWeight: FontWeight.w700)),
          const SizedBox(height: 12),
          ListTile(
            tileColor: AppTokens.card,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppTokens.radius)),
            title: const Text('Giọng đọc AI'),
            subtitle: Text(_selectedVoice),
            trailing: const Icon(Icons.keyboard_arrow_up_rounded),
            onTap: _showVoiceBottomSheet,
          ),
          const SizedBox(height: 14),
          Text('Tốc độ đọc: ${(_speed * 100).round()}%'),
          Slider(value: _speed, min: 0.7, max: 1.5, onChanged: (v) => setState(() => _speed = v)),
          Text('Âm gốc (BGM): ${(_origVol * 100).round()}%'),
          Slider(value: _origVol, min: 0.0, max: 1.0, onChanged: (v) => setState(() => _origVol = v)),
          Text('Giọng AI: ${(_voiceVol * 100).round()}%'),
          Slider(value: _voiceVol, min: 0.5, max: 2.0, onChanged: (v) => setState(() => _voiceVol = v)),
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
                width: 96,
                height: 96,
                child: CircularProgressIndicator(value: 0.72, strokeWidth: 8, color: AppTokens.purple),
              ),
              const SizedBox(height: 18),
              const Text('72% · Đang tạo giọng đọc AI (Bước 3/4)',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
              const SizedBox(height: 6),
              const Text('Còn khoảng ~9 giây · Hỗ trợ chạy nền',
                  style: TextStyle(color: AppTokens.textSecondary)),
              const SizedBox(height: 20),
              OutlinedButton.icon(
                onPressed: () => setState(() => _step = 1),
                icon: const Icon(Icons.close_rounded, color: AppTokens.error),
                label: const Text('Hủy xử lý', style: TextStyle(color: AppTokens.error)),
              ),
            ],
          ),
        ),
      );
    }
    // Step 3: Result & Swipeable Subtitle Editor
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _subs.length,
      itemBuilder: (_, i) {
        final s = _subs[i];
        return Dismissible(
          key: ValueKey(s.index),
          onDismissed: (_) => setState(() => _subs.removeAt(i)),
          background: Container(
            alignment: Alignment.centerRight,
            padding: const EdgeInsets.only(right: 20),
            color: AppTokens.error.withOpacity(0.25),
            child: const Icon(Icons.delete_outline_rounded, color: AppTokens.error),
          ),
          child: Container(
            margin: const EdgeInsets.only(bottom: 10),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTokens.card,
              borderRadius: BorderRadius.circular(AppTokens.radius),
              border: Border.all(color: AppTokens.border),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('#${s.index} · ${s.timeRange} (Chạm để phát, vuốt để xóa)',
                    style: const TextStyle(fontSize: 11, color: AppTokens.textSecondary)),
                const SizedBox(height: 4),
                Text(s.original, style: const TextStyle(fontSize: 12, color: AppTokens.textSecondary)),
                const SizedBox(height: 4),
                TextFormField(
                  initialValue: s.translated,
                  onChanged: (v) => s.translated = v,
                  style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _sourceBtn(IconData icon, String text) {
    return ListTile(
      tileColor: AppTokens.card,
      minVerticalPadding: 14,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(AppTokens.radius),
        side: const BorderSide(color: AppTokens.border),
      ),
      leading: Icon(icon, color: AppTokens.blue),
      title: Text(text, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
      trailing: const Icon(Icons.chevron_right_rounded),
      onTap: () => HapticFeedback.selectionClick(),
    );
  }

  void _showVoiceBottomSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTokens.card,
      builder: (_) {
        final voices = ['Ban Mai (Nữ · Local)', 'Mạnh Dũng (Nam · Local)', 'TikTok VN — Nữ 01', 'TikTok VN — Nam 01'];
        return ListView(
          shrinkWrap: true,
          padding: const EdgeInsets.all(16),
          children: voices
              .map((v) => ListTile(
                    title: Text(v),
                    trailing: IconButton(
                      icon: const Icon(Icons.volume_up_rounded, color: AppTokens.blue),
                      onPressed: () => HapticFeedback.lightImpact(),
                    ),
                    onTap: () {
                      setState(() => _selectedVoice = v);
                      Navigator.pop(context);
                    },
                  ))
              .toList(),
        );
      },
    );
  }
}

class ProjectsScreen extends StatelessWidget {
  final List<ProjectItem> projects;
  const ProjectsScreen({super.key, required this.projects});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('Tất cả dự án', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
        const SizedBox(height: 12),
        ...projects.map((p) => Card(
              color: AppTokens.card,
              margin: const EdgeInsets.only(bottom: 10),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppTokens.radius)),
              child: ListTile(
                minVerticalPadding: 14,
                leading: const Icon(Icons.movie_creation_rounded, color: AppTokens.purple),
                title: Text(p.title, maxLines: 1, overflow: TextOverflow.ellipsis),
                subtitle: Text('Thời lượng: ${p.duration}'),
                trailing: HomeScreen._statusBadge(p.status),
              ),
            )),
      ],
    );
  }
}

class VoiceLibraryScreen extends StatelessWidget {
  const VoiceLibraryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final voices = const [
      ('Ban Mai', 'Tiếng Việt · Nữ (Piper Offline)', true),
      ('Mạnh Dũng', 'Tiếng Việt · Nam (Piper Offline)', true),
      ('TikTok BV074', 'Tiếng Việt · Nữ (SessionID)', false),
      ('Jessie US', 'English · Female (SessionID)', false),
    ];
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('Thư viện giọng đọc AI', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
        const SizedBox(height: 12),
        ...voices.map((v) => Card(
              color: AppTokens.card,
              margin: const EdgeInsets.only(bottom: 10),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(AppTokens.radius)),
              child: ListTile(
                leading: IconButton(
                  icon: const Icon(Icons.play_arrow_rounded, color: AppTokens.blue),
                  onPressed: () => HapticFeedback.lightImpact(),
                ),
                title: Text(v.$1, style: const TextStyle(fontWeight: FontWeight.w700)),
                subtitle: Text(v.$2),
                trailing: Icon(v.$3 ? Icons.favorite_rounded : Icons.favorite_border_rounded,
                    color: v.$3 ? AppTokens.error : AppTokens.textSecondary),
              ),
            )),
      ],
    );
  }
}

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: const [
        Text('Cài đặt hệ thống', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w800)),
        SizedBox(height: 12),
        ListTile(
          tileColor: AppTokens.card,
          leading: Icon(Icons.key_rounded, color: AppTokens.purple),
          title: Text('Gemini API Key & TikTok Session ID'),
          subtitle: Text('•••••••••••••••• (Đã mã hóa an toàn)'),
        ),
        SizedBox(height: 8),
        ListTile(
          tileColor: AppTokens.card,
          leading: Icon(Icons.hd_rounded, color: AppTokens.blue),
          title: Text('Chất lượng xuất video'),
          subtitle: Text('1080p Full HD · 60 FPS (H.264)'),
        ),
        SizedBox(height: 8),
        ListTile(
          tileColor: AppTokens.card,
          leading: Icon(Icons.storage_rounded, color: AppTokens.success),
          title: Text('Bộ nhớ đệm mô hình Offline'),
          subtitle: Text('Đã dùng 1.4 GB / Còn trống 28.5 GB'),
        ),
      ],
    );
  }
}
