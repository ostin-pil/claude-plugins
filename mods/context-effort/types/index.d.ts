export type Gauge = {
  /** Input tokens the last response was answered over; null before the live window's first response. */
  tokens: number | null
  /** The session model's context window, in tokens. */
  window: number
  /** tokens over window, 0 to 100; null with tokens. */
  percent: number | null
  /**
   * The effort the main loop's last model request was sent at: a level, a number as text,
   * or null when the request carried none (the model's own default). Undefined until a step is seen.
   */
  effort?: string | null
}

declare module 'claude-code' {
  interface PluginState {
    'context-effort': { gauge: Shaped<Gauge | null> }
  }
}
