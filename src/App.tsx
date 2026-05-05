/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from 'react';
import { ViewState, ApiKeys } from './types';
import { Sidebar } from './components/Sidebar';
import { Chat } from './components/Chat';
import { Settings } from './components/Settings';
import { ArchitectureDocs } from './components/ArchitectureDocs';

export default function App() {
  const [currentView, setCurrentView] = useState<ViewState>('architecture');
  const [apiKeys, setApiKeys] = useState<ApiKeys>({ deepseek: '', anthropic: '' });
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const saved = localStorage.getItem('deepreasoning_keys');
    if (saved) {
      try {
        setApiKeys(JSON.parse(saved));
      } catch (e) {}
    }
    setIsLoaded(true);
  }, []);

  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem('deepreasoning_keys', JSON.stringify(apiKeys));
    }
  }, [apiKeys, isLoaded]);

  if (!isLoaded) return null;

  return (
    <div className="flex h-screen bg-[#0a0a0a] text-white overflow-hidden font-sans">
      <Sidebar currentView={currentView} setView={setCurrentView} />
      
      <main className="flex-1 relative overflow-y-auto">
        <div className="absolute inset-0">
          {currentView === 'architecture' && <ArchitectureDocs />}
          {currentView === 'keys' && <Settings apiKeys={apiKeys} setApiKeys={setApiKeys} />}
          {currentView === 'chat' && <Chat apiKeys={apiKeys} />}
        </div>
      </main>
    </div>
  );
}
