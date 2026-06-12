"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Command,
  FolderTree,
  ListTodo,
  Bell,
  Brain,
  BookOpen,
  History,
  Settings,
  PanelLeftClose,
  PanelLeftOpen,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/cn";

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  exact?: boolean;
}

const KEY = "wos_nav_expanded";

export function IconNav({ workspaceId }: { workspaceId: number }) {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    setExpanded(localStorage.getItem(KEY) === "1");
  }, []);

  function toggle() {
    setExpanded((prev) => {
      const next = !prev;
      localStorage.setItem(KEY, next ? "1" : "0");
      return next;
    });
  }

  const base = `/w/${workspaceId}`;

  const main: NavItem[] = [
    { href: base, label: "Cockpit", icon: Command, exact: true },
    { href: `${base}/files`, label: "Explorer", icon: FolderTree },
    { href: `${base}/tasks`, label: "Tasks", icon: ListTodo },
    { href: `${base}/reminders`, label: "Reminders", icon: Bell },
    { href: `${base}/memory`, label: "Memory", icon: Brain },
    { href: `${base}/knowledge`, label: "Knowledge", icon: BookOpen },
    { href: `${base}/runs`, label: "Runs", icon: History },
  ];

  const settings: NavItem = {
    href: `${base}/settings`,
    label: "Settings",
    icon: Settings,
  };

  function isActive(item: NavItem) {
    if (item.exact) return pathname === item.href;
    return pathname === item.href || pathname.startsWith(item.href + "/");
  }

  return (
    <nav
      className={cn(
        "flex flex-shrink-0 flex-col gap-1 border-r border-line bg-ink-1 py-2 transition-[width] duration-150",
        expanded ? "w-44 px-2" : "w-12 items-center"
      )}
    >
      <button
        onClick={toggle}
        title={expanded ? "Collapse" : "Expand"}
        className={cn(
          "flex h-8 items-center rounded-md text-fg-3 transition-colors hover:bg-ink-2 hover:text-fg",
          expanded ? "w-full justify-start gap-2.5 px-2" : "w-8 justify-center"
        )}
      >
        {expanded ? (
          <PanelLeftClose className="h-4 w-4" />
        ) : (
          <PanelLeftOpen className="h-4 w-4" />
        )}
        {expanded && <span className="text-[12px]">Collapse</span>}
      </button>

      <div className="my-1 h-px w-full bg-line" />

      {main.map((item) => (
        <NavButton
          key={item.href}
          item={item}
          active={isActive(item)}
          expanded={expanded}
        />
      ))}

      <div className="mt-auto">
        <NavButton item={settings} active={isActive(settings)} expanded={expanded} />
      </div>
    </nav>
  );
}

function NavButton({
  item,
  active,
  expanded,
}: {
  item: NavItem;
  active: boolean;
  expanded: boolean;
}) {
  const Icon = item.icon;
  return (
    <Link
      href={item.href}
      title={item.label}
      className={cn(
        "flex h-8 items-center rounded-md text-fg-3 transition-colors hover:bg-ink-2 hover:text-fg",
        expanded ? "w-full justify-start gap-2.5 px-2" : "w-8 justify-center",
        active && "bg-ink-2 text-fg"
      )}
    >
      <Icon className="h-4 w-4 flex-shrink-0" />
      {expanded && <span className="truncate text-[12px]">{item.label}</span>}
    </Link>
  );
}
