import React from 'react';
import { motion } from 'motion/react';
import { KeyRound, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { ApiKeys } from '../types';

interface SettingsProps {
  apiKeys: ApiKeys;
  setApiKeys: (keys: ApiKeys) => void;
}

export function Settings({ apiKeys, setApiKeys }: SettingsProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setApiKeys({ ...apiKeys, [name]: value });
  };

  return (
    <div className="max-w-2xl mx-auto p-8">
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-8"
      >
        <header>
          <h2 className="text-3xl font-semibold text-white mb-2 flex items-center gap-3">
            <KeyRound className="w-8 h-8 text-indigo-400" />
            API Configurations
          </h2>
          <p className="text-gray-400">
            BYOK (Bring Your Own Key) security model. Your keys never leave your browser unencrypted and are heavily guarded by TLS when interacting with our stateless Rust backend.
          </p>
        </header>

        <div className="bg-gray-900/50 border border-red-900/30 rounded-xl p-4 flex gap-4 text-orange-200/80">
          <ShieldAlert className="w-6 h-6 flex-shrink-0 text-orange-400" />
          <div className="text-sm">
            <p className="font-semibold text-orange-300">Stateless Architecture</p>
            <p>These keys are saved locally in your browser leveraging `localStorage`. The DeepReasoning API merely acts as a secure passthrough and orchestration layer.</p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300 flex items-center justify-between">
              DeepSeek API Key
              {apiKeys.deepseek && <CheckCircle2 className="w-4 h-4 text-emerald-500" />}
            </label>
            <input
              type="password"
              name="deepseek"
              value={apiKeys.deepseek}
              onChange={handleChange}
              placeholder="sk-..."
              className="w-full bg-gray-950 border border-gray-800 text-gray-100 rounded-lg px-4 py-3 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 outline-none transition-all placeholder:text-gray-700 font-mono text-sm"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300 flex items-center justify-between">
              Anthropic API Key
              {apiKeys.anthropic && <CheckCircle2 className="w-4 h-4 text-emerald-500" />}
            </label>
            <input
              type="password"
              name="anthropic"
              value={apiKeys.anthropic}
              onChange={handleChange}
              placeholder="sk-ant-..."
              className="w-full bg-gray-950 border border-gray-800 text-gray-100 rounded-lg px-4 py-3 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 outline-none transition-all placeholder:text-gray-700 font-mono text-sm"
            />
          </div>
        </div>
      </motion.div>
    </div>
  );
}
