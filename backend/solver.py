"""
Shift Solver - シフト表自動生成ロジック
Version: 2.1.0

主要機能:
- 多段階フェーズによるシフト配置
- ルール準拠チェック
- スコアリングによる最適解探索
- 平準化とバランス調整
"""
import random
import calendar
import copy
from typing import List, Dict, Tuple, Set

from .models import StaffData, ShiftTypes
from .rules import ShiftRuleChecker


# =============================================================================
# 定数定義
# =============================================================================

class SolverConfig:
    """ソルバー設定値"""
    # スコアペナルティ
    PENALTY_OFF_DAYS = 100       # 公休数の差異ペナルティ（1日あたり）
    PENALTY_NIGHT_TARGET = 50   # 夜勤目標差異ペナルティ（1回あたり）
    PENALTY_EARLY_MISSING = 300  # 早番欠員ペナルティ
    PENALTY_LATE_MISSING = 300   # 遅番欠員ペナルティ
    PENALTY_NIGHT_MISSING = 500  # 夜勤欠員ペナルティ
    PENALTY_DAY_SHORTAGE = 100   # 日勤帯不足ペナルティ
    PENALTY_DUPLICATE = 500      # 早番・遅番重複ペナルティ
    PENALTY_VARIANCE = 30        # 人員バラつきペナルティ係数
    PENALTY_RANGE = 50           # 人員差ペナルティ（差が3以上の場合）
    
    # 最低人員数
    MIN_DAY_STAFF = 3            # 日勤帯最低人員
    MAX_CONSECUTIVE_WORK = 5     # 最大連勤日数
    
    # 平準化調整
    BALANCE_ITERATIONS = 30      # 平準化調整の最大反復回数
    ADJUST_ITERATIONS = 20       # 人員調整の最大反復回数
    
    # 早期終了スコア閾値
    EARLY_EXIT_SCORE = -100


# =============================================================================
# メインソルバークラス
# =============================================================================

class ShiftSolver:
    """
    シフト表を自動生成するソルバー
    
    処理フロー:
    1. Phase 0: 前月末シフト処理
    2. Phase 1: 固定シフト・希望休・希望シフト設定
    3. Phase 2: 夜勤希望の配置
    4. Phase 3: 毎日の夜勤配置
    5. Phase 4: 早番・遅番の配置
    6. Phase 5: 日勤で埋める
    7. Phase 6: 公休の最適配置
    8. Phase 6b: 残スロット処理
    9. Phase 7: 人員平準化
    10. Phase 8: 人員調整（不足解消）
    11. Phase 9: 早番・遅番重複解消
    12. Final: 最終クリーンアップ
    """
    
    def __init__(self, staff_data: List[StaffData], year: int, month: int, 
                 target_off_days: int, max_attempts: int = 2500):
        """
        Args:
            staff_data: スタッフデータリスト
            year: 年
            month: 月
            target_off_days: 常勤スタッフの目標公休日数
            max_attempts: 最大試行回数
        """
        self.year = year
        self.month = month
        self.target_off_days = target_off_days
        self.max_attempts = max_attempts
        
        _, self.days = calendar.monthrange(year, month)
        self.staff_dict_list = [s.dict() for s in staff_data]
        self.regulars = [s for s in self.staff_dict_list if s["type"] == 0]
        
        self.work_limits = self._calc_work_limits()
        self.rule_checker = ShiftRuleChecker(self.staff_dict_list, self.days)
    
    # =========================================================================
    # ユーティリティメソッド
    # =========================================================================
    
    def _calc_work_limits(self) -> Dict[str, int]:
        """各スタッフの勤務日数上限を計算"""
        limits = {}
        for s in self.staff_dict_list:
            if s["type"] != 0:
                limits[s["name"]] = 99  # パートは制限なし
            else:
                extra_off = len(s["refresh_days"]) + len(s["paid_leave_days"])
                limits[s["name"]] = self.days - (self.target_off_days + extra_off)
        return limits
    
    def _count_day_staff(self, schedule: Dict, day_idx: int, shift_types: List[str]) -> int:
        """特定の日の特定シフトの人数をカウント"""
        return sum(1 for s in self.staff_dict_list 
                   if schedule[s["name"]][day_idx].strip() in shift_types)
    
    def _count_required_off(self, day_idx: int, schedule: Dict) -> int:
        """その日の希望休・有休・リ休の数"""
        cnt = 0
        for s in self.staff_dict_list:
            val = schedule[s["name"]][day_idx]
            if val == ShiftTypes.HOPE_OFF or val.strip() in [ShiftTypes.PAID, ShiftTypes.REFRESH]:
                cnt += 1
        return cnt
    
    def _get_daily_counts(self, schedule: Dict) -> List[int]:
        """各日の日勤帯人員数を取得"""
        return [self._count_day_staff(schedule, d, ShiftTypes.DAY_SHIFTS) 
                for d in range(self.days)]
    
    def _calc_variance(self, counts: List[int]) -> float:
        """人員数の分散を計算"""
        if not counts:
            return 0
        avg = sum(counts) / len(counts)
        return sum((c - avg) ** 2 for c in counts) / len(counts)
    
    def _count_current_off(self, name: str, schedule: Dict) -> int:
        """現在の公休数をカウント（希望休含む）"""
        return sum(1 for x in schedule[name] if x.strip() == ShiftTypes.OFF)
    
    def _place_night_shift(self, name: str, day_idx: int, schedule: Dict, 
                           night_counts: Dict[str, int]) -> None:
        """夜勤とそれに伴う明け・公休を配置"""
        schedule[name][day_idx] = ShiftTypes.NIGHT
        night_counts[name] += 1
        
        # 明けの配置
        if day_idx + 1 < self.days:
            if schedule[name][day_idx + 1] != ShiftTypes.HOPE_OFF:
                schedule[name][day_idx + 1] = ShiftTypes.NIGHT_REST
        
        # 公休の配置（空の場合のみ）
        if day_idx + 2 < self.days and schedule[name][day_idx + 2] == "":
            schedule[name][day_idx + 2] = ShiftTypes.OFF
    
    def _try_convert_to_shift(self, name: str, day_idx: int, schedule: Dict,
                               target_shift: str, fallback_shifts: List[str] = None) -> bool:
        """
        シフトを変換を試みる
        
        Returns:
            変換成功したかどうか
        """
        original = schedule[name][day_idx]
        schedule[name][day_idx] = ""
        
        # メインのシフトを試す
        if self.rule_checker.check_rules(name, day_idx, schedule, target_shift):
            schedule[name][day_idx] = target_shift
            return True
        
        # フォールバックシフトを試す
        if fallback_shifts:
            for shift in fallback_shifts:
                if self.rule_checker.check_rules(name, day_idx, schedule, shift):
                    schedule[name][day_idx] = shift
                    return True
        
        # 失敗時は元に戻す
        schedule[name][day_idx] = original
        return False
    
    # =========================================================================
    # Phase 0: 前月末シフト処理
    # =========================================================================
    
    def _phase0_prev_month(self, schedule: Dict, fixed_days: Dict[str, Set[int]]) -> None:
        """前月末シフトに基づく1日目の強制設定"""
        for s in self.staff_dict_list:
            name = s["name"]
            prev = s["prev_shift"].strip()
            
            if prev == ShiftTypes.NIGHT_REST:
                # 前月末が明けなら1日目は公休
                schedule[name][0] = ShiftTypes.OFF
                fixed_days[name].add(0)
            elif prev == ShiftTypes.NIGHT:
                # 前月末が夜勤なら1日目は明け、2日目は公休
                schedule[name][0] = ShiftTypes.NIGHT_REST
                fixed_days[name].add(0)
                if self.days > 1:
                    schedule[name][1] = ShiftTypes.OFF
                    fixed_days[name].add(1)
    
    # =========================================================================
    # Phase 1: 固定シフトと希望の設定
    # =========================================================================
    
    def _phase1_fixed_and_requests(self, schedule: Dict, fixed_days: Dict[str, Set[int]], 
                                    night_counts: Dict[str, int]) -> None:
        """固定シフトと希望の設定"""
        for s in self.staff_dict_list:
            name = s["name"]
            
            # 年始固定シフト（1-3日）
            self._set_fixed_shifts(s, schedule, fixed_days, night_counts)
            
            # 休暇設定
            self._set_vacation_requests(s, schedule, fixed_days)
            
            # 希望シフト
            self._set_shift_requests(s, schedule, fixed_days)
            
            # パート設定
            self._set_part_time_shifts(s, schedule)
    
    def _set_fixed_shifts(self, staff: Dict, schedule: Dict, 
                          fixed_days: Dict[str, Set[int]], night_counts: Dict[str, int]) -> None:
        """年始固定シフトを設定"""
        name = staff["name"]
        for i in range(min(3, self.days)):
            if i in fixed_days[name]:
                continue
            if len(staff["fixed_shifts"]) > i and staff["fixed_shifts"][i]:
                fs = staff["fixed_shifts"][i]
                schedule[name][i] = fs
                fixed_days[name].add(i)
                
                if fs == ShiftTypes.NIGHT:
                    night_counts[name] += 1
                    if i + 1 < self.days and schedule[name][i+1] == "":
                        schedule[name][i+1] = ShiftTypes.NIGHT_REST
                        fixed_days[name].add(i+1)
                    if i + 2 < self.days:
                        if schedule[name][i+2] == "":
                            schedule[name][i+2] = ShiftTypes.OFF
                            fixed_days[name].add(i+2)
                        elif schedule[name][i+2] == ShiftTypes.HOPE_OFF:
                            fixed_days[name].add(i+2)
    
    def _set_vacation_requests(self, staff: Dict, schedule: Dict, 
                                fixed_days: Dict[str, Set[int]]) -> None:
        """休暇リクエストを設定"""
        name = staff["name"]
        
        # 希望休
        for d in staff["req_off"]:
            if 0 < d <= self.days and schedule[name][d-1] == "":
                schedule[name][d-1] = ShiftTypes.HOPE_OFF
                fixed_days[name].add(d-1)
        
        # リフレッシュ休暇
        for d in staff["refresh_days"]:
            if 0 < d <= self.days and schedule[name][d-1] == "":
                schedule[name][d-1] = ShiftTypes.REFRESH
                fixed_days[name].add(d-1)
        
        # 有給休暇
        for d in staff["paid_leave_days"]:
            if 0 < d <= self.days and schedule[name][d-1] == "":
                schedule[name][d-1] = ShiftTypes.PAID
                fixed_days[name].add(d-1)
    
    def _set_shift_requests(self, staff: Dict, schedule: Dict, 
                            fixed_days: Dict[str, Set[int]]) -> None:
        """シフト希望を設定"""
        name = staff["name"]
        
        request_types = [
            ("req_early", ShiftTypes.EARLY),
            ("req_late", ShiftTypes.LATE),
            ("req_day", ShiftTypes.DAY),
        ]
        
        for req_key, shift_type in request_types:
            for d in staff[req_key]:
                if 0 < d <= self.days and schedule[name][d-1] == "":
                    if self.rule_checker.check_rules(name, d-1, schedule, shift_type):
                        schedule[name][d-1] = shift_type
                        fixed_days[name].add(d-1)
    
    def _set_part_time_shifts(self, staff: Dict, schedule: Dict) -> None:
        """パートスタッフのシフトを設定"""
        name = staff["name"]
        
        if staff["type"] == 1:  # 日勤パート
            for d in range(self.days):
                if schedule[name][d] == "":
                    schedule[name][d] = ShiftTypes.DAY
                    
        elif staff["type"] == 2:  # 早番パート
            for d in range(self.days):
                if schedule[name][d] == "":
                    # 早番が不足している日のみ早番、それ以外は日勤
                    if self._count_day_staff(schedule, d, [ShiftTypes.EARLY]) == 0:
                        schedule[name][d] = ShiftTypes.EARLY
                    else:
                        schedule[name][d] = ShiftTypes.DAY
    
    # =========================================================================
    # Phase 2: 夜勤希望の配置
    # =========================================================================
    
    def _phase2_night_requests(self, schedule: Dict, fixed_days: Dict[str, Set[int]], 
                                night_counts: Dict[str, int]) -> None:
        """夜勤希望の配置"""
        for s in self.staff_dict_list:
            name = s["name"]
            if "req_night" not in s or s["type"] != 0:
                continue
                
            for d_idx in s["req_night"]:
                d = d_idx - 1
                if 0 <= d < self.days and d not in fixed_days[name]:
                    if self.rule_checker.can_place_night(name, d, schedule):
                        self._place_night_with_fixed(name, d, schedule, fixed_days, night_counts)
    
    def _place_night_with_fixed(self, name: str, day_idx: int, schedule: Dict,
                                 fixed_days: Dict[str, Set[int]], 
                                 night_counts: Dict[str, int]) -> None:
        """夜勤を配置し、関連日をfixed_daysに追加"""
        schedule[name][day_idx] = ShiftTypes.NIGHT
        night_counts[name] += 1
        fixed_days[name].add(day_idx)
        
        if day_idx + 1 < self.days and (day_idx + 1) not in fixed_days[name]:
            if schedule[name][day_idx + 1] != ShiftTypes.HOPE_OFF:
                schedule[name][day_idx + 1] = ShiftTypes.NIGHT_REST
            fixed_days[name].add(day_idx + 1)
        
        if day_idx + 2 < self.days and (day_idx + 2) not in fixed_days[name]:
            if schedule[name][day_idx + 2] == "":
                schedule[name][day_idx + 2] = ShiftTypes.OFF
                fixed_days[name].add(day_idx + 2)
            elif schedule[name][day_idx + 2] == ShiftTypes.HOPE_OFF:
                fixed_days[name].add(day_idx + 2)
    
    # =========================================================================
    # Phase 3: 毎日の夜勤配置
    # =========================================================================
    
    def _phase3_daily_night(self, schedule: Dict, night_counts: Dict[str, int]) -> None:
        """毎日の夜勤配置（希望休に合わせて最適化）"""
        # 希望休の2日前に夜勤を優先配置
        self._align_nights_with_off_days(schedule, night_counts)
        
        # 残りの日に夜勤配置
        self._fill_remaining_nights(schedule, night_counts)
    
    def _align_nights_with_off_days(self, schedule: Dict, night_counts: Dict[str, int]) -> None:
        """希望休に合わせて夜勤を配置"""
        for s in self.regulars:
            name = s["name"]
            if night_counts[name] >= s["night_target"]:
                continue
            
            off_days = set(s["req_off"] + s["refresh_days"] + s["paid_leave_days"])
            
            for off_day in sorted(off_days):
                night_day = off_day - 3  # 希望休の2日前（0-indexed）
                if night_day < 0 or night_day >= self.days:
                    continue
                
                if self._count_day_staff(schedule, night_day, [ShiftTypes.NIGHT]) > 0:
                    continue
                
                if self.rule_checker.can_place_night(name, night_day, schedule):
                    self._place_night_shift(name, night_day, schedule, night_counts)
                    
                    if night_counts[name] >= s["night_target"]:
                        break
    
    def _fill_remaining_nights(self, schedule: Dict, night_counts: Dict[str, int]) -> None:
        """残りの日に夜勤を配置"""
        days_order = list(range(self.days))
        random.shuffle(days_order)
        
        for d in days_order:
            if self._count_day_staff(schedule, d, [ShiftTypes.NIGHT]) > 0:
                continue
            
            candidates = self._get_night_candidates(d, schedule, night_counts)
            
            if candidates:
                chosen = self._select_best_candidate(candidates)
                self._place_night_shift(chosen["name"], d, schedule, night_counts)
    
    def _get_night_candidates(self, day_idx: int, schedule: Dict, 
                               night_counts: Dict[str, int]) -> List[Tuple[Dict, int]]:
        """夜勤配置可能な候補者とその優先度を取得"""
        candidates = []
        for s in self.regulars:
            name = s["name"]
            if self.rule_checker.can_place_night(name, day_idx, schedule):
                priority = s["night_target"] - night_counts[name]
                candidates.append((s, priority))
        return candidates
    
    def _select_best_candidate(self, candidates: List[Tuple[Dict, int]]) -> Dict:
        """最も優先度の高い候補者を選択"""
        candidates.sort(key=lambda x: -x[1])
        top_priority = candidates[0][1]
        top_cands = [c for c in candidates if c[1] == top_priority]
        random.shuffle(top_cands)
        return top_cands[0][0]
    
    # =========================================================================
    # Phase 4: 早番・遅番の配置
    # =========================================================================
    
    def _phase4_early_late(self, schedule: Dict) -> None:
        """早番・遅番の配置（毎日各1名）"""
        for d in range(self.days):
            self._place_late_shift(d, schedule)
            self._place_early_shift(d, schedule)
    
    def _place_late_shift(self, day_idx: int, schedule: Dict) -> None:
        """遅番を配置"""
        if self._count_day_staff(schedule, day_idx, [ShiftTypes.LATE]) > 0:
            return
            
        candidates = [s for s in self.regulars 
                      if schedule[s["name"]][day_idx] == "" 
                      and self.rule_checker.check_rules(s["name"], day_idx, schedule, ShiftTypes.LATE)]
        
        if candidates:
            random.shuffle(candidates)
            schedule[candidates[0]["name"]][day_idx] = ShiftTypes.LATE
    
    def _place_early_shift(self, day_idx: int, schedule: Dict) -> None:
        """早番を配置"""
        if self._count_day_staff(schedule, day_idx, [ShiftTypes.EARLY]) > 0:
            return
            
        candidates = [s for s in self.regulars 
                      if schedule[s["name"]][day_idx] == "" 
                      and self.rule_checker.check_rules(s["name"], day_idx, schedule, ShiftTypes.EARLY)]
        
        # 早番パートも候補に追加
        for s in self.staff_dict_list:
            if s["type"] == 2 and schedule[s["name"]][day_idx] == "":
                candidates.append(s)
        
        if candidates:
            random.shuffle(candidates)
            schedule[candidates[0]["name"]][day_idx] = ShiftTypes.EARLY
    
    # =========================================================================
    # Phase 5-6: 日勤・公休の配置
    # =========================================================================
    
    def _phase5_fill_day(self, schedule: Dict) -> None:
        """日勤で埋める（平準化を考慮）"""
        for s in self.regulars:
            name = s["name"]
            empty_days = [d for d in range(self.days) if schedule[name][d] == ""]
            empty_days.sort(key=lambda d: self._count_day_staff(schedule, d, ShiftTypes.DAY_SHIFTS))
            
            for d in empty_days:
                curr_work = sum(1 for x in schedule[name] if self.rule_checker.is_work_shift(x))
                if curr_work >= self.work_limits[name]:
                    break
                if self.rule_checker.check_rules(name, d, schedule, ShiftTypes.DAY):
                    schedule[name][d] = ShiftTypes.DAY
    
    def _phase6_fill_off(self, schedule: Dict) -> None:
        """公休の最適配置（目標数を超えないように）"""
        for s in self.regulars:
            name = s["name"]
            
            current_off = self._count_current_off(name, schedule)
            if current_off >= self.target_off_days:
                continue
            
            empty_days = [d for d in range(self.days) if schedule[name][d] == ""]
            if not empty_days:
                continue
            
            needed_off = self.target_off_days - current_off
            day_scores = self._calc_off_day_scores(name, empty_days, schedule)
            
            placed_count = 0
            for d, _ in day_scores:
                if placed_count >= needed_off:
                    break
                if self.rule_checker.check_rules(name, d, schedule, ShiftTypes.OFF):
                    schedule[name][d] = ShiftTypes.OFF
                    placed_count += 1
    
    def _calc_off_day_scores(self, name: str, empty_days: List[int], 
                              schedule: Dict) -> List[Tuple[int, int]]:
        """公休配置の優先度スコアを計算"""
        day_scores = []
        for d in empty_days:
            day_cnt = self._count_day_staff(schedule, d, ShiftTypes.DAY_SHIFTS)
            fixed_off = self._count_required_off(d, schedule)
            others_empty = sum(1 for s2 in self.regulars 
                               if s2["name"] != name and schedule[s2["name"]][d] == "")
            score = day_cnt + others_empty - fixed_off
            day_scores.append((d, score))
        
        day_scores.sort(key=lambda x: -x[1])
        return day_scores
    
    def _phase6b_fill_remaining_with_day(self, schedule: Dict) -> None:
        """残りの空スロットを日勤または公休で埋める"""
        for s in self.regulars:
            name = s["name"]
            empty_days = [d for d in range(self.days) if schedule[name][d] == ""]
            empty_days.sort(key=lambda d: self._count_day_staff(schedule, d, ShiftTypes.DAY_SHIFTS))
            
            for d in empty_days:
                self._fill_empty_slot(name, d, schedule)
    
    def _fill_empty_slot(self, name: str, day_idx: int, schedule: Dict) -> None:
        """空スロットを埋める（日勤→早番→遅番→公休の順）"""
        shift_order = [ShiftTypes.DAY, ShiftTypes.EARLY, ShiftTypes.LATE, ShiftTypes.OFF]
        
        for shift in shift_order:
            if self.rule_checker.check_rules(name, day_idx, schedule, shift):
                schedule[name][day_idx] = shift
                return
    
    # =========================================================================
    # Phase 7-9: 調整フェーズ
    # =========================================================================
    
    def _phase7_balance(self, schedule: Dict, fixed_days: Dict[str, Set[int]]) -> None:
        """人員平準化調整"""
        for _ in range(SolverConfig.BALANCE_ITERATIONS):
            daily_counts = self._get_daily_counts(schedule)
            if not daily_counts:
                break
            
            max_day = max(range(self.days), key=lambda d: daily_counts[d])
            min_day = min(range(self.days), key=lambda d: daily_counts[d])
            
            if daily_counts[max_day] - daily_counts[min_day] < 2:
                break
            
            if not self._try_swap_shifts(schedule, fixed_days, max_day, min_day):
                break
    
    def _try_swap_shifts(self, schedule: Dict, fixed_days: Dict[str, Set[int]],
                          max_day: int, min_day: int) -> bool:
        """日勤と公休をスワップして平準化を試みる"""
        for s in self.regulars:
            name = s["name"]
            if max_day in fixed_days[name] or min_day in fixed_days[name]:
                continue
            
            if schedule[name][max_day] == ShiftTypes.DAY and schedule[name][min_day] == ShiftTypes.OFF:
                schedule[name][max_day] = ""
                schedule[name][min_day] = ""
                
                if (self.rule_checker.check_rules(name, max_day, schedule, ShiftTypes.OFF) and 
                    self.rule_checker.check_rules(name, min_day, schedule, ShiftTypes.DAY)):
                    schedule[name][max_day] = ShiftTypes.OFF
                    schedule[name][min_day] = ShiftTypes.DAY
                    return True
                else:
                    schedule[name][max_day] = ShiftTypes.DAY
                    schedule[name][min_day] = ShiftTypes.OFF
        
        return False
    
    def _phase8_adjust(self, schedule: Dict, fixed_days: Dict[str, Set[int]]) -> None:
        """人員調整（不足解消）"""
        for _ in range(SolverConfig.ADJUST_ITERATIONS):
            if not self._adjust_shortages(schedule, fixed_days):
                break
    
    def _adjust_shortages(self, schedule: Dict, fixed_days: Dict[str, Set[int]]) -> bool:
        """不足を解消する調整を1回行う"""
        for d in range(self.days):
            early_cnt = self._count_day_staff(schedule, d, [ShiftTypes.EARLY])
            late_cnt = self._count_day_staff(schedule, d, [ShiftTypes.LATE])
            day_total = self._count_day_staff(schedule, d, ShiftTypes.DAY_SHIFTS)
            
            # 早番不足
            if early_cnt == 0:
                if self._convert_day_to_shift(schedule, fixed_days, d, ShiftTypes.EARLY):
                    return True
            
            # 遅番不足
            if late_cnt == 0:
                if self._convert_day_to_shift(schedule, fixed_days, d, ShiftTypes.LATE):
                    return True
            
            # 日勤帯不足
            if day_total < SolverConfig.MIN_DAY_STAFF:
                if self._convert_off_to_day(schedule, fixed_days, d):
                    return True
        
        return False
    
    def _convert_day_to_shift(self, schedule: Dict, fixed_days: Dict[str, Set[int]],
                               day_idx: int, target_shift: str) -> bool:
        """日勤を指定シフトに変換"""
        for s in self.regulars:
            name = s["name"]
            if day_idx in fixed_days[name]:
                continue
            if schedule[name][day_idx] == ShiftTypes.DAY:
                if self._try_convert_to_shift(name, day_idx, schedule, target_shift):
                    return True
        return False
    
    def _convert_off_to_day(self, schedule: Dict, fixed_days: Dict[str, Set[int]],
                            day_idx: int) -> bool:
        """公休を日勤に変換"""
        for s in self.regulars:
            name = s["name"]
            if day_idx in fixed_days[name]:
                continue
            if schedule[name][day_idx] == ShiftTypes.OFF:
                # 他に人員が余っている日があるか確認
                other_days = [od for od in range(self.days) 
                              if od != day_idx 
                              and schedule[name][od] == ShiftTypes.OFF 
                              and od not in fixed_days[name]
                              and self._count_day_staff(schedule, od, ShiftTypes.DAY_SHIFTS) >= 4]
                
                if other_days and self._try_convert_to_shift(name, day_idx, schedule, ShiftTypes.DAY):
                    return True
        return False
    
    def _phase9_reduce_duplicates(self, schedule: Dict, fixed_days: Dict[str, Set[int]]) -> None:
        """早番・遅番過多の調整（厳守：各日1名ずつ）"""
        for d in range(self.days):
            self._reduce_shift_duplicates(schedule, fixed_days, d, ShiftTypes.EARLY, ShiftTypes.LATE)
            self._reduce_shift_duplicates(schedule, fixed_days, d, ShiftTypes.LATE, ShiftTypes.EARLY)
    
    def _reduce_shift_duplicates(self, schedule: Dict, fixed_days: Dict[str, Set[int]],
                                  day_idx: int, target_shift: str, alt_shift: str) -> None:
        """特定シフトの重複を解消"""
        while self._count_day_staff(schedule, day_idx, [target_shift]) > 1:
            staff_list = [s for s in self.staff_dict_list 
                          if schedule[s["name"]][day_idx] == target_shift 
                          and s["type"] == 0
                          and day_idx not in fixed_days[s["name"]]]
            
            if not staff_list:
                break
            
            converted = False
            for s in staff_list:
                name = s["name"]
                schedule[name][day_idx] = ""
                
                # 日勤を試す
                if self.rule_checker.check_rules(name, day_idx, schedule, ShiftTypes.DAY):
                    schedule[name][day_idx] = ShiftTypes.DAY
                    converted = True
                    break
                # 代替シフトを試す（不足している場合のみ）
                elif self._count_day_staff(schedule, day_idx, [alt_shift]) == 0:
                    if self.rule_checker.check_rules(name, day_idx, schedule, alt_shift):
                        schedule[name][day_idx] = alt_shift
                        converted = True
                        break
                
                schedule[name][day_idx] = target_shift
            
            if not converted:
                # 最後の手段：ルールを無視して日勤に変更
                for s in staff_list:
                    schedule[s["name"]][day_idx] = ShiftTypes.DAY
                    break
    
    # =========================================================================
    # 最終処理
    # =========================================================================
    
    def _phase_final_cleanup(self, schedule: Dict) -> None:
        """最終クリーンアップ: 空スロットを埋める"""
        for s in self.staff_dict_list:
            name = s["name"]
            for d in range(self.days):
                if schedule[name][d] == "":
                    if self.rule_checker.check_rules(name, d, schedule, ShiftTypes.DAY):
                        schedule[name][d] = ShiftTypes.DAY
                    elif self.rule_checker.check_rules(name, d, schedule, ShiftTypes.OFF):
                        schedule[name][d] = ShiftTypes.OFF
                    else:
                        schedule[name][d] = ShiftTypes.DAY  # 強制配置
    
    # =========================================================================
    # スコアリング・エラー収集
    # =========================================================================
    
    def _calc_score(self, schedule: Dict) -> int:
        """スケジュールのスコアを計算"""
        score = 0
        
        # 公休数ペナルティ
        for s in self.staff_dict_list:
            if s["type"] == 0:
                cnt = sum(1 for x in schedule[s["name"]] if x.strip() == ShiftTypes.OFF)
                score -= abs(cnt - self.target_off_days) * SolverConfig.PENALTY_OFF_DAYS
        
        # 夜勤目標ペナルティ
        for s in self.staff_dict_list:
            if s["night_target"] > 0:
                cnt = schedule[s["name"]].count(ShiftTypes.NIGHT)
                score -= abs(cnt - s["night_target"]) * SolverConfig.PENALTY_NIGHT_TARGET
        
        # 欠員ペナルティ
        score -= self._calc_missing_penalty(schedule)
        
        # 重複ペナルティ
        score -= self._calc_duplicate_penalty(schedule)
        
        # 平準化ペナルティ
        score -= self._calc_variance_penalty(schedule)
        
        return score
    
    def _calc_missing_penalty(self, schedule: Dict) -> int:
        """欠員ペナルティを計算"""
        penalty = 0
        
        early_missing = sum(1 for d in range(self.days) 
                            if self._count_day_staff(schedule, d, [ShiftTypes.EARLY]) == 0)
        late_missing = sum(1 for d in range(self.days) 
                           if self._count_day_staff(schedule, d, [ShiftTypes.LATE]) == 0)
        night_missing = sum(1 for d in range(self.days) 
                            if self._count_day_staff(schedule, d, [ShiftTypes.NIGHT]) == 0)
        day_shortage = sum(1 for d in range(self.days) 
                           if self._count_day_staff(schedule, d, ShiftTypes.DAY_SHIFTS) < SolverConfig.MIN_DAY_STAFF)
        
        penalty += early_missing * SolverConfig.PENALTY_EARLY_MISSING
        penalty += late_missing * SolverConfig.PENALTY_LATE_MISSING
        penalty += night_missing * SolverConfig.PENALTY_NIGHT_MISSING
        penalty += day_shortage * SolverConfig.PENALTY_DAY_SHORTAGE
        
        return penalty
    
    def _calc_duplicate_penalty(self, schedule: Dict) -> int:
        """重複ペナルティを計算"""
        early_duplicate = sum(1 for d in range(self.days) 
                              if self._count_day_staff(schedule, d, [ShiftTypes.EARLY]) > 1)
        late_duplicate = sum(1 for d in range(self.days) 
                             if self._count_day_staff(schedule, d, [ShiftTypes.LATE]) > 1)
        
        return (early_duplicate + late_duplicate) * SolverConfig.PENALTY_DUPLICATE
    
    def _calc_variance_penalty(self, schedule: Dict) -> int:
        """平準化ペナルティを計算"""
        daily_counts = self._get_daily_counts(schedule)
        variance = self._calc_variance(daily_counts)
        penalty = int(variance * SolverConfig.PENALTY_VARIANCE)
        
        if daily_counts:
            max_cnt = max(daily_counts)
            min_cnt = min(daily_counts)
            if max_cnt - min_cnt >= 3:
                penalty += (max_cnt - min_cnt) * SolverConfig.PENALTY_RANGE
        
        return penalty
    
    def _collect_errors(self, schedule: Dict) -> List[str]:
        """エラーを収集"""
        errors = []
        
        # シフト配置エラー
        for d in range(self.days):
            early_cnt = self._count_day_staff(schedule, d, [ShiftTypes.EARLY])
            late_cnt = self._count_day_staff(schedule, d, [ShiftTypes.LATE])
            
            if early_cnt == 0:
                errors.append(f"{d+1}日: 早番を配置できませんでした")
            elif early_cnt > 1:
                errors.append(f"{d+1}日: 早番が{early_cnt}名います（1名が原則）")
            
            if late_cnt == 0:
                errors.append(f"{d+1}日: 遅番を配置できませんでした")
            elif late_cnt > 1:
                errors.append(f"{d+1}日: 遅番が{late_cnt}名います（1名が原則）")
            
            if not any(schedule[s["name"]][d] == ShiftTypes.NIGHT for s in self.staff_dict_list):
                errors.append(f"{d+1}日: 夜勤を配置できませんでした")
        
        # 空スロットエラー
        for s in self.staff_dict_list:
            name = s["name"]
            empty_days = [d+1 for d in range(self.days) if schedule[name][d] == ""]
            if empty_days:
                errors.append(f"{name}: {','.join(map(str, empty_days))}日が未配置です")
        
        return errors
    
    # =========================================================================
    # メイン処理
    # =========================================================================
    
    def solve(self) -> Tuple[Dict, List[str]]:
        """
        シフトを計算する
        
        Returns:
            (schedule, errors): シフト表とエラーリストのタプル
        """
        best_schedule = None
        best_score = -999999
        
        for _ in range(self.max_attempts):
            schedule = {s["name"]: [""] * self.days for s in self.staff_dict_list}
            night_counts = {s["name"]: 0 for s in self.staff_dict_list}
            fixed_days = {s["name"]: set() for s in self.staff_dict_list}
            
            # 各フェーズを実行
            self._phase0_prev_month(schedule, fixed_days)
            self._phase1_fixed_and_requests(schedule, fixed_days, night_counts)
            self._phase2_night_requests(schedule, fixed_days, night_counts)
            self._phase3_daily_night(schedule, night_counts)
            self._phase4_early_late(schedule)
            self._phase5_fill_day(schedule)
            self._phase6_fill_off(schedule)
            self._phase6b_fill_remaining_with_day(schedule)
            self._phase7_balance(schedule, fixed_days)
            self._phase8_adjust(schedule, fixed_days)
            self._phase9_reduce_duplicates(schedule, fixed_days)
            self._phase_final_cleanup(schedule)
            
            # スコア計算
            score = self._calc_score(schedule)
            
            if score > best_score:
                best_score = score
                best_schedule = copy.deepcopy(schedule)
            
            # 早期終了判定
            if self._should_exit_early(schedule, score):
                break
        
        errors = self._collect_errors(best_schedule) if best_schedule else []
        return best_schedule, errors
    
    def _should_exit_early(self, schedule: Dict, score: int) -> bool:
        """早期終了すべきかどうか判定"""
        if score <= SolverConfig.EARLY_EXIT_SCORE:
            return False
        
        early_missing = sum(1 for d in range(self.days) 
                            if self._count_day_staff(schedule, d, [ShiftTypes.EARLY]) == 0)
        late_missing = sum(1 for d in range(self.days) 
                           if self._count_day_staff(schedule, d, [ShiftTypes.LATE]) == 0)
        night_missing = sum(1 for d in range(self.days) 
                            if self._count_day_staff(schedule, d, [ShiftTypes.NIGHT]) == 0)
        day_shortage = sum(1 for d in range(self.days) 
                           if self._count_day_staff(schedule, d, ShiftTypes.DAY_SHIFTS) < SolverConfig.MIN_DAY_STAFF)
        
        return early_missing == 0 and late_missing == 0 and night_missing == 0 and day_shortage == 0
