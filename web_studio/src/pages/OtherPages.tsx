import React, { useState } from 'react';
import { useStudioStore } from '../store/useStudioStore';
import { Card, PrimaryButton, SecondaryButton, StatusBadge } from '../components/ui';

export const ProjectsPage: React.FC = () => {
  const { projects, setRoute } = useStudioStore();
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<'all' | 'done' | 'processing' | 'error'>('all');

  const filtered = projects.filter(
    (p) => (filter === 'all' || p.status === filter) && p.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-bold">Thư viện Dự án Video</h1>
        <div className="flex flex-wrap items-center gap-2">
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Tìm dự án..."
            className="px-3 py-1.5 rounded-[10px] bg-[#171A23] border border-[#262B38] text-xs"
          />
          {(['all', 'done', 'processing', 'error'] as const).map((f) => (
            <SecondaryButton
              key={f}
              onClick={() => setFilter(f)}
              className={`text-xs py-1.5 ${filter === f ? 'border-[#7C5CFF] text-white' : ''}`}
            >
              {f === 'all' ? 'Tất cả' : f === 'done' ? 'Hoàn tất' : f === 'processing' ? 'Đang xử lý' : 'Lỗi'}
            </SecondaryButton>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {filtered.map((p) => (
          <Card key={p.id} className="space-y-3">
            <div className="h-32 rounded-[10px] bg-[#0F1117] border border-[#262B38] flex items-center justify-center text-2xl">
              🎬
            </div>
            <div className="font-bold text-sm truncate" title={p.title}>
              {p.title}
            </div>
            <div className="flex items-center justify-between text-xs text-[#8B93A7]">
              <span>{p.duration} · {p.resolution}</span>
              <StatusBadge status={p.status} />
            </div>
            <div className="flex gap-2">
              <PrimaryButton onClick={() => setRoute('studio')} className="flex-1 text-xs">
                Mở trong Studio
              </PrimaryButton>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export const VoiceLibraryPage: React.FC = () => {
  const { voices, toggleFavoriteVoice, showToast } = useStudioStore();
  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Thư viện Giọng đọc AI (Piper Local &amp; TikTok SessionID)</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
        {voices.map((v) => (
          <Card key={v.id} className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-bold text-sm">{v.name}</div>
                <div className="text-xs text-[#8B93A7]">{v.lang} · {v.gender}</div>
              </div>
              <button
                aria-label="Yêu thích"
                onClick={() => toggleFavoriteVoice(v.id)}
                className="text-lg"
              >
                {v.favorite ? '❤️' : '🤍'}
              </button>
            </div>
            <div className="text-[11px] px-2 py-0.5 rounded bg-[#0F1117] border border-[#262B38] inline-block text-[#8B93A7]">
              Engine: {v.engine}
            </div>
            <SecondaryButton
              onClick={() => showToast('info', `Đang phát thử giọng ${v.name}...`)}
              className="w-full text-xs"
            >
              🔊 Nghe mẫu giọng
            </SecondaryButton>
          </Card>
        ))}
      </div>
    </div>
  );
};

export const QueuePage: React.FC = () => {
  const { queue, retryQueueJob, cancelQueueJob, showToast } = useStudioStore();
  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Hàng đợi Xử lý Video</h1>
      <div className="space-y-3">
        {queue.map((job) => (
          <Card key={job.id} className="flex flex-wrap items-center justify-between gap-4">
            <div className="space-y-1 min-w-[220px]">
              <div className="font-bold text-sm">{job.videoName}</div>
              <div className="text-xs text-[#8B93A7]">{job.currentStep} · Còn {job.eta}</div>
            </div>
            <div className="flex-1 max-w-xs">
              <div className="h-2 rounded-full bg-[#0F1117] overflow-hidden border border-[#262B38]">
                <div className="h-full bg-gradient-to-r from-[#7C5CFF] to-[#4F8CFF]" style={{ width: `${job.progress}%` }} />
              </div>
            </div>
            <div className="flex items-center gap-2">
              <StatusBadge status={job.status} />
              {job.status === 'error' && (
                <PrimaryButton onClick={() => retryQueueJob(job.id)} className="text-xs">
                  Thử lại
                </PrimaryButton>
              )}
              {job.status === 'running' && (
                <SecondaryButton onClick={() => cancelQueueJob(job.id)} className="text-xs">
                  Hủy
                </SecondaryButton>
              )}
              {job.status === 'done' && (
                <PrimaryButton onClick={() => showToast('success', `Đang tải về ${job.videoName}`)} className="text-xs">
                  Tải về 1080p
                </PrimaryButton>
              )}
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};

export const SettingsPage: React.FC = () => {
  const store = useStudioStore();
  const [showKey, setShowKey] = useState(false);

  return (
    <div className="max-w-3xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Cài đặt &amp; Tài khoản</h1>
      <Card className="space-y-4">
        <div className="text-sm font-bold">Bảo mật API Key &amp; TikTok Session ID</div>
        <div>
          <label className="text-xs text-[#8B93A7] block mb-1">Gemini API Key</label>
          <div className="flex gap-2">
            <input
              type={showKey ? 'text' : 'password'}
              value={store.apiKey}
              onChange={(e) => store.updateConfig({ apiKey: e.target.value })}
              className="flex-1 px-3 py-2 rounded-[10px] bg-[#0F1117] border border-[#262B38] text-xs"
            />
            <SecondaryButton onClick={() => setShowKey(!showKey)} className="text-xs">
              {showKey ? 'Ẩn' : 'Hiện'}
            </SecondaryButton>
          </div>
        </div>
        <div>
          <label className="text-xs text-[#8B93A7] block mb-1">TikTok Session ID</label>
          <input
            type={showKey ? 'text' : 'password'}
            value={store.tiktokSessionId}
            onChange={(e) => store.updateConfig({ tiktokSessionId: e.target.value })}
            className="w-full px-3 py-2 rounded-[10px] bg-[#0F1117] border border-[#262B38] text-xs"
          />
        </div>
        <PrimaryButton onClick={() => store.showToast('success', 'Đã lưu cài đặt hệ thống!')}>
          Lưu cài đặt
        </PrimaryButton>
      </Card>
    </div>
  );
};
