// Defense-in-depth: strip any AI identity, tooling, or process references
// that slip through the backend sanitizer before rendering output to clients.

const STRIP_PATTERNS: [RegExp, string][] = [
  // AI self-identification
  [/As Claude[,\s]/gi, ''],
  [/As an AI (language model|assistant|system)[,\s]/gi, ''],
  [/I am Claude[.\s]/gi, ''],
  [/I'?m Claude[.\s]/gi, ''],
  [/Claude (here|speaking|responding)[.\s,]/gi, ''],
  [/powered by (Anthropic|OpenAI|Claude|GPT)[.\s,]/gi, ''],
  [/using (the )?(GPT|Claude|Anthropic|OpenAI)[- ]/gi, ''],
  // Provider comment prefix (legacy stored outputs)
  [/^<!--\s*provider:[^>]*-->\s*/i, ''],
  // Tool/skill/plugin disclosure
  [/I (used|called|invoked|queried|executed) (the )?(web_search|search|query_\w+|retriev\w+|tool|plugin|skill)\b/gi, 'Based on available data,'],
  [/Using (the )?(web_search|search_tool|retrieval|RAG|skill|plugin)\b/gi, ''],
  [/\[TOOL (CALL|USE|RESULT)\][^\n]*/gi, ''],
  [/(tool_use|tool_call|function_call)[:\s][^\n]*/gi, ''],
  // Model names in text
  [/\b(claude-\S+|gpt-4\S*|gpt-3\S*|gemini-\S+)\b/gi, 'our AI'],
];

export function sanitizeOutput(text: string): string {
  if (!text) return text;
  let result = text;
  for (const [pattern, replacement] of STRIP_PATTERNS) {
    result = result.replace(pattern, replacement);
  }
  return result.trim();
}
