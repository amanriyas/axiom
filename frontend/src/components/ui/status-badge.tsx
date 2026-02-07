"use client";

import { cn } from "@/lib/utils";
import { Check, Clock, Loader2, AlertCircle, Pause } from "lucide-react";

type StatusType =
  | "pending"
  | "onboarding"
  | "in_progress"
  | "running"
  | "completed"
  | "failed"
  | "processing"
  | "indexed"
  | "skipped";

interface StatusBadgeProps {
  status: StatusType;
  className?: string;
}

const statusConfig: Record<
  StatusType,
  { label: string; className: string; icon?: React.ElementType }
> = {
  pending: {
    label: "Pending",
    className: "border-[#6b6b6b] text-[#6b6b6b]",
    icon: Clock,
  },
  onboarding: {
    label: "In Progress",
    className: "border-[#14b8a6] text-[#14b8a6]",
    icon: Loader2,
  },
  in_progress: {
    label: "In Progress",
    className: "border-[#14b8a6] text-[#14b8a6]",
    icon: Loader2,
  },
  running: {
    label: "Running",
    className: "border-[#14b8a6] text-[#14b8a6]",
    icon: Loader2,
  },
  completed: {
    label: "Completed",
    className: "border-[#22c55e] text-[#22c55e]",
    icon: Check,
  },
  failed: {
    label: "Failed",
    className: "border-[#ef4444] text-[#ef4444]",
    icon: AlertCircle,
  },
  processing: {
    label: "Processing",
    className: "border-[#f59e0b] text-[#f59e0b]",
    icon: Loader2,
  },
  indexed: {
    label: "Indexed",
    className: "border-[#22c55e] text-[#22c55e]",
    icon: Check,
  },
  skipped: {
    label: "Skipped",
    className: "border-[#6b6b6b] text-[#6b6b6b]",
    icon: Pause,
  },
};

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const config = statusConfig[status] || statusConfig.pending;
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        config.className,
        className
      )}
    >
      {Icon && (
        <Icon
          className={cn(
            "h-3 w-3",
            (status === "running" || status === "processing" || status === "onboarding" || status === "in_progress") &&
              "animate-spin"
          )}
        />
      )}
      {config.label}
    </span>
  );
}
