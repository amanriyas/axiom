// TypeScript types matching backend schemas

// Auth types
export interface User {
  id: number;
  email: string;
  name: string;
  role: "admin" | "hr" | "viewer";
  is_active: boolean;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  name: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

export interface Token {
  access_token: string;
  token_type: string;
}

// Employee types
export type EmployeeStatus = "pending" | "onboarding" | "completed" | "failed";

export interface Employee {
  id: number;
  name: string;
  email: string;
  role: string;
  department: string;
  start_date: string;
  manager_email: string | null;
  buddy_email: string | null;
  status: EmployeeStatus;
  created_at: string;
  updated_at: string;
}

export interface EmployeeCreate {
  name: string;
  email: string;
  role: string;
  department: string;
  start_date: string;
  manager_email?: string | null;
  buddy_email?: string | null;
}

export interface EmployeeUpdate {
  name?: string;
  email?: string;
  role?: string;
  department?: string;
  start_date?: string;
  manager_email?: string | null;
  buddy_email?: string | null;
  status?: EmployeeStatus;
}

// Policy types
export interface Policy {
  id: number;
  title: string;
  filename: string;
  file_size: number | null;
  is_embedded: boolean;
  uploaded_at: string;
}

// Onboarding types
export type StepType =
  | "parse_data"
  | "welcome_email"
  | "offer_letter"
  | "plan_30_60_90"
  | "schedule_events"
  | "equipment_request";

export type StepStatus = "pending" | "running" | "completed" | "failed" | "skipped";

export type WorkflowStatus = "pending" | "running" | "completed" | "failed";

export interface OnboardingStep {
  id: number;
  step_type: StepType;
  step_order: number;
  status: StepStatus;
  result: string | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
}

export interface OnboardingWorkflow {
  id: number;
  employee_id: number;
  status: WorkflowStatus;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
  created_at: string;
  steps: OnboardingStep[];
}

export interface OnboardingStartResponse {
  workflow_id: number;
  employee_id: number;
  message: string;
}

// Calendar types
export interface CalendarEvent {
  id: string;
  title: string;
  date: string;
  status: "created" | "mock";
}

// Generic response types
export interface MessageResponse {
  message: string;
}

export interface BulkUploadResponse {
  total: number;
  created: number;
  errors: string[];
}

// SSE Event types for agent activity
export interface AgentEvent {
  type: "init" | "task" | "done" | "think" | "active" | "error" | "step_update";
  message: string;
  timestamp: string;
  step_type?: StepType;
  step_status?: StepStatus;
}

// Dashboard stats
export interface DashboardStats {
  pending: number;
  in_progress: number;
  completed: number;
  avg_time_days: number;
  pending_trend: number;
  in_progress_trend: number;
  completed_trend: number;
  avg_time_trend: number;
}
