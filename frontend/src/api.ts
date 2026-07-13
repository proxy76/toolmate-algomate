import axios, { AxiosError, AxiosRequestConfig } from "axios";

import type {
  AdminBlogPost,
  AdminUser,
  BlogPost,
  BlogPostSummary,
  GenerateResponse,
  Profile,
  SimulateResponse,
  TopicsResponse,
  User,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api/v1";

const client = axios.create({ baseURL: API_BASE, timeout: 15000 });

const ACCESS_KEY = "algomate.access";
const REFRESH_KEY = "algomate.refresh";

export const tokenStore = {
  get access() {
    return localStorage.getItem(ACCESS_KEY);
  },
  get refresh() {
    return localStorage.getItem(REFRESH_KEY);
  },
  set(access: string, refresh: string) {
    localStorage.setItem(ACCESS_KEY, access);
    localStorage.setItem(REFRESH_KEY, refresh);
  },
  setAccess(access: string) {
    localStorage.setItem(ACCESS_KEY, access);
  },
  clear() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

client.interceptors.request.use((config) => {
  const access = tokenStore.access;
  if (access && config.headers) {
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccess(): Promise<string | null> {
  if (!tokenStore.refresh) return null;
  if (!refreshPromise) {
    refreshPromise = client
      .post("/auth/refresh/", { refresh: tokenStore.refresh }, { _skipAuthRefresh: true } as AxiosRequestConfig)
      .then((res) => {
        const access = res.data.access as string;
        tokenStore.setAccess(access);
        return access;
      })
      .catch(() => {
        tokenStore.clear();
        return null;
      })
      .finally(() => {
        refreshPromise = null;
      });
  }
  return refreshPromise;
}

/** Clear the session and bounce to login. `superseded` = the account was taken
 *  over by a newer login on another device; `expired` = tokens no longer valid. */
function forceLogout(reason: "superseded" | "expired") {
  tokenStore.clear();
  if (typeof window !== "undefined") {
    const path = window.location.pathname;
    if (path !== "/login" && path !== "/register") {
      window.location.assign(`/login?ended=${reason}`);
    }
  }
}

client.interceptors.response.use(
  (r) => r,
  async (error: AxiosError) => {
    const config = error.config as AxiosRequestConfig & { _retried?: boolean };
    if (error.response?.status === 401 && config && !(config as any)._skipAuthRefresh) {
      if (!config._retried) {
        const newAccess = await refreshAccess();
        if (newAccess) {
          config._retried = true;
          config.headers = { ...(config.headers || {}), Authorization: `Bearer ${newAccess}` };
          return client.request(config);
        }
        // refresh failed → the session is genuinely over
        forceLogout("expired");
      } else {
        // token refreshed fine but the request is still unauthorized → the
        // server rejected our session id: a newer login took over the account
        forceLogout("superseded");
      }
    }
    return Promise.reject(error);
  },
);

// --- API surface ---

export const api = {
  // auth
  register: (data: { email: string; username: string; password: string; profile: Profile }) =>
    client.post<{ detail: string }>("/auth/register/", data).then((r) => r.data),

  verifyEmail: (token: string) =>
    client.post<{ detail: string }>("/auth/verify-email/", { token }).then((r) => r.data),

  resendVerification: (email: string) =>
    client.post<{ detail: string }>("/auth/resend-verification/", { email }).then((r) => r.data),

  // `email` accepts the email OR the username (the backend resolves either).
  login: (data: { email: string; password: string }) =>
    client.post<{ access: string; refresh: string }>("/auth/login/", data).then((r) => r.data),

  me: () => client.get<User>("/auth/me/").then((r) => r.data),

  // exercises
  topics: () => client.get<TopicsResponse>("/exercises/topics/").then((r) => r.data),

  generate: (data: {
    profile: Profile;
    topics: string[];
    difficulty: number;
    count: number;
    seed?: string;
  }) => client.post<GenerateResponse>("/exercises/generate/", data).then((r) => r.data),

  simulate: (data: { profile: Profile; difficulty?: number; seed?: string }) =>
    client.post<SimulateResponse>("/exercises/simulate/", data).then((r) => r.data),

  exportSimulatePdf: (exam: SimulateResponse, session = "Simulare") =>
    client
      .post(
        "/exercises/export-pdf/",
        { ...exam, session },
        { responseType: "blob" },
      )
      .then((r) => r.data as Blob),

  saveSession: (data: {
    profile: Profile;
    topics: string[];
    difficulty: number;
    seed: string;
    items: unknown[];
  }) => client.post("/exercises/sessions/", data).then((r) => r.data),

  listSessions: () => client.get("/exercises/sessions/").then((r) => r.data),

  // blog
  blogList: () => client.get<BlogPostSummary[]>("/blog/posts/").then((r) => r.data),
  blogPost: (slug: string) => client.get<BlogPost>(`/blog/posts/${slug}/`).then((r) => r.data),

  // admin (staff only)
  adminListUsers: () => client.get<AdminUser[]>("/auth/admin/users/").then((r) => r.data),
  adminListPosts: () => client.get<AdminBlogPost[]>("/blog/admin/posts/").then((r) => r.data),
  adminCreatePost: (data: {
    title: string;
    excerpt: string;
    body_md: string;
    is_published: boolean;
  }) => client.post<AdminBlogPost>("/blog/admin/posts/", data).then((r) => r.data),

  // contact
  contact: (data: { name: string; email: string; subject: string; body: string }) =>
    client.post("/contact/", data).then((r) => r.data),
};

/** Machine-readable error code from the API body (e.g. "email_not_verified"). */
export function apiErrorCode(err: unknown): string | undefined {
  if (axios.isAxiosError(err)) {
    return (err.response?.data as any)?.code;
  }
  return undefined;
}

export function apiErrorMessage(err: unknown): string {
  if (axios.isAxiosError(err)) {
    const data = err.response?.data as any;
    if (data?.detail) return String(data.detail);
    if (data && typeof data === "object") {
      const first = Object.entries(data)[0];
      if (first) {
        const [field, val] = first;
        const msg = Array.isArray(val) ? val[0] : String(val);
        return `${field}: ${msg}`;
      }
    }
    return err.message;
  }
  return "A apărut o eroare.";
}
