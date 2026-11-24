import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'screens/home_screen.dart';
import 'screens/projects_screen.dart';
import 'screens/settings_screen.dart';
import 'screens/voice_library_screen.dart';
import 'screens/wizard_screen.dart';
import 'state/studio_controller.dart';
import 'theme/app_tokens.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));
  runApp(const HikariMobileApp());
}

class HikariMobileApp extends StatefulWidget {
  const HikariMobileApp({super.key});

  @override
  State<HikariMobileApp> createState() => _HikariMobileAppState();
}

class _HikariMobileAppState extends State<HikariMobileApp> {
  final StudioController _controller = StudioController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (_, __) {
        return MaterialApp(
          title: 'Hikari Tsukimi – AI Dubbing Studio',
          debugShowCheckedModeBanner: false,
          theme: AppTokens.buildTheme(),
          home: MobileRootShell(controller: _controller),
        );
      },
    );
  }
}

class MobileRootShell extends StatefulWidget {
  final StudioController controller;
  const MobileRootShell({super.key, required this.controller});

  @override
  State<MobileRootShell> createState() => _MobileRootShellState();
}

class _MobileRootShellState extends State<MobileRootShell> {
  int _tabIndex = 0;

  void _openCreateWizard() {
    HapticFeedback.mediumImpact();
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => WizardScreen(controller: widget.controller),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final pages = [
      HomeScreen(controller: widget.controller, onStartWizard: _openCreateWizard),
      ProjectsScreen(controller: widget.controller),
      VoiceLibraryScreen(controller: widget.controller),
      SettingsScreen(controller: widget.controller),
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
          tooltip: 'Tạo dự án mới',
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
              _buildTabItem(0, Icons.home_rounded, 'Trang chủ'),
              _buildTabItem(1, Icons.video_library_rounded, 'Dự án'),
              const SizedBox(width: 48),
              _buildTabItem(2, Icons.record_voice_over_rounded, 'Giọng'),
              _buildTabItem(3, Icons.settings_rounded, 'Cài đặt'),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTabItem(int index, IconData icon, String label) {
    final selected = _tabIndex == index;
    return InkWell(
      onTap: () {
        HapticFeedback.selectionClick();
        setState(() => _tabIndex = index);
      },
      borderRadius: BorderRadius.circular(12),
      child: ConstrainedBox(
        constraints: const BoxConstraints(minWidth: 64, minHeight: AppTokens.minTouch),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 22, color: selected ? AppTokens.purple : AppTokens.textSecondary),
            const SizedBox(height: 2),
            Text(
              label,
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
              style: TextStyle(
                fontSize: 11,
                fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                color: selected ? AppTokens.textPrimary : AppTokens.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
