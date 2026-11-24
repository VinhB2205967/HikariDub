import 'package:flutter/material.dart';
import '../state/studio_controller.dart';
import '../theme/app_tokens.dart';
import '../widgets/shared_widgets.dart';

class SettingsScreen extends StatefulWidget {
  final StudioController controller;
  const SettingsScreen({super.key, required this.controller});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _hideSecrets = true;

  @override
  Widget build(BuildContext context) {
    final c = widget.controller;
    return ListView(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 92),
      children: [
        const Text('Cài đặt & Bộ nhớ', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800)),
        const SizedBox(height: 14),
        StudioCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('API Key & TikTok Session ID', style: TextStyle(fontWeight: FontWeight.w700)),
                  TextButton(
                    onPressed: () => setState(() => _hideSecrets = !_hideSecrets),
                    child: Text(_hideSecrets ? 'Hiện' : 'Ẩn'),
                  ),
                ],
              ),
              Text(
                _hideSecrets ? 'Gemini API: •••••••••••••••••••••' : 'Gemini API: ${c.apiKey}',
                style: const TextStyle(fontSize: 12, color: AppTokens.textSecondary),
              ),
              const SizedBox(height: 4),
              Text(
                _hideSecrets ? 'Session ID: •••••••••••••••••••••' : 'Session ID: ${c.tiktokSessionId}',
                style: const TextStyle(fontSize: 12, color: AppTokens.textSecondary),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        StudioCard(
          child: Column(
            children: [
              ListTile(
                contentPadding: EdgeInsets.zero,
                leading: const Icon(Icons.hd_rounded, color: AppTokens.blue),
                title: const Text('Chất lượng xuất video'),
                subtitle: Text(c.exportQuality),
              ),
              const Divider(color: AppTokens.border),
              const ListTile(
                contentPadding: EdgeInsets.zero,
                leading: Icon(Icons.language_rounded, color: AppTokens.purple),
                title: Text('Ngôn ngữ hiển thị'),
                subtitle: Text('Tiếng Việt (Mặc định)'),
              ),
              const Divider(color: AppTokens.border),
              const ListTile(
                contentPadding: EdgeInsets.zero,
                leading: Icon(Icons.dark_mode_rounded, color: AppTokens.warning),
                title: Text('Giao diện'),
                subtitle: Text('Dark Theme (#0F1117)'),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        StudioCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Dung lượng bộ nhớ mô hình Offline', style: TextStyle(fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(6),
                child: const LinearProgressIndicator(
                  value: 0.34,
                  minHeight: 8,
                  backgroundColor: AppTokens.bg,
                  color: AppTokens.success,
                ),
              ),
              const SizedBox(height: 6),
              const Text('Đã dùng 1.4 GB (Whisper + Piper Tiếng Việt) / Còn trống 28.5 GB',
                  style: TextStyle(fontSize: 12, color: AppTokens.textSecondary)),
            ],
          ),
        ),
      ],
    );
  }
}
