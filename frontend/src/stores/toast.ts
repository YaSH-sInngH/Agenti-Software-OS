"use client";

import { create } from "zustand";

export type ToastKind = "info" | "success" | "error" | "working";

export interface Toast {
  id: number;
  kind: ToastKind;
  message: string;
}

let counter = 0;

interface ToastState {
  toasts: Toast[];
  push: (kind: ToastKind, message: string) => number;
  dismiss: (id: number) => void;
}

export const useToasts = create<ToastState>((set) => ({
  toasts: [],
  push: (kind, message) => {
    const id = ++counter;
    set((s) => ({ toasts: [...s.toasts, { id, kind, message }] }));
    if (kind !== "working") {
      setTimeout(() => {
        set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }));
      }, 3500);
    }
    return id;
  },
  dismiss: (id) =>
    set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));

export const toast = {
  success: (m: string) => useToasts.getState().push("success", m),
  error: (m: string) => useToasts.getState().push("error", m),
  info: (m: string) => useToasts.getState().push("info", m),
  working: (m: string) => useToasts.getState().push("working", m),
  dismiss: (id: number) => useToasts.getState().dismiss(id),
};
