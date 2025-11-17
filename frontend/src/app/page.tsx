'use client';

import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  ArrowRight,
  Shield,
  Zap,
  MessageSquare,
  Wallet,
  FileText,
  Mic,
  Brain,
  Lock,
  TrendingUp,
  CheckCircle2,
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
              <span className="text-sm font-bold">IOB</span>
            </div>
            <span className="font-bold text-xl">MAIIS</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/auth/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/auth/signup">
              <Button>Get Started</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="flex-1">
        <div className="container flex flex-col items-center justify-center gap-8 py-24 md:py-32">
          <div className="flex flex-col items-center gap-4 text-center">
            <div className="inline-flex items-center rounded-full border px-3 py-1 text-sm">
              <Brain className="mr-2 h-4 w-4" />
              AI-Powered Banking Assistant
            </div>
            <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl max-w-3xl">
              Banking Made
              <span className="text-primary"> Intelligent</span>
            </h1>
            <p className="max-w-2xl text-lg text-muted-foreground md:text-xl">
              Experience the future of banking with our multimodal AI assistant. Chat, manage accounts,
              process documents, and use voice commands—all in one powerful platform.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 mt-4">
              <Link href="/auth/signup">
                <Button size="lg" className="w-full sm:w-auto">
                  Start Free Trial
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/auth/login">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mt-12 w-full max-w-4xl">
            <div className="flex flex-col items-center">
              <div className="text-3xl font-bold text-primary">99.9%</div>
              <div className="text-sm text-muted-foreground">Uptime</div>
            </div>
            <div className="flex flex-col items-center">
              <div className="text-3xl font-bold text-primary">24/7</div>
              <div className="text-sm text-muted-foreground">AI Support</div>
            </div>
            <div className="flex flex-col items-center">
              <div className="text-3xl font-bold text-primary">100K+</div>
              <div className="text-sm text-muted-foreground">Transactions</div>
            </div>
            <div className="flex flex-col items-center">
              <div className="text-3xl font-bold text-primary">256-bit</div>
              <div className="text-sm text-muted-foreground">Encryption</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-t bg-muted/50 py-24">
        <div className="container">
          <div className="flex flex-col items-center gap-4 text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
              Powerful Features
            </h2>
            <p className="max-w-2xl text-muted-foreground md:text-lg">
              Everything you need to manage your finances efficiently with AI assistance
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <MessageSquare className="h-10 w-10 text-primary mb-2" />
                <CardTitle>AI Chat Assistant</CardTitle>
                <CardDescription>
                  Natural language conversations with RAG-powered AI for instant banking support
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Real-time streaming responses
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Context-aware answers
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    24/7 availability
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Wallet className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Smart Banking</CardTitle>
                <CardDescription>
                  Complete account management with intelligent insights and analytics
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Multiple account types
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Instant transfers
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Transaction tracking
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <FileText className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Document Processing</CardTitle>
                <CardDescription>
                  OCR-powered document analysis for automatic data extraction
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Automated OCR
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Smart categorization
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Secure storage
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Mic className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Voice Banking</CardTitle>
                <CardDescription>
                  Hands-free banking with speech-to-text and text-to-speech capabilities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Voice commands
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Audio responses
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Multi-language support
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Shield className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Enterprise Security</CardTitle>
                <CardDescription>
                  Bank-grade security with encryption and compliance standards
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    256-bit encryption
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    JWT authentication
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Audit logging
                  </li>
                </ul>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Zap className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Real-time Analytics</CardTitle>
                <CardDescription>
                  Live insights and visualizations of your financial data
                </CardDescription>
              </CardHeader>
              <CardContent>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Interactive charts
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Spending insights
                  </li>
                  <li className="flex items-center gap-2">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    Custom reports
                  </li>
                </ul>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="border-t py-24">
        <div className="container">
          <div className="flex flex-col items-center gap-4 text-center mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
              Built with Modern Technology
            </h2>
            <p className="max-w-2xl text-muted-foreground md:text-lg">
              Enterprise-grade architecture powered by cutting-edge AI and cloud technologies
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3">
            <Card>
              <CardHeader>
                <Brain className="h-10 w-10 text-primary mb-2" />
                <CardTitle>AI & Machine Learning</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                <p>Powered by Ollama LLMs with RAG (Retrieval Augmented Generation) for accurate,
                context-aware responses using your own data.</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <Lock className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Secure Infrastructure</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                <p>Built on PostgreSQL, Redis, and Qdrant vector database with Docker containerization
                for reliability and security.</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <TrendingUp className="h-10 w-10 text-primary mb-2" />
                <CardTitle>Scalable Architecture</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground">
                <p>FastAPI backend with Next.js frontend, designed to handle high traffic and grow
                with your needs.</p>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="border-t bg-muted/50 py-24">
        <div className="container">
          <div className="flex flex-col items-center gap-8 text-center">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl max-w-3xl">
              Ready to transform your banking experience?
            </h2>
            <p className="max-w-2xl text-muted-foreground md:text-lg">
              Join thousands of users who are already experiencing the future of AI-powered banking.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/auth/signup">
                <Button size="lg">
                  Get Started Now
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/auth/login">
                <Button size="lg" variant="outline">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12">
        <div className="container">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <span className="text-sm font-bold">IOB</span>
              </div>
              <span className="font-bold text-xl">MAIIS</span>
            </div>
            <p className="text-sm text-muted-foreground">
              © 2025 IOB MAIIS. All rights reserved.
            </p>
            <div className="flex gap-4 text-sm text-muted-foreground">
              <Link href="/privacy" className="hover:text-foreground">Privacy</Link>
              <Link href="/terms" className="hover:text-foreground">Terms</Link>
              <Link href="/contact" className="hover:text-foreground">Contact</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
