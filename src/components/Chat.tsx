import React, { useState } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Send, BrainCircuit, MessageSquare, Loader2 } from 'lucide-react';
import { Message, ApiKeys } from '../types';

interface ChatProps {
  apiKeys: ApiKeys;
}

export function Chat({ apiKeys }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isSynthesizing, setIsSynthesizing] = useState(false);

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !apiKeys.deepseek || !apiKeys.anthropic) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim(),
      timestamp: Date.now(),
    };

    setMessages([...messages, userMsg]);
    setInput('');
    setIsSynthesizing(true);

    // Mock orchestration delay to represent Rust backend
    setTimeout(() => {
      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        reasoning: "Analyzing the user's input.\\nConnecting concepts using chain of thought.\\nFormulating a strategic synthesis for Claude to interpret...",
        content: "Based on the internal reasoning, here is the synthesis from Claude. The architecture relies on the highly concurrent Rust backend routing the parsed token streams.",
        timestamp: Date.now() + 1,
      };
      setMessages(prev => [...prev, assistantMsg]);
      setIsSynthesizing(false);
    }, 2000);
  };

  const hasKeys = apiKeys.deepseek && apiKeys.anthropic;

  return (
    <div className="flex flex-col h-full bg-[#0a0a0a]">
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 pb-32">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center text-gray-500 space-y-4">
            <BrainCircuit className="w-16 h-16 text-indigo-500/20" />
            <div className="max-w-md">
              <h3 className="text-xl font-medium text-gray-300 mb-2">DeepReasoning Chat</h3>
              <p className="text-sm">Initiate a prompt to trigger the DeepSeek CoT engine, which will seamlessly pipeline results into Anthropic Claude for optimal synthesis.</p>
            </div>
            {!hasKeys && (
              <p className="text-orange-400/80 text-sm mt-4 bg-orange-400/10 px-4 py-2 rounded-full border border-orange-400/20">
                Please configure your BYOK API Keys in the Config tab.
              </p>
            )}
          </div>
        ) : (
          <AnimatePresence initial={false}>
            {messages.map((msg) => (
              <motion.div
                key={msg.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-1">
                    <BrainCircuit className="w-5 h-5 text-white" />
                  </div>
                )}
                
                <div className={`flex flex-col gap-2 max-w-[85%] ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                  {msg.role === 'user' ? (
                    <div className="bg-white text-black px-5 py-3 rounded-2xl rounded-tr-sm text-[15px] leading-relaxed shadow-sm">
                      {msg.content}
                    </div>
                  ) : (
                    <div className="space-y-3 w-full">
                      {/* DeepSeek Reasoning Block */}
                      {msg.reasoning && (
                        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 text-sm text-gray-400 font-mono relative overflow-hidden pl-5 relative before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1 before:bg-indigo-500/50">
                          <div className="flex items-center gap-2 mb-2 text-xs text-indigo-400 uppercase tracking-widest font-semibold font-sans">
                            <Loader2 className="w-3 h-3 animate-spin"/> DeepSeek R1 Thinking
                          </div>
                          {msg.reasoning}
                        </div>
                      )}
                      {/* Claude Final Output Blocks */}
                      <div className="text-gray-200 text-[15px] leading-relaxed pl-2 border-l border-transparent">
                        <div className="flex items-center gap-2 mb-2 text-xs text-purple-400 uppercase tracking-widest font-semibold font-sans">
                          <MessageSquare className="w-3 h-3" /> Claude Synthesis
                        </div>
                        {msg.content}
                      </div>
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
            {isSynthesizing && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex gap-4"
              >
                <div className="w-8 h-8 rounded-full bg-gray-800 flex items-center justify-center flex-shrink-0">
                  <Loader2 className="w-4 h-4 text-gray-400 animate-spin" />
                </div>
                <div className="flex items-center text-sm font-mono text-gray-500 uppercase tracking-widest">
                  Orchestrating streams...
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        )}
      </div>

      <div className="absolute bottom-0 left-0 right-0 p-4 md:p-8 bg-gradient-to-t from-[#0a0a0a] via-[#0a0a0a] to-transparent">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto relative group">
          <input
            type="text"
            disabled={!hasKeys}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={hasKeys ? "Query the DeepReasoning orchestration..." : "Configure API Keys first"}
            className="w-full bg-gray-900/90 backdrop-blur border border-gray-800 text-white rounded-2xl pl-5 pr-14 py-4 focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 outline-none transition-all placeholder:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed shadow-xl shadow-black/50"
          />
          <button
            type="submit"
            disabled={!hasKeys || !input.trim()}
            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-xl transition-colors"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
