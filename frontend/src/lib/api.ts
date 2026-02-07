// API client with JWT authentication handling

import {
  User,
  UserCreate,
  UserLogin,
  Token,
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
  Policy,
  OnboardingWorkflow,
  OnboardingStartResponse,
  MessageResponse,
  BulkUploadResponse,
  Notification,
  JurisdictionInfo,
  JurisdictionTemplate,
  GeneratedDocument,
  ApprovalRequest,
  ChatConversation,
  ChatMessage,
  ComplianceItem,
  ComplianceSummary,
  CompliancePrediction,
} from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "/proxy";

// Token management
let accessToken: string | null = null;

export function setToken(token: string | null) {
  accessToken = token;
  if (token) {
    localStorage.setItem("access_token", token);
  } else {
    localStorage.removeItem("access_token");
  }
}

export function getToken(): string | null {
  if (accessToken) return accessToken;
  if (typeof window !== "undefined") {
    accessToken = localStorage.getItem("access_token");
  }
  return accessToken;
}

export function clearToken() {
  accessToken = null;
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
  }
}

// Base fetch with auth
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...((options.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));

    // Global 401 handler — stale/invalid token → clear and redirect to login
    if (response.status === 401) {
      clearToken();
      if (typeof window !== "undefined" && !window.location.pathname.startsWith("/login")) {
        window.location.href = "/login";
      }
    }

    const error = new Error(errorData.detail || `HTTP error ${response.status}`);
    (error as Error & { status?: number }).status = response.status;
    throw error;
  }

  return response.json();
}

// Auth API
export const authApi = {
  signup: (data: UserCreate): Promise<User> =>
    apiFetch("/api/auth/signup", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (data: UserLogin): Promise<Token> =>
    apiFetch("/api/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  googleAuth: (token: string): Promise<Token> =>
    apiFetch("/api/auth/google", {
      method: "POST",
      body: JSON.stringify({ token }),
    }),

  me: (): Promise<User> => apiFetch("/api/auth/me"),

  updateProfile: (data: { name?: string; email?: string }): Promise<User> =>
    apiFetch("/api/auth/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  changePassword: (data: {
    current_password: string;
    new_password: string;
  }): Promise<MessageResponse> =>
    apiFetch("/api/auth/password", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  notifications: (): Promise<Notification[]> =>
    apiFetch("/api/auth/notifications"),
};

// Employee API
export const employeeApi = {
  list: (): Promise<Employee[]> => apiFetch("/api/employees/"),

  get: (id: number): Promise<Employee> => apiFetch(`/api/employees/${id}`),

  create: (data: EmployeeCreate): Promise<Employee> =>
    apiFetch("/api/employees/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  update: (id: number, data: EmployeeUpdate): Promise<Employee> =>
    apiFetch(`/api/employees/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  delete: (id: number): Promise<MessageResponse> =>
    apiFetch(`/api/employees/${id}`, {
      method: "DELETE",
    }),

  uploadCsv: async (file: File): Promise<BulkUploadResponse> => {
    const formData = new FormData();
    formData.append("file", file);
    return apiFetch("/api/employees/upload", {
      method: "POST",
      body: formData,
    });
  },
};

// Policy API
export const policyApi = {
  list: (): Promise<Policy[]> => apiFetch("/api/policies/"),

  get: (id: number): Promise<Policy> => apiFetch(`/api/policies/${id}`),

  upload: async (title: string, file: File): Promise<Policy> => {
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);
    return apiFetch("/api/policies/upload", {
      method: "POST",
      body: formData,
    });
  },

  delete: (id: number): Promise<MessageResponse> =>
    apiFetch(`/api/policies/${id}`, {
      method: "DELETE",
    }),

  getDownloadUrl: (id: number): string => `${API_URL}/api/policies/${id}/download`,

  reembed: (id: number): Promise<Policy> =>
    apiFetch(`/api/policies/${id}/reembed`, {
      method: "POST",
    }),
};

// Onboarding API
export const onboardingApi = {
  start: (employeeId: number): Promise<OnboardingStartResponse> =>
    apiFetch(`/api/onboarding/${employeeId}/start`, {
      method: "POST",
    }),

  getStatus: (employeeId: number): Promise<OnboardingWorkflow> =>
    apiFetch(`/api/onboarding/${employeeId}/status`),

  getWorkflow: (workflowId: number): Promise<OnboardingWorkflow> =>
    apiFetch(`/api/onboarding/workflow/${workflowId}`),

  pause: (employeeId: number): Promise<MessageResponse> =>
    apiFetch(`/api/onboarding/${employeeId}/pause`, {
      method: "POST",
    }),

  resume: (employeeId: number): Promise<MessageResponse> =>
    apiFetch(`/api/onboarding/${employeeId}/resume`, {
      method: "POST",
    }),

  retry: (employeeId: number): Promise<OnboardingStartResponse> =>
    apiFetch(`/api/onboarding/${employeeId}/retry`, {
      method: "POST",
    }),

  getExportUrl: (employeeId: number): string =>
    `${API_URL}/api/onboarding/${employeeId}/export`,

  // SSE stream URL (not a fetch, used with EventSource)
  getStreamUrl: (employeeId: number): string => {
    const token = getToken();
    const base = `${API_URL}/api/onboarding/${employeeId}/stream`;
    return token ? `${base}?token=${encodeURIComponent(token)}` : base;
  },

  getTemplates: (): Promise<Record<string, string>> =>
    apiFetch("/api/onboarding/templates"),

  updateTemplates: (templates: Record<string, string>): Promise<MessageResponse> =>
    apiFetch("/api/onboarding/templates", {
      method: "PUT",
      body: JSON.stringify(templates),
    }),
};

// Jurisdiction API
export const jurisdictionApi = {
  list: (): Promise<JurisdictionInfo[]> =>
    apiFetch("/api/jurisdictions"),

  get: (code: string): Promise<JurisdictionInfo> =>
    apiFetch(`/api/jurisdictions/${code}`),

  getTemplates: (code: string): Promise<JurisdictionTemplate[]> =>
    apiFetch(`/api/jurisdictions/${code}/templates`),
};

// Document API
export const documentApi = {
  getByEmployee: (employeeId: number): Promise<GeneratedDocument[]> =>
    apiFetch(`/api/documents/employee/${employeeId}`),

  get: (id: number): Promise<GeneratedDocument> =>
    apiFetch(`/api/documents/${id}`),

  update: (id: number, data: { content?: string; status?: string }): Promise<GeneratedDocument> =>
    apiFetch(`/api/documents/${id}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  getDownloadUrl: (id: number): string =>
    `${API_URL}/api/documents/${id}/download`,
};

// Approval API
export const approvalApi = {
  list: (): Promise<ApprovalRequest[]> =>
    apiFetch("/api/approvals"),

  getPendingCount: (): Promise<{ count: number }> =>
    apiFetch("/api/approvals/pending/count"),

  get: (id: number): Promise<ApprovalRequest> =>
    apiFetch(`/api/approvals/${id}`),

  approve: (id: number, notes?: string): Promise<ApprovalRequest> =>
    apiFetch(`/api/approvals/${id}/approve`, {
      method: "POST",
      body: JSON.stringify({ action: "approve", notes }),
    }),

  reject: (id: number, notes?: string): Promise<ApprovalRequest> =>
    apiFetch(`/api/approvals/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ action: "reject", notes }),
    }),

  requestRevision: (id: number, notes?: string): Promise<ApprovalRequest> =>
    apiFetch(`/api/approvals/${id}/revision`, {
      method: "POST",
      body: JSON.stringify({ action: "revision", notes }),
    }),

  getByEmployee: (employeeId: number): Promise<ApprovalRequest[]> =>
    apiFetch(`/api/approvals/employee/${employeeId}`),
};

// Chat API
export const chatApi = {
  createConversation: (title?: string): Promise<ChatConversation> =>
    apiFetch("/api/chat/conversations", {
      method: "POST",
      body: JSON.stringify({ title }),
    }),

  listConversations: (): Promise<ChatConversation[]> =>
    apiFetch("/api/chat/conversations"),

  getConversation: (id: number): Promise<ChatConversation> =>
    apiFetch(`/api/chat/conversations/${id}`),

  getMessages: (conversationId: number): Promise<ChatMessage[]> =>
    apiFetch(`/api/chat/conversations/${conversationId}/messages`),

  sendMessage: (conversationId: number, content: string): Promise<ChatMessage> =>
    apiFetch(`/api/chat/conversations/${conversationId}/messages`, {
      method: "POST",
      body: JSON.stringify({ content }),
    }),

  deleteConversation: (id: number): Promise<MessageResponse> =>
    apiFetch(`/api/chat/conversations/${id}`, { method: "DELETE" }),

  clearAll: (): Promise<MessageResponse> =>
    apiFetch("/api/chat/conversations", { method: "DELETE" }),

  getStreamUrl: (conversationId: number, content: string): string => {
    const token = getToken();
    const base = `${API_URL}/api/chat/conversations/${conversationId}/stream`;
    const params = new URLSearchParams();
    if (token) params.set("token", token);
    params.set("content", content);
    return `${base}?${params.toString()}`;
  },
};

// Compliance API
export const complianceApi = {
  list: (): Promise<ComplianceItem[]> =>
    apiFetch("/api/compliance"),

  getSummary: (): Promise<ComplianceSummary> =>
    apiFetch("/api/compliance/summary"),

  getAlerts: (): Promise<ComplianceItem[]> =>
    apiFetch("/api/compliance/alerts"),

  getExpired: (): Promise<ComplianceItem[]> =>
    apiFetch("/api/compliance/expired"),

  getPredictions: (): Promise<CompliancePrediction[]> =>
    apiFetch("/api/compliance/predictions"),

  getByEmployee: (employeeId: number): Promise<ComplianceItem[]> =>
    apiFetch(`/api/compliance/employee/${employeeId}`),

  create: (data: {
    employee_id: number;
    item_type: string;
    description: string;
    expiry_date?: string;
  }): Promise<ComplianceItem> =>
    apiFetch("/api/compliance", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};