export type Spawn = {
  agentId: string | null
  type: string
  description: string
  model: string
  nested: boolean
  workflow: boolean
  at: number
  turns: number
  outputTokens: number
}

declare module 'claude-code' {
  interface PluginState {
    'agent-count': { spawns: Shaped<Spawn[]> }
  }
}
