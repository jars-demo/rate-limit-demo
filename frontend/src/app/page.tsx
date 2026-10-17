import Link from 'next/link'

import { CopyButton } from '@/components/CopyButton'
import { REPO_URL } from '@/components/Shell'
import { CHAPTERS } from '@/lib/workshop'

// Real output of `uv run python -m limits simulate --pattern edge`.
const EDGE = [
  { name: 'none', allowed: 20, worst: 20 },
  { name: 'fixed-window', allowed: 20, worst: 20 },
  { name: 'sliding-log', allowed: 10, worst: 10 },
  { name: 'token-bucket', allowed: 11, worst: 11 },
]

const PARTS = [
  ['Fixed window', 'lab/limits/fixed_window.py', 'A counter per second. Simple, with a hole.'],
  ['Sliding log', 'lab/limits/sliding_log.py', 'Exact over any second, paid for in memory.'],
  ['Token bucket', 'lab/limits/token_bucket.py', 'Bursts on purpose, a steady average.'],
  ['Polite client', 'lab/limits/client.py', 'Backoff, jitter and Retry-After.'],
]

const QUICKSTART = `git clone https://github.com/jars-demo/rate-limit-demo.git
cd rate-limit-demo/lab
uv sync
uv run python -m limits simulate`

export default function Home() {
  const minutes = CHAPTERS.reduce((sum, chapter) => sum + chapter.minutes, 0)

  return (
    <div className="mx-auto flex max-w-5xl flex-col gap-20 px-4 pt-16 pb-24 sm:pt-24">
      <section className="grid items-start gap-12 lg:grid-cols-[1.05fr_1fr]">
        <div className="flex min-w-0 flex-col gap-6">
          <p className="font-mono text-[12px] tracking-wider text-muted uppercase">
            Backend workshop · {CHAPTERS.length} chapters · {minutes} minutes
          </p>
          <h1 className="text-[2.75rem] leading-[1.05] font-bold tracking-[-0.035em] text-balance sm:text-[3.5rem]">
            Rate limits from scratch.
          </h1>
          <p className="max-w-xl text-[18px] leading-relaxed text-ink-2">
            One busy client should not take your API down for everyone. Build three rate limiters in
            plain Python, put them in front of a real HTTP server, break them on purpose, and write
            the client that backs off politely.
          </p>
          <ul className="flex flex-col gap-1.5 text-[15px] text-ink-2">
            <li>No dependencies: Python standard library only.</li>
            <li>A simulator with a fake clock: replay traffic in milliseconds.</li>
            <li>A real server answering 429 with Retry-After, and a hammer to test it.</li>
            <li>Every chapter ends with an exercise and a way to check it.</li>
          </ul>
          <div className="flex flex-wrap gap-3 pt-2">
            <Link
              href="/workshop/01-why-rate-limits"
              className="inline-flex h-11 items-center rounded-lg bg-accent px-5 text-[15px] font-semibold text-white hover:bg-accent-strong"
            >
              Start the workshop
            </Link>
            <a
              href={REPO_URL}
              className="inline-flex h-11 items-center rounded-lg border border-line-strong bg-canvas px-5 text-[15px] font-medium hover:bg-surface-2"
            >
              View the code
            </a>
          </div>
        </div>

        <figure className="code min-w-0 overflow-hidden rounded-xl">
          <figcaption className="flex items-center justify-between gap-3 border-b border-white/10 px-4 py-2.5 text-[12px] text-[#a8a29e]">
            <span>python -m limits simulate</span>
            <span>limit 10 per second</span>
          </figcaption>
          <div className="overflow-x-auto px-4 py-4 text-[12.5px] leading-[1.75]">
            <div className="whitespace-pre text-[#a8a29e]">
              {'20 requests between 0.90s and 1.09s\n\n'}
              {'limiter'.padEnd(14)}
              {'allowed'.padStart(8)}
              {'worst 1s'.padStart(10)}
            </div>
            {EDGE.map((row) => (
              <div key={row.name} className="whitespace-pre">
                {row.name.padEnd(14)}
                {String(row.allowed).padStart(8)}
                <span className={row.worst > 10 ? 'text-[#fb923c]' : 'text-[#86efac]'}>
                  {String(row.worst).padStart(10)}
                </span>
              </div>
            ))}
            <div className="mt-3 border-t border-white/10 pt-3 text-[#a8a29e]">
              The fixed window let twice the limit through.
            </div>
          </div>
        </figure>
      </section>

      <section aria-labelledby="parts" className="flex flex-col gap-6">
        <h2 id="parts" className="text-[1.6rem] font-bold tracking-[-0.02em]">
          What you build
        </h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {PARTS.map(([name, file, about]) => (
            <div
              key={name}
              className="flex flex-col gap-2 rounded-xl border border-line bg-canvas p-5"
            >
              <span className="text-[15px] font-semibold">{name}</span>
              <code className="font-mono text-[12px] break-all text-accent">{file}</code>
              <span className="text-[14px] text-ink-2">{about}</span>
            </div>
          ))}
        </div>
      </section>

      <section aria-labelledby="chapters" className="grid gap-10 lg:grid-cols-[1fr_1.3fr]">
        <div className="flex flex-col gap-3">
          <h2 id="chapters" className="text-[1.6rem] font-bold tracking-[-0.02em]">
            {CHAPTERS.length} short chapters
          </h2>
          <p className="text-[15px] leading-relaxed text-ink-2">
            Each one is a few minutes of reading, one thing to run, and an exercise. By the end you
            can pick a limiter, a key and a limit for a real API, and explain why.
          </p>
        </div>
        <ol className="overflow-hidden rounded-xl border border-line bg-canvas">
          {CHAPTERS.map((chapter) => (
            <li key={chapter.slug} className="border-b border-line last:border-b-0">
              <Link
                href={`/workshop/${chapter.slug}`}
                className="flex items-baseline gap-4 px-4 py-3.5 hover:bg-surface-2"
              >
                <span className="w-7 shrink-0 font-mono text-[13px] text-accent">
                  {chapter.number}
                </span>
                <span className="min-w-0 flex-1 text-[15px] font-medium">{chapter.title}</span>
                <span className="shrink-0 font-mono text-[12px] text-muted">
                  {chapter.minutes} min
                </span>
              </Link>
            </li>
          ))}
        </ol>
      </section>

      <section aria-labelledby="start" className="flex flex-col gap-4">
        <h2 id="start" className="text-[1.6rem] font-bold tracking-[-0.02em]">
          Run it in a minute
        </h2>
        <p className="text-[15px] text-ink-2">
          You need{' '}
          <a href="https://docs.astral.sh/uv/" className="text-accent underline underline-offset-4">
            uv
          </a>{' '}
          and git. uv installs Python for you.
        </p>
        <div className="code relative max-w-2xl overflow-x-auto rounded-xl px-4 pt-10 pb-4 text-[13px] leading-relaxed">
          <div className="absolute top-2 right-2">
            <CopyButton text={QUICKSTART} />
          </div>
          <pre>{QUICKSTART}</pre>
        </div>
      </section>
    </div>
  )
}
