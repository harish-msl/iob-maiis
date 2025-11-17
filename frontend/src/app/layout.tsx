import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import { ThemeProvider } from 'next-themes'
import { Toaster } from 'sonner'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'IOB MAIIS - Multimodal AI Banking Assistant',
  description: 'Enterprise-grade RAG-powered multimodal AI banking assistant',
  keywords: ['banking', 'AI', 'RAG', 'multimodal', 'finance'],
  authors: [{ name: 'IOB MAIIS Team' }],
  openGraph: {
    title: 'IOB MAIIS - Multimodal AI Banking Assistant',
    description: 'Enterprise-grade RAG-powered multimodal AI banking assistant',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
          <Toaster
            position="top-right"
            expand={false}
            richColors
            closeButton
            toastOptions={{
              duration: 4000,
              style: {
                background: 'hsl(var(--background))',
                color: 'hsl(var(--foreground))',
                border: '1px solid hsl(var(--border))',
              },
            }}
          />
        </ThemeProvider>
      </body>
    </html>
  )
}
