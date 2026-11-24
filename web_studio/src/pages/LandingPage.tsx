import React, { useState } from 'react';
import { I18N, useStudioStore } from '../store/useStudioStore';
import { Card, PrimaryButton, SecondaryButton } from '../components/ui';

export const LandingPage: React.FC = () => {
  const { lang, setRoute } = useStudioStore();
  const t = I18N[lang];
  const [afterMode, setAfterMode] = useState(true);

  return (
    <div className="max-w-6xl mx-auto px-4 py-10 space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-5 max-w-3xl mx-auto">
        <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-semibold bg-[#7C5CFF]/15 text-[#A594FF] border border-[#7C5CFF]/35">
          ✦ Hikari Tsukimi v3.0 · Local-First &amp; Cloud AI Studio
        </span>
        <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-[#E6E8EE] leading-tight">
          {t.heroTitle}
        </h1>
        <p className="text-base text-[#8B93A7] leading-relaxed">{t.heroSub}</p>
        <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
          <PrimaryButton onClick={() => setRoute('studio')} className="px-6 py-3 text-sm">
            {t.ctaTryStudio} →
          </PrimaryButton>
          <SecondaryButton onClick={() => setRoute('voices')} className="px-5 py-3 text-sm">
            Nghe thử 24 giọng đọc AI
          </SecondaryButton>
        </div>
      </section>

      {/* Before / After Interactive Demo */}
      <section className="space-y-4">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <h2 className="text-xl font-bold">So sánh Trước &amp; Sau khi xử lý</h2>
          <div className="inline-flex rounded-[10px] p-1 bg-[#171A23] border border-[#262B38]">
            <button
              onClick={() => setAfterMode(false)}
              className={`px-3 py-1.5 rounded-[8px] text-xs font-semibold transition ${!afterMode ? 'bg-[#1E2230] text-white' : 'text-[#8B93A7]'}`}
            >
              Trước (Video gốc tiếng Trung)
            </button>
            <button
              onClick={() => setAfterMode(true)}
              className={`px-3 py-1.5 rounded-[8px] text-xs font-semibold transition ${afterMode ? 'bg-gradient-to-r from-[#7C5CFF] to-[#4F8CFF] text-white' : 'text-[#8B93A7]'}`}
            >
              Sau (Đã lồng tiếng Việt + Giữ BGM 1080p)
            </button>
          </div>
        </div>
        <Card className="p-6 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-2 max-w-xl">
            <div className="text-xs font-semibold uppercase tracking-wider text-[#4F8CFF]">
              {afterMode ? 'Bản thành phẩm 1080p 60fps' : 'Bản gốc chưa dịch'}
            </div>
            <div className="text-lg font-bold text-[#E6E8EE]">
              {afterMode
                ? '“Đã bảo mua xe bản cao cấp đi mà bạn cứ không nghe!”'
                : '“就说买车买高配的你就是不听”'}
            </div>
            <p className="text-xs text-[#8B93A7]">
              {afterMode
                ? 'Giọng đọc: Ban Mai (Piper Local) · Nhạc nền BGM giữ nguyên 35% · Đã che mờ phụ đề cứng gốc.'
                : 'Âm thanh gốc có tiếng hiệu ứng lớn ở 12 giây đầu và phụ đề cứng tiếng Trung.'}
            </p>
          </div>
          <PrimaryButton onClick={() => setRoute('studio')}>Thử với video của bạn</PrimaryButton>
        </Card>
      </section>

      {/* 4 Steps */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">Quy trình 4 bước tự động</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            ['1. Bóc băng Whisper', 'Chuẩn hóa WAV 16kHz và nhận diện mốc thời gian chuẩn từng mili-giây.'],
            ['2. Dịch ngữ cảnh AI', 'Dịch mượt theo phong cách Review phim, Tiên hiệp, Hài hước hoặc Đời thường.'],
            ['3. Tạo giọng đọc AI', '6 giọng Piper Offline siêu tốc và 18 giọng TikTok TTS tự nhiên.'],
            ['4. Ghép & Xuất 1080p', 'Trộn nhạc nền BGM, che phụ đề gốc, chèn Logo/Watermark chuẩn 60fps.'],
          ].map(([title, desc]) => (
            <Card key={title} className="space-y-2">
              <div className="text-sm font-bold text-[#E6E8EE]">{title}</div>
              <p className="text-xs text-[#8B93A7] leading-relaxed">{desc}</p>
            </Card>
          ))}
        </div>
      </section>

      {/* Pricing (Free / Pro) */}
      <section className="space-y-4">
        <h2 className="text-xl font-bold">Bảng giá minh bạch</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card className="space-y-4">
            <div className="text-lg font-bold">Free Forever (Local Offline)</div>
            <div className="text-2xl font-extrabold">0đ / trọn đời</div>
            <ul className="text-xs text-[#8B93A7] space-y-2">
              <li>✓ Bóc băng Faster-Whisper trên GPU/CPU cá nhân</li>
              <li>✓ 6 giọng đọc Piper Tiếng Việt 100% Offline</li>
              <li>✓ Dịch miễn phí Google Web &amp; Xuất 1080p không watermark</li>
            </ul>
            <SecondaryButton onClick={() => setRoute('studio')} className="w-full">
              Bắt đầu miễn phí
            </SecondaryButton>
          </Card>
          <Card className="space-y-4 border-[#7C5CFF]">
            <div className="flex items-center justify-between">
              <span className="text-lg font-bold">Pro Creator Studio</span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-bold bg-[#7C5CFF]/20 text-[#A594FF]">Khuyên dùng</span>
            </div>
            <div className="text-2xl font-extrabold">BYOK (Dùng API Key riêng)</div>
            <ul className="text-xs text-[#8B93A7] space-y-2">
              <li>✓ Dịch ngữ cảnh sâu bằng Gemini 4 Argon / 3.5 Flash</li>
              <li>✓ Đầy đủ 18 giọng đọc TikTok SessionID đa ngôn ngữ</li>
              <li>✓ Lọc giọng tách lời &amp; giữ nhạc nền BGM tự động</li>
            </ul>
            <PrimaryButton onClick={() => setRoute('studio')} className="w-full">
              Mở Pro Studio ngay
            </PrimaryButton>
          </Card>
        </div>
      </section>

      {/* FAQ & Footer */}
      <section className="space-y-3 border-t border-[#262B38] pt-8">
        <h2 className="text-lg font-bold">Câu hỏi thường gặp (FAQ)</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-[#8B93A7]">
          <Card>
            <div className="font-bold text-[#E6E8EE] mb-1">Ứng dụng có cần mạng để tạo giọng đọc không?</div>
            Không. 6 giọng Piper Tiếng Việt chạy 100% offline trên máy tính của bạn.
          </Card>
          <Card>
            <div className="font-bold text-[#E6E8EE] mb-1">Video xuất ra có bị dính logo/watermark bắt buộc không?</div>
            Không. Video xuất ra sạch 100%, bạn chỉ chèn Logo/Watermark của riêng bạn nếu muốn.
          </Card>
        </div>
        <footer className="pt-6 text-center text-xs text-[#8B93A7]">
          © 2026 Hikari Tsukimi — AI Dubbing &amp; Creative Studio.
        </footer>
      </section>
    </div>
  );
};
