export type Role = "user" | "assistant" | "system";

export interface Message {
  role: Role;
  content: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  expires_at: string;
}

export interface UserResponse {
  id: number;
  email: string;
  token: Token;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
}

export interface SessionResponse {
  session_id: string;
  name: string;
  token: Token;
}

export interface ChatResponse {
  messages: Message[];
}

export interface StreamChunk {
  content: string;
  done: boolean;
}

export interface ConnectDbRequest {
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
  driver?: string;
  sslmode?: string | null;
}

export interface ConnectDbResponse {
  connected: boolean;
  dialect: string;
  table_count: number;
}

export interface GrantFolderResponse {
  granted: boolean;
  folder: string;
}

export interface SourceStatus {
  db_connected: boolean;
  dialect?: string | null;
  folder?: string | null;
}

// --- Data Agent streaming (observable timeline) ---

export type StreamEvent =
  | { type: "tool_start"; name: string; input?: string }
  | { type: "tool_end"; name: string; output?: string }
  | { type: "token"; content: string }
  | { type: "done" }
  | { type: "error"; content?: string };

export interface ToolStep {
  id: number;
  name: string;
  input?: string;
  output?: string;
  done: boolean;
}

export interface UserTurn {
  role: "user";
  content: string;
}

export interface AssistantTurn {
  role: "assistant";
  steps: ToolStep[];
  content: string;
  streaming: boolean;
  error?: string;
}

export type Turn = UserTurn | AssistantTurn;

export type AppointmentStatus = "pending" | "checked_in" | "receiving" | "completed" | "cancelled" | "no_show";
export type CheckInMethod = "qr_code" | "manual";
export type AlertStatus = "open" | "acknowledged" | "resolved";
export type AlertSeverity = "info" | "warning" | "critical";

export interface DashboardSummary {
  pending_appointments: number;
  completed_appointments: number;
  check_ins: number;
  late_loads: number;
}

export interface Driver {
  id: number;
  name: string;
  cpf: string;
  email?: string | null;
  phone?: string | null;
  company?: string | null;
  notes: string;
  created_at: string;
}

export interface Vehicle {
  id: number;
  driver_id: number;
  plate: string;
  model?: string | null;
  color?: string | null;
  year?: number | null;
  created_at: string;
}

export interface Supplier {
  id: number;
  name: string;
  contact_email?: string | null;
  contact_phone?: string | null;
  authorized_email_domain?: string | null;
  created_at: string;
}

export interface Appointment {
  id: number;
  driver_id: number;
  vehicle_id: number;
  supplier_id: number;
  scheduled_at: string;
  dock?: string | null;
  load_reference?: string | null;
  status: AppointmentStatus;
  notes: string;
  created_by_user_id?: number | null;
  created_at: string;
}

export interface CheckIn {
  id: number;
  appointment_id: number;
  checked_in_at?: string | null;
  method: CheckInMethod;
  notes: string;
  confirmed_by_user_id?: number | null;
  created_at: string;
}

export interface YardAlert {
  id: number;
  appointment_id: number;
  alert_type: string;
  severity: AlertSeverity;
  message: string;
  status: AlertStatus;
  resolved_at?: string | null;
  resolved_by_user_id?: number | null;
  created_at: string;
}

export interface AppointmentDetail {
  appointment: Appointment;
  driver: Driver;
  vehicle: Vehicle;
  supplier: Supplier;
  check_ins: CheckIn[];
  alerts: YardAlert[];
}
