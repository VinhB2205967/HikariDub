import React from 'react';
import { I18N, PageRoute, useStudioStore } from './store/useStudioStore';
import { ToastBanner } from './components/ui';
import { LandingPage } from './pages/LandingPage';
import { StudioPage } from './pages/StudioPage';
import { ProjectsPage, VoiceLibraryPage, QueuePage, SettingsPage } from './pages/OtherPages';

export const App: React.FC = () => {
  const { route, setRoute, lang, setLang } = useStudioStore();
  const t = I18N[lang];

  const navItems: { id: PageRoute; label: string }[] = [
    { id: 'landing', label: t.navLanding },
    { id: 'studio', label: t.navStudio },
    { id: 'projects', label: t.navProjects },
    { id: 'voices', label: t.navVoices },
    { id: 'queue', label: t.navQueue },
    { id: 'settings', label: t.navSettings },
  ];

  return (
    <div className="min-h-screen bg-[#0F1117] text-[#E6E8EE] font-sans antialiased flex flex-col">
      {/* Top Navigation Bar (56px) */}
      <header className="h-[56px] px-4 bg-[#171A23] border-b border-[#262B38] flex items-center justify-between gap-4 shrink-0">
        <div className="flex items-center gap-3">
          <div
            onClick={() => setRoute('landing')}
            className="w-8 h-8 rounded-[10px] bg-gradient-to-r from-[#7C5CFF] to-[#4F8CFF] flex items-center justify-center font-bold cursor-pointer"
          >
            ✦
          </div>
          <span className="font-bold text-sm tracking-tight">{t.brand} Studio v3.0</span>
        </div>

        <nav className="flex items-center gap-1 overflow-x-auto">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setRoute(item.id)}
              className={`px-3 py-1.5 rounded-[8px] text-xs font-semibold transition whitespace-nowrap ${
                route === item.id
                  ? 'bg-[#7C5CFF]/20 text-white border border-[#7C5CFF]/50'
                  : 'text-[#8B93A7] hover:text-white'
              }`}
            >
              {item.label}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setLang(lang === 'vi' ? 'en' : 'vi')}
            className="px-2.5 py-1 rounded-[8px] bg-[#1E2230] border border-[#262B38] text-xs font-semibold"
          >
            {lang.toUpperCase()}
          </button>
        </div>
      </header>

      {/* Active Page View */}
      <div className="flex-1 min-h-0">
        {route === 'landing' && <LandingPage />}
        {route === 'studio' && <StudioPage />}
        {route === 'projects' && <ProjectsPage />}
        {route === 'voices' && <VoiceLibraryPage />}
        {route === 'queue' && <QueuePage />}
        {route === 'settings' && <SettingsPage />}
      </div>

      <ToastBanner />
    </div>
  );
};

export default App;
