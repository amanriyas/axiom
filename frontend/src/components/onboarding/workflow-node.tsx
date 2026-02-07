"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps, type Node } from "@xyflow/react";
import {
  Check,
  Loader2,
  AlertCircle,
  Clock,
  FileText,
  Mail,
  Calendar,
  Monitor,
} from "lucide-react";
import type { StepType, StepStatus } from "@/types";

export interface WorkflowNodeData extends Record<string, unknown> {
  label: string;
  stepType: StepType;
  status: StepStatus;
}

export type WorkflowNodeType = Node<WorkflowNodeData, "workflow">;

const stepIcons: Record<StepType, React.ElementType> = {
  parse_data: FileText,
  welcome_email: Mail,
  offer_letter: FileText,
  plan_30_60_90: FileText,
  schedule_events: Calendar,
  equipment_request: Monitor,
};

function getStatusStyles(status: StepStatus) {
  switch (status) {
    case "completed":
      return {
        border: "border-[#22c55e]",
        bg: "bg-[#22c55e]/10",
        iconBg: "bg-[#22c55e]/20",
        iconColor: "text-[#22c55e]",
        textColor: "text-[#22c55e]",
      };
    case "running":
      return {
        border: "border-[#14b8a6]",
        bg: "bg-[#14b8a6]/10",
        iconBg: "bg-[#14b8a6]/20",
        iconColor: "text-[#14b8a6]",
        textColor: "text-[#14b8a6]",
      };
    case "failed":
      return {
        border: "border-[#ef4444]",
        bg: "bg-[#ef4444]/10",
        iconBg: "bg-[#ef4444]/20",
        iconColor: "text-[#ef4444]",
        textColor: "text-[#ef4444]",
      };
    default:
      return {
        border: "border-[#3f3f46]",
        bg: "bg-[#27272a]",
        iconBg: "bg-[#3f3f46]",
        iconColor: "text-[#71717a]",
        textColor: "text-[#71717a]",
      };
  }
}

function getStatusIcon(status: StepStatus) {
  switch (status) {
    case "completed":
      return <Check className="h-5 w-5" />;
    case "running":
      return <Loader2 className="h-5 w-5 animate-spin" />;
    case "failed":
      return <AlertCircle className="h-5 w-5" />;
    default:
      return <Clock className="h-5 w-5" />;
  }
}

function WorkflowNodeComponent({ data }: NodeProps<WorkflowNodeType>) {
  const nodeData = data;
  const styles = getStatusStyles(nodeData.status);
  const StatusIcon = getStatusIcon(nodeData.status);
  const StepIcon = stepIcons[nodeData.stepType];

  return (
    <>
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-[#52525b] !border-[#71717a] !w-3 !h-3"
      />
      <div
        className={`
          flex items-center gap-4 px-5 py-4 rounded-xl border-2 min-w-[240px]
          ${styles.border} ${styles.bg}
          shadow-lg transition-all duration-200
          hover:shadow-xl hover:scale-[1.02]
          cursor-pointer
        `}
      >
        <div
          className={`
            flex items-center justify-center h-10 w-10 rounded-full shrink-0
            ${styles.iconBg} ${styles.iconColor}
          `}
        >
          {StatusIcon}
        </div>
        <div className="flex-1 min-w-0 pr-2">
          <p className="font-semibold text-base text-foreground truncate">
            {nodeData.label}
          </p>
          <p className={`text-sm ${styles.textColor} capitalize`}>
            {nodeData.status === "running" ? "In Progress" : nodeData.status}
          </p>
        </div>
        <StepIcon className="h-5 w-5 text-muted-foreground shrink-0" />
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-[#52525b] !border-[#71717a] !w-3 !h-3"
      />
    </>
  );
}

export const WorkflowNode = memo(WorkflowNodeComponent);
