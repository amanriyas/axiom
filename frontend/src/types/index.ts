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
  jurisdiction: string;
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
  jurisdiction?: string;
}

export interface EmployeeUpdate {
  name?: string;
  email?: string;
  role?: string;
  department?: string;
  start_date?: string;
  manager_email?: string | null;
  buddy_email?: string | null;
  jurisdiction?: string;
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
  | "detect_jurisdiction"
  | "employment_contract"
  | "nda"
  | "equity_agreement"
  | "offer_letter"
  | "welcome_email"
  | "plan_30_60_90"
  | "schedule_events"
  | "equipment_request";

export type StepStatus = "pending" | "running" | "completed" | "failed" | "skipped";

export type WorkflowStatus = "pending" | "running" | "paused" | "awaiting_approval" | "completed" | "failed";

export interface OnboardingStep {
  id: number;
  step_type: StepType;
  step_order: number;
  status: StepStatus;
  result: string | null;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  requires_approval: boolean;
  approval_status: string | null;
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

// Jurisdiction types
export interface JurisdictionInfo {
  code: string;
  name: string;
  template_count: number;
}

export interface JurisdictionTemplate {
  id: number;
  jurisdiction_code: string;
  jurisdiction_name: string;
  document_type: string;
  template_name: string;
  created_at: string;
}

// Document types
export type DocumentStatus = "draft" | "pending_review" | "approved" | "rejected" | "revision_requested";

export interface GeneratedDocument {
  id: number;
  employee_id: number;
  document_type: string;
  title: string;
  content: string;
  jurisdiction: string;
  status: DocumentStatus;
  version: number;
  created_at: string;
  updated_at: string;
}

// Approval types
export type ApprovalStatus = "pending" | "approved" | "rejected" | "revision_requested";

export interface ApprovalRequest {
  id: number;
  employee_id: number;
  document_id: number;
  status: ApprovalStatus;
  reviewer_id: number | null;
  reviewer_notes: string | null;
  created_at: string;
  reviewed_at: string | null;
  employee_name: string | null;
  document_title: string | null;
  document_type: string | null;
}

// Chat types
export interface ChatMessage {
  id: number;
  conversation_id: number;
  role: "user" | "assistant";
  content: string;
  sources: string | null;
  created_at: string;
}

export interface ChatConversation {
  id: number;
  title: string;
  user_id: number | null;
  started_at: string;
  last_message_at: string;
  messages: ChatMessage[];
}

// Compliance types
export type ComplianceStatus = "valid" | "expiring_soon" | "expired" | "pending";

export interface ComplianceItem {
  id: number;
  employee_id: number;
  item_type: string;
  description: string;
  status: ComplianceStatus;
  expiry_date: string | null;
  reminder_sent: boolean;
  created_at: string;
  employee_name: string | null;
  days_remaining: number | null;
}

export interface ComplianceSummary {
  total: number;
  valid: number;
  expiring_soon: number;
  expired: number;
}

export interface CompliancePrediction {
  employee_id: number;
  employee_name: string;
  item_type: string;
  description: string;
  expiry_date: string;
  days_remaining: number;
  risk_level: "low" | "medium" | "high" | "critical";
  recommended_action: string;
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
  type: "init" | "task" | "done" | "think" | "active" | "error" | "step_update" | "approval_gate";
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

// Notification type
export interface Notification {
  id: string;
  title: string;
  description: string;
  type: "onboarding" | "employee" | "policy" | "approval" | "compliance";
  timestamp: string;
  read: boolean;
}
