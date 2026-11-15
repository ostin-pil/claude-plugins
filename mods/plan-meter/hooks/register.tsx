import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register, SessionRateLimit } from 'claude-code'

import type { View, PlanWindow } from '../types'

// What the band draws. The ledger lives in $.store: it survives sessions and
// is shared by every session that loads this mod.
const view = atom({ plugin: 'plan-meter', key: 'view' } as const, null, {
  shape: 'view-2',
})

type Bucket = {
  spent: Record<string, number> // window kind -> percentage points spent
  turns: number
  outputTokens: number
  inputTokens: number
}
type RunBucket = Bucket & { startedAt: string; models: string[] }
type Ledger = {
  v: 2
  byModel: Record<string, Bucket>
  byRun: Record<string, RunBucket>
  resets: { at: string; kind: string; from: number; to: number }[]
}
// The last account-wide reading any session saw. Deltas are taken against
// this shared reading, so two sessions running the mod do not both count the
// same movement.
type Last = Record<string, PlanWindow>

const freshLedger = (): Ledger => ({ v: 2, byModel: {}, byRun: {}, resets: [] })
const blank = (): Bucket => ({ spent: {}, turns: 0, outputTokens: 0, inputTokens: 0 })
const round1 = (n: number) => Math.round(n * 10) / 10
const toWindows = (list: SessionRateLimit[]): PlanWindow[] =>
  list.map(w => ({ kind: w.kind, percentUsed: w.percentUsed, resetsAt: w.resetsAt }))
const shortModel = (m: string) => m.replace(/^claude-/, '').replace(/\[.*\]$/, '')
const LABEL: Record<string, string> = { five_hour: '5h', seven_day: 'week', spend_limit: 'spend' }
const label = (kind: string) => LABEL[kind] ?? kind.replace(/^seven_day_/, 'wk ').replace(/_/g, ' ')
const DAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
const pad = (n: number) => (n < 10 ? `0${n}` : `${n}`)
const when = (iso: string | undefined, kind: string) => {
  if (!iso) return '?'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return '?'
  const hm = `${pad(d.getHours())}:${pad(d.getMinutes())}`
  return kind === 'five_hour' ? hm : `${DAYS[d.getDay()]} ${hm}`
}
const spentText = (spent: Record<string, number>) =>
  Object.entries(spent)
    .map(([k, v]) => `${label(k)} +${round1(v)}`)
    .join(' · ') || 'nothing yet'

async function loadLedger($: EngineInterface): Promise<Ledger> {
  const raw = (await $.store.get('ledger')) as Ledger | undefined
  return raw && raw.v === 2 ? raw : freshLedger()
}

// The run this session counts toward. A batch run names itself in PLAN_METER_RUN and only its own
// session counts toward it; a label opened with /meter run counts in every session that has no
// label of its own. (With one shared label, the parent session's own work was counted against
// the batch.)
async function currentRun($: EngineInterface): Promise<string | null> {
  const fromEnv = await $.env.get('PLAN_METER_RUN')
  if (fromEnv) return fromEnv
  return ((await $.store.get('run')) as string | undefined) ?? null
}

async function refreshView($: EngineInterface, windows: PlanWindow[]) {
  const model = shortModel(await $.session.model())
  const run = await currentRun($)
  const ledger = await loadLedger($)
  const runSpent = run ? ledger.byRun[run]?.spent ?? {} : {}
  await update($, view, () => ({ windows, model, run, runSpent }))
}

function advise($: EngineInterface, windows: PlanWindow[], toasted: Set<string>) {
  const week = windows.find(w => w.kind === 'seven_day')
  for (const w of windows) {
    for (const t of [80, 90, 95]) {
      const key = `${w.kind}:${w.resetsAt}:${t}`
      if (w.percentUsed < t || toasted.has(key)) continue
      toasted.add(key)
      let tip = ''
      if (w.kind !== 'five_hour' && w.resetsAt) {
        const hours = (new Date(w.resetsAt).getTime() - Date.now()) / 3.6e6
        tip =
          hours > 36
            ? ` Resets in ${Math.round(hours / 24)} days: a good moment for a Full reset.`
            : ` Resets in ${Math.round(hours)} hours: wait rather than spend a Full reset.`
      }
      if (w.kind === 'five_hour' && week && week.percentUsed < 70) {
        tip = ` The week is at ${week.percentUsed}%: wait for ${when(w.resetsAt, w.kind)} rather than spend a Full reset.`
      }
      $.ui.toast(`${label(w.kind)} usage at ${w.percentUsed}%.${tip}`)
    }
  }
}

export const register: Register = on => {
  const toasted = new Set<string>()

  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'meter',
      description: 'Plan usage ledger: /meter · /meter run <label> · /meter run off · /meter clear',
    })
    // A batch run names its label in the environment (`PLAN_METER_RUN`), since `claude -p`
    // cannot type /meter run. Only that session counts toward it.
    const fromEnv = await $.env.get('PLAN_METER_RUN')
    if (fromEnv) {
      const ledger = await loadLedger($)
      ledger.byRun[fromEnv] ??= { ...blank(), startedAt: new Date().toISOString(), models: [] }
      await $.store.set('ledger', ledger)
    }
    const u = await $.session.usage()
    await refreshView($, toWindows(u.rateLimits))
    return next(e)
  })

  // Token counts per model: main thread and subagents alike.
  on('turn.complete', async ($, e, next) => {
    if (e.usage) {
      const ledger = await loadLedger($)
      const m = shortModel(e.usage.model)
      const b = (ledger.byModel[m] ??= blank())
      b.outputTokens += e.usage.output_tokens ?? 0
      b.inputTokens +=
        (e.usage.input_tokens ?? 0) +
        (e.usage.cache_read_input_tokens ?? 0) +
        (e.usage.cache_creation_input_tokens ?? 0)
      if (!e.agentId) b.turns += 1
      const run = await currentRun($)
      const r = run ? ledger.byRun[run] : undefined
      if (r) {
        r.outputTokens += e.usage.output_tokens ?? 0
        if (!e.agentId) r.turns += 1
        if (!r.models.includes(m)) r.models.push(m)
      }
      await $.store.set('ledger', ledger)
    }
    return next(e)
  })

  // PlanWindow movement, attributed to the session's model and the open run.
  on('session.measure', async ($, e, next) => {
    if (!e.changed.includes('rateLimits')) return next(e)
    const now = toWindows(e.rateLimits)
    const last = ((await $.store.get('last')) as Last | undefined) ?? {}
    const ledger = await loadLedger($)
    const model = shortModel(await $.session.model())
    const run = await currentRun($)
    const b = (ledger.byModel[model] ??= blank())
    const r = run ? ledger.byRun[run] : undefined

    for (const w of now) {
      const a = last[w.kind]
      if (!a) continue
      let d = w.percentUsed - a.percentUsed
      if (a.resetsAt !== w.resetsAt || d < 0) {
        ledger.resets.push({ at: new Date().toISOString(), kind: w.kind, from: a.percentUsed, to: w.percentUsed })
        ledger.resets = ledger.resets.slice(-50)
        d = w.percentUsed
      }
      if (d <= 0) continue
      b.spent[w.kind] = round1((b.spent[w.kind] ?? 0) + d)
      if (r) r.spent[w.kind] = round1((r.spent[w.kind] ?? 0) + d)
    }

    const nextLast: Last = { ...last }
    for (const w of now) nextLast[w.kind] = w
    await $.store.set('ledger', ledger)
    await $.store.set('last', nextLast)
    await refreshView($, now)
    advise($, now, toasted)
    return next(e)
  })

  on('command.run', { command: 'meter' }, async ($, e) => {
    const args = e.args.trim().split(/\s+/).filter(Boolean)
    const ledger = await loadLedger($)
    const u = await $.session.usage()
    const windows = toWindows(u.rateLimits)

    if (args[0] === 'run') {
      const name = args.slice(1).join('-')
      if (!name) return { text: 'Usage: /meter run <label>, or /meter run off' }
      if (name === 'off') {
        await $.store.delete('run')
        await refreshView($, windows)
        return { text: 'Run closed. Usage is still counted per model.' }
      }
      ledger.byRun[name] ??= { ...blank(), startedAt: new Date().toISOString(), models: [] }
      await $.store.set('ledger', ledger)
      await $.store.set('run', name)
      await refreshView($, windows)
      return { text: `Run "${name}" is open. PlanWindow movement counts toward it until /meter run off.` }
    }

    if (args[0] === 'clear') {
      await $.store.set('ledger', freshLedger())
      await $.store.delete('run')
      await refreshView($, windows)
      return { text: 'Ledger cleared.' }
    }

    const fmtK = (n: number) => `${Math.round(n / 1000)}k`
    const lines: string[] = []
    lines.push(
      windows.length
        ? 'Now: ' + windows.map(w => `${label(w.kind)} ${w.percentUsed}% (resets ${when(w.resetsAt, w.kind)})`).join(', ') + '.'
        : 'Now: no plan reading yet (one arrives with the first response).',
    )
    const models = Object.entries(ledger.byModel)
    if (models.length) {
      lines.push('', 'By model (window points spent · main turns · output tokens; input counts include cache reads):')
      for (const [m, bk] of models)
        lines.push(`  ${m}: ${spentText(bk.spent)} · ${bk.turns} turns · ${fmtK(bk.outputTokens)} out`)
    }
    const runs = Object.entries(ledger.byRun)
    if (runs.length) {
      lines.push('', 'By run:')
      for (const [name, rb] of runs)
        lines.push(
          `  ${name}: ${spentText(rb.spent)} · ${rb.turns} turns · ${fmtK(rb.outputTokens)} out · ${rb.models.join(', ') || '-'}`,
        )
    }
    if (ledger.resets.length) {
      lines.push('', 'PlanWindow resets seen (a window rolling over, or a Full reset):')
      for (const x of ledger.resets.slice(-6)) lines.push(`  ${x.at.slice(0, 16)} ${label(x.kind)}: ${x.from}% to ${x.to}%`)
    }
    lines.push('', 'Percentages are account-wide: another session working at the same time is counted here too.')
    return { text: lines.join('\n') }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const v = await read($, view)
    if (e.props.hasSurvey || v === null || v.windows.length === 0) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    const color = (w: PlanWindow) => (w.percentUsed >= 90 ? 'red' : w.percentUsed >= 75 ? 'yellow' : undefined)
    return (
      <Box>
        {v.windows.map((w, i) => (
          <Text key={w.kind} color={color(w)} dimColor={w.percentUsed < 75}>
            {i > 0 ? ' · ' : ''}
            {label(w.kind)} {w.percentUsed}% until {when(w.resetsAt, w.kind)}
          </Text>
        ))}
        <Text dimColor> · {v.model}</Text>
        {v.run && <Text color="cyan"> · run {v.run}: {spentText(v.runSpent)}</Text>}
      </Box>
    )
  })
}
