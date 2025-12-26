// Type definitions for Shift Manager

export interface StaffData {
  name: string;
  type: number; // 0=常勤, 1=パート(日勤のみ), 2=パート(早番のみ)
  night_target: number;
  req_night: number[];
  req_early: number[];
  req_late: number[];
  req_day: number[];
  req_off: number[];
  req_work: number[];
  refresh_days: number[];
  paid_leave_days: number[];
  prev_shift: string;
  prev_streak: number;
  fixed_shifts: string[]; // [1日, 2日, 3日]
}

export interface ShiftRequest {
  year: number;
  month: number;
  target_off_days: number;
  staff_data: StaffData[];
  max_attempts?: number;
}

export interface ShiftResponse {
  schedule: Record<string, string[]>;
  errors: string[];
  year: number;
  month: number;
  days: number;
}

export type ShiftType = "早" | "日" | "遅" | "夜" | "・" | "◎" | "有" | "リ休" | "";



