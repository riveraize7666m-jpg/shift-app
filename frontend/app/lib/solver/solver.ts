/**
 * Shift Solver - シフト表自動生成ソルバー
 * Version: 2.1.0
 */

import {
  StaffData,
  Schedule,
  FixedDays,
  NightCounts,
  ShiftTypes,
  SolverConfig,
  getDaysInMonth,
} from './types';
import { ShiftRuleChecker } from './rules';

export class ShiftSolver {
  private year: number;
  private month: number;
  private targetOffDays: number;
  private maxAttempts: number;
  private days: number;
  private staffDictList: StaffData[];
  private regulars: StaffData[];
  private workLimits: Record<string, number>;
  private ruleChecker: ShiftRuleChecker;

  constructor(
    staffData: StaffData[],
    year: number,
    month: number,
    targetOffDays: number,
    maxAttempts: number = SolverConfig.DEFAULT_MAX_ATTEMPTS
  ) {
    this.year = year;
    this.month = month;
    this.targetOffDays = targetOffDays;
    this.maxAttempts = maxAttempts;
    this.days = getDaysInMonth(year, month);
    this.staffDictList = staffData;
    this.regulars = staffData.filter(s => s.type === 0);
    this.workLimits = this.calcWorkLimits();
    this.ruleChecker = new ShiftRuleChecker(staffData, this.days);
  }

  // ユーティリティメソッド
  private calcWorkLimits(): Record<string, number> {
    const limits: Record<string, number> = {};
    for (const s of this.staffDictList) {
      if (s.type !== 0) {
        limits[s.name] = 99;
      } else {
        const extraOff = s.refresh_days.length + s.paid_leave_days.length;
        limits[s.name] = this.days - (this.targetOffDays + extraOff);
      }
    }
    return limits;
  }

  private countDayStaff(schedule: Schedule, dayIdx: number, shiftTypes: string[]): number {
    return this.staffDictList.filter(
      s => shiftTypes.includes(schedule[s.name][dayIdx].trim())
    ).length;
  }

  private countRequiredOff(dayIdx: number, schedule: Schedule): number {
    let cnt = 0;
    for (const s of this.staffDictList) {
      const val = schedule[s.name][dayIdx];
      if (val === ShiftTypes.HOPE_OFF || 
          val.trim() === ShiftTypes.PAID || 
          val.trim() === ShiftTypes.REFRESH) {
        cnt++;
      }
    }
    return cnt;
  }

  private getDailyCounts(schedule: Schedule): number[] {
    return Array.from({ length: this.days }, (_, d) =>
      this.countDayStaff(schedule, d, ShiftTypes.DAY_SHIFTS)
    );
  }

  private calcVariance(counts: number[]): number {
    if (counts.length === 0) return 0;
    const avg = counts.reduce((a, b) => a + b, 0) / counts.length;
    return counts.reduce((sum, c) => sum + Math.pow(c - avg, 2), 0) / counts.length;
  }

  private countCurrentOff(name: string, schedule: Schedule): number {
    return schedule[name].filter(x => x.trim() === ShiftTypes.OFF).length;
  }

  private shuffle<T>(array: T[]): T[] {
    const result = [...array];
    for (let i = result.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [result[i], result[j]] = [result[j], result[i]];
    }
    return result;
  }

  private placeNightShift(
    name: string, 
    dayIdx: number, 
    schedule: Schedule, 
    nightCounts: NightCounts
  ): void {
    schedule[name][dayIdx] = ShiftTypes.NIGHT;
    nightCounts[name]++;

    if (dayIdx + 1 < this.days) {
      if (schedule[name][dayIdx + 1] !== ShiftTypes.HOPE_OFF) {
        schedule[name][dayIdx + 1] = ShiftTypes.NIGHT_REST;
      }
    }

    if (dayIdx + 2 < this.days && schedule[name][dayIdx + 2] === "") {
      schedule[name][dayIdx + 2] = ShiftTypes.OFF;
    }
  }

  // Phase 0: 前月末シフト処理
  private phase0PrevMonth(schedule: Schedule, fixedDays: FixedDays): void {
    for (const s of this.staffDictList) {
      const name = s.name;
      const prev = s.prev_shift.trim();

      if (prev === ShiftTypes.NIGHT_REST) {
        schedule[name][0] = ShiftTypes.OFF;
        fixedDays[name].add(0);
      } else if (prev === ShiftTypes.NIGHT) {
        schedule[name][0] = ShiftTypes.NIGHT_REST;
        fixedDays[name].add(0);
        if (this.days > 1) {
          schedule[name][1] = ShiftTypes.OFF;
          fixedDays[name].add(1);
        }
      }
    }
  }

  // Phase 1: 固定シフトと希望の設定
  private phase1FixedAndRequests(
    schedule: Schedule, 
    fixedDays: FixedDays, 
    nightCounts: NightCounts
  ): void {
    for (const s of this.staffDictList) {
      const name = s.name;

      // 年始固定シフト
      for (let i = 0; i < Math.min(3, this.days); i++) {
        if (fixedDays[name].has(i)) continue;
        if (s.fixed_shifts.length > i && s.fixed_shifts[i]) {
          const fs = s.fixed_shifts[i];
          schedule[name][i] = fs;
          fixedDays[name].add(i);

          if (fs === ShiftTypes.NIGHT) {
            nightCounts[name]++;
            if (i + 1 < this.days && schedule[name][i + 1] === "") {
              schedule[name][i + 1] = ShiftTypes.NIGHT_REST;
              fixedDays[name].add(i + 1);
            }
            if (i + 2 < this.days) {
              if (schedule[name][i + 2] === "") {
                schedule[name][i + 2] = ShiftTypes.OFF;
                fixedDays[name].add(i + 2);
              } else if (schedule[name][i + 2] === ShiftTypes.HOPE_OFF) {
                fixedDays[name].add(i + 2);
              }
            }
          }
        }
      }

      // 希望休
      for (const d of s.req_off) {
        if (d > 0 && d <= this.days && schedule[name][d - 1] === "") {
          schedule[name][d - 1] = ShiftTypes.HOPE_OFF;
          fixedDays[name].add(d - 1);
        }
      }

      // リフレッシュ休暇
      for (const d of s.refresh_days) {
        if (d > 0 && d <= this.days && schedule[name][d - 1] === "") {
          schedule[name][d - 1] = ShiftTypes.REFRESH;
          fixedDays[name].add(d - 1);
        }
      }

      // 有給休暇
      for (const d of s.paid_leave_days) {
        if (d > 0 && d <= this.days && schedule[name][d - 1] === "") {
          schedule[name][d - 1] = ShiftTypes.PAID;
          fixedDays[name].add(d - 1);
        }
      }

      // 希望シフト
      for (const d of s.req_early) {
        if (d > 0 && d <= this.days && schedule[name][d - 1] === "") {
          if (this.ruleChecker.checkRules(name, d - 1, schedule, ShiftTypes.EARLY)) {
            schedule[name][d - 1] = ShiftTypes.EARLY;
            fixedDays[name].add(d - 1);
          }
        }
      }

      for (const d of s.req_late) {
        if (d > 0 && d <= this.days && schedule[name][d - 1] === "") {
          if (this.ruleChecker.checkRules(name, d - 1, schedule, ShiftTypes.LATE)) {
            schedule[name][d - 1] = ShiftTypes.LATE;
            fixedDays[name].add(d - 1);
          }
        }
      }

      for (const d of s.req_day) {
        if (d > 0 && d <= this.days && schedule[name][d - 1] === "") {
          if (this.ruleChecker.checkRules(name, d - 1, schedule, ShiftTypes.DAY)) {
            schedule[name][d - 1] = ShiftTypes.DAY;
            fixedDays[name].add(d - 1);
          }
        }
      }

      // パート設定
      if (s.type === 1) {
        for (let d = 0; d < this.days; d++) {
          if (schedule[name][d] === "") {
            schedule[name][d] = ShiftTypes.DAY;
          }
        }
      } else if (s.type === 2) {
        for (let d = 0; d < this.days; d++) {
          if (schedule[name][d] === "") {
            if (this.countDayStaff(schedule, d, [ShiftTypes.EARLY]) === 0) {
              schedule[name][d] = ShiftTypes.EARLY;
            } else {
              schedule[name][d] = ShiftTypes.DAY;
            }
          }
        }
      }
    }
  }

  // Phase 2: 夜勤希望の配置
  private phase2NightRequests(
    schedule: Schedule, 
    fixedDays: FixedDays, 
    nightCounts: NightCounts
  ): void {
    for (const s of this.staffDictList) {
      const name = s.name;
      if (!s.req_night || s.type !== 0) continue;

      for (const dIdx of s.req_night) {
        const d = dIdx - 1;
        if (d >= 0 && d < this.days && !fixedDays[name].has(d)) {
          if (this.ruleChecker.canPlaceNight(name, d, schedule)) {
            schedule[name][d] = ShiftTypes.NIGHT;
            nightCounts[name]++;
            fixedDays[name].add(d);

            if (d + 1 < this.days && !fixedDays[name].has(d + 1)) {
              if (schedule[name][d + 1] !== ShiftTypes.HOPE_OFF) {
                schedule[name][d + 1] = ShiftTypes.NIGHT_REST;
              }
              fixedDays[name].add(d + 1);
            }

            if (d + 2 < this.days && !fixedDays[name].has(d + 2)) {
              if (schedule[name][d + 2] === "") {
                schedule[name][d + 2] = ShiftTypes.OFF;
                fixedDays[name].add(d + 2);
              } else if (schedule[name][d + 2] === ShiftTypes.HOPE_OFF) {
                fixedDays[name].add(d + 2);
              }
            }
          }
        }
      }
    }
  }

  // Phase 3: 毎日の夜勤配置
  private phase3DailyNight(schedule: Schedule, nightCounts: NightCounts): void {
    // 希望休に合わせて夜勤を配置
    for (const s of this.regulars) {
      const name = s.name;
      if (nightCounts[name] >= s.night_target) continue;

      const offDays = new Set([...s.req_off, ...s.refresh_days, ...s.paid_leave_days]);

      for (const offDay of [...offDays].sort((a, b) => a - b)) {
        const nightDay = offDay - 3;
        if (nightDay < 0 || nightDay >= this.days) continue;

        if (this.countDayStaff(schedule, nightDay, [ShiftTypes.NIGHT]) > 0) continue;

        if (this.ruleChecker.canPlaceNight(name, nightDay, schedule)) {
          this.placeNightShift(name, nightDay, schedule, nightCounts);
          if (nightCounts[name] >= s.night_target) break;
        }
      }
    }

    // 残りの日に夜勤配置
    const daysOrder = this.shuffle(Array.from({ length: this.days }, (_, i) => i));

    for (const d of daysOrder) {
      if (this.countDayStaff(schedule, d, [ShiftTypes.NIGHT]) > 0) continue;

      const candidates: [StaffData, number][] = [];
      for (const s of this.regulars) {
        if (this.ruleChecker.canPlaceNight(s.name, d, schedule)) {
          const priority = s.night_target - nightCounts[s.name];
          candidates.push([s, priority]);
        }
      }

      if (candidates.length > 0) {
        candidates.sort((a, b) => b[1] - a[1]);
        const topPriority = candidates[0][1];
        const topCands = candidates.filter(c => c[1] === topPriority);
        const chosen = topCands[Math.floor(Math.random() * topCands.length)][0];
        this.placeNightShift(chosen.name, d, schedule, nightCounts);
      }
    }
  }

  // Phase 4: 早番・遅番の配置
  private phase4EarlyLate(schedule: Schedule): void {
    for (let d = 0; d < this.days; d++) {
      // 遅番配置
      if (this.countDayStaff(schedule, d, [ShiftTypes.LATE]) === 0) {
        const candidates = this.regulars.filter(
          s => schedule[s.name][d] === "" &&
               this.ruleChecker.checkRules(s.name, d, schedule, ShiftTypes.LATE)
        );
        if (candidates.length > 0) {
          const chosen = candidates[Math.floor(Math.random() * candidates.length)];
          schedule[chosen.name][d] = ShiftTypes.LATE;
        }
      }

      // 早番配置
      if (this.countDayStaff(schedule, d, [ShiftTypes.EARLY]) === 0) {
        const candidates = this.regulars.filter(
          s => schedule[s.name][d] === "" &&
               this.ruleChecker.checkRules(s.name, d, schedule, ShiftTypes.EARLY)
        );
        // 早番パートも候補に
        for (const s of this.staffDictList) {
          if (s.type === 2 && schedule[s.name][d] === "") {
            candidates.push(s);
          }
        }
        if (candidates.length > 0) {
          const chosen = candidates[Math.floor(Math.random() * candidates.length)];
          schedule[chosen.name][d] = ShiftTypes.EARLY;
        }
      }
    }
  }

  // Phase 5: 日勤で埋める
  private phase5FillDay(schedule: Schedule): void {
    for (const s of this.regulars) {
      const name = s.name;
      let emptyDays = Array.from({ length: this.days }, (_, i) => i)
        .filter(d => schedule[name][d] === "");

      emptyDays.sort((a, b) => 
        this.countDayStaff(schedule, a, ShiftTypes.DAY_SHIFTS) -
        this.countDayStaff(schedule, b, ShiftTypes.DAY_SHIFTS)
      );

      for (const d of emptyDays) {
        const currWork = schedule[name].filter(x => this.ruleChecker.isWorkShift(x)).length;
        if (currWork >= this.workLimits[name]) break;
        if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.DAY)) {
          schedule[name][d] = ShiftTypes.DAY;
        }
      }
    }
  }

  // Phase 6: 公休の最適配置
  private phase6FillOff(schedule: Schedule): void {
    for (const s of this.regulars) {
      const name = s.name;
      const currentOff = this.countCurrentOff(name, schedule);
      if (currentOff >= this.targetOffDays) continue;

      const emptyDays = Array.from({ length: this.days }, (_, i) => i)
        .filter(d => schedule[name][d] === "");
      if (emptyDays.length === 0) continue;

      const neededOff = this.targetOffDays - currentOff;

      const dayScores: [number, number][] = emptyDays.map(d => {
        const dayCnt = this.countDayStaff(schedule, d, ShiftTypes.DAY_SHIFTS);
        const fixedOff = this.countRequiredOff(d, schedule);
        const othersEmpty = this.regulars.filter(
          s2 => s2.name !== name && schedule[s2.name][d] === ""
        ).length;
        return [d, dayCnt + othersEmpty - fixedOff];
      });

      dayScores.sort((a, b) => b[1] - a[1]);

      let placedCount = 0;
      for (const [d] of dayScores) {
        if (placedCount >= neededOff) break;
        if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.OFF)) {
          schedule[name][d] = ShiftTypes.OFF;
          placedCount++;
        }
      }
    }
  }

  // Phase 6b: 残りの空スロットを埋める
  private phase6bFillRemaining(schedule: Schedule): void {
    for (const s of this.regulars) {
      const name = s.name;
      let emptyDays = Array.from({ length: this.days }, (_, i) => i)
        .filter(d => schedule[name][d] === "");

      emptyDays.sort((a, b) =>
        this.countDayStaff(schedule, a, ShiftTypes.DAY_SHIFTS) -
        this.countDayStaff(schedule, b, ShiftTypes.DAY_SHIFTS)
      );

      for (const d of emptyDays) {
        const shiftOrder = [ShiftTypes.DAY, ShiftTypes.EARLY, ShiftTypes.LATE, ShiftTypes.OFF];
        for (const shift of shiftOrder) {
          if (this.ruleChecker.checkRules(name, d, schedule, shift)) {
            schedule[name][d] = shift;
            break;
          }
        }
      }
    }
  }

  // Phase 7: 人員平準化
  private phase7Balance(schedule: Schedule, fixedDays: FixedDays): void {
    for (let iter = 0; iter < SolverConfig.BALANCE_ITERATIONS; iter++) {
      const dailyCounts = this.getDailyCounts(schedule);
      if (dailyCounts.length === 0) break;

      let maxDay = 0, minDay = 0;
      for (let d = 0; d < this.days; d++) {
        if (dailyCounts[d] > dailyCounts[maxDay]) maxDay = d;
        if (dailyCounts[d] < dailyCounts[minDay]) minDay = d;
      }

      if (dailyCounts[maxDay] - dailyCounts[minDay] < 2) break;

      let improved = false;
      for (const s of this.regulars) {
        const name = s.name;
        if (fixedDays[name].has(maxDay) || fixedDays[name].has(minDay)) continue;

        if (schedule[name][maxDay] === ShiftTypes.DAY && 
            schedule[name][minDay] === ShiftTypes.OFF) {
          schedule[name][maxDay] = "";
          schedule[name][minDay] = "";

          if (this.ruleChecker.checkRules(name, maxDay, schedule, ShiftTypes.OFF) &&
              this.ruleChecker.checkRules(name, minDay, schedule, ShiftTypes.DAY)) {
            schedule[name][maxDay] = ShiftTypes.OFF;
            schedule[name][minDay] = ShiftTypes.DAY;
            improved = true;
            break;
          } else {
            schedule[name][maxDay] = ShiftTypes.DAY;
            schedule[name][minDay] = ShiftTypes.OFF;
          }
        }
      }

      if (!improved) break;
    }
  }

  // Phase 8: 人員調整
  private phase8Adjust(schedule: Schedule, fixedDays: FixedDays): void {
    for (let iter = 0; iter < SolverConfig.ADJUST_ITERATIONS; iter++) {
      let improved = false;

      for (let d = 0; d < this.days; d++) {
        const earlyCnt = this.countDayStaff(schedule, d, [ShiftTypes.EARLY]);
        const lateCnt = this.countDayStaff(schedule, d, [ShiftTypes.LATE]);
        const dayTotal = this.countDayStaff(schedule, d, ShiftTypes.DAY_SHIFTS);

        // 早番不足
        if (earlyCnt === 0) {
          for (const s of this.regulars) {
            const name = s.name;
            if (fixedDays[name].has(d)) continue;
            if (schedule[name][d] === ShiftTypes.DAY) {
              schedule[name][d] = "";
              if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.EARLY)) {
                schedule[name][d] = ShiftTypes.EARLY;
                improved = true;
                break;
              } else {
                schedule[name][d] = ShiftTypes.DAY;
              }
            }
          }
        }

        // 遅番不足
        if (lateCnt === 0) {
          for (const s of this.regulars) {
            const name = s.name;
            if (fixedDays[name].has(d)) continue;
            if (schedule[name][d] === ShiftTypes.DAY) {
              schedule[name][d] = "";
              if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.LATE)) {
                schedule[name][d] = ShiftTypes.LATE;
                improved = true;
                break;
              } else {
                schedule[name][d] = ShiftTypes.DAY;
              }
            }
          }
        }

        // 日勤帯不足
        if (dayTotal < SolverConfig.MIN_DAY_STAFF) {
          for (const s of this.regulars) {
            const name = s.name;
            if (fixedDays[name].has(d)) continue;
            if (schedule[name][d] === ShiftTypes.OFF) {
              const otherDays = Array.from({ length: this.days }, (_, od) => od)
                .filter(od => od !== d &&
                  schedule[name][od] === ShiftTypes.OFF &&
                  !fixedDays[name].has(od) &&
                  this.countDayStaff(schedule, od, ShiftTypes.DAY_SHIFTS) >= 4
                );

              if (otherDays.length > 0) {
                schedule[name][d] = "";
                if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.DAY)) {
                  schedule[name][d] = ShiftTypes.DAY;
                  improved = true;
                  break;
                } else {
                  schedule[name][d] = ShiftTypes.OFF;
                }
              }
            }
          }
        }
      }

      if (!improved) break;
    }
  }

  // Phase 9: 早番・遅番重複解消
  private phase9ReduceDuplicates(schedule: Schedule, fixedDays: FixedDays): void {
    for (let d = 0; d < this.days; d++) {
      // 早番の重複解消
      while (this.countDayStaff(schedule, d, [ShiftTypes.EARLY]) > 1) {
        const earlyStaff = this.staffDictList.filter(
          s => schedule[s.name][d] === ShiftTypes.EARLY &&
               s.type === 0 &&
               !fixedDays[s.name].has(d)
        );

        if (earlyStaff.length === 0) break;

        let converted = false;
        for (const s of earlyStaff) {
          const name = s.name;
          schedule[name][d] = "";

          if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.DAY)) {
            schedule[name][d] = ShiftTypes.DAY;
            converted = true;
            break;
          } else if (this.countDayStaff(schedule, d, [ShiftTypes.LATE]) === 0) {
            if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.LATE)) {
              schedule[name][d] = ShiftTypes.LATE;
              converted = true;
              break;
            }
          }

          schedule[name][d] = ShiftTypes.EARLY;
        }

        if (!converted) {
          schedule[earlyStaff[0].name][d] = ShiftTypes.DAY;
        }
      }

      // 遅番の重複解消
      while (this.countDayStaff(schedule, d, [ShiftTypes.LATE]) > 1) {
        const lateStaff = this.staffDictList.filter(
          s => schedule[s.name][d] === ShiftTypes.LATE &&
               s.type === 0 &&
               !fixedDays[s.name].has(d)
        );

        if (lateStaff.length === 0) break;

        let converted = false;
        for (const s of lateStaff) {
          const name = s.name;
          schedule[name][d] = "";

          if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.DAY)) {
            schedule[name][d] = ShiftTypes.DAY;
            converted = true;
            break;
          } else if (this.countDayStaff(schedule, d, [ShiftTypes.EARLY]) === 0) {
            if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.EARLY)) {
              schedule[name][d] = ShiftTypes.EARLY;
              converted = true;
              break;
            }
          }

          schedule[name][d] = ShiftTypes.LATE;
        }

        if (!converted) {
          schedule[lateStaff[0].name][d] = ShiftTypes.DAY;
        }
      }
    }
  }

  // 最終クリーンアップ
  private phaseFinalCleanup(schedule: Schedule): void {
    for (const s of this.staffDictList) {
      const name = s.name;
      for (let d = 0; d < this.days; d++) {
        if (schedule[name][d] === "") {
          if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.DAY)) {
            schedule[name][d] = ShiftTypes.DAY;
          } else if (this.ruleChecker.checkRules(name, d, schedule, ShiftTypes.OFF)) {
            schedule[name][d] = ShiftTypes.OFF;
          } else {
            schedule[name][d] = ShiftTypes.DAY;
          }
        }
      }
    }
  }

  // スコア計算
  private calcScore(schedule: Schedule): number {
    let score = 0;

    // 公休数ペナルティ
    for (const s of this.staffDictList) {
      if (s.type === 0) {
        const cnt = schedule[s.name].filter(x => x.trim() === ShiftTypes.OFF).length;
        score -= Math.abs(cnt - this.targetOffDays) * SolverConfig.PENALTY_OFF_DAYS;
      }
    }

    // 夜勤目標ペナルティ
    for (const s of this.staffDictList) {
      if (s.night_target > 0) {
        const cnt = schedule[s.name].filter(x => x === ShiftTypes.NIGHT).length;
        score -= Math.abs(cnt - s.night_target) * SolverConfig.PENALTY_NIGHT_TARGET;
      }
    }

    // 欠員ペナルティ
    for (let d = 0; d < this.days; d++) {
      if (this.countDayStaff(schedule, d, [ShiftTypes.EARLY]) === 0) {
        score -= SolverConfig.PENALTY_EARLY_MISSING;
      }
      if (this.countDayStaff(schedule, d, [ShiftTypes.LATE]) === 0) {
        score -= SolverConfig.PENALTY_LATE_MISSING;
      }
      if (this.countDayStaff(schedule, d, [ShiftTypes.NIGHT]) === 0) {
        score -= SolverConfig.PENALTY_NIGHT_MISSING;
      }
      if (this.countDayStaff(schedule, d, ShiftTypes.DAY_SHIFTS) < SolverConfig.MIN_DAY_STAFF) {
        score -= SolverConfig.PENALTY_DAY_SHORTAGE;
      }
    }

    // 重複ペナルティ
    for (let d = 0; d < this.days; d++) {
      if (this.countDayStaff(schedule, d, [ShiftTypes.EARLY]) > 1) {
        score -= SolverConfig.PENALTY_DUPLICATE;
      }
      if (this.countDayStaff(schedule, d, [ShiftTypes.LATE]) > 1) {
        score -= SolverConfig.PENALTY_DUPLICATE;
      }
    }

    // 平準化ペナルティ
    const dailyCounts = this.getDailyCounts(schedule);
    const variance = this.calcVariance(dailyCounts);
    score -= Math.floor(variance * SolverConfig.PENALTY_VARIANCE);

    if (dailyCounts.length > 0) {
      const maxCnt = Math.max(...dailyCounts);
      const minCnt = Math.min(...dailyCounts);
      if (maxCnt - minCnt >= 3) {
        score -= (maxCnt - minCnt) * SolverConfig.PENALTY_RANGE;
      }
    }

    return score;
  }

  // エラー収集
  private collectErrors(schedule: Schedule): string[] {
    const errors: string[] = [];

    for (let d = 0; d < this.days; d++) {
      const earlyCnt = this.countDayStaff(schedule, d, [ShiftTypes.EARLY]);
      const lateCnt = this.countDayStaff(schedule, d, [ShiftTypes.LATE]);

      if (earlyCnt === 0) {
        errors.push(`${d + 1}日: 早番を配置できませんでした`);
      } else if (earlyCnt > 1) {
        errors.push(`${d + 1}日: 早番が${earlyCnt}名います（1名が原則）`);
      }

      if (lateCnt === 0) {
        errors.push(`${d + 1}日: 遅番を配置できませんでした`);
      } else if (lateCnt > 1) {
        errors.push(`${d + 1}日: 遅番が${lateCnt}名います（1名が原則）`);
      }

      const hasNight = this.staffDictList.some(
        s => schedule[s.name][d] === ShiftTypes.NIGHT
      );
      if (!hasNight) {
        errors.push(`${d + 1}日: 夜勤を配置できませんでした`);
      }
    }

    // 空スロットチェック
    for (const s of this.staffDictList) {
      const emptyDays = Array.from({ length: this.days }, (_, i) => i)
        .filter(d => schedule[s.name][d] === "")
        .map(d => d + 1);
      if (emptyDays.length > 0) {
        errors.push(`${s.name}: ${emptyDays.join(',')}日が未配置です`);
      }
    }

    return errors;
  }

  // メイン処理
  solve(): { schedule: Schedule; errors: string[] } {
    let bestSchedule: Schedule | null = null;
    let bestScore = -999999;

    for (let attempt = 0; attempt < this.maxAttempts; attempt++) {
      const schedule: Schedule = {};
      const nightCounts: NightCounts = {};
      const fixedDays: FixedDays = {};

      for (const s of this.staffDictList) {
        schedule[s.name] = Array(this.days).fill("");
        nightCounts[s.name] = 0;
        fixedDays[s.name] = new Set();
      }

      // 各フェーズを実行
      this.phase0PrevMonth(schedule, fixedDays);
      this.phase1FixedAndRequests(schedule, fixedDays, nightCounts);
      this.phase2NightRequests(schedule, fixedDays, nightCounts);
      this.phase3DailyNight(schedule, nightCounts);
      this.phase4EarlyLate(schedule);
      this.phase5FillDay(schedule);
      this.phase6FillOff(schedule);
      this.phase6bFillRemaining(schedule);
      this.phase7Balance(schedule, fixedDays);
      this.phase8Adjust(schedule, fixedDays);
      this.phase9ReduceDuplicates(schedule, fixedDays);
      this.phaseFinalCleanup(schedule);

      // スコア計算
      const score = this.calcScore(schedule);

      if (score > bestScore) {
        bestScore = score;
        bestSchedule = JSON.parse(JSON.stringify(schedule));
      }

      // 早期終了
      if (score > SolverConfig.EARLY_EXIT_SCORE) {
        let canExit = true;
        for (let d = 0; d < this.days; d++) {
          if (this.countDayStaff(schedule, d, [ShiftTypes.EARLY]) === 0 ||
              this.countDayStaff(schedule, d, [ShiftTypes.LATE]) === 0 ||
              this.countDayStaff(schedule, d, [ShiftTypes.NIGHT]) === 0 ||
              this.countDayStaff(schedule, d, ShiftTypes.DAY_SHIFTS) < SolverConfig.MIN_DAY_STAFF) {
            canExit = false;
            break;
          }
        }
        if (canExit) break;
      }
    }

    const errors = bestSchedule ? this.collectErrors(bestSchedule) : [];
    return { schedule: bestSchedule || {}, errors };
  }
}

