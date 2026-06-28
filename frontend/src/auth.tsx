import { createContext, ReactNode, useContext, useEffect, useState } from "react";

import { api, tokenStore } from "./api";
import type { User } from "./types";

interface AuthState {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthCtx = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  async function refreshUser() {
    if (!tokenStore.access) {
      setUser(null);
      return;
    }
    try {
      const me = await api.me();
      setUser(me);
    } catch {
      tokenStore.clear();
      setUser(null);
    }
  }

  useEffect(() => {
    (async () => {
      await refreshUser();
      setLoading(false);
    })();
  }, []);

  async function login(email: string, password: string) {
    const { access, refresh } = await api.login({ email, password });
    tokenStore.set(access, refresh);
    await refreshUser();
  }

  function logout() {
    tokenStore.clear();
    setUser(null);
  }

  return (
    <AuthCtx.Provider value={{ user, loading, login, logout, refreshUser }}>
      {children}
    </AuthCtx.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthCtx);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
