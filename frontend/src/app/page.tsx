"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowRight,
  FileText,
  Calendar,
  Shield,
  Users,
  CheckCircle2,
  Globe,
  Sparkles,
  Mail,
  Play,
  ChevronDown,
  Github,
  Twitter,
  Linkedin,
  ArrowUpRight,
  Building2,
  MessageSquare,
  BarChart3,
  Workflow,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { getToken } from "@/lib/api";

// Intersection Observer hook for scroll animations
function useInView(threshold = 0.1) {
  const ref = useRef<HTMLDivElement>(null);
  const [isInView, setIsInView] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsInView(true);
        }
      },
      { threshold, rootMargin: "0px 0px -50px 0px" }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [threshold]);

  return { ref, isInView };
}

// Animated section wrapper component
function AnimatedSection({
  children,
  className = "",
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}) {
  const { ref, isInView } = useInView(0.1);

  return (
    <div
      ref={ref}
      className={`transition-all duration-700 ease-out ${className}`}
      style={{
        opacity: isInView ? 1 : 0,
        transform: isInView ? "translateY(0)" : "translateY(40px)",
        transitionDelay: `${delay}ms`,
      }}
    >
      {children}
    </div>
  );
}

// Feature data
const features = [
  {
    icon: FileText,
    title: "Smart Contract Generation",
    description: "Jurisdiction-aware employment contracts, NDAs, and equity agreements generated instantly from your policies.",
    color: "from-emerald-500 to-teal-500",
  },
  {
    icon: Globe,
    title: "Multi-Jurisdiction Support",
    description: "Automatic compliance with US, UK, UAE, Germany, and Singapore employment laws and regulations.",
    color: "from-blue-500 to-cyan-500",
  },
  {
    icon: Shield,
    title: "Human-in-the-Loop Approval",
    description: "Review and approve generated documents before they're sent. Full control with zero bottlenecks.",
    color: "from-purple-500 to-pink-500",
  },
  {
    icon: Calendar,
    title: "Automatic Scheduling",
    description: "Orientation, manager 1:1s, and buddy meetups scheduled on Google Calendar without lifting a finger.",
    color: "from-orange-500 to-amber-500",
  },
];

// Stats data
const stats = [
  { value: "40+", label: "Hours Saved", sublabel: "per new hire" },
  { value: "4", label: "Documents", sublabel: "auto-generated" },
  { value: "5", label: "Jurisdictions", sublabel: "supported" },
  { value: "0", label: "Manual Steps", sublabel: "required" },
];

// Testimonials
const testimonials = [
  {
    quote: "We onboarded 50 engineers across 3 countries in a single week. What used to take our HR team months now happens automatically.",
    author: "Sarah Chen",
    role: "VP of People",
    company: "TechScale Inc",
  },
  {
    quote: "The jurisdiction-aware contracts alone saved us from countless compliance headaches. It just knows what each country requires.",
    author: "Marcus Weber",
    role: "Head of HR",
    company: "GlobalFlow",
  },
  {
    quote: "Finally, an onboarding system that doesn't require babysitting. Set it up once, and it handles everything.",
    author: "Priya Sharma",
    role: "COO",
    company: "Velocity Labs",
  },
];

// FAQ data
const faqs = [
  {
    question: "How does Axiom generate compliant documents?",
    answer: "Axiom uses your uploaded company policies combined with jurisdiction-specific legal templates. Our system retrieves relevant policy sections and generates documents that comply with local employment laws for each country.",
  },
  {
    question: "Can I review documents before they're sent?",
    answer: "Absolutely. Every generated document goes through an approval gate where you can review, request revisions, or approve. Nothing gets sent without your explicit approval.",
  },
  {
    question: "What jurisdictions are supported?",
    answer: "Currently, Axiom supports the United States, United Kingdom, United Arab Emirates, Germany, and Singapore. Each jurisdiction has specific contract templates that comply with local labor laws.",
  },
  {
    question: "How does the calendar integration work?",
    answer: "Once you connect your Google Calendar, Axiom automatically schedules orientation sessions, manager 1:1 meetings, and buddy meetups based on availability and your company's onboarding timeline.",
  },
  {
    question: "Can I import employees in bulk?",
    answer: "Yes! Upload a CSV file with your new hire data and Axiom will process them all simultaneously. Each employee gets their own onboarding workflow with real-time progress tracking.",
  },
  {
    question: "Is my company data secure?",
    answer: "All data is encrypted at rest and in transit. Your policy documents are stored securely and only used to generate documents for your organization. We never share or use your data for training.",
  },
];

export default function LandingPage() {
  const router = useRouter();
  const [scrolled, setScrolled] = useState(false);
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [activeScreenshot, setActiveScreenshot] = useState(0);

  useEffect(() => {
    const token = getToken();
    if (token) {
      router.push("/dashboard");
    }
  }, [router]);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Auto-rotate screenshots
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveScreenshot((prev) => (prev + 1) % 2);
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white overflow-x-hidden">
      {/* Header */}
      <header
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
          scrolled ? "bg-[#0a0a0a]/95 backdrop-blur-lg border-b border-white/10 shadow-lg" : ""
        }`}
      >
        <div className="container mx-auto flex h-16 items-center justify-between px-4 lg:px-8">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500 transition-transform group-hover:scale-105">
              <span className="text-sm font-bold text-white">A</span>
            </div>
            <span className="text-lg font-semibold">Axiom</span>
          </Link>

          <nav className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-gray-400 hover:text-white transition-colors">Features</a>
            <a href="#how-it-works" className="text-sm text-gray-400 hover:text-white transition-colors">How It Works</a>
            <a href="#testimonials" className="text-sm text-gray-400 hover:text-white transition-colors">Testimonials</a>
            <a href="#faq" className="text-sm text-gray-400 hover:text-white transition-colors">FAQ</a>
          </nav>

          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost" className="text-gray-300 hover:text-white hover:bg-white/10">
                Sign In
              </Button>
            </Link>
            <Link href="/signup">
              <Button className="bg-emerald-500 hover:bg-emerald-600 text-white">
                Get Started
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-28 pb-8 lg:pt-36 lg:pb-12 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-b from-emerald-500/10 via-transparent to-transparent" />
        <div className="absolute top-20 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-emerald-500/20 rounded-full blur-[120px] opacity-30" />

        <div className="container mx-auto px-4 lg:px-8 relative">
          <AnimatedSection className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <Badge className="mb-6 bg-emerald-500/10 text-emerald-400 border-emerald-500/20 hover:bg-emerald-500/20 px-4 py-1.5">
              <Sparkles className="w-3.5 h-3.5 mr-2" />
              Employee Onboarding, Reimagined
            </Badge>

            {/* App Name */}
            <h1 className="text-5xl sm:text-6xl lg:text-8xl font-bold tracking-tight mb-4 gradient-text">
              Axiom
            </h1>

            {/* Tagline */}
            <p className="text-2xl sm:text-3xl lg:text-5xl font-bold tracking-tight mb-6 leading-[1.1] text-white">
              From Offer to Orientation.{" "}
              <span className="gradient-text">Automatically.</span>
            </p>

            {/* Subheadline */}
            <p className="text-lg sm:text-xl text-gray-400 max-w-2xl mx-auto mb-8">
              New hire accepted? Contracts, compliance docs, welcome emails, and calendar events
              — all generated and scheduled with zero manual work.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
              <Link href="/signup">
                <Button size="lg" className="bg-emerald-500 hover:bg-emerald-600 text-white px-8 h-12 text-base group">
                  Start Onboarding
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
              <Link href="#how-it-works">
                <Button size="lg" variant="outline" className="border-gray-700 hover:bg-white/5 text-white px-8 h-12 text-base group">
                  <Play className="mr-2 h-4 w-4" />
                  See How It Works
                </Button>
              </Link>
            </div>
          </AnimatedSection>

          {/* Screenshot Gallery */}
          <AnimatedSection delay={200} className="max-w-5xl mx-auto">
            <div className="relative">
              {/* Main Screenshot Container */}
              <div className="relative rounded-xl border border-white/10 bg-gradient-to-b from-white/5 to-transparent p-1 shadow-2xl shadow-emerald-500/10">
                <div className="rounded-lg overflow-hidden bg-[#0f0f0f]">
                  {/* Browser Chrome */}
                  <div className="flex items-center gap-2 px-3 py-2 bg-[#1a1a1a] border-b border-white/10">
                    <div className="flex items-center gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full bg-red-500/80" />
                      <div className="w-2.5 h-2.5 rounded-full bg-yellow-500/80" />
                      <div className="w-2.5 h-2.5 rounded-full bg-green-500/80" />
                    </div>
                    <div className="flex-1 flex justify-center">
                      <div className="bg-[#0f0f0f] rounded-md px-3 py-0.5 text-xs text-gray-500">
                        app.axiom.io
                      </div>
                    </div>
                  </div>

                  {/* Screenshots */}
                  <div className="relative overflow-hidden bg-[#0a0a0a]">
                    {/* Workflow Screenshot */}
                    <div
                      className={`transition-all duration-700 ease-in-out ${
                        activeScreenshot === 0 ? "opacity-100" : "opacity-0 absolute inset-0"
                      }`}
                    >
                      <img
                        src="/screenshots/workflow.png"
                        alt="Axiom Workflow Pipeline"
                        className="w-full h-auto max-h-[500px] object-contain"
                      />
                    </div>

                    {/* Employees Screenshot */}
                    <div
                      className={`transition-all duration-700 ease-in-out ${
                        activeScreenshot === 1 ? "opacity-100" : "opacity-0 absolute inset-0"
                      }`}
                    >
                      <img
                        src="/screenshots/employees.png"
                        alt="Axiom Employee Management"
                        className="w-full h-auto max-h-[500px] object-contain"
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Screenshot Indicators */}
              <div className="flex items-center justify-center gap-2 mt-4">
                <button
                  onClick={() => setActiveScreenshot(0)}
                  className={`w-2 h-2 rounded-full transition-all ${
                    activeScreenshot === 0 ? "bg-emerald-500 w-6" : "bg-gray-600 hover:bg-gray-500"
                  }`}
                />
                <button
                  onClick={() => setActiveScreenshot(1)}
                  className={`w-2 h-2 rounded-full transition-all ${
                    activeScreenshot === 1 ? "bg-emerald-500 w-6" : "bg-gray-600 hover:bg-gray-500"
                  }`}
                />
              </div>

              {/* Screenshot Labels */}
              <div className="flex items-center justify-center gap-6 mt-3 text-sm text-gray-500">
                <button
                  onClick={() => setActiveScreenshot(0)}
                  className={`transition-colors ${activeScreenshot === 0 ? "text-emerald-400" : "hover:text-gray-300"}`}
                >
                  Workflow Pipeline
                </button>
                <span className="text-gray-700">|</span>
                <button
                  onClick={() => setActiveScreenshot(1)}
                  className={`transition-colors ${activeScreenshot === 1 ? "text-emerald-400" : "hover:text-gray-300"}`}
                >
                  Employee Management
                </button>
              </div>
            </div>
          </AnimatedSection>
        </div>
      </section>

      {/* Quote Section */}
      <section className="py-16 lg:py-20 border-y border-white/5 bg-gradient-to-b from-transparent via-emerald-500/5 to-transparent">
        <AnimatedSection className="container mx-auto px-4 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <div className="text-6xl sm:text-8xl text-emerald-500/30 font-serif mb-4">"</div>
            <blockquote className="text-2xl sm:text-3xl lg:text-4xl font-medium leading-relaxed mb-6 -mt-8">
              HR teams spend <span className="text-emerald-400">40+ hours</span> onboarding each new hire.
              <br className="hidden sm:block" />
              What if it took <span className="text-emerald-400">zero</span>?
            </blockquote>
            <p className="text-gray-500 text-lg">
              Contracts. Compliance. Calendars. <span className="text-white">Done.</span>
            </p>
          </div>
        </AnimatedSection>
      </section>

      {/* Features Section */}
      <section id="features" className="py-16 lg:py-20">
        <div className="container mx-auto px-4 lg:px-8">
          <AnimatedSection className="text-center mb-12">
            <Badge className="mb-4 bg-white/5 text-gray-300 border-white/10">Features</Badge>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
              Automate the Entire Journey
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              From the moment an offer is accepted to their first day, every step happens automatically.
            </p>
          </AnimatedSection>

          <div className="grid md:grid-cols-2 gap-5 lg:gap-6">
            {features.map((feature, index) => {
              const Icon = feature.icon;
              return (
                <AnimatedSection key={feature.title} delay={index * 100}>
                  <div className="group relative rounded-2xl border border-white/10 bg-[#111]/50 p-6 lg:p-8 hover:border-emerald-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/5 h-full">
                    <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br ${feature.color} mb-4`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-xl font-semibold mb-2 group-hover:text-emerald-400 transition-colors">
                      {feature.title}
                    </h3>
                    <p className="text-gray-400 leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </AnimatedSection>
              );
            })}
          </div>
        </div>
      </section>

      {/* How It Works / Pipeline Section */}
      <section id="how-it-works" className="py-16 lg:py-20 bg-gradient-to-b from-transparent via-[#111]/50 to-transparent">
        <div className="container mx-auto px-4 lg:px-8">
          <AnimatedSection className="text-center mb-12">
            <Badge className="mb-4 bg-white/5 text-gray-300 border-white/10">How It Works</Badge>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
              10-Step Pipeline, Zero Manual Work
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Every onboarding follows a structured workflow with full visibility at each stage.
            </p>
          </AnimatedSection>

          {/* Pipeline steps */}
          <div className="max-w-4xl mx-auto">
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {[
                { num: "01", title: "Parse Employee Data", desc: "Extract info from CSV or form submission", icon: Users },
                { num: "02", title: "Detect Jurisdiction", desc: "Identify country and compliance requirements", icon: Globe },
                { num: "03", title: "Employment Contract", desc: "Generate jurisdiction-specific contract", icon: FileText },
                { num: "04", title: "NDA & Equity", desc: "Create confidentiality and stock agreements", icon: Shield },
                { num: "05", title: "Offer Letter", desc: "Compile comprehensive offer package", icon: Mail },
                { num: "06", title: "Approval Gate", desc: "Human review before proceeding", icon: CheckCircle2 },
                { num: "07", title: "Welcome Email", desc: "Send personalized welcome message", icon: Sparkles },
                { num: "08", title: "30-60-90 Plan", desc: "Generate first 90 days roadmap", icon: BarChart3 },
                { num: "09", title: "Schedule Events", desc: "Book orientation and meetings", icon: Calendar },
                { num: "10", title: "Equipment Request", desc: "Initiate IT provisioning workflow", icon: Workflow },
              ].map((step, index) => (
                <AnimatedSection key={step.num} delay={index * 50}>
                  <div className="group relative rounded-xl border border-white/10 bg-[#0f0f0f] p-4 hover:border-emerald-500/50 transition-all duration-300 h-full">
                    <div className="flex items-start gap-3">
                      <span className="text-xl font-bold text-emerald-500/30 group-hover:text-emerald-500/50 transition-colors">
                        {step.num}
                      </span>
                      <div className="flex-1 min-w-0">
                        <h4 className="font-semibold mb-0.5 group-hover:text-emerald-400 transition-colors text-sm">
                          {step.title}
                        </h4>
                        <p className="text-xs text-gray-500">{step.desc}</p>
                      </div>
                    </div>
                  </div>
                </AnimatedSection>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 lg:py-20 border-y border-white/5">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 lg:gap-8">
            {stats.map((stat, index) => (
              <AnimatedSection key={stat.label} delay={index * 100} className="text-center">
                <div className="text-4xl sm:text-5xl lg:text-6xl font-bold gradient-text mb-2">
                  {stat.value}
                </div>
                <div className="text-base font-medium text-white mb-0.5">{stat.label}</div>
                <div className="text-sm text-gray-500">{stat.sublabel}</div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* Additional Features */}
      <section className="py-16 lg:py-20">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="grid lg:grid-cols-3 gap-5">
            <AnimatedSection delay={0}>
              <div className="rounded-2xl border border-white/10 bg-[#111]/50 p-6 hover:border-emerald-500/50 transition-all duration-300 h-full">
                <MessageSquare className="w-10 h-10 text-emerald-400 mb-4" />
                <h3 className="text-xl font-semibold mb-2">Policy Chatbot</h3>
                <p className="text-gray-400 mb-4 text-sm">
                  Employees can ask questions about company policies and get instant, accurate answers powered by your documents.
                </p>
                <Link href="/chat" className="text-emerald-400 text-sm font-medium inline-flex items-center hover:underline">
                  Try the chatbot <ArrowUpRight className="w-4 h-4 ml-1" />
                </Link>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={100}>
              <div className="rounded-2xl border border-white/10 bg-[#111]/50 p-6 hover:border-emerald-500/50 transition-all duration-300 h-full">
                <BarChart3 className="w-10 h-10 text-blue-400 mb-4" />
                <h3 className="text-xl font-semibold mb-2">Compliance Tracking</h3>
                <p className="text-gray-400 mb-4 text-sm">
                  Monitor visa expirations, certifications, and training requirements with predictive alerts before deadlines.
                </p>
                <Link href="/compliance" className="text-blue-400 text-sm font-medium inline-flex items-center hover:underline">
                  View dashboard <ArrowUpRight className="w-4 h-4 ml-1" />
                </Link>
              </div>
            </AnimatedSection>

            <AnimatedSection delay={200}>
              <div className="rounded-2xl border border-white/10 bg-[#111]/50 p-6 hover:border-emerald-500/50 transition-all duration-300 h-full">
                <Workflow className="w-10 h-10 text-purple-400 mb-4" />
                <h3 className="text-xl font-semibold mb-2">Real-Time Pipeline</h3>
                <p className="text-gray-400 mb-4 text-sm">
                  Watch each onboarding progress step-by-step with live updates and detailed reasoning logs.
                </p>
                <Link href="/onboarding" className="text-purple-400 text-sm font-medium inline-flex items-center hover:underline">
                  See in action <ArrowUpRight className="w-4 h-4 ml-1" />
                </Link>
              </div>
            </AnimatedSection>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-16 lg:py-20 bg-gradient-to-b from-transparent via-[#111]/50 to-transparent">
        <div className="container mx-auto px-4 lg:px-8">
          <AnimatedSection className="text-center mb-12">
            <Badge className="mb-4 bg-white/5 text-gray-300 border-white/10">Testimonials</Badge>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
              Trusted by Growing Teams
            </h2>
          </AnimatedSection>

          <div className="grid md:grid-cols-3 gap-5">
            {testimonials.map((testimonial, index) => (
              <AnimatedSection key={testimonial.author} delay={index * 100}>
                <div className="rounded-2xl border border-white/10 bg-[#111]/50 p-6 h-full">
                  <div className="text-4xl text-emerald-500/30 mb-3">"</div>
                  <p className="text-gray-300 mb-5 leading-relaxed -mt-2 text-sm">
                    {testimonial.quote}
                  </p>
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-emerald-500 to-teal-500 flex items-center justify-center text-white font-semibold">
                      {testimonial.author.charAt(0)}
                    </div>
                    <div>
                      <div className="font-medium text-sm">{testimonial.author}</div>
                      <div className="text-xs text-gray-500">{testimonial.role}, {testimonial.company}</div>
                    </div>
                  </div>
                </div>
              </AnimatedSection>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Cards Section */}
      <section className="py-16 lg:py-20 border-t border-white/5">
        <div className="container mx-auto px-4 lg:px-8">
          <AnimatedSection className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
              Ready to Transform Onboarding?
            </h2>
            <p className="text-gray-400 text-lg max-w-2xl mx-auto">
              Start automating your employee onboarding workflow today.
            </p>
          </AnimatedSection>

          <div className="grid md:grid-cols-3 gap-5 max-w-4xl mx-auto">
            <AnimatedSection delay={0}>
              <Link href="/signup" className="group block h-full">
                <div className="rounded-2xl border border-emerald-500/50 bg-emerald-500/10 p-6 text-center hover:bg-emerald-500/20 transition-all duration-300 h-full">
                  <div className="w-14 h-14 rounded-full bg-emerald-500 mx-auto mb-4 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <ArrowRight className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Get Started Free</h3>
                  <p className="text-gray-400 text-sm">
                    Create your account and onboard your first employee in minutes.
                  </p>
                </div>
              </Link>
            </AnimatedSection>

            <AnimatedSection delay={100}>
              <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="group block h-full">
                <div className="rounded-2xl border border-white/10 bg-[#111]/50 p-6 text-center hover:border-white/30 transition-all duration-300 h-full">
                  <div className="w-14 h-14 rounded-full bg-white/10 mx-auto mb-4 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Github className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">View on GitHub</h3>
                  <p className="text-gray-400 text-sm">
                    Explore the codebase, contribute, or self-host your instance.
                  </p>
                </div>
              </a>
            </AnimatedSection>

            <AnimatedSection delay={200}>
              <Link href="/login" className="group block h-full">
                <div className="rounded-2xl border border-white/10 bg-[#111]/50 p-6 text-center hover:border-white/30 transition-all duration-300 h-full">
                  <div className="w-14 h-14 rounded-full bg-white/10 mx-auto mb-4 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <Building2 className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">Enterprise</h3>
                  <p className="text-gray-400 text-sm">
                    Need custom integrations or dedicated support? Let's talk.
                  </p>
                </div>
              </Link>
            </AnimatedSection>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-16 lg:py-20 bg-gradient-to-b from-transparent via-[#111]/50 to-transparent">
        <div className="container mx-auto px-4 lg:px-8">
          <AnimatedSection className="text-center mb-12">
            <Badge className="mb-4 bg-white/5 text-gray-300 border-white/10">FAQ</Badge>
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4">
              Frequently Asked Questions
            </h2>
          </AnimatedSection>

          <AnimatedSection delay={100} className="max-w-3xl mx-auto">
            {faqs.map((faq, index) => (
              <div key={index} className="border-b border-white/10 last:border-0">
                <button
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full py-5 flex items-center justify-between text-left hover:text-emerald-400 transition-colors"
                >
                  <span className="font-medium pr-4 text-sm">{faq.question}</span>
                  <ChevronDown
                    className={`w-5 h-5 text-gray-500 transition-transform flex-shrink-0 ${
                      openFaq === index ? "rotate-180" : ""
                    }`}
                  />
                </button>
                <div
                  className={`overflow-hidden transition-all duration-300 ${
                    openFaq === index ? "max-h-96 pb-5" : "max-h-0"
                  }`}
                >
                  <p className="text-gray-400 leading-relaxed text-sm">{faq.answer}</p>
                </div>
              </div>
            ))}
          </AnimatedSection>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-16 lg:py-20">
        <AnimatedSection className="container mx-auto px-4 lg:px-8">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-6">
              Onboard With Confidence.
              <br />
              <span className="gradient-text">Automate With Axiom.</span>
            </h2>
            <p className="text-gray-400 text-lg mb-8 max-w-2xl mx-auto">
              Join forward-thinking HR teams who've eliminated manual onboarding forever.
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Link href="/signup">
                <Button size="lg" className="bg-emerald-500 hover:bg-emerald-600 text-white px-8 h-12 text-base group">
                  Get Started Free
                  <ArrowRight className="ml-2 h-4 w-4 transition-transform group-hover:translate-x-1" />
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline" className="border-gray-700 hover:bg-white/5 text-white px-8 h-12 text-base">
                  Sign In
                </Button>
              </Link>
            </div>
          </div>
        </AnimatedSection>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-10 lg:py-12">
        <div className="container mx-auto px-4 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-10">
            {/* Brand */}
            <div className="col-span-2 md:col-span-1">
              <Link href="/" className="flex items-center gap-2 mb-4">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-emerald-500">
                  <span className="text-sm font-bold text-white">A</span>
                </div>
                <span className="text-lg font-semibold">Axiom</span>
              </Link>
              <p className="text-sm text-gray-500 mb-4">
                Zero-touch employee onboarding platform that automates everything.
              </p>
              <div className="flex items-center gap-4">
                <a href="https://twitter.com" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-white transition-colors">
                  <Twitter className="w-5 h-5" />
                </a>
                <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-white transition-colors">
                  <Github className="w-5 h-5" />
                </a>
                <a href="https://linkedin.com" target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-white transition-colors">
                  <Linkedin className="w-5 h-5" />
                </a>
              </div>
            </div>

            {/* Product */}
            <div>
              <h4 className="font-semibold mb-4 text-sm">Product</h4>
              <ul className="space-y-2.5 text-sm text-gray-500">
                <li><a href="#features" className="hover:text-white transition-colors">Features</a></li>
                <li><a href="#how-it-works" className="hover:text-white transition-colors">How It Works</a></li>
                <li><Link href="/signup" className="hover:text-white transition-colors">Pricing</Link></li>
                <li><a href="#faq" className="hover:text-white transition-colors">FAQ</a></li>
              </ul>
            </div>

            {/* Company */}
            <div>
              <h4 className="font-semibold mb-4 text-sm">Company</h4>
              <ul className="space-y-2.5 text-sm text-gray-500">
                <li><a href="#" className="hover:text-white transition-colors">About</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Blog</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Careers</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Contact</a></li>
              </ul>
            </div>

            {/* Legal */}
            <div>
              <h4 className="font-semibold mb-4 text-sm">Legal</h4>
              <ul className="space-y-2.5 text-sm text-gray-500">
                <li><a href="#" className="hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-white transition-colors">Security</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-white/10 pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-xs text-gray-500">
              © {new Date().getFullYear()} Axiom. All rights reserved.
            </p>
            <p className="text-xs text-gray-600">
              Transforming how companies onboard talent.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
