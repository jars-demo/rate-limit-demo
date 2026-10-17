import type { Metadata, Viewport } from 'next'
import { JetBrains_Mono, Space_Grotesk } from 'next/font/google'

import { Shell } from '@/components/Shell'

import './globals.css'

const sans = Space_Grotesk({
  variable: '--font-face-sans',
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
})
const mono = JetBrains_Mono({
  variable: '--font-face-mono',
  subsets: ['latin'],
  weight: ['400', '500'],
})

export const metadata: Metadata = {
  title: { default: 'Rate limits from scratch', template: '%s · Rate limits from scratch' },
  description:
    'A hands-on backend workshop: build fixed window, sliding log and token bucket rate limiters in plain Python, put them in front of a real HTTP server, and write a client that backs off politely.',
}

export const viewport: Viewport = { themeColor: '#fcfbf8' }

export default function RootLayout({ children }: LayoutProps<'/'>) {
  return (
    <html lang="en" className={`${sans.variable} ${mono.variable} h-full antialiased`}>
      <body className="flex min-h-full flex-col">
        <a
          href="#main"
          className="sr-only bg-ink px-4 py-2 text-canvas focus:not-sr-only focus:fixed focus:top-4 focus:left-4 focus:z-50"
        >
          Skip to content
        </a>
        <Shell>{children}</Shell>
      </body>
    </html>
  )
}
