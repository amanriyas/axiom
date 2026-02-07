"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowRight, Zap, Clock, FileText, Calendar, Shield, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { getToken } from "@/lib/api";

const features = [
  {
    icon: Zap,
    title: "Zero-Touch Automation",
    description: "From offer acceptance to first day, everything happens automatically.",
  },
  {
    icon: Clock,
    title: "Save Hours of Work",
    description: "Eliminate manual onboarding tasks and let AI handle the heavy lifting.",
  },
  {
    icon: FileText,
    title: "Smart Document Generation",
    description: "AI generates personalized offer letters and 30-60-90 plans using your policies.",
  },
  {
    icon: Calendar,
    title: "Automatic Scheduling",
    description: "Orientation, 1:1s, and buddy meetups scheduled without any manual work.",
  },
  {
    icon: Shield,
    title: "Policy-Aware",
    description: "RAG-powered system ensures all documents align with your company policies.",
  },
  {
    icon: Users,
    title: "Bulk Import",
    description: "Import hundreds of new hires via CSV and onboard them all at once.",
  },
];

export default function LandingPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to dashboard if already logged in
    const token = getToken();
    if (token) {
      router.push("/dashboard");
    }
  }, [router]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border">
        <div className="container mx-auto flex h-16 items-center justify-between px-4">
          <Link href="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
              <span className="text-sm font-bold text-primary-foreground">A</span>
            </div>
            <span className="text-lg font-semibold">Axiom</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/signup">
              <Button>Get Started</Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="container mx-auto px-4 py-24 text-center">
        <div className="mx-auto max-w-3xl space-y-6">
          <h1 className="text-5xl font-bold tracking-tight">
            Zero-Touch Employee Onboarding
          </h1>
          <p className="text-xl text-muted-foreground">
            AI-powered platform that automates the entire onboarding workflow.
            From contract generation to calendar scheduling — zero manual intervention required.
          </p>
          <div className="flex items-center justify-center gap-4 pt-4">
            <Link href="/signup">
              <Button size="lg">
                Get Started
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline">
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-4 py-16">
        <h2 className="mb-12 text-center text-3xl font-bold">
          Everything automated, nothing manual
        </h2>
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <div
                key={feature.title}
                className="rounded-lg border border-border bg-card p-6"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                  <Icon className="h-6 w-6 text-primary" />
                </div>
                <h3 className="mb-2 text-lg font-semibold">{feature.title}</h3>
                <p className="text-muted-foreground">{feature.description}</p>
              </div>
            );
          })}
        </div>
      </section>

      {/* CTA */}
      <section className="container mx-auto px-4 py-24 text-center">
        <div className="mx-auto max-w-2xl space-y-6">
          <h2 className="text-3xl font-bold">Ready to automate onboarding?</h2>
          <p className="text-muted-foreground">
            Start onboarding new employees with zero manual work today.
          </p>
          <Link href="/signup">
            <Button size="lg">
              Create Free Account
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>Built for the hackathon. Powered by AI.</p>
        </div>
      </footer>
    </div>
  );
}
