export type ViewState = 'chat' | 'keys' | 'architecture';

export interface Message {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  reasoning?: string; // For DeepSeek CoT
  timestamp: number;
}

export interface ApiKeys {
  deepseek: string;
  anthropic: string;
}
