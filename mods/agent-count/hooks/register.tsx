import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Spawn } from '../types'

// Every sub-agent this session started, in order. Session state: it survives a reload of the mod
// and starts empty in a new session. A session log that reports how many sub-agents ran needs the
// count that ran, which is not the count the session launched: sub-agents start their own (four
// launched can be thirteen run), so nested spawns are counted here too.
const spawns = atom({ plugin: 'agent-count', key: 'spawns' } as const, [], { shape: 'spawns-1' })

const short = (m: string) => m.replace(/^claude-/, '').replace(/\[.*\]$/, '')

function tally(list: Spawn[]) {
  const top = list.filter(s => !s.nested).length
  const nested = list.length - top
  const by = (key: (s: Spawn) => string) => {
    const m: Record<string, number> = {}
    for (const s of list) m[key(s)] = (m[key(s)] ?? 0) + 1
    return Object.entries(m)
      .sort((a, b) => b[1] - a[1])
      .map(([k, n]) => `${n} ${k}`)
      .join(', ')
  }
  const out = list.reduce((n, s) => n + s.outputTokens, 0)
  return { top, nested, total: list.length, byType: by(s => s.type), byModel: by(s => short(s.model)), out }
}

async function showStatus($: EngineInterface) {
  const t = tally(await read($, spawns))
  $.ui.status(t.total ? `agents ${t.total}${t.nested ? ` (${t.nested} nested)` : ''}` : undefined)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'agent-count',
      description: 'How many sub-agents ran this session, nested ones included, as a line for the session log',
    })
    await showStatus($)
    return next(e)
  })

  on('agent.spawn', async ($, e, next) => {
    const r = await next(e)
    if ('model' in r && r.model) {
      const s: Spawn = {
        agentId: r.agentId ?? null,
        type: e.subagentType,
        description: e.description,
        model: r.model,
        nested: Boolean(e.parentAgentId),
        workflow: Boolean(e.workflow),
        at: await $.clock.now(),
        turns: 0,
        outputTokens: 0,
      }
      await update($, spawns, list => [...list, s])
      await showStatus($)
    }
    return r
  })

  // A sub-agent's turns carry its id; their tokens are added to its row.
  on('turn.complete', async ($, e, next) => {
    if (e.agentId && e.usage) {
      const id = e.agentId
      const out = e.usage.output_tokens ?? 0
      await update($, spawns, list =>
        list.map(s => (s.agentId === id ? { ...s, turns: s.turns + 1, outputTokens: s.outputTokens + out } : s)),
      )
    }
    return next(e)
  })

  on('command.run', { command: 'agent-count' }, async $ => {
    const list = await read($, spawns)
    if (list.length === 0) return { text: 'No sub-agents have run in this session (since the mod loaded).' }
    const t = tally(list)
    const lines = [
      `Sub-agents: ${t.top} started by the session, ${t.total} ran in total` +
        (t.nested ? ` (${t.nested} started by other sub-agents)` : '') +
        `. By type: ${t.byType}. By model: ${t.byModel}. Output tokens: ${Math.round(t.out / 1000)}k.`,
      '',
      ...list.map(
        (s, i) =>
          `${i + 1}. ${s.nested ? '  nested ' : ''}${s.type} on ${short(s.model)}${s.workflow ? ' (workflow)' : ''}: ` +
          `${s.description} · ${s.turns} turns · ${Math.round(s.outputTokens / 1000)}k out`,
      ),
      '',
      'Counted from when this mod loaded. Whether any of them wrote files is not something it can see: say that in the log.',
    ]
    return { text: lines.join('\n') }
  })
}
