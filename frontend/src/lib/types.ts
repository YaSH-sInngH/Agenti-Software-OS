export interface User {
  id: number;
  name: string;
  email: string;
}

export interface Workspace {
  id: number;
  name: string;
  created_at: string | null;
}

export interface AgentParam {
  name: string;
  type: string;
  required: boolean;
  description: string;
  enum?: string[];
}

export interface AgentAction {
  name: string;
  description: string;
  parameters: AgentParam[];
}

export type AgentScope = "workspace" | "web" | "system";

export interface AgentManifest {
  name: string;
  description: string;
  icon: string;
  scope: AgentScope;
  actions: AgentAction[];
}

export interface Step {
  agent: string;
  action: string;
  parameters: Record<string, unknown>;
}

export interface StepResult {
  agent: string;
  action: string;
  result: Record<string, unknown> & { success?: boolean; message?: string };
}

export interface PlanResponse {
  workspace_id: number;
  plan: unknown;
  steps: Step[];
}

export interface DashboardCounts {
  tasks_total: number;
  tasks_pending: number;
  reminders_total: number;
  reminders_pending: number;
  memories_total: number;
  indexed_files: number;
}

export interface RunSummary {
  id: number;
  workspace_id: number;
  message: string;
  status: string;
  created_at: string | null;
  step_count?: number;
}

export type StepStatus = "pending" | "working" | "done" | "error";

export interface FileNode {
  name: string;
  path: string;
  type: "file" | "folder";
  size?: number;
  children?: FileNode[];
}

export interface FileContent {
  path: string;
  content: string | null;
  encoding: string;
  message?: string;
}

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: string;
  due_date: string | null;
}

export interface Reminder {
  id: number;
  message: string;
  remind_at: string | null;
  status: string;
}

export interface Memory {
  id: number;
  text: string;
  type: string;
  created_at: string | null;
}

export interface RunDetail extends RunSummary {
  plan: Step[] | null;
  results: StepResult[] | null;
  response: string | null;
}
