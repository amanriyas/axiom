"use client";

import { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Check,
  Clock,
  Loader2,
  AlertCircle,
  RefreshCw,
  Pause,
  Play,
  FileDown,
  Mail,
  FileText,
  Calendar,
  Monitor,
  User,
  Building,
  Trash2,
  ChevronDown,
  ChevronRight,
  Users,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { toast } from "sonner";
import { employeeApi, onboardingApi } from "@/lib/api";
import { useSSEStream } from "@/hooks/use-sse-stream";
import { WorkflowGraph } from "@/components/onboarding/workflow-graph";
import { Employee, OnboardingWorkflow, StepType, StepStatus } from "@/types";

const stepConfig: Record<StepType, { label: string; icon: React.ElementType }> = {
  parse_data: { label: "Parse Employee Data", icon: FileText },
  welcome_email: { label: "Generate Welcome Email", icon: Mail },
  offer_letter: { label: "Generate Offer Letter", icon: FileText },
  plan_30_60_90: { label: "Create 30-60-90 Plan", icon: FileText },
  schedule_events: { label: "Schedule Events", icon: Calendar },
  equipment_request: { label: "Equipment Request", icon: Monitor },
};

const stepOrder: StepType[] = [
  "parse_data",
  "welcome_email",
  "offer_letter",
  "plan_30_60_90",
  "schedule_events",
  "equipment_request",
];

function getStepStatusIcon(status: StepStatus, size: "sm" | "md" = "md") {
  const sizeClass = size === "sm" ? "h-4 w-4" : "h-5 w-5";
  switch (status) {
    case "completed":
      return <Check className={`${sizeClass} text-[#22c55e]`} />;
    case "running":
      return <Loader2 className={`${sizeClass} text-[#14b8a6] animate-spin`} />;
    case "failed":
      return <AlertCircle className={`${sizeClass} text-[#ef4444]`} />;
    case "skipped":
      return <Clock className={`${sizeClass} text-[#6b6b6b]`} />;
    default:
      return <Clock className={`${sizeClass} text-[#6b6b6b]`} />;
  }
}

function getEventTypeColor(type: string) {
  switch (type) {
    case "init":
      return "text-blue-400";
    case "task":
      return "text-yellow-400";
    case "done":
      return "text-green-400";
    case "think":
      return "text-purple-400";
    case "active":
      return "text-cyan-400";
    case "error":
      return "text-red-400";
    default:
      return "text-muted-foreground";
  }
}

export default function OnboardingWorkflowPage() {
  const params = useParams();
  const router = useRouter();
  const employeeId = Number(params.id);

  const [employee, setEmployee] = useState<Employee | null>(null);
  const [workflow, setWorkflow] = useState<OnboardingWorkflow | null>(null);
  const [loading, setLoading] = useState(true);
  const [isStarting, setIsStarting] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [streamUrl, setStreamUrl] = useState<string | null>(null);
  const [outputsExpanded, setOutputsExpanded] = useState(true);

  const scrollRef = useRef<HTMLDivElement>(null);

  const { events, isConnected, clearEvents } = useSSEStream(streamUrl, {
    onEvent: (event) => {
      if (scrollRef.current) {
        scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
      }
      if (event.type === "step_update" || event.type === "done") {
        fetchWorkflowStatus();
      }
    },
    onComplete: () => {
      fetchWorkflowStatus();
    },
  });

  useEffect(() => {
    fetchData();
  }, [employeeId]);

  const fetchData = async () => {
    try {
      const [emp, wf] = await Promise.all([
        employeeApi.get(employeeId),
        onboardingApi.getStatus(employeeId).catch(() => null),
      ]);
      setEmployee(emp);
      setWorkflow(wf);
    } catch (error) {
      console.error("Failed to fetch data:", error);
      toast.error("Failed to load employee data");
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkflowStatus = async () => {
    try {
      const wf = await onboardingApi.getStatus(employeeId);
      setWorkflow(wf);
    } catch {
      // Ignore errors during polling
    }
  };

  const handleStartOnboarding = async () => {
    setIsStarting(true);
    try {
      await onboardingApi.start(employeeId);
      toast.success("Onboarding started");
      setStreamUrl(onboardingApi.getStreamUrl(employeeId));
      await fetchWorkflowStatus();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to start onboarding";
      toast.error(message);
    } finally {
      setIsStarting(false);
    }
  };

  const handlePauseResume = () => {
    setIsPaused(!isPaused);
    toast.info(isPaused ? "Workflow resumed" : "Workflow paused");
  };

  const getInitials = (name: string) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase()
      .slice(0, 2);
  };

  const getCompletedCount = () => {
    if (!workflow?.steps.length) return 0;
    return workflow.steps.filter((s) => s.status === "completed").length;
  };

  const getTotalSteps = () => {
    return workflow?.steps.length || stepOrder.length;
  };

  const calculateProgress = () => {
    if (!workflow?.steps.length) return 0;
    const completed = workflow.steps.filter((s) => s.status === "completed").length;
    return Math.round((completed / workflow.steps.length) * 100);
  };

  const getCurrentStep = (): { name: string; index: number } | null => {
    if (!workflow?.steps) return null;
    const runningStep = workflow.steps.find((s) => s.status === "running");
    if (runningStep) {
      const config = stepConfig[runningStep.step_type];
      const index = stepOrder.indexOf(runningStep.step_type) + 1;
      return { name: config.label, index };
    }
    const completedCount = getCompletedCount();
    if (completedCount === getTotalSteps()) {
      return { name: "Completed", index: getTotalSteps() };
    }
    return null;
  };

  const getGeneratedOutputs = () => {
    if (!workflow?.steps) return [];
    return workflow.steps
      .filter((s) => s.status === "completed" && s.result)
      .map((s) => ({
        stepType: s.step_type,
        label: stepConfig[s.step_type].label,
        icon: stepConfig[s.step_type].icon,
      }));
  };

  if (loading) {
    return (
      <div className="flex flex-col h-screen">
        <div className="flex h-16 items-center justify-between border-b border-border bg-background px-6">
          <div className="flex items-center gap-4">
            <Skeleton className="h-8 w-8" />
            <Skeleton className="h-6 w-48" />
          </div>
        </div>
        <div className="flex-1 flex">
          <Skeleton className="w-72 h-full" />
          <Skeleton className="flex-1 h-full" />
          <Skeleton className="w-80 h-full" />
        </div>
      </div>
    );
  }

  if (!employee) {
    return (
      <div className="flex flex-col h-screen">
        <div className="flex h-16 items-center justify-between border-b border-border bg-background px-6">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push("/employees")}>
              <ArrowLeft className="h-4 w-4" />
            </Button>
            <h1 className="text-xl font-semibold">Onboarding Workflow</h1>
          </div>
        </div>
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <p className="text-muted-foreground mb-4">Employee not found</p>
            <Button onClick={() => router.push("/employees")}>
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Employees
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const progress = calculateProgress();
  const completedCount = getCompletedCount();
  const totalSteps = getTotalSteps();
  const currentStep = getCurrentStep();
  const generatedOutputs = getGeneratedOutputs();

  return (
    <div className="flex flex-col h-screen">
      {/* Top Bar */}
      <div className="flex h-14 items-center justify-between border-b border-border bg-background px-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => router.push("/employees")}>
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-lg font-semibold">Onboarding</h1>
          {isConnected && (
            <Badge variant="outline" className="border-[#22c55e] text-[#22c55e]">
              <span className="mr-1.5 h-2 w-2 rounded-full bg-[#22c55e] animate-pulse" />
              Live
            </Badge>
          )}
        </div>
        {!workflow && (
          <Button onClick={handleStartOnboarding} disabled={isStarting}>
            {isStarting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Start Onboarding
          </Button>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar - Employee Info & Progress */}
        <div className="w-72 border-r border-border bg-background flex flex-col shrink-0">
          <ScrollArea className="flex-1">
            <div className="p-4 space-y-6">
              {/* Employee Profile */}
              <div className="space-y-4">
                <div className="flex items-center gap-3">
                  <Avatar className="h-12 w-12 bg-[#14b8a6]">
                    <AvatarFallback className="bg-[#14b8a6] text-white font-semibold">
                      {getInitials(employee.name)}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-semibold text-lg">{employee.name}</p>
                    <p className="text-sm text-muted-foreground">{employee.role}</p>
                  </div>
                </div>

                <Separator />

                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-3">
                    <Calendar className="h-4 w-4 text-muted-foreground shrink-0" />
                    <div>
                      <p className="text-muted-foreground text-xs">Start Date</p>
                      <p className="font-medium">{new Date(employee.start_date).toLocaleDateString()}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Building className="h-4 w-4 text-muted-foreground shrink-0" />
                    <div>
                      <p className="text-muted-foreground text-xs">Department</p>
                      <p className="font-medium">{employee.department}</p>
                    </div>
                  </div>
                  {employee.manager_email && (
                    <div className="flex items-center gap-3">
                      <User className="h-4 w-4 text-muted-foreground shrink-0" />
                      <div>
                        <p className="text-muted-foreground text-xs">Manager</p>
                        <p className="font-medium">{employee.manager_email.split("@")[0]}</p>
                      </div>
                    </div>
                  )}
                  {employee.buddy_email && (
                    <div className="flex items-center gap-3">
                      <Users className="h-4 w-4 text-muted-foreground shrink-0" />
                      <div>
                        <p className="text-muted-foreground text-xs">Buddy</p>
                        <p className="font-medium">{employee.buddy_email.split("@")[0]}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>

              <Separator />

              {/* Progress Section */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                    Progress
                  </h3>
                  <span className="text-sm font-medium">{completedCount} of {totalSteps}</span>
                </div>
                <Progress value={progress} className="h-2" />

                {/* Step List */}
                <div className="space-y-1">
                  {stepOrder.map((stepType) => {
                    const step = workflow?.steps.find((s) => s.step_type === stepType);
                    const config = stepConfig[stepType];
                    const status = step?.status || "pending";

                    return (
                      <div
                        key={stepType}
                        className={`flex items-center gap-2 py-2 px-2 rounded-md text-sm transition-colors ${
                          status === "running" ? "bg-[#14b8a6]/10" : ""
                        }`}
                      >
                        <div className="shrink-0">
                          {getStepStatusIcon(status, "sm")}
                        </div>
                        <span
                          className={`truncate ${
                            status === "completed"
                              ? "text-muted-foreground line-through"
                              : status === "running"
                              ? "text-[#14b8a6] font-medium"
                              : "text-foreground"
                          }`}
                        >
                          {config.label}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <Separator />

              {/* Generated Outputs */}
              <div className="space-y-3">
                <button
                  onClick={() => setOutputsExpanded(!outputsExpanded)}
                  className="flex items-center justify-between w-full"
                >
                  <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                    Generated Outputs
                  </h3>
                  {outputsExpanded ? (
                    <ChevronDown className="h-4 w-4 text-muted-foreground" />
                  ) : (
                    <ChevronRight className="h-4 w-4 text-muted-foreground" />
                  )}
                </button>
                {outputsExpanded && (
                  <div className="space-y-2">
                    {generatedOutputs.length === 0 ? (
                      <p className="text-sm text-muted-foreground italic">
                        No outputs generated yet
                      </p>
                    ) : (
                      generatedOutputs.map((output) => {
                        const Icon = output.icon;
                        return (
                          <Button
                            key={output.stepType}
                            variant="ghost"
                            className="w-full justify-start text-sm h-9"
                            size="sm"
                          >
                            <Icon className="mr-2 h-4 w-4 text-[#14b8a6]" />
                            {output.label}
                          </Button>
                        );
                      })
                    )}
                  </div>
                )}
              </div>
            </div>
          </ScrollArea>
        </div>

        {/* Center - Workflow Graph */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="px-4 py-3 border-b border-border">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
              Workflow Graph
            </h2>
          </div>
          <div className="flex-1 relative">
            <WorkflowGraph
              steps={workflow?.steps || []}
              onNodeClick={(stepType) => {
                const step = workflow?.steps.find((s) => s.step_type === stepType);
                if (step?.result) {
                  toast.info(`${stepConfig[stepType].label}: View output`);
                }
              }}
            />
          </div>
        </div>

        {/* Right Panel - Agent Reasoning */}
        <div className="w-80 border-l border-border bg-background flex flex-col">
          <div className="px-4 py-3 border-b border-border flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="h-2 w-2 rounded-full bg-[#22c55e] animate-pulse" />
              <h2 className="text-sm font-semibold uppercase tracking-wide text-[#14b8a6]">
                Agent Reasoning
              </h2>
            </div>
            <Button variant="ghost" size="sm" onClick={clearEvents} className="h-8 px-2">
              <Trash2 className="h-4 w-4 mr-1" />
              Clear
            </Button>
          </div>
          <ScrollArea className="flex-1" ref={scrollRef}>
            <div className="p-4 space-y-3 font-mono text-sm">
              {events.length === 0 ? (
                <p className="text-muted-foreground italic text-center py-8">
                  {workflow ? "Waiting for activity..." : "Start onboarding to see agent reasoning"}
                </p>
              ) : (
                events.map((event, i) => (
                  <div key={i} className="space-y-0.5">
                    <span className="text-muted-foreground text-xs">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                    <p className={`${getEventTypeColor(event.type)} break-words`}>
                      {event.type === "done" && "✓ "}
                      {event.type === "task" && "▶ "}
                      {event.message}
                    </p>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
          <div className="border-t px-4 py-2 text-xs text-muted-foreground">
            Agent: GPT-4 Turbo • Tokens: {events.length * 50}
          </div>
        </div>
      </div>

      {/* Bottom Bar */}
      <div className="h-14 border-t border-border bg-background px-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Avatar className="h-8 w-8 bg-[#14b8a6]">
            <AvatarFallback className="bg-[#14b8a6] text-white text-xs font-semibold">
              {getInitials(employee.name)}
            </AvatarFallback>
          </Avatar>
          <Button
            variant="outline"
            size="sm"
            onClick={handlePauseResume}
            disabled={!workflow || workflow.status === "completed" || workflow.status === "failed"}
          >
            <Pause className="mr-2 h-4 w-4" />
            Pause
          </Button>
          <Button
            variant="default"
            size="sm"
            onClick={handlePauseResume}
            disabled={!workflow || workflow.status === "completed" || workflow.status === "failed"}
            className="bg-[#14b8a6] hover:bg-[#14b8a6]/90"
          >
            <Play className="mr-2 h-4 w-4" />
            Resume
          </Button>
        </div>

        <div className="flex items-center gap-2 text-sm">
          {currentStep ? (
            <>
              <span className="text-muted-foreground">
                Step {currentStep.index} of {totalSteps}
              </span>
              <span className="text-muted-foreground">—</span>
              <span className="font-medium text-foreground">{currentStep.name}</span>
            </>
          ) : workflow?.status === "pending" ? (
            <span className="text-muted-foreground">Waiting to start...</span>
          ) : workflow ? (
            <span className="text-muted-foreground">
              {completedCount} of {totalSteps} steps completed
            </span>
          ) : (
            <span className="text-muted-foreground">Not started</span>
          )}
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" size="sm" disabled={!workflow}>
            <RefreshCw className="mr-2 h-4 w-4" />
            Retry Failed
          </Button>
          <Button variant="outline" size="sm" disabled={!workflow}>
            <FileDown className="mr-2 h-4 w-4" />
            Export Report
          </Button>
        </div>
      </div>
    </div>
  );
}
