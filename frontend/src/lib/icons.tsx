import {
  Folder,
  Terminal,
  FileText,
  Brain,
  BookOpen,
  ListTodo,
  Globe,
  Database,
  Bell,
  BarChart3,
  Users,
  Code,
  Bot,
  type LucideIcon,
} from "lucide-react";
import type { AgentScope } from "./types";

const AGENT_ICONS: Record<string, LucideIcon> = {
  file_agent: Folder,
  terminal_agent: Terminal,
  document_agent: FileText,
  memory_agent: Brain,
  knowledge_agent: BookOpen,
  task_agent: ListTodo,
  browser_agent: Globe,
  indexer_agent: Database,
  reminder_agent: Bell,
  report_agent: BarChart3,
  resume_agent: Users,
  codebase_agent: Code,
};

export function agentIcon(name: string): LucideIcon {
  return AGENT_ICONS[name] ?? Bot;
}

export const SCOPE_LABEL: Record<AgentScope, string> = {
  workspace: "WS",
  web: "WEB",
  system: "SYS",
};

export function prettyAgent(name: string): string {
  return name
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
