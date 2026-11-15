export type PlanWindow = { kind: string; percentUsed: number; resetsAt?: string }

export type View = {
  windows: PlanWindow[]
  model: string
  run: string | null
  runSpent: Record<string, number>
}

declare module 'claude-code' {
  interface PluginState {
    'plan-meter': { view: Shaped<View | null> }
  }
}
