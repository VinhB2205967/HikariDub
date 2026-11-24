import React from 'react';
import { useStudioStore } from '../store/useStudioStore';

export const Card: React.FC<{ children: React.ReactNode; className?: string }> = ({ children, className = '' }) => (
  <div className={`rounded-[12px] bg-[#171A23]/90 backdrop-blur border border-[#262B38] p-4 shadow-sm ${className}`}>
    {children}
  </div>
);

export const PrimaryButton: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <button
    {...props}
    className={`px-4 py-2 rounded-[10px] font-semibold text-[13px] text-white bg-gradient-to-r from-[#7C5CFF] to-[#4F8CFF] hover:brightness-110 active:scale-[0.99] disabled:opacity-45 disabled:pointer-events-none transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[#7C5CFF] ${className}`}
  >
    {children}
  </button>
);

export const SecondaryButton: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement>> = ({
  children,
  className = '',
  ...props
}) => (
  <button
    {...props}
    className={`px-3.5 py-2 rounded-[10px] font-medium text-[13px] text-[#E6E8EE] bg-[#1E2230] hover:bg-[#272C3F] border border-[#262B38] hover:border-[#4F8CFF]/60 disabled:opacity-40 transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-[#4F8CFF] ${className}`}
  >
    {children}
  </button>
);

export const StatusBadge: React.FC<{ status: 'done' | 'processing' | 'running' | 'error' | 'waiting' | 'cancelled' }> = ({
  status,
}) => {
  const map = {
    done: { label: 'Hoàn tất', cls: 'bg-[#2ECC71]/15 text-[#2ECC71] border-[#2ECC71]/35' },
    processing: { label: 'Đang xử lý', cls: 'bg-[#4F8CFF]/15 text-[#4F8CFF] border-[#4F8CFF]/35' },
    running: { label: 'Đang chạy', cls: 'bg-[#7C5CFF]/20 text-[#A594FF] border-[#7C5CFF]/40' },
    error: { label: 'Lỗi', cls: 'bg-[#FF5C5C]/15 text-[#FF5C5C] border-[#FF5C5C]/35' },
    waiting: { label: 'Chờ', cls: 'bg-[#1E2230] text-[#8B93A7] border-[#262B38]' },
    cancelled: { label: 'Đã hủy', cls: 'bg-[#F5A524]/15 text-[#F5A524] border-[#F5A524]/35' },
  }[status];

  return (
    <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border whitespace-nowrap ${map.cls}`}>
      {map.label}
    </span>
  );
};

export const ToastBanner: React.FC = () => {
  const toast = useStudioStore((s) => s.toast);
  if (!toast) return null;
  const colors = {
    success: 'border-[#2ECC71] bg-[#171A23] text-[#2ECC71]',
    error: 'border-[#FF5C5C] bg-[#171A23] text-[#FF5C5C]',
    info: 'border-[#4F8CFF] bg-[#171A23] text-[#4F8CFF]',
  }[toast.type];

  return (
    <div
      role="status"
      aria-live="polite"
      className={`fixed bottom-20 right-6 z-50 px-4 py-2.5 rounded-[12px] border shadow-xl text-[13px] font-semibold transition-all ${colors}`}
    >
      {toast.message}
    </div>
  );
};
