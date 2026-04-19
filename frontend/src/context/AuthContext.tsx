"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import api, { clearTokens, setTokens } from "@/lib/api";
import { getRefreshToken, isLoggedIn } from "@/lib/auth";

export type CurrentUser = {
  id: number;
  email: string;
  full_name: string;
  first_name: string;
  last_name: string;
  phone_number: string | null;
  bio: string | null;
  trader_level: string;
  timezone: string;
  is_email_verified: boolean;
  profile: {
    trading_goal: string;
    experience_level: string;
    preferred_market: string;
    risk_appetite: string;
    onboarding_completed: boolean;
  };
};

type LoginPayload = {
  email: string;
  password: string;
};

type AuthContextValue = {
  user: CurrentUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (payload: LoginPayload) => Promise<CurrentUser>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<CurrentUser | null>;
  setUser: (user: CurrentUser | null) => void;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

async function fetchCurrentUser(): Promise<CurrentUser> {
  const response = await api.get<CurrentUser>("/me/");
  return response.data;
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!isLoggedIn()) {
      setUser(null);
      return null;
    }

    try {
      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
      return currentUser;
    } catch {
      clearTokens();
      setUser(null);
      return null;
    }
  }, []);

  useEffect(() => {
    let mounted = true;

    const hydrateUser = async () => {
      try {
        if (!isLoggedIn()) {
          if (mounted) {
            setUser(null);
          }
          return;
        }

        const currentUser = await fetchCurrentUser();

        if (mounted) {
          setUser(currentUser);
        }
      } catch {
        clearTokens();
        if (mounted) {
          setUser(null);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    void hydrateUser();

    return () => {
      mounted = false;
    };
  }, []);

  const login = useCallback(async ({ email, password }: LoginPayload) => {
    setLoading(true);

    try {
      const response = await api.post<{ access: string; refresh: string }>(
        "/token/",
        {
          email,
          password,
        },
      );

      setTokens({
        access: response.data.access,
        refresh: response.data.refresh,
      });

      const currentUser = await fetchCurrentUser();
      setUser(currentUser);
      return currentUser;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    const refreshToken = getRefreshToken();

    setLoading(true);

    try {
      if (refreshToken) {
        await api.post("/logout/", { refresh: refreshToken });
      }
    } catch {
      // Even if logout fails remotely, local session should still be cleared.
    } finally {
      clearTokens();
      setUser(null);
      setLoading(false);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      loading,
      isAuthenticated: Boolean(user),
      login,
      logout,
      refreshUser,
      setUser,
    }),
    [user, loading, login, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider.");
  }

  return context;
}
