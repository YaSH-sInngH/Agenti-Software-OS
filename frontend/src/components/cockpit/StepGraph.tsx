"use client";

import { useMemo } from "react";
import {
  ReactFlow,
  Background,
  Handle,
  Position,
  type Node,
  type Edge,
  type NodeProps,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { agentIcon, prettyAgent } from "@/lib/icons";
import { cn } from "@/lib/cn";
import type { RunStep } from "@/hooks/useRun";

type StepNodeData = { step: RunStep };

function AgentStepNode({ data }: NodeProps) {
  const { step } = data as StepNodeData;
  const Icon = agentIcon(step.agent);
  return (
    <div
      className={cn(
        "w-[210px] rounded-md border border-l-[3px] border-line border-l-ink-4 bg-ink-1 px-3 py-2.5",
        step.status === "working" && "border-l-work bg-work/10",
        step.status === "done" && "border-l-done",
        step.status === "error" && "border-l-err"
      )}
    >
      <Handle
        type="target"
        position={Position.Top}
        className="!h-1.5 !w-1.5 !border-0 !bg-ink-4"
      />
      <div className="flex items-center gap-2">
        <div
          className={cn(
            "flex h-5 w-5 flex-shrink-0 items-center justify-center rounded border border-line bg-ink-2 text-fg-2",
            step.status === "working" && "border-work/30 text-work-2",
            step.status === "done" && "border-done/25 text-done-2"
          )}
        >
          <Icon className="h-3 w-3" />
        </div>
        <span className="flex-1 truncate text-[12px] font-semibold text-fg">
          {prettyAgent(step.agent)}
        </span>
      </div>
      <div className="mt-1 truncate font-mono text-[10px] text-fg-3">
        {step.action}
      </div>
      <Handle
        type="source"
        position={Position.Bottom}
        className="!h-1.5 !w-1.5 !border-0 !bg-ink-4"
      />
    </div>
  );
}

const nodeTypes = { agentStep: AgentStepNode };

export function StepGraph({ steps }: { steps: RunStep[] }) {
  const nodes: Node[] = useMemo(
    () =>
      steps.map((s, i) => ({
        id: String(i),
        type: "agentStep",
        position: { x: 40, y: i * 108 },
        data: { step: s },
      })),
    [steps]
  );

  const edges: Edge[] = useMemo(
    () =>
      steps.slice(1).map((_, i) => {
        const next = steps[i + 1];
        const working = next?.status === "working";
        return {
          id: `e${i}-${i + 1}`,
          source: String(i),
          target: String(i + 1),
          animated: working,
          style: { stroke: working ? "#2563EB" : "#2A2A2A", strokeWidth: 1.5 },
        };
      }),
    [steps]
  );

  return (
    <div className="h-[420px] overflow-hidden rounded-lg border border-line bg-ink-0">
      <ReactFlow
        key={steps.length}
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.25 }}
        proOptions={{ hideAttribution: true }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable={false}
        zoomOnScroll={false}
        panOnScroll
        minZoom={0.5}
        maxZoom={1.2}
      >
        <Background color="var(--color-ink-4)" gap={20} size={1} />
      </ReactFlow>
    </div>
  );
}
