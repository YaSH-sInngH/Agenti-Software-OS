"use client";

import { create } from "zustand";

interface UiState {
  activeCount: number;
  setActiveCount: (n: number) => void;
}

export const useUi = create<UiState>((set) => ({
  activeCount: 0,
  setActiveCount: (n) => set({ activeCount: n }),
}));
