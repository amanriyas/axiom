"use client";

import { useCallback, useEffect, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
  type NodeTypes,
  BackgroundVariant,
  ConnectionLineType,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { WorkflowNode, type WorkflowNodeData, type WorkflowNodeType } from "./workflow-node";
import type { OnboardingStep, StepType, StepStatus } from "@/types";

const nodeTypes: NodeTypes = {
  workflow: WorkflowNode,
};

const stepLabels: Record<StepType, string> = {
  parse_data: "Parse Employee Data",
  detect_jurisdiction: "Detect Jurisdiction",
  employment_contract: "Employment Contract",
  nda: "Non-Disclosure Agreement",
  equity_agreement: "Equity Agreement",
  offer_letter: "Offer Letter",
  welcome_email: "Generate Welcome Email",
  plan_30_60_90: "Create 30-60-90 Plan",
  schedule_events: "Schedule Events",
  equipment_request: "Equipment Request",
};

const defaultEdgeOptions = {
  type: "smoothstep",
  animated: true,
  style: {
    stroke: "#52525b",
    strokeWidth: 2,
    strokeDasharray: "6 6",
  },
};

interface WorkflowGraphProps {
  steps: OnboardingStep[];
  onNodeClick?: (stepType: StepType) => void;
}

export function WorkflowGraph({ steps, onNodeClick }: WorkflowGraphProps) {
  const getStepStatus = useCallback(
    (stepType: StepType): StepStatus => {
      const step = steps.find((s) => s.step_type === stepType);
      return step?.status || "pending";
    },
    [steps]
  );

  const initialNodes: WorkflowNodeType[] = useMemo(
    () => [
      {
        id: "parse_data",
        type: "workflow" as const,
        position: { x: 250, y: 0 },
        data: {
          label: stepLabels.parse_data,
          stepType: "parse_data" as StepType,
          status: getStepStatus("parse_data"),
        },
      },
      {
        id: "detect_jurisdiction",
        type: "workflow" as const,
        position: { x: 250, y: 120 },
        data: {
          label: stepLabels.detect_jurisdiction,
          stepType: "detect_jurisdiction" as StepType,
          status: getStepStatus("detect_jurisdiction"),
        },
      },
      {
        id: "employment_contract",
        type: "workflow" as const,
        position: { x: 0, y: 250 },
        data: {
          label: stepLabels.employment_contract,
          stepType: "employment_contract" as StepType,
          status: getStepStatus("employment_contract"),
        },
      },
      {
        id: "nda",
        type: "workflow" as const,
        position: { x: 500, y: 250 },
        data: {
          label: stepLabels.nda,
          stepType: "nda" as StepType,
          status: getStepStatus("nda"),
        },
      },
      {
        id: "equity_agreement",
        type: "workflow" as const,
        position: { x: 0, y: 380 },
        data: {
          label: stepLabels.equity_agreement,
          stepType: "equity_agreement" as StepType,
          status: getStepStatus("equity_agreement"),
        },
      },
      {
        id: "offer_letter",
        type: "workflow" as const,
        position: { x: 500, y: 380 },
        data: {
          label: stepLabels.offer_letter,
          stepType: "offer_letter" as StepType,
          status: getStepStatus("offer_letter"),
        },
      },
      {
        id: "welcome_email",
        type: "workflow" as const,
        position: { x: 250, y: 520 },
        data: {
          label: stepLabels.welcome_email,
          stepType: "welcome_email" as StepType,
          status: getStepStatus("welcome_email"),
        },
      },
      {
        id: "plan_30_60_90",
        type: "workflow" as const,
        position: { x: 0, y: 650 },
        data: {
          label: stepLabels.plan_30_60_90,
          stepType: "plan_30_60_90" as StepType,
          status: getStepStatus("plan_30_60_90"),
        },
      },
      {
        id: "schedule_events",
        type: "workflow" as const,
        position: { x: 500, y: 650 },
        data: {
          label: stepLabels.schedule_events,
          stepType: "schedule_events" as StepType,
          status: getStepStatus("schedule_events"),
        },
      },
      {
        id: "equipment_request",
        type: "workflow" as const,
        position: { x: 250, y: 780 },
        data: {
          label: stepLabels.equipment_request,
          stepType: "equipment_request" as StepType,
          status: getStepStatus("equipment_request"),
        },
      },
    ],
    [getStepStatus]
  );

  const initialEdges: Edge[] = useMemo(
    () => [
      {
        id: "e-parse-jurisdiction",
        source: "parse_data",
        target: "detect_jurisdiction",
        ...defaultEdgeOptions,
      },
      {
        id: "e-jurisdiction-contract",
        source: "detect_jurisdiction",
        target: "employment_contract",
        ...defaultEdgeOptions,
      },
      {
        id: "e-jurisdiction-nda",
        source: "detect_jurisdiction",
        target: "nda",
        ...defaultEdgeOptions,
      },
      {
        id: "e-contract-equity",
        source: "employment_contract",
        target: "equity_agreement",
        ...defaultEdgeOptions,
      },
      {
        id: "e-nda-offer",
        source: "nda",
        target: "offer_letter",
        ...defaultEdgeOptions,
      },
      {
        id: "e-equity-welcome",
        source: "equity_agreement",
        target: "welcome_email",
        ...defaultEdgeOptions,
        label: "⏸ Approval Gate",
        labelStyle: { fill: "#a1a1aa", fontSize: 10 },
        labelBgStyle: { fill: "#18181b", fillOpacity: 0.8 },
      },
      {
        id: "e-offer-welcome",
        source: "offer_letter",
        target: "welcome_email",
        ...defaultEdgeOptions,
        label: "⏸ Approval Gate",
        labelStyle: { fill: "#a1a1aa", fontSize: 10 },
        labelBgStyle: { fill: "#18181b", fillOpacity: 0.8 },
      },
      {
        id: "e-welcome-plan",
        source: "welcome_email",
        target: "plan_30_60_90",
        ...defaultEdgeOptions,
      },
      {
        id: "e-welcome-schedule",
        source: "welcome_email",
        target: "schedule_events",
        ...defaultEdgeOptions,
      },
      {
        id: "e-plan-equipment",
        source: "plan_30_60_90",
        target: "equipment_request",
        ...defaultEdgeOptions,
      },
      {
        id: "e-schedule-equipment",
        source: "schedule_events",
        target: "equipment_request",
        ...defaultEdgeOptions,
      },
    ],
    []
  );

  const [nodes, setNodes, onNodesChange] = useNodesState<WorkflowNodeType>(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Update nodes when steps change
  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        data: {
          ...node.data,
          status: getStepStatus(node.id as StepType),
        },
      }))
    );
  }, [steps, getStepStatus, setNodes]);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: WorkflowNodeType) => {
      if (onNodeClick) {
        onNodeClick(node.id as StepType);
      }
    },
    [onNodeClick]
  );

  return (
    <div className="h-full w-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        connectionLineType={ConnectionLineType.SmoothStep}
        fitView
        fitViewOptions={{
          padding: 0.3,
          minZoom: 0.6,
          maxZoom: 1.2,
        }}
        minZoom={0.4}
        maxZoom={1.5}
        defaultViewport={{ x: 0, y: 0, zoom: 0.85 }}
        defaultEdgeOptions={defaultEdgeOptions}
        proOptions={{ hideAttribution: true }}
        className="bg-background"
      >
        <Background
          variant={BackgroundVariant.Dots}
          gap={20}
          size={1}
          color="#3f3f46"
        />
        <Controls
          className="!bg-[#27272a] !border-[#3f3f46] !rounded-lg [&>button]:!bg-[#27272a] [&>button]:!border-[#3f3f46] [&>button]:!text-foreground [&>button:hover]:!bg-[#3f3f46]"
          showInteractive={false}
        />
        <MiniMap
          className="!bg-[#18181b] !border-[#3f3f46] !rounded-lg"
          nodeColor={(node) => {
            const data = node.data as WorkflowNodeData | undefined;
            const status = data?.status;
            switch (status) {
              case "completed":
                return "#22c55e";
              case "running":
                return "#14b8a6";
              case "failed":
                return "#ef4444";
              default:
                return "#3f3f46";
            }
          }}
          maskColor="rgba(0, 0, 0, 0.7)"
        />
      </ReactFlow>
    </div>
  );
}
