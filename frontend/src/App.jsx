import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import DiscoverScreen from './components/DiscoverScreen';
import AnalyzeScreen from './components/AnalyzeScreen';
import RoutineScreen from './components/RoutineScreen';
import Footer from './components/Footer';

export default function App() {
  const [activeTab, setActiveTab] = useState('discover');
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'light';
  });

  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'light' ? 'dark' : 'light'));
  };

  return (
    <div class="min-h-screen flex flex-col app-bg app-text antialiased transition-colors duration-250">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} theme={theme} toggleTheme={toggleTheme} />

      <main class="flex-grow max-w-[1180px] w-full mx-auto px-6 py-8">
        {activeTab === 'discover' && <DiscoverScreen />}
        {activeTab === 'analyze' && <AnalyzeScreen />}
        {activeTab === 'routine' && <RoutineScreen />}
      </main>

      <Footer />
    </div>
  );
}
