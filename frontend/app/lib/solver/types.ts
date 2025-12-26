/**
 * Shift Solver Types - 型定義
 * Version: 2.1.0
 */

// スタッフ種別
export const StaffType = {
  REGULAR: 0,      // 常勤
  PART_DAY: 1,     // パート（日勤のみ）
  PART_EARLY: 2,   // パート（早番のみ）
} as const;

// シフト種別
export const ShiftTypes = {
  EARLY: "早",           // 早番
  DAY: "日",             // 日勤
  LATE: "遅",            // 遅番
  NIGHT: "夜",           // 夜勤
  NIGHT_REST: "・",      // 明け（夜勤後の休息）
  OFF: "◎",              // 公休
  HOPE_OFF: "◎ ",        // 希望休（末尾スペースで区別）
  PAID: "有",            // 有休
  REFRESH: "リ休",       // リフレッシュ休暇

  // グループ定義
  DAY_SHIFTS: ["早", "日", "遅"] as string[],
  WORK_SHIFTS: ["早", "日", "遅", "夜", "・"] as string[],
  REST_SHIFTS: ["◎", "有", "リ休"] as string[],
} as const;

// スタッフデータ
export interface StaffData {
  name: string;
  type: number;
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
  fixed_shifts: string[];
}

// シフトリクエスト
export interface ShiftRequest {
  year: number;
  month: number;
  target_off_days: number;
  staff_data: StaffData[];
  max_attempts?: number;
}

// シフトレスポンス
export interface ShiftResponse {
  schedule: Record<string, string[]>;
  errors: string[];
  year: number;
  month: number;
  days: number;
}

// スケジュール型
export type Schedule = Record<string, string[]>;

// 固定日型
export type FixedDays = Record<string, Set<number>>;

// 夜勤カウント型
export type NightCounts = Record<string, number>;

// ソルバー設定
export const SolverConfig = {
  // スコアペナルティ
  PENALTY_OFF_DAYS: 100,
  PENALTY_NIGHT_TARGET: 50,
  PENALTY_EARLY_MISSING: 300,
  PENALTY_LATE_MISSING: 300,
  PENALTY_NIGHT_MISSING: 500,
  PENALTY_DAY_SHORTAGE: 100,
  PENALTY_DUPLICATE: 500,
  PENALTY_VARIANCE: 30,
  PENALTY_RANGE: 50,

  // 最低人員数
  MIN_DAY_STAFF: 3,
  MAX_CONSECUTIVE_WORK: 5,

  // 調整回数
  BALANCE_ITERATIONS: 30,
  ADJUST_ITERATIONS: 20,

  // 早期終了
  EARLY_EXIT_SCORE: -100,

  // デフォルト試行回数
  DEFAULT_MAX_ATTEMPTS: 2500,
} as const;

// ヘルパー関数
export function isDayShift(shift: string): boolean {
  return ShiftTypes.DAY_SHIFTS.includes(shift.trim());
}

export function isWorkShift(shift: string): boolean {
  return ShiftTypes.WORK_SHIFTS.includes(shift.trim());
}

export function isRestShift(shift: string): boolean {
  return ShiftTypes.REST_SHIFTS.includes(shift.trim());
}

export function getDaysInMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate();
}

