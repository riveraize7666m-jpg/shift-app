/**
 * Shift Rule Checker - ルールチェッカー
 * Version: 2.1.0
 */

import { StaffData, Schedule, ShiftTypes, isWorkShift } from './types';

export class ShiftRuleChecker {
  private staffDictList: StaffData[];
  private days: number;
  private staffCache: Map<string, StaffData>;

  static readonly MAX_CONSECUTIVE_WORK = 5;
  static readonly MAX_DAY_SHIFT_STREAK = 3;

  constructor(staffDictList: StaffData[], days: number) {
    this.staffDictList = staffDictList;
    this.days = days;
    this.staffCache = new Map(staffDictList.map(s => [s.name, s]));
  }

  isWorkShift(val: string): boolean {
    const v = val?.trim() || "";
    return ShiftTypes.WORK_SHIFTS.includes(v);
  }

  isRestShift(val: string): boolean {
    const v = val?.trim() || "";
    return ShiftTypes.REST_SHIFTS.includes(v) || v === "";
  }

  getStaffInfo(name: string): StaffData {
    return this.staffCache.get(name)!;
  }

  getPrevShift(name: string, dayIdx: number, schedule: Schedule): string {
    if (dayIdx === 0) {
      return this.getStaffInfo(name).prev_shift.trim();
    }
    return schedule[name][dayIdx - 1].trim();
  }

  /**
   * 逆行チェック
   * 禁止: 日→早、遅→早、遅→日
   */
  checkReverse(prev: string, nextShift: string): boolean {
    if (prev === ShiftTypes.DAY && nextShift === ShiftTypes.EARLY) {
      return true;
    }
    if (prev === ShiftTypes.LATE && 
        (nextShift === ShiftTypes.EARLY || nextShift === ShiftTypes.DAY)) {
      return true;
    }
    return false;
  }

  /**
   * 連勤数をカウント
   */
  countConsecutiveWork(name: string, dayIdx: number, schedule: Schedule): number {
    const staffInfo = this.getStaffInfo(name);
    let streak = 0;
    let d = dayIdx - 1;

    while (d >= 0) {
      const val = schedule[name][d].trim();
      if (this.isWorkShift(val)) {
        streak++;
        d--;
      } else {
        break;
      }
    }

    if (d < 0) {
      streak += staffInfo.prev_streak;
    }

    return streak;
  }

  /**
   * 連勤中に夜勤があるかチェック
   */
  hasNightInStreak(name: string, dayIdx: number, schedule: Schedule): boolean {
    const staffInfo = this.getStaffInfo(name);
    let d = dayIdx - 1;

    while (d >= 0) {
      const val = schedule[name][d].trim();
      if (this.isWorkShift(val)) {
        if (val === ShiftTypes.NIGHT || val === ShiftTypes.NIGHT_REST) {
          return true;
        }
        d--;
      } else {
        break;
      }
    }

    if (d < 0) {
      const prevShift = staffInfo.prev_shift.trim();
      if (prevShift === ShiftTypes.NIGHT || prevShift === ShiftTypes.NIGHT_REST) {
        return true;
      }
    }

    return false;
  }

  /**
   * 日勤帯のみの連勤数をカウント
   */
  private countDayShiftStreak(name: string, dayIdx: number, schedule: Schedule): number {
    const staffInfo = this.getStaffInfo(name);
    let dayStreak = 0;

    // 前方の日勤帯連勤
    let d = dayIdx - 1;
    while (d >= 0) {
      const val = schedule[name][d].trim();
      if (ShiftTypes.DAY_SHIFTS.includes(val)) {
        dayStreak++;
        d--;
      } else if (val === ShiftTypes.NIGHT || val === ShiftTypes.NIGHT_REST) {
        break;
      } else {
        break;
      }
    }

    // 前月からの日勤帯連勤を加算
    if (d < 0) {
      const prevShiftVal = staffInfo.prev_shift.trim();
      if (ShiftTypes.DAY_SHIFTS.includes(prevShiftVal)) {
        dayStreak += staffInfo.prev_streak;
      }
    }

    dayStreak += 1; // 現在のシフト分

    // 後方の日勤帯連勤
    d = dayIdx + 1;
    while (d < this.days) {
      const val = schedule[name][d].trim();
      if (ShiftTypes.DAY_SHIFTS.includes(val)) {
        dayStreak++;
        d++;
      } else if (val === ShiftTypes.NIGHT || val === ShiftTypes.NIGHT_REST) {
        break;
      } else {
        break;
      }
    }

    return dayStreak;
  }

  /**
   * 翌日以降の連勤中に夜勤があるか
   */
  private hasNightInFutureStreak(name: string, dayIdx: number, schedule: Schedule): boolean {
    let d = dayIdx + 1;
    while (d < this.days) {
      const val = schedule[name][d].trim();
      if (this.isWorkShift(val)) {
        if (val === ShiftTypes.NIGHT || val === ShiftTypes.NIGHT_REST) {
          return true;
        }
        d++;
      } else {
        break;
      }
    }
    return false;
  }

  /**
   * メインルールチェック
   */
  checkRules(name: string, dayIdx: number, schedule: Schedule, shiftType: string): boolean {
    const staffInfo = this.getStaffInfo(name);
    const shiftClean = shiftType.trim();
    const prev = this.getPrevShift(name, dayIdx, schedule);

    // ルール1: 明け(・)の翌日は公休(◎)のみ
    if (prev === ShiftTypes.NIGHT_REST && shiftClean !== ShiftTypes.OFF) {
      return false;
    }

    // ルール2a: 前日との逆行禁止
    if (ShiftTypes.DAY_SHIFTS.includes(shiftClean)) {
      if (this.checkReverse(prev, shiftClean)) {
        return false;
      }
    }

    // ルール2b: 翌日との逆行禁止
    if (dayIdx + 1 < this.days) {
      const nextShift = schedule[name][dayIdx + 1].trim();
      if (ShiftTypes.DAY_SHIFTS.includes(nextShift)) {
        if (this.checkReverse(shiftClean, nextShift)) {
          return false;
        }
      }
    }

    // 休みタイプはここまででOK
    if (ShiftTypes.REST_SHIFTS.includes(shiftClean)) {
      return true;
    }

    // 明け(・)は夜勤の翌日のみ
    if (shiftClean === ShiftTypes.NIGHT_REST && prev !== ShiftTypes.NIGHT) {
      return false;
    }

    // ルール3: 連勤チェック
    if (!this.checkConsecutiveWorkLimit(name, dayIdx, schedule, shiftClean)) {
      return false;
    }

    // ルール4: 常勤の日勤帯のみ連勤は3連勤まで
    if (!this.checkDayShiftStreakLimit(name, dayIdx, schedule, shiftClean, staffInfo)) {
      return false;
    }

    return true;
  }

  private checkConsecutiveWorkLimit(
    name: string, 
    dayIdx: number, 
    schedule: Schedule, 
    shiftClean: string
  ): boolean {
    const streakBefore = this.countConsecutiveWork(name, dayIdx, schedule);

    let streakAfter = 0;
    let d = dayIdx + 1;
    while (d < this.days) {
      const val = schedule[name][d].trim();
      if (this.isWorkShift(val)) {
        streakAfter++;
        d++;
      } else {
        break;
      }
    }

    // 夜勤は2日分としてカウント
    const currentAdd = shiftClean === ShiftTypes.NIGHT ? 2 : 1;
    const totalStreak = streakBefore + currentAdd + streakAfter;

    return totalStreak <= ShiftRuleChecker.MAX_CONSECUTIVE_WORK;
  }

  private checkDayShiftStreakLimit(
    name: string,
    dayIdx: number,
    schedule: Schedule,
    shiftClean: string,
    staffInfo: StaffData
  ): boolean {
    if (staffInfo.type !== 0 || !ShiftTypes.DAY_SHIFTS.includes(shiftClean)) {
      return true;
    }

    let hasNight = this.hasNightInStreak(name, dayIdx, schedule);
    hasNight = hasNight || this.hasNightInFutureStreak(name, dayIdx, schedule);

    const dayStreak = this.countDayShiftStreak(name, dayIdx, schedule);

    // 4連勤以上の日勤帯のみは禁止
    if (dayStreak >= 4 && !hasNight) {
      return false;
    }

    return true;
  }

  /**
   * 夜勤を配置できるかチェック
   */
  canPlaceNight(name: string, dayIdx: number, schedule: Schedule): boolean {
    const staffInfo = this.getStaffInfo(name);

    // 常勤のみ夜勤可能
    if (staffInfo.type !== 0) {
      return false;
    }

    // 既にシフトが入っている場合は不可
    if (schedule[name][dayIdx] !== "") {
      return false;
    }

    // 翌日のチェック（明けが入れられるか）
    if (!this.canPlaceNightRest(name, dayIdx + 1, schedule)) {
      return false;
    }

    // 翌々日のチェック（公休が入れられるか）
    if (!this.canPlaceOffAfterNight(name, dayIdx + 2, schedule)) {
      return false;
    }

    return this.checkRules(name, dayIdx, schedule, ShiftTypes.NIGHT);
  }

  private canPlaceNightRest(name: string, dayIdx: number, schedule: Schedule): boolean {
    if (dayIdx >= this.days) {
      return true;
    }

    const nextVal = schedule[name][dayIdx];
    const nextValStripped = nextVal.trim();

    // 希望休（スペース付き）の場合は上書き不可
    if (nextVal === ShiftTypes.HOPE_OFF) {
      return false;
    }

    return nextValStripped === "" || nextValStripped === ShiftTypes.NIGHT_REST;
  }

  private canPlaceOffAfterNight(name: string, dayIdx: number, schedule: Schedule): boolean {
    if (dayIdx >= this.days) {
      return true;
    }

    const next2Val = schedule[name][dayIdx];
    const next2ValStripped = next2Val.trim();

    // 有休・リ休の場合は不可
    if (next2ValStripped === ShiftTypes.PAID || next2ValStripped === ShiftTypes.REFRESH) {
      return false;
    }

    // 希望休は許可
    if (next2Val === ShiftTypes.HOPE_OFF) {
      return true;
    }

    return next2ValStripped === "" || next2ValStripped === ShiftTypes.OFF;
  }
}

