export type Role = "admin" | "employee";

export type User = {
  id: number;
  username: string;
  email?: string;
  full_name?: string;
  phone?: string;
  job_title?: string;
  department?: string;
  salary_ruble?: string | number | null;
  role: Role;
  is_active: boolean;
  is_staff?: boolean;
  is_approved: boolean;
  approved_at?: string | null;
  approved_by?: number | null;
  approved_by_username?: string | null;
  created_at?: string;
  updated_at?: string;
  last_login?: string | null;
};

export type AuthBundle = {
  user: User;
  access: string;
  refresh: string;
  token: string;
  token_type: string;
};

export type Attendance = {
  id: number;
  user: number | string;
  username: string;
  user_full_name?: string;
  work_date: string;
  clock_in: string | null;
  clock_out: string | null;
  hours: number;
};

export type Schedule = {
  id: number;
  user: number | string;
  username: string;
  user_full_name?: string;
  week_start: string;
  day_of_week: string;
  shift_start: string;
  shift_end: string;
};

export type Task = {
  id: number;
  title: string;
  description?: string;
  assigned_to: number;
  assigned_to_username?: string;
  assigned_to_full_name?: string;
  created_by?: number | null;
  created_by_username?: string | null;
  status: "todo" | "in_progress" | "done" | "cancelled";
  priority: "low" | "medium" | "high" | "urgent";
  due_date?: string | null;
  created_at: string;
  updated_at?: string;
};

export type CalendarEvent = {
  id: number;
  title: string;
  description?: string;
  user?: number | null;
  username?: string | null;
  user_full_name?: string | null;
  created_by?: number | null;
  created_by_username?: string | null;
  start_at: string;
  end_at?: string | null;
  location?: string;
  created_at?: string;
  updated_at?: string;
};

export type WeeklyChart = {
  week_start: string;
  week_end: string;
  total_hours: number;
  by_user: Array<{
    user_id: number;
    username: string;
    full_name?: string;
    total_hours: number;
    days: Array<{ date: string; clock_in?: string | null; clock_out?: string | null; hours: number }>;
  }>;
  by_day: Array<{ date: string; hours: number; records: number }>;
};

export type DashboardStats = {
  members_total: number;
  members_active: number;
  members_pending_approval: number;
  admins_total: number;
  attendance_today: number;
  tasks_open: number;
  tasks_done: number;
  events_this_week: number;
  weekly_chart: WeeklyChart;
};

export type Paginated<T> = {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
};
