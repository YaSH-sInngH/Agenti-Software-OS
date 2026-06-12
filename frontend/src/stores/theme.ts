"use client";

import { create } from "zustand";

export type Theme = "dark" | "light";
const KEY = "wos_theme";

function apply(theme: Theme) {
  if (typeof document !== "undefined") {
    document.documentElement.dataset.theme = theme;
  }
}

interface ThemeState {
  theme: Theme;
  setTheme: (t: Theme) => void;
  init: () => void;
}

export const useTheme = create<ThemeState>((set) => ({
  theme: "dark",
  setTheme: (t) => {
    if (typeof localStorage !== "undefined") localStorage.setItem(KEY, t);
    apply(t);
    set({ theme: t });
  },
  init: () => {
    const stored =
      (typeof localStorage !== "undefined" &&
        (localStorage.getItem(KEY) as Theme)) ||
      "dark";
    apply(stored);
    set({ theme: stored });
  },
}));
