"""
Pydantic Models for Shift Manager API
Version: 2.1.0

このモジュールはAPIのリクエスト/レスポンスモデルと
シフト種別の定数を定義します。
"""
from pydantic import BaseModel, Field
from typing import List, Dict


# =============================================================================
# スタッフ種別定数
# =============================================================================

class StaffType:
    """スタッフ種別"""
    REGULAR = 0      # 常勤
    PART_DAY = 1     # パート（日勤のみ）
    PART_EARLY = 2   # パート（早番のみ）


# =============================================================================
# シフト種別定数
# =============================================================================

class ShiftTypes:
    """
    シフト種別の定数
    
    シフト記号:
    - 早: 早番（朝シフト）
    - 日: 日勤（通常日中シフト）
    - 遅: 遅番（夕方〜夜シフト）
    - 夜: 夜勤（夜間シフト）
    - ・: 明け（夜勤後の休息日）
    - ◎: 公休
    - ◎ : 希望休（末尾スペースで公休と区別）
    - 有: 有給休暇
    - リ休: リフレッシュ休暇
    """
    # 基本シフト
    EARLY = "早"           # 早番
    DAY = "日"             # 日勤
    LATE = "遅"            # 遅番
    NIGHT = "夜"           # 夜勤
    NIGHT_REST = "・"      # 明け（夜勤後の休息）
    
    # 休暇
    OFF = "◎"              # 公休
    HOPE_OFF = "◎ "        # 希望休（末尾スペースで区別）
    PAID = "有"            # 有休
    REFRESH = "リ休"       # リフレッシュ休暇
    
    # グループ定義
    DAY_SHIFTS = [EARLY, DAY, LATE]                    # 日勤帯
    WORK_SHIFTS = [EARLY, DAY, LATE, NIGHT, NIGHT_REST]  # 勤務シフト
    REST_SHIFTS = [OFF, PAID, REFRESH]                 # 休暇シフト
    
    @classmethod
    def is_day_shift(cls, shift: str) -> bool:
        """日勤帯シフトかどうか"""
        return shift.strip() in cls.DAY_SHIFTS
    
    @classmethod
    def is_work_shift(cls, shift: str) -> bool:
        """勤務シフトかどうか"""
        return shift.strip() in cls.WORK_SHIFTS
    
    @classmethod
    def is_rest_shift(cls, shift: str) -> bool:
        """休暇シフトかどうか"""
        return shift.strip() in cls.REST_SHIFTS


# =============================================================================
# Pydantic Models
# =============================================================================

class StaffData(BaseModel):
    """
    スタッフの設定データ
    
    Attributes:
        name: スタッフ名
        type: スタッフ種別（0=常勤, 1=パート日勤, 2=パート早番）
        night_target: 夜勤目標回数
        req_night: 夜勤希望日リスト（1-indexed）
        req_early: 早番希望日リスト（1-indexed）
        req_late: 遅番希望日リスト（1-indexed）
        req_day: 日勤希望日リスト（1-indexed）
        req_off: 希望休日リスト（1-indexed）
        req_work: 出勤希望日リスト（1-indexed）- 現在未使用
        refresh_days: リフレッシュ休暇日リスト（1-indexed）
        paid_leave_days: 有給休暇日リスト（1-indexed）
        prev_shift: 前月末シフト
        prev_streak: 前月からの連勤日数
        fixed_shifts: 年始固定シフト [1日, 2日, 3日]
    """
    name: str = Field(description="スタッフ名")
    type: int = Field(
        default=StaffType.REGULAR,
        description="スタッフ種別: 0=常勤, 1=パート(日勤のみ), 2=パート(早番のみ)"
    )
    night_target: int = Field(default=0, ge=0, le=10, description="夜勤目標回数")
    
    # 希望シフト
    req_night: List[int] = Field(default_factory=list, description="夜勤希望日（1-indexed）")
    req_early: List[int] = Field(default_factory=list, description="早番希望日（1-indexed）")
    req_late: List[int] = Field(default_factory=list, description="遅番希望日（1-indexed）")
    req_day: List[int] = Field(default_factory=list, description="日勤希望日（1-indexed）")
    req_off: List[int] = Field(default_factory=list, description="希望休日（1-indexed）")
    req_work: List[int] = Field(default_factory=list, description="出勤希望日（1-indexed）- 未使用")
    
    # 休暇
    refresh_days: List[int] = Field(default_factory=list, description="リフレッシュ休暇日（1-indexed）")
    paid_leave_days: List[int] = Field(default_factory=list, description="有給休暇日（1-indexed）")
    
    # 前月情報
    prev_shift: str = Field(default=ShiftTypes.OFF, description="前月末シフト")
    prev_streak: int = Field(default=0, ge=0, le=10, description="前月からの連勤日数")
    
    # 年始固定
    fixed_shifts: List[str] = Field(default_factory=list, description="年始固定シフト [1日, 2日, 3日]")


class ShiftRequest(BaseModel):
    """
    シフト作成リクエスト
    
    Attributes:
        year: 対象年（2025-2030）
        month: 対象月（1-12）
        target_off_days: 常勤スタッフの目標公休日数
        staff_data: スタッフ設定リスト
        max_attempts: 最大試行回数（最適解探索用）
    """
    year: int = Field(ge=2025, le=2030, description="年")
    month: int = Field(ge=1, le=12, description="月")
    target_off_days: int = Field(ge=1, le=15, description="常勤スタッフの目標公休日数")
    staff_data: List[StaffData] = Field(description="スタッフ設定リスト")
    max_attempts: int = Field(default=2500, ge=1, le=10000, description="最大試行回数")


class ShiftResponse(BaseModel):
    """
    シフト作成レスポンス
    
    Attributes:
        schedule: シフト表 {スタッフ名: [日1のシフト, 日2のシフト, ...]}
        errors: エラー/警告メッセージのリスト
        year: 対象年
        month: 対象月
        days: 月の日数
    """
    schedule: Dict[str, List[str]] = Field(description="シフト表 {スタッフ名: [日1, 日2, ...]}")
    errors: List[str] = Field(default_factory=list, description="エラーメッセージのリスト")
    year: int = Field(description="対象年")
    month: int = Field(description="対象月")
    days: int = Field(description="月の日数")
