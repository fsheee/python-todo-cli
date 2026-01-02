/**
 * Root layout for Next.js app
 */

import type { Metadata } from 'next'
import '@/styles/globals.css'

export const metadata: Metadata = {
  title: 'Todo Assistant - AI Chatbot',
  description: 'Manage your todos with AI-powered conversation',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
