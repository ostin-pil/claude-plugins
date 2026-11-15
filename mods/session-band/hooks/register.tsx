import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'

import type { Band, Live } from '../types'

// The lifecycle rules this band watches, in a repo where every session works in its own worktree
// on `feature/session-<n>-<thread>-<what>`: `git worktree list` says which sessions are live; one
// session per thread; merge `main` into the branch before writing STATE.md, and check again before
// finalizing, since a parallel session can land on `main` in between; keep the main checkout clean
// and never switch it off main.
const band = atom({ plugin: 'session-band', key: 'band' } as const, null, { shape: 'band-1' })
const SESSION = /^feature\/session-(\d+)-([a-z]+)-(.+)$/
// Backslash to forward slash, without a backslash in the source.
const slash = (p: string) => p.split(String.fromCharCode(92)).join('/')

async function git($: EngineInterface, cwd: string, args: string[]) {
  try {
    const r = await $.process.run(['git', ...args], { cwd, timeoutMs: 15000 })
    return r.exitCode === 0 ? r.stdout : null
  } catch {
    return null
  }
}

async function scan($: EngineInterface) {
  const cwd = await $.session.cwd()
  const top = await git($, cwd, ['rev-parse', '--show-toplevel', '--abbrev-ref', 'HEAD'])
  if (top === null) {
    await update($, band, () => null)
    return
  }
  const [root = '', branch = ''] = top.trim().split(/\r?\n/)
  const porcelain = (await git($, cwd, ['worktree', 'list', '--porcelain'])) ?? ''
  const trees: { path: string; branch: string }[] = []
  for (const block of porcelain.split(/\r?\n\r?\n/)) {
    const path = /^worktree (.+)$/m.exec(block)?.[1]
    if (!path) continue
    const b = /^branch refs\/heads\/(.+)$/m.exec(block)?.[1] ?? '(detached)'
    trees.push({ path, branch: b })
  }
  const live: Live[] = []
  for (const t of trees) {
    const m = SESSION.exec(t.branch)
    if (m) live.push({ n: Number(m[1]), thread: m[2] ?? '?', topic: m[3] ?? '?', isHere: t.branch === branch })
  }
  live.sort((a, b) => a.n - b.n)
  const here = live.find(l => l.isHere) ?? null
  const primary = trees[0]
  let mainAhead = 0
  if (here) {
    const n = await git($, cwd, ['rev-list', '--count', `HEAD..main`])
    mainAhead = n ? Number(n.trim()) || 0 : 0
  }
  let primaryDirty = 0
  if (primary) {
    const st = await git($, primary.path, ['status', '--porcelain'])
    primaryDirty = st ? st.split(/\r?\n/).filter(Boolean).length : 0
  }
  const repo = slash(primary?.path ?? root).split('/').filter(Boolean).pop() ?? root
  const next: Band = {
    repo,
    branch,
    here,
    isPrimary: slash(primary?.path ?? '').toLowerCase() === slash(root).toLowerCase(),
    live,
    mainAhead,
    primaryBranch: primary?.branch ?? '?',
    primaryDirty,
  }
  await update($, band, () => next)
}

let busy = false

async function refresh($: EngineInterface) {
  if (busy) return
  busy = true
  try {
    await scan($)
  } finally {
    busy = false
  }
}

export const register: Register = on => {

  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'sessions', description: 'Rescan the live sessions band now' })
    void refresh($)
    $.clock.every(90_000, () => refresh($))
    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    if (!e.agentId) void refresh($)
    return next(e)
  })

  on('command.run', { command: 'sessions' }, async $ => {
    await refresh($)
    const b = await read($, band)
    if (!b) return { text: 'Not in a git repository.' }
    const list = b.live.map(l => `${l.n} ${l.thread} (${l.topic})${l.isHere ? ' <- this one' : ''}`).join('\n  ')
    return { text: `${b.repo}: ${b.live.length} live session(s)\n  ${list || 'none'}` }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const b = await read($, band)
    if (e.props.hasSurvey || b === null || (b.live.length === 0 && b.primaryDirty === 0)) return next(e)
    const { Box, Text } = $.ui.resolve(e)
    const others = b.live.filter(l => !l.isHere)
    const sameThread = b.here ? others.filter(l => l.thread === b.here!.thread) : []
    const primaryOff = /^feature\/session-/.test(b.primaryBranch)
    return (
      <Box>
        <Text dimColor>{b.repo} · </Text>
        {b.here ? (
          <Text color="cyan">
            session {b.here.n} {b.here.thread}
          </Text>
        ) : (
          <Text dimColor>{b.isPrimary ? 'main checkout' : b.branch}</Text>
        )}
        <Text dimColor>
          {others.length ? ` · also live: ${others.map(l => `${l.n} ${l.thread}`).join(', ')}` : ' · no other live session'}
        </Text>
        {sameThread.length > 0 && <Text color="yellow"> · two {b.here!.thread} sessions: name file partitions</Text>}
        {b.mainAhead > 0 && (
          <Text color="yellow">
            {' '}
            · main moved {b.mainAhead} commit{b.mainAhead === 1 ? '' : 's'}: merge it before STATE.md
          </Text>
        )}
        {primaryOff && <Text color="red"> · main checkout is on {b.primaryBranch}</Text>}
        {b.primaryDirty > 0 && (
          <Text color="yellow">
            {' '}
            · main checkout has {b.primaryDirty} uncommitted change{b.primaryDirty === 1 ? '' : 's'}
          </Text>
        )}
      </Box>
    )
  })
}
