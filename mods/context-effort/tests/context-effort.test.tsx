import { expect, test } from 'claude-code/testing'

const ROW = {
  plugin: 'context-effort',
  component: 'AbovePrompt',
  props: {
    hasSurvey: false,
    isCollapsed: false,
    isWorking: false,
    maxRows: 3,
    bodyColumns: 100,
    scroll: { offset: 0, bodyRows: 3 },
    view: {},
  },
} as const

const stepDone = (e: { turnId: string; index: number }) => ({
  turnId: e.turnId,
  index: e.index,
  answer: '',
  toolUses: [],
  stopReason: 'end_turn' as const,
  usage: null,
})

test('the row shows the context fill and the main loop effort, not a sub-agent one', async ($, on) => {
  on('session.usage', () => ({
    value: { startedAt: 0, context: { tokens: 76_000, window: 200_000, percent: 38 }, rateLimits: [] },
  }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('turn.step', async function* (_, e) {
    return stepDone(e)
  })

  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  const main = $.turn.step({ turnId: 't1', index: 0, model: 'opus', effort: 'high', messageCount: 1 })
  for await (const _ of main) void _
  await main.result
  const sub = $.turn.step({ turnId: 't2', index: 0, model: 'haiku', effort: 'low', messageCount: 1, agentId: 'a1' })
  for await (const _ of sub) void _
  await sub.result

  for (const surface of ['terminal', 'desktop'] as const) {
    const ui = await $.ui.mount({ ...ROW, surface })
    expect((await ui.find({ type: 'Text', text: /^38%$/ }))?.text).toBe('38%')
    expect((await ui.find({ type: 'Text', text: /76k of 200k/ }))?.text).toContain('76k of 200k')
    expect((await ui.find({ type: 'Text', text: /^high$/ }))?.text).toBe('high')
    expect(await ui.find({ type: 'Text', text: /^low$/ })).toBeUndefined()
    await ui.unmount()
  }
})

test('a new measurement moves the fill, and a step with no effort reads as the model default', async ($, on) => {
  on('session.usage', () => ({ value: { startedAt: 0, context: { window: 1_000_000 }, rateLimits: [] } }))
  on('session.start', (_, e) => ({ cwd: e.cwd }))
  on('session.measure', (_, e) => ({ changed: e.changed }))
  on('turn.step', async function* (_, e) {
    return stepDone(e)
  })

  await $.session.start({ cwd: '/', surface: 'terminal', isInteractive: true })

  let ui = await $.ui.mount({ ...ROW, surface: 'terminal' })
  expect((await ui.find({ type: 'Text', text: /new window/ }))?.text).toContain('new window')
  expect((await ui.find({ type: 'Text', text: /not sent yet/ }))?.text).toBe('not sent yet')
  await ui.unmount()

  await $.session.measure({
    context: { tokens: 900_000, window: 1_000_000, percent: 90 },
    rateLimits: [],
    changed: ['context'],
  })
  const step = $.turn.step({ turnId: 't1', index: 0, model: 'sonnet', messageCount: 1 })
  for await (const _ of step) void _
  await step.result

  ui = await $.ui.mount({ ...ROW, surface: 'terminal' })
  expect((await ui.find({ type: 'Text', text: /^90%$/ }))?.text).toBe('90%')
  expect((await ui.find({ type: 'Text', text: /900k of 1M/ }))?.text).toContain('900k of 1M')
  expect((await ui.find({ type: 'Text', text: /model default/ }))?.text).toBe('model default')
  await ui.unmount()
})
