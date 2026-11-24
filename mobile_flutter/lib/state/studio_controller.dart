import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

class SubtitleLine {
  int id;
  String timeRange;
  String original;
  String translated;
  SubtitleLine({
    required this.id,
    required this.timeRange,
    required this.original,
    required this.translated,
  });
}

class ProjectModel {
  final String id;
  final String title;
  final String duration;
  final String status; // 'processing' | 'done' | 'error'
  final double progress;
  final String errorReason;
  const ProjectModel({
    required this.id,
    required this.title,
    required this.duration,
    required this.status,
    this.progress = 1.0,
    this.errorReason = '',
  });
}

class VoiceModel {
  final String id;
  final String name;
  final String langGroup;
  final String engine;
  bool isFavorite;
  VoiceModel({
    required this.id,
    required this.name,
    required this.langGroup,
    required this.engine,
    this.isFavorite = false,
  });
}

class StudioController extends ChangeNotifier {
  bool isLoadingSkeleton = false;
  bool isOffline = false;
  bool lowStorageWarning = false;
  bool videoTooLongWarning = false;
  String? pushBannerMessage;

  String selectedVoiceId = 'piper:banmai';
  String sourceLang = 'Tự động';
  String targetLang = 'Tiếng Việt';
  String translateStyle = 'Tự nhiên / Đời thường';
  double voiceSpeed = 1.0;
  double origVolume = 0.35;
  double voiceVolume = 1.0;
  String exportQuality = '1080p Full HD (60fps)';
  String apiKey = 'AIzaSyHikariMobileKey2026';
  String tiktokSessionId = '1b90e9ddb342a84d9bd2aac87d700dc5';

  List<ProjectModel> projects = [
    const ProjectModel(
      id: 'p1',
      title: 'Review Anime Tập 12 - Bản Lồng Tiếng',
      duration: '02:15',
      status: 'done',
      progress: 1.0,
    ),
    const ProjectModel(
      id: 'p2',
      title: 'Vlog Du Lịch Kyoto Mùa Thu',
      duration: '04:40',
      status: 'processing',
      progress: 0.65,
    ),
    const ProjectModel(
      id: 'p3',
      title: 'Highlight Chung Kết Thế Giới',
      duration: '01:18',
      status: 'error',
      progress: 0.35,
      errorReason: 'Mất kết nối mạng khi đang dịch Bước 2.',
    ),
  ];

  List<VoiceModel> voices = [
    VoiceModel(id: 'piper:banmai', name: 'Ban Mai (Nữ)', langGroup: 'Tiếng Việt', engine: 'Piper Offline', isFavorite: true),
    VoiceModel(id: 'piper:manhdung', name: 'Mạnh Dũng (Nam)', langGroup: 'Tiếng Việt', engine: 'Piper Offline', isFavorite: true),
    VoiceModel(id: 'piper:ngochuyen', name: 'Ngọc Huyền (Nữ)', langGroup: 'Tiếng Việt', engine: 'Piper Offline'),
    VoiceModel(id: 'tiktok:BV074', name: 'TikTok Nữ 01 (BV074)', langGroup: 'Tiếng Việt', engine: 'TikTok SessionID', isFavorite: true),
    VoiceModel(id: 'tiktok:en_us_002', name: 'Jessie (US Female)', langGroup: 'English', engine: 'TikTok SessionID'),
    VoiceModel(id: 'tiktok:jp_001', name: 'Sakura (JP Female)', langGroup: '日本語', engine: 'TikTok SessionID'),
  ];

  List<SubtitleLine> subtitles = [
    SubtitleLine(id: 1, timeRange: '00:01.2 → 00:04.0', original: '就说买车买高配的你就是不听', translated: 'Đã bảo mua xe bản cao cấp đi mà bạn cứ không nghe!'),
    SubtitleLine(id: 2, timeRange: '00:04.2 → 00:08.0', original: '现在好了，要成为它的智能饭盒了吧', translated: 'Giờ thì hay rồi, sắp thành hộp cơm thông minh của nó luôn.'),
    SubtitleLine(id: 3, timeRange: '00:08.3 → 00:12.1', original: '偏偏在这个时候相当灵敏啊', translated: 'Đúng lúc nguy cấp thế này thì nó lại nhạy đến lạ thường!'),
  ];

  void toggleFavoriteVoice(String id) {
    HapticFeedback.selectionClick();
    for (final v in voices) {
      if (v.id == id) v.isFavorite = !v.isFavorite;
    }
    notifyListeners();
  }

  void selectVoice(String id) {
    HapticFeedback.selectionClick();
    selectedVoiceId = id;
    notifyListeners();
  }

  void deleteSubtitle(int index) {
    HapticFeedback.mediumImpact();
    if (index >= 0 && index < subtitles.length) {
      subtitles.removeAt(index);
      notifyListeners();
    }
  }

  void mergeSubtitleWithNext(int index) {
    HapticFeedback.lightImpact();
    if (index >= 0 && index + 1 < subtitles.length) {
      final cur = subtitles[index];
      final nxt = subtitles[index + 1];
      final startPart = cur.timeRange.split('→').first.trim();
      final endPart = nxt.timeRange.split('→').last.trim();
      cur.timeRange = '$startPart → $endPart';
      cur.original = '${cur.original} ${nxt.original}';
      cur.translated = '${cur.translated} ${nxt.translated}';
      subtitles.removeAt(index + 1);
      notifyListeners();
    }
  }

  int replaceAllSubtitles(String findStr, String replaceStr) {
    if (findStr.trim().isEmpty) return 0;
    int count = 0;
    for (final s in subtitles) {
      if (s.translated.contains(findStr)) {
        s.translated = s.translated.replaceAll(findStr, replaceStr);
        count++;
      }
    }
    if (count > 0) {
      HapticFeedback.mediumImpact();
      notifyListeners();
    }
    return count;
  }

  void retryProject(String id) {
    HapticFeedback.lightImpact();
    projects = projects.map((p) {
      if (p.id == id) {
        return ProjectModel(id: p.id, title: p.title, duration: p.duration, status: 'processing', progress: 0.45);
      }
      return p;
    }).toList();
    notifyListeners();
  }

  void triggerPushNotification(String msg) {
    HapticFeedback.heavyImpact();
    pushBannerMessage = msg;
    notifyListeners();
  }

  void clearPushBanner() {
    pushBannerMessage = null;
    notifyListeners();
  }

  void toggleEdgeCase({bool? offline, bool? lowStorage, bool? longVideo}) {
    if (offline != null) isOffline = offline;
    if (lowStorage != null) lowStorageWarning = lowStorage;
    if (longVideo != null) videoTooLongWarning = longVideo;
    notifyListeners();
  }
}
