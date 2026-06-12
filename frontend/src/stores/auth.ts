"use client";

import { create } from "zustand";
import { apiFetch, setToken, clearToken, getToken } from "@/lib/api";
import type { User } from "@/lib/types";

interface AuthState {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  loadUser: () => Promise<User | null>;
  logout: () => void;
}

async function authenticate(email: string, password: string) {
  const data = await apiFetch<{ access_token: string }>("/api/auth/login", {
    method: "POST",
    body: { email, password },
  });
  setToken(data.access_token);
  return apiFetch<User>("/api/me");
}

export const useAuth = create<AuthState>((set) => ({
  user: null,

  login: async (email, password) => {
    const me = await authenticate(email, password);
    set({ user: me });
  },

  register: async (name, email, password) => {
    await apiFetch("/api/auth/signup", {
      method: "POST",
      body: { name, email, password },
    });
    const me = await authenticate(email, password);
    set({ user: me });
  },

  loadUser: async () => {
    if (!getToken()) {
      set({ user: null });
      return null;
    }
    try {
      const me = await apiFetch<User>("/api/me");
      set({ user: me });
      return me;
    } catch {
      clearToken();
      set({ user: null });
      return null;
    }
  },

  logout: () => {
    clearToken();
    set({ user: null });
  },
}));
