export type Live = { n: number; thread: string; topic: string; isHere: boolean }

export type Band = {
  repo: string
  branch: string
  here: Live | null
  isPrimary: boolean
  live: Live[]
  mainAhead: number
  primaryBranch: string
  primaryDirty: number
}

declare module 'claude-code' {
  interface PluginState {
    'session-band': { band: Shaped<Band | null> }
  }
}
