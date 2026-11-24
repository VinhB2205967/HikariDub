import { create } from 'zustand';

export type PageRoute = 'landing' | 'studio' | 'projects' | 'voices' | 'queue' | 'settings';
export type StepStatus = 'waiting' | 'running' | 'done' | 'error';

export interface SubtitleLine {
  id: number;
  startMs: number;
  endMs: number;
  timeText: string;
  original: string;
  translated: string;
}

export interface ProjectCard {
  id: string;
  title: string;
  duration: string;
  resolution: string;
  status: 'done' | 'processing' | 'error';
  updatedAt: string;
  progress: number;
}

export interface VoiceOption {
  id: string;
  name: string;
  lang: string;
  gender: 'Nữ' | 'Nam';
  engine: 'Piper Local' | 'TikTok SessionID';
  favorite: boolean;
}

export interface QueueJob {
  id: string;
  videoName: string;
  currentStep: string;
  progress: number;
  status: 'running' | 'done' | 'error' | 'cancelled';
  eta: string;
}

export const I18N = {
  vi: {
    brand: 'Hikari Tsukimi',
    heroTitle: 'Lồng tiếng AI cho mọi video trong vài phút',
    heroSub: 'Bóc băng chuẩn từng mili-giây bằng Whisper, dịch ngữ cảnh AI, tạo giọng đọc tự nhiên và xuất video 1080p 60fps không watermark.',
    ctaTryStudio: 'Mở Phòng Thu Studio',
    navLanding: 'Giới thiệu',
    navStudio: 'Phòng thu',
    navProjects: 'Dự án',
    navVoices: 'Thư viện giọng',
    navQueue: 'Hàng đợi',
    navSettings: 'Cài đặt',
    startAuto: 'Bắt đầu xử lý',
    cancel: 'Hủy tiến trình',
  },
  en: {
    brand: 'Hikari Tsukimi',
    heroTitle: 'AI Dubbing for Any Video in Minutes',
    heroSub: 'Millisecond-accurate Whisper transcription, context-aware translation, natural AI voices, and clean 1080p 60fps export.',
    ctaTryStudio: 'Launch Studio',
    navLanding: 'Overview',
    navStudio: 'Studio',
    navProjects: 'Projects',
    navVoices: 'Voice Library',
    navQueue: 'Queue',
    navSettings: 'Settings',
    startAuto: 'Start Processing',
    cancel: 'Cancel',
  },
};

interface StudioState {
  route: PageRoute;
  theme: 'dark' | 'light';
  lang: 'vi' | 'en';
  toast: { type: 'success' | 'error' | 'info'; message: string } | null;

  // Active Studio state
  videoName: string;
  videoDurationSec: number;
  currentTimeSec: number;
  uploadProgress: number;
  whisperModel: string;
  selectedVoiceId: string;
  targetLang: string;
  stylePreset: string;
  vocalSep: boolean;
  origVolume: number;
  voiceVolume: number;
  activeOverlayTab: 'mask' | 'logo' | 'watermark';
  watermarkText: string;

  // Pipeline 4-step state machine
  steps: StepStatus[];
  overallProgress: number;
  etaText: string;
  isProcessing: boolean;

  // Data collections
  subtitles: SubtitleLine[];
  projects: ProjectCard[];
  voices: VoiceOption[];
  queue: QueueJob[];
  apiKey: string;
  tiktokSessionId: string;

  // Actions
  setRoute: (r: PageRoute) => void;
  toggleTheme: () => void;
  setLang: (l: 'vi' | 'en') => void;
  showToast: (type: 'success' | 'error' | 'info', message: string) => void;
  updateConfig: (patch: Partial<StudioState>) => void;
  updateSubtitle: (id: number, field: 'original' | 'translated', val: string) => void;
  replaceAllSubtitles: (findStr: string, replaceStr: string) => void;
  toggleFavoriteVoice: (id: string) => void;
  simulateUploadVideo: (fileName: string) => void;
  startPipelineMock: () => void;
  cancelPipelineMock: () => void;
  retryQueueJob: (id: string) => void;
  cancelQueueJob: (id: string) => void;
}

let pipelineTimer: number | null = null;

export const useStudioStore = create<StudioState>((set, get) => ({
  route: 'studio',
  theme: 'dark',
  lang: 'vi',
  toast: null,

  videoName: 'snaptik_review_anime_ep12.mp4',
  videoDurationSec: 36,
  currentTimeSec: 8,
  uploadProgress: 100,
  whisperModel: 'small',
  selectedVoiceId: 'piper:banmai',
  targetLang: 'Tiếng Việt',
  stylePreset: 'Tự nhiên / Đời thường',
  vocalSep: true,
  origVolume: 35,
  voiceVolume: 100,
  activeOverlayTab: 'mask',
  watermarkText: 'HIKARI TSUKIMI STUDIO',

  steps: ['done', 'done', 'waiting', 'waiting'],
  overallProgress: 50,
  etaText: 'Sẵn sàng xử lý',
  isProcessing: false,

  subtitles: [
    { id: 1, startMs: 1200, endMs: 4200, timeText: '00:01.2 → 00:04.2', original: '就说买车买高配的你就是不听', translated: 'Đã bảo mua xe bản cao cấp đi mà bạn cứ không nghe!' },
    { id: 2, startMs: 4500, endMs: 8100, timeText: '00:04.5 → 00:08.1', original: '现在好了，要成为它的智能饭盒了吧', translated: 'Giờ thì hay rồi, sắp biến thành hộp cơm thông minh của nó luôn rồi.' },
    { id: 3, startMs: 8400, endMs: 12500, timeText: '00:08.4 → 00:12.5', original: '想跟别人展示的时候偏偏打不开', translated: 'Lúc muốn khoe với người khác thì lại chẳng tài nào mở nổi.' },
    { id: 4, startMs: 12800, endMs: 16900, timeText: '00:12.8 → 00:16.9', original: '偏偏在这个时候相当灵敏啊', translated: 'Đúng lúc nguy cấp thế này thì nó lại nhạy đến lạ thường!' },
  ],

  projects: [
    { id: 'p1', title: 'Review Anime Tập 12 - Bản Lồng Tiếng.mp4', duration: '02:15', resolution: '1080p 60fps', status: 'done', updatedAt: '10 phút trước', progress: 100 },
    { id: 'p2', title: 'Tổng Hợp Công Nghệ AI 2026.mp4', duration: '05:40', resolution: '1080p 60fps', status: 'processing', updatedAt: 'Đang chạy', progress: 68 },
    { id: 'p3', title: 'Highlight Giải Đấu Mùa Thu.mp4', duration: '01:30', resolution: '1080p 60fps', status: 'error', updatedAt: '1 giờ trước', progress: 35 },
  ],

  voices: [
    { id: 'piper:banmai', name: 'Ban Mai', lang: 'Tiếng Việt', gender: 'Nữ', engine: 'Piper Local', favorite: true },
    { id: 'piper:manhdung', name: 'Mạnh Dũng', lang: 'Tiếng Việt', gender: 'Nam', engine: 'Piper Local', favorite: true },
    { id: 'piper:ngochuyen', name: 'Ngọc Huyền', lang: 'Tiếng Việt', gender: 'Nữ', engine: 'Piper Local', favorite: false },
    { id: 'tiktok:BV074_streaming', name: 'TikTok VN Nữ 01', lang: 'Tiếng Việt', gender: 'Nữ', engine: 'TikTok SessionID', favorite: true },
    { id: 'tiktok:BV075_streaming', name: 'TikTok VN Nam 01', lang: 'Tiếng Việt', gender: 'Nam', engine: 'TikTok SessionID', favorite: false },
    { id: 'tiktok:en_us_002', name: 'Jessie (US)', lang: 'English', gender: 'Nữ', engine: 'TikTok SessionID', favorite: false },
  ],

  queue: [
    { id: 'q1', videoName: 'Tổng Hợp Công Nghệ AI 2026.mp4', currentStep: 'Bước 3/4: Tạo giọng đọc Piper', progress: 68, status: 'running', eta: '~14 giây' },
    { id: 'q2', videoName: 'Review Anime Tập 12.mp4', currentStep: 'Hoàn tất xuất 1080p', progress: 100, status: 'done', eta: '0 giây' },
    { id: 'q3', videoName: 'Highlight Giải Đấu Mùa Thu.mp4', currentStep: 'Lỗi hạn mức API ở Bước 2', progress: 35, status: 'error', eta: 'Tạm dừng' },
  ],

  apiKey: 'AIzaSyDemoKeyForHikariStudioV3',
  tiktokSessionId: '1b90e9ddb342a84d9bd2aac87d700dc5',

  setRoute: (route) => set({ route }),
  toggleTheme: () => set((s) => ({ theme: s.theme === 'dark' ? 'light' : 'dark' })),
  setLang: (lang) => set({ lang }),
  showToast: (type, message) => {
    set({ toast: { type, message } });
    window.setTimeout(() => set({ toast: null }), 3500);
  },
  updateConfig: (patch) => set((s) => ({ ...s, ...patch })),

  updateSubtitle: (id, field, val) =>
    set((s) => ({
      subtitles: s.subtitles.map((sub) => (sub.id === id ? { ...sub, [field]: val } : sub)),
    })),

  replaceAllSubtitles: (findStr, replaceStr) => {
    if (!findStr.trim()) return;
    let count = 0;
    const next = get().subtitles.map((s) => {
      if (s.translated.includes(findStr)) {
        count++;
        return { ...s, translated: s.translated.split(findStr).join(replaceStr) };
      }
      return s;
    });
    set({ subtitles: next });
    get().showToast('success', `Đã thay thế ${count} dòng phụ đề.`);
  },

  toggleFavoriteVoice: (id) =>
    set((s) => ({
      voices: s.voices.map((v) => (v.id === id ? { ...v, favorite: !v.favorite } : v)),
    })),

  simulateUploadVideo: (fileName) => {
    set({ videoName: fileName, uploadProgress: 15, steps: ['waiting', 'waiting', 'waiting', 'waiting'], overallProgress: 0 });
    const iv = window.setInterval(() => {
      const cur = get().uploadProgress;
      if (cur >= 100) {
        window.clearInterval(iv);
        get().showToast('success', `Đã tải lên video: ${fileName}`);
      } else {
        set({ uploadProgress: Math.min(100, cur + 30) });
      }
    }, 180);
  },

  startPipelineMock: () => {
    if (pipelineTimer) window.clearInterval(pipelineTimer);
    set({
      isProcessing: true,
      overallProgress: 5,
      steps: ['running', 'waiting', 'waiting', 'waiting'],
      etaText: 'Đang bóc băng Whisper · Còn ~24s',
    });
    pipelineTimer = window.setInterval(() => {
      const p = get().overallProgress + 12;
      if (p >= 100) {
        if (pipelineTimer) window.clearInterval(pipelineTimer);
        set({
          isProcessing: false,
          overallProgress: 100,
          steps: ['done', 'done', 'done', 'done'],
          etaText: 'Hoàn tất xuất video 1080p 60fps!',
        });
        get().showToast('success', 'Đã xử lý & xuất video 1080p thành công!');
      } else if (p < 30) {
        set({ overallProgress: p, steps: ['running', 'waiting', 'waiting', 'waiting'], etaText: 'Bước 1/4: Đang bóc băng Whisper...' });
      } else if (p < 55) {
        set({ overallProgress: p, steps: ['done', 'running', 'waiting', 'waiting'], etaText: 'Bước 2/4: Đang dịch phụ đề AI...' });
      } else if (p < 80) {
        set({ overallProgress: p, steps: ['done', 'done', 'running', 'waiting'], etaText: 'Bước 3/4: Đang tạo giọng đọc AI...' });
      } else {
        set({ overallProgress: p, steps: ['done', 'done', 'done', 'running'], etaText: 'Bước 4/4: Đang ghép & xuất 1080p...' });
      }
    }, 350);
  },

  cancelPipelineMock: () => {
    if (pipelineTimer) window.clearInterval(pipelineTimer);
    set({
      isProcessing: false,
      steps: ['waiting', 'waiting', 'waiting', 'waiting'],
      overallProgress: 0,
      etaText: 'Đã hủy tiến trình',
    });
    get().showToast('info', 'Đã dừng tiến trình xử lý.');
  },

  retryQueueJob: (id) =>
    set((s) => ({
      queue: s.queue.map((j) => (j.id === id ? { ...j, status: 'running', progress: 20, currentStep: 'Đang thử lại Bước 2/4...', eta: '~18 giây' } : j)),
    })),

  cancelQueueJob: (id) =>
    set((s) => ({
      queue: s.queue.map((j) => (j.id === id ? { ...j, status: 'cancelled', eta: 'Đã hủy' } : j)),
    })),
}));
