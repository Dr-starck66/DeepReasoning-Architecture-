import React from 'react';
import { ViewState } from '../types';
import { MessageSquare, KeyRound, BookOpen, Command } from 'lucide-react';
import { motion } from 'motion/react';

interface SidebarProps {
  currentView: ViewState;
  setView: (view: ViewState) => void;
}

export function Sidebar({ currentView, setView }: SidebarProps) {
  const navItems = [
    { id: 'chat' as ViewState, label: 'Chat UI', icon: MessageSquare },
    { id: 'keys' as ViewState, label: 'BYOK Config', icon: KeyRound },
    { id: 'architecture' as ViewState, label: 'Architecture Docs', icon: BookOpen },
  ];

  return (
    <div className="w-64 bg-black border-r border-gray-900 flex flex-col pt-8 pb-4">
      <div className="px-6 mb-10 flex items-center gap-3 text-white">
        <div className="w-8 h-8 rounded-lg bg-white flex items-center justify-center shadow-[0_0_15px_rgba(255,255,255,0.3)]">
          <Command className="w-5 h-5 text-black" />
        </div>
        <div>
          <h1 className="font-semibold text-[15px] tracking-tight">DeepReasoning</h1>
          <p className="text-[10px] text-gray-500 uppercase tracking-widest font-mono">v1.2.0 - Orchestrator</p>
        </div>
      </div>

      <nav className="flex-1 px-4 space-y-2">
        {navItems.map((item) => {
          const isActive = currentView === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setView(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all relative ${
                isActive ? 'text-white' : 'text-gray-500 hover:text-gray-300 hover:bg-gray-900/50'
              }`}
            >
              <item.icon className={`w-4 h-4 ${isActive ? 'text-indigo-400' : ''}`} />
              {item.label}
              {isActive && (
                <motion.div
                  layoutId="sidebar-active"
                  className="absolute inset-0 bg-gray-900 border border-gray-800 rounded-lg -z-10"
                  transition={{ type: "spring", stiffness: 300, damping: 30 }}
                />
              )}
            </button>
          );
        })}
      </nav>

      <div className="px-6 pb-2">
        <div className="p-4 bg-gray-900/30 border border-gray-800/50 rounded-xl text-xs text-gray-500 font-mono tracking-tight leading-relaxed">
          Stateless Rust API<br/>
          R1 ➔ Claude Pipeline<br/>
          End-to-End TLS
        </div>
      </div>
    </div>
  );
}
