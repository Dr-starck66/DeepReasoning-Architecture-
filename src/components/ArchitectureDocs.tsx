import React from 'react';
import { motion } from 'motion/react';
import { Server, Shield, Network, Zap } from 'lucide-react';

export function ArchitectureDocs() {
  return (
    <div className="max-w-4xl mx-auto p-8 text-gray-200">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-12"
      >
        <header className="space-y-4">
          <h1 className="text-4xl font-semibold tracking-tight text-white mb-2">
            DeepReasoning Architecture
          </h1>
          <p className="text-lg text-gray-400">
            A high-performance LLM orchestration system combining DeepSeek reasoning with Claude synthesis.
          </p>
        </header>

        <section className="space-y-6">
          <div className="flex items-center gap-3 text-blue-400 mb-4">
            <Zap className="w-6 h-6" />
            <h2 className="text-2xl font-medium text-white">The 3 Core Pillars</h2>
          </div>

          <div className="grid gap-6">
            <div className="bg-gray-900/50 border border-gray-800 p-6 rounded-xl">
              <div className="flex items-center gap-3 mb-3">
                <Network className="w-5 h-5 text-indigo-400" />
                <h3 className="text-xl font-medium text-white">1. Rust Orchestration Engine</h3>
              </div>
              <p className="text-gray-400 leading-relaxed mb-4">
                The high-performance Rust backend (v1.75+) manages concurrent asynchronous streams. It first opens a channel to the DeepSeek API, streams the Chain of Thought (CoT), and immediately pipelines the resulting context into the Anthropic API request for final synthesis.
              </p>
              <ul className="list-disc list-inside text-sm text-gray-500 space-y-1">
                <li>Zero-copy stream parsing where possible</li>
                <li>Tokio-based async runtime for minimal latency overhead</li>
                <li>Memory-safe configuration management (`src/config.rs`)</li>
              </ul>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 p-6 rounded-xl">
              <div className="flex items-center gap-3 mb-3">
                <Shield className="w-5 h-5 text-emerald-400" />
                <h3 className="text-xl font-medium text-white">2. Secure BYOK Model</h3>
              </div>
              <p className="text-gray-400 leading-relaxed mb-4">
                "Bring Your Own Key" (BYOK) architecture ensures no user keys are stored permanently in a centralized database. Keys are injected at the frontend, stored in local browser state, and transmitted securely via TLS headers (`X-DeepSeek-Key`, `X-Anthropic-Key`) directly to the stateless Rust handlers.
              </p>
            </div>

            <div className="bg-gray-900/50 border border-gray-800 p-6 rounded-xl">
              <div className="flex items-center gap-3 mb-3">
                <Server className="w-5 h-5 text-amber-400" />
                <h3 className="text-xl font-medium text-white">3. Unified React Client</h3>
              </div>
              <p className="text-gray-400 leading-relaxed mb-4">
                The frontend orchestrates the visual state, creating a seamless unified chat feed. It renders the DeepSeek "internal monologue" distinctly (e.g., collapsed or grayed out) before revealing the final synthesized response from Claude, optimizing the UX for long-reasoning tasks.
              </p>
            </div>
          </div>
        </section>
      </motion.div>
    </div>
  );
}
