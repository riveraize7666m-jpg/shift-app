"""
Shift Rule Checking Functions
シフトルールのチェック関数群

Version: 2.1.0

主要ルール:
1. 明け(・)の翌日は公休(◎)のみ
2. 逆行禁止（日→早、遅→早、遅→日）
3. 6連勤以上禁止（5連勤まで）
4. 常勤の日勤帯のみ連勤は3連勤まで（5連勤は必ず夜勤・明けを含む）
"""
from typing import List, Dict
from .models import ShiftTypes


class ShiftRuleChecker:
    """
    シフトルールをチェックするクラス
    
    このクラスは以下のルールを強制します:
    - 明けの翌日は必ず公休
    - 逆行シフトの禁止
    - 連勤制限（最大5連勤）
    - 日勤帯のみの連勤は3連勤まで
    """
    
    # 連勤制限
    MAX_CONSECUTIVE_WORK = 5
    MAX_DAY_SHIFT_STREAK = 3
    
    def __init__(self, staff_dict_list: List[Dict], days: int):
        """
        Args:
            staff_dict_list: スタッフ情報の辞書リスト
            days: 月の日数
        """
        self.staff_dict_list = staff_dict_list
        self.days = days
        self._staff_cache = {s["name"]: s for s in staff_dict_list}
    
    # =========================================================================
    # 基本判定メソッド
    # =========================================================================
    
    def is_work_shift(self, val: str) -> bool:
        """勤務シフトかどうか（連勤カウント用）"""
        v = val.strip() if val else ""
        return v in ShiftTypes.WORK_SHIFTS
    
    def is_rest_shift(self, val: str) -> bool:
        """休みシフトかどうか"""
        v = val.strip() if val else ""
        return v in ShiftTypes.REST_SHIFTS or v == ""
    
    def get_staff_info(self, name: str) -> Dict:
        """スタッフ情報を取得（キャッシュ使用）"""
        return self._staff_cache[name]
    
    def get_prev_shift(self, name: str, day_idx: int, schedule: Dict) -> str:
        """前日のシフトを取得"""
        if day_idx == 0:
            return self.get_staff_info(name)["prev_shift"].strip()
        return schedule[name][day_idx - 1].strip()
    
    # =========================================================================
    # 逆行チェック
    # =========================================================================
    
    def check_reverse(self, prev: str, next_shift: str) -> bool:
        """
        逆行チェック
        
        禁止パターン:
        - 日 → 早
        - 遅 → 早
        - 遅 → 日
        
        Args:
            prev: 前のシフト
            next_shift: 次のシフト
            
        Returns:
            True=逆行あり（禁止）, False=逆行なし（OK）
        """
        if prev == ShiftTypes.DAY and next_shift == ShiftTypes.EARLY:
            return True
        if prev == ShiftTypes.LATE and next_shift in [ShiftTypes.EARLY, ShiftTypes.DAY]:
            return True
        return False
    
    # =========================================================================
    # 連勤カウント
    # =========================================================================
    
    def count_consecutive_work(self, name: str, day_idx: int, schedule: Dict) -> int:
        """
        day_idxの前までの連勤数をカウント（前月からの連勤を含む）
        
        Args:
            name: スタッフ名
            day_idx: 対象日（0-indexed）
            schedule: 現在のスケジュール
            
        Returns:
            連勤日数
        """
        staff_info = self.get_staff_info(name)
        streak = 0
        d = day_idx - 1
        
        while d >= 0:
            val = schedule[name][d].strip()
            if self.is_work_shift(val):
                streak += 1
                d -= 1
            else:
                break
        
        # 前月からの連勤を加算
        if d < 0:
            streak += staff_info["prev_streak"]
        
        return streak
    
    def has_night_in_streak(self, name: str, day_idx: int, schedule: Dict) -> bool:
        """
        連勤中に夜勤があるかチェック
        
        Args:
            name: スタッフ名
            day_idx: 対象日（0-indexed）
            schedule: 現在のスケジュール
            
        Returns:
            夜勤が含まれる場合True
        """
        staff_info = self.get_staff_info(name)
        d = day_idx - 1
        
        while d >= 0:
            val = schedule[name][d].strip()
            if self.is_work_shift(val):
                if val in [ShiftTypes.NIGHT, ShiftTypes.NIGHT_REST]:
                    return True
                d -= 1
            else:
                break
        
        # 前月の夜勤チェック
        if d < 0 and staff_info["prev_shift"].strip() in [ShiftTypes.NIGHT, ShiftTypes.NIGHT_REST]:
            return True
        
        return False
    
    def _count_day_shift_streak(self, name: str, day_idx: int, schedule: Dict) -> int:
        """日勤帯のみの連勤数をカウント"""
        staff_info = self.get_staff_info(name)
        day_streak = 0
        
        # 前方の日勤帯連勤
        d = day_idx - 1
        while d >= 0:
            val = schedule[name][d].strip()
            if val in ShiftTypes.DAY_SHIFTS:
                day_streak += 1
                d -= 1
            elif val in [ShiftTypes.NIGHT, ShiftTypes.NIGHT_REST]:
                break
            else:
                break
        
        # 前月からの日勤帯連勤を加算
        if d < 0:
            prev_shift_val = staff_info["prev_shift"].strip()
            if prev_shift_val in ShiftTypes.DAY_SHIFTS:
                day_streak += staff_info["prev_streak"]
        
        day_streak += 1  # 現在のシフト分
        
        # 後方の日勤帯連勤
        d = day_idx + 1
        while d < self.days:
            val = schedule[name][d].strip()
            if val in ShiftTypes.DAY_SHIFTS:
                day_streak += 1
                d += 1
            elif val in [ShiftTypes.NIGHT, ShiftTypes.NIGHT_REST]:
                break
            else:
                break
        
        return day_streak
    
    def _has_night_in_future_streak(self, name: str, day_idx: int, schedule: Dict) -> bool:
        """翌日以降の連勤中に夜勤があるか"""
        d = day_idx + 1
        while d < self.days:
            val = schedule[name][d].strip()
            if self.is_work_shift(val):
                if val in [ShiftTypes.NIGHT, ShiftTypes.NIGHT_REST]:
                    return True
                d += 1
            else:
                break
        return False
    
    # =========================================================================
    # メインルールチェック
    # =========================================================================
    
    def check_rules(self, name: str, day_idx: int, schedule: Dict, shift_type: str) -> bool:
        """
        シフトルールをチェック（前後両方向）
        
        Args:
            name: スタッフ名
            day_idx: 対象日（0-indexed）
            schedule: 現在のスケジュール
            shift_type: 配置しようとしているシフト種別
            
        Returns:
            配置可能な場合True
        """
        staff_info = self.get_staff_info(name)
        shift_clean = shift_type.strip()
        prev = self.get_prev_shift(name, day_idx, schedule)
        
        # ルール1: 明け(・)の翌日は公休(◎)のみ
        if prev == ShiftTypes.NIGHT_REST and shift_clean != ShiftTypes.OFF:
            return False
        
        # ルール2a: 前日との逆行禁止
        if shift_clean in ShiftTypes.DAY_SHIFTS:
            if self.check_reverse(prev, shift_clean):
                return False
        
        # ルール2b: 翌日との逆行禁止（翌日が既に決まっている場合）
        if day_idx + 1 < self.days:
            next_shift = schedule[name][day_idx + 1].strip()
            if next_shift in ShiftTypes.DAY_SHIFTS:
                if self.check_reverse(shift_clean, next_shift):
                    return False
        
        # 休みタイプはここまででOK
        if shift_clean in ShiftTypes.REST_SHIFTS:
            return True
        
        # 明け(・)は夜勤の翌日のみ
        if shift_clean == ShiftTypes.NIGHT_REST and prev != ShiftTypes.NIGHT:
            return False
        
        # ルール3: 連勤チェック
        if not self._check_consecutive_work_limit(name, day_idx, schedule, shift_clean):
            return False
        
        # ルール4: 常勤の日勤帯のみ連勤は3連勤まで
        if not self._check_day_shift_streak_limit(name, day_idx, schedule, shift_clean, staff_info):
            return False
        
        return True
    
    def _check_consecutive_work_limit(self, name: str, day_idx: int, 
                                       schedule: Dict, shift_clean: str) -> bool:
        """連勤上限チェック"""
        streak_before = self.count_consecutive_work(name, day_idx, schedule)
        
        streak_after = 0
        d = day_idx + 1
        while d < self.days:
            val = schedule[name][d].strip()
            if self.is_work_shift(val):
                streak_after += 1
                d += 1
            else:
                break
        
        # 夜勤は2日分としてカウント（夜勤+明け）
        current_add = 2 if shift_clean == ShiftTypes.NIGHT else 1
        total_streak = streak_before + current_add + streak_after
        
        return total_streak <= self.MAX_CONSECUTIVE_WORK
    
    def _check_day_shift_streak_limit(self, name: str, day_idx: int, 
                                       schedule: Dict, shift_clean: str, 
                                       staff_info: Dict) -> bool:
        """日勤帯のみ連勤制限チェック"""
        if staff_info["type"] != 0 or shift_clean not in ShiftTypes.DAY_SHIFTS:
            return True
        
        has_night = self.has_night_in_streak(name, day_idx, schedule)
        has_night = has_night or self._has_night_in_future_streak(name, day_idx, schedule)
        
        day_streak = self._count_day_shift_streak(name, day_idx, schedule)
        
        # 4連勤以上の日勤帯のみは禁止
        if day_streak >= 4 and not has_night:
            return False
        
        return True
    
    # =========================================================================
    # 夜勤配置チェック
    # =========================================================================
    
    def can_place_night(self, name: str, day_idx: int, schedule: Dict) -> bool:
        """
        夜勤を配置できるかチェック
        
        確認事項:
        - 常勤のみ夜勤可能
        - 当日が空いている
        - 翌日に明けが入れられる
        - 翌々日に公休が入れられる（または希望休がある）
        - 基本ルールを満たす
        
        Args:
            name: スタッフ名
            day_idx: 対象日（0-indexed）
            schedule: 現在のスケジュール
            
        Returns:
            配置可能な場合True
        """
        staff_info = self.get_staff_info(name)
        
        # 常勤のみ夜勤可能
        if staff_info["type"] != 0:
            return False
        
        # 既にシフトが入っている場合は不可
        if schedule[name][day_idx] != "":
            return False
        
        # 翌日のチェック（明けが入れられるか）
        if not self._can_place_night_rest(name, day_idx + 1, schedule):
            return False
        
        # 翌々日のチェック（公休が入れられるか）
        if not self._can_place_off_after_night(name, day_idx + 2, schedule):
            return False
        
        return self.check_rules(name, day_idx, schedule, ShiftTypes.NIGHT)
    
    def _can_place_night_rest(self, name: str, day_idx: int, schedule: Dict) -> bool:
        """翌日に明けが入れられるかチェック"""
        if day_idx >= self.days:
            return True
        
        next_val = schedule[name][day_idx]
        next_val_stripped = next_val.strip()
        
        # 希望休（スペース付き）の場合は上書き不可
        if next_val == ShiftTypes.HOPE_OFF:
            return False
        
        return next_val_stripped in ["", ShiftTypes.NIGHT_REST]
    
    def _can_place_off_after_night(self, name: str, day_idx: int, schedule: Dict) -> bool:
        """翌々日に公休が入れられるかチェック"""
        if day_idx >= self.days:
            return True
        
        next2_val = schedule[name][day_idx]
        next2_val_stripped = next2_val.strip()
        
        # 有休・リ休の場合は不可
        if next2_val_stripped in [ShiftTypes.PAID, ShiftTypes.REFRESH]:
            return False
        
        # 希望休は許可（上書きしない）
        if next2_val == ShiftTypes.HOPE_OFF:
            return True
        
        return next2_val_stripped in ["", ShiftTypes.OFF]
