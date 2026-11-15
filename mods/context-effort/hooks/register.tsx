import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, SessionContextUsage } from 'claude-code'

import type { Gauge } from '../types'

// One row above the prompt: how full the live context window is (the status line's
// used_percentage, from the last response) and the effort the main loop's last model
// request went out at, after any downgrade for the model. A sub-agent's steps are left out,
// since they run at their own effort.
const gauge = atom({ plugin: 'context-effort', key: 'gauge' } as const, null, { shape: 'gauge-1' })

function tokensText(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(n % 1_000_000 === 0 ? 0 : 1)}M`
  if (n >= 10_000) return `${Math.round(n / 1000)}k`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`
  return String(n)
}

async function setContext($: EngineInterface, c: SessionContextUsage) {
  await update($, gauge, g => ({
    ...(g ?? {}),
    tokens: c.tokens ?? null,
    window: c.window,
    percent: c.percent ?? null,
  }))
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    try {
      const usage = await $.session.usage()
      await setContext($, usage.context)
    } catch {
      // No reading yet; session.measure fills it in after the first response.
    }
    return next(e)
  })

  on('session.measure', async ($, e, next) => {
    await setContext($, e.context)
    return next(e)
  })

  on('turn.step', async function* ($, e, next) {
    if (!e.agentId) {
      const effort = e.effort === undefined ? null : String(e.effort)
      await update($, gauge, g => (g ? { ...g, effort } : { tokens: null, window: 0, percent: null, effort }))
    }
    return yield* next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const g = await read($, gauge)
    if (e.props.hasSurvey || g === null || g.window === 0) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    const pct = g.percent
    const fill = pct === null ? undefined : pct >= 85 ? 'red' : pct >= 70 ? 'yellow' : undefined
    const used = g.tokens === null ? 'new window' : `${tokensText(g.tokens)} of ${tokensText(g.window)}`
    const effort = g.effort === undefined ? 'not sent yet' : g.effort === null ? 'model default' : g.effort
    const effortColor = g.effort === 'low' ? 'yellow' : g.effort === 'max' ? 'magenta' : undefined
    return (
      <Box>
        <Text dimColor>context </Text>
        <Text color={fill} dimColor={fill === undefined}>
          {pct === null ? '0%' : `${pct}%`}
        </Text>
        <Text dimColor> ({used}) · effort </Text>
        <Text color={effortColor} dimColor={effortColor === undefined && g.effort == null}>
          {effort}
        </Text>
      </Box>
    )
  })
}
