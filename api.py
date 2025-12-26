"""
FastAPI backend for shift scheduling system
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import random
import calendar
import copy
from datetime import date

app = FastAPI(title="Shift Manager API", version="1.0.0")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# Pydantic Models
# ==========================================

class StaffData(BaseModel):
    """スタッフの設定データ"""
    name: str
    type: int = Field(description="0=常勤, 1=パート(日勤のみ), 2=パート(早番のみ)")
    night_target: int = Field(default=0, description="夜勤目標回数")
    req_night: List[int] = Field(default_factory=list, description="夜勤希望日")
    req_early: List[int] = Field(default_factory=list, description="早番希望日")
    req_late: List[int] = Field(default_factory=list, description="遅番希望日")
    req_day: List[int] = Field(default_factory=list, description="日勤希望日")
    req_off: List[int] = Field(default_factory=list, description="希望休日")
    req_work: List[int] = Field(default_factory=list, description="出勤希望日")
    refresh_days: List[int] = Field(default_factory=list, description="リフレッシュ休暇日")
    paid_leave_days: List[int] = Field(default_factory=list, description="有給休暇日")
    prev_shift: str = Field(default="◎", description="前月末シフト")
    prev_streak: int = Field(default=0, description="前月からの連勤日数")
    fixed_shifts: List[str] = Field(default_factory=list, description="年始固定シフト [1日, 2日, 3日]")


class ShiftRequest(BaseModel):
    """シフト作成リクエスト"""
    year: int = Field(ge=2025, le=2030, description="年")
    month: int = Field(ge=1, le=12, description="月")
    target_off_days: int = Field(ge=1, le=15, description="常勤スタッフの目標公休日数")
    staff_data: List[StaffData] = Field(description="スタッフ設定リスト")
    max_attempts: int = Field(default=2500, ge=1, le=10000, description="最大試行回数")


class ShiftResponse(BaseModel):
    """シフト作成レスポンス"""
    schedule: Dict[str, List[str]] = Field(description="シフト表 {スタッフ名: [日1, 日2, ...]}")
    errors: List[str] = Field(default_factory=list, description="エラーメッセージのリスト")
    year: int
    month: int
    days: int


# ==========================================
# Utility Functions
# ==========================================

def parse_days(input_str: Optional[str]) -> List[int]:
    """日付文字列をパースして整数リストに変換"""
    if not input_str or not input_str.strip():
        return []
    try:
        fixed_str = input_str.replace('，', ',').translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        return sorted(list(set([int(x.strip()) for x in fixed_str.split(',') if x.strip().isdigit()])))
    except:
        return []


# ==========================================
# Shift Calculation Logic
# ==========================================

def solve_shift(staff_data: List[StaffData], year: int, month: int, target_off_days: int, max_attempts: int = 2500) -> tuple:
    """
    シフトを計算する
    
    Returns:
        (schedule_dict, errors_list)
        schedule_dict: {スタッフ名: [シフト文字列...]}
        errors_list: エラーメッセージのリスト
    """
    _, days = calendar.monthrange(year, month)
    DAYS = days
    errors = []
    best_schedule = None
    best_score = -999999

    # スタッフデータを辞書形式に変換（後方互換性のため）
    staff_dict_list = [s.dict() for s in staff_data]

    # 勤務日数の上限計算
    work_limits = {}
    for s in staff_dict_list:
        if s["type"] != 0:
            work_limits[s["name"]] = 99
        else:
            extra_off = len(s["refresh_days"]) + len(s["paid_leave_days"])
            work_limits[s["name"]] = DAYS - (target_off_days + extra_off)

    def is_work_shift(val):
        """勤務シフトかどうか（連勤カウント用）"""
        v = val.strip() if val else ""
        return v in ["早", "日", "遅", "夜", "・"]

    def is_rest_shift(val):
        """休みシフトかどうか"""
        v = val.strip() if val else ""
        return v in ["◎", "有", "リ休"] or v == ""

    def get_prev_shift(name, day_idx, current_sched):
        """前日のシフトを取得"""
        staff_info = next(s for s in staff_dict_list if s["name"] == name)
        if day_idx == 0:
            return staff_info["prev_shift"].strip()
        return current_sched[name][day_idx - 1].strip()

    def check_reverse(prev, next_shift):
        """逆行チェック: True=逆行あり（禁止）"""
        if prev == "日" and next_shift == "早":
            return True
        if prev == "遅" and next_shift in ["早", "日"]:
            return True
        return False

    def count_consecutive_work(name, day_idx, current_sched):
        """day_idxの前までの連勤数をカウント"""
        staff_info = next(s for s in staff_dict_list if s["name"] == name)
        streak = 0
        d = day_idx - 1
        while d >= 0:
            val = current_sched[name][d].strip()
            if is_work_shift(val):
                streak += 1
                d -= 1
            else:
                break
        if d < 0:
            streak += staff_info["prev_streak"]
        return streak

    def has_night_in_streak(name, day_idx, current_sched):
        """連勤中に夜勤があるかチェック"""
        staff_info = next(s for s in staff_dict_list if s["name"] == name)
        d = day_idx - 1
        while d >= 0:
            val = current_sched[name][d].strip()
            if is_work_shift(val):
                if val in ["夜", "・"]:
                    return True
                d -= 1
            else:
                break
        if d < 0 and staff_info["prev_shift"].strip() in ["夜", "・"]:
            return True
        return False

    def check_rules(name, day_idx, current_sched, shift_type):
        """シフトルールをチェック（前後両方向）"""
        staff_info = next(s for s in staff_dict_list if s["name"] == name)
        shift_clean = shift_type.strip()
        prev = get_prev_shift(name, day_idx, current_sched)

        # ルール1: 明け(・)の翌日は公休(◎)のみ
        if prev == "・" and shift_clean != "◎":
            return False

        # ルール2a: 前日との逆行禁止
        if shift_clean in ["早", "日", "遅"]:
            if check_reverse(prev, shift_clean):
                return False

        # ルール2b: 翌日との逆行禁止（翌日が既に決まっている場合）
        if day_idx + 1 < DAYS:
            next_shift = current_sched[name][day_idx + 1].strip()
            if next_shift in ["早", "日", "遅"]:
                if check_reverse(shift_clean, next_shift):
                    return False

        # 休みタイプはここまででOK
        if shift_clean in ["◎", "有", "リ休"]:
            return True

        # 明け(・)は夜勤の翌日のみ
        if shift_clean == "・" and prev != "夜":
            return False

        # ルール3: 連勤チェック（前後両方向）
        streak_before = count_consecutive_work(name, day_idx, current_sched)
        
        streak_after = 0
        d = day_idx + 1
        while d < DAYS:
            val = current_sched[name][d].strip()
            if is_work_shift(val):
                streak_after += 1
                d += 1
            else:
                break

        if shift_clean == "夜":
            current_add = 2
        else:
            current_add = 1

        total_streak = streak_before + current_add + streak_after

        # 6連勤以上は禁止（5連勤まで）
        if total_streak > 5:
            return False

        # ルール4: 常勤の日勤帯のみ連勤は4連勤まで
        if staff_info["type"] == 0 and shift_clean in ["早", "日", "遅"]:
            has_night = has_night_in_streak(name, day_idx, current_sched)
            
            d = day_idx + 1
            while d < DAYS:
                val = current_sched[name][d].strip()
                if is_work_shift(val):
                    if val in ["夜", "・"]:
                        has_night = True
                        break
                    d += 1
                else:
                    break
            
            day_streak = 0
            d = day_idx - 1
            while d >= 0:
                val = current_sched[name][d].strip()
                if val in ["早", "日", "遅"]:
                    day_streak += 1
                    d -= 1
                elif val in ["夜", "・"]:
                    break
                else:
                    break
            day_streak += 1
            
            d = day_idx + 1
            while d < DAYS:
                val = current_sched[name][d].strip()
                if val in ["早", "日", "遅"]:
                    day_streak += 1
                    d += 1
                elif val in ["夜", "・"]:
                    break
                else:
                    break
            
            if day_streak >= 5 and not has_night:
                return False

        return True

    def can_place_night(name, day_idx, current_sched):
        """夜勤を配置できるかチェック"""
        staff_info = next(s for s in staff_dict_list if s["name"] == name)
        
        if staff_info["type"] != 0:
            return False
        if current_sched[name][day_idx] != "":
            return False
        
        if day_idx + 1 < DAYS:
            next_val = current_sched[name][day_idx + 1].strip()
            if next_val not in ["", "・"]:
                return False
        
        if day_idx + 2 < DAYS:
            next2_val = current_sched[name][day_idx + 2].strip()
            if next2_val in ["有", "リ休"]:
                return False
            if next2_val not in ["", "◎"]:
                return False

        return check_rules(name, day_idx, current_sched, "夜")

    def count_day_staff(schedule, day_idx, shift_types):
        """特定の日の特定シフトの人数をカウント"""
        return sum(1 for s in staff_dict_list if schedule[s["name"]][day_idx].strip() in shift_types)

    def count_required_off(day_idx, schedule):
        """その日の希望休・有休・リ休の数"""
        cnt = 0
        for s in staff_dict_list:
            val = schedule[s["name"]][day_idx]
            if val == "◎ " or val.strip() in ["有", "リ休"]:
                cnt += 1
        return cnt

    # メインループ
    for attempt in range(max_attempts):
        schedule = {s["name"]: [""] * DAYS for s in staff_dict_list}
        night_counts = {s["name"]: 0 for s in staff_dict_list}
        regulars = [s for s in staff_dict_list if s["type"] == 0]

        # Phase 1: 固定シフトと希望の設定
        for s in staff_dict_list:
            name = s["name"]

            # 年始固定シフト
            for i in range(min(3, DAYS)):
                if len(s["fixed_shifts"]) > i and s["fixed_shifts"][i] != "":
                    fs = s["fixed_shifts"][i]
                    schedule[name][i] = fs
                    if fs == "夜":
                        night_counts[name] += 1
                        if i + 1 < DAYS and schedule[name][i+1] == "":
                            schedule[name][i+1] = "・"
                        if i + 2 < DAYS and schedule[name][i+2] == "":
                            schedule[name][i+2] = "◎"

            # 希望休（◎ に空白を付けてマーク）
            for d in s["req_off"]:
                if 0 < d <= DAYS and schedule[name][d-1] == "":
                    schedule[name][d-1] = "◎ "

            # リフレッシュ休暇
            for d in s["refresh_days"]:
                if 0 < d <= DAYS and schedule[name][d-1] == "":
                    schedule[name][d-1] = "リ休"

            # 有給休暇
            for d in s["paid_leave_days"]:
                if 0 < d <= DAYS and schedule[name][d-1] == "":
                    schedule[name][d-1] = "有"

            # パート設定
            if s["type"] == 1:
                for d in range(DAYS):
                    if schedule[name][d] == "":
                        schedule[name][d] = "日"
            elif s["type"] == 2:
                for d in range(DAYS):
                    if schedule[name][d] == "":
                        schedule[name][d] = "早"

        # Phase 2: 夜勤希望の配置
        for s in staff_dict_list:
            name = s["name"]
            if "req_night" in s and s["type"] == 0:
                for d_idx in s["req_night"]:
                    d = d_idx - 1
                    if 0 <= d < DAYS and can_place_night(name, d, schedule):
                        schedule[name][d] = "夜"
                        night_counts[name] += 1
                        if d + 1 < DAYS:
                            schedule[name][d+1] = "・"
                        if d + 2 < DAYS and schedule[name][d+2] == "":
                            schedule[name][d+2] = "◎"

        # Phase 3: 毎日の夜勤配置
        days_order = list(range(DAYS))
        random.shuffle(days_order)

        for d in days_order:
            if count_day_staff(schedule, d, ["夜"]) > 0:
                continue

            candidates = []
            for s in regulars:
                name = s["name"]
                if can_place_night(name, d, schedule):
                    priority = s["night_target"] - night_counts[name]
                    candidates.append((s, priority))

            if candidates:
                candidates.sort(key=lambda x: -x[1])
                top_priority = candidates[0][1]
                top_cands = [c for c in candidates if c[1] == top_priority]
                random.shuffle(top_cands)

                chosen = top_cands[0][0]
                name = chosen["name"]
                schedule[name][d] = "夜"
                night_counts[name] += 1
                if d + 1 < DAYS:
                    schedule[name][d+1] = "・"
                if d + 2 < DAYS and schedule[name][d+2] == "":
                    schedule[name][d+2] = "◎"

        # Phase 4: 早番・遅番の配置（毎日各1名）
        for d in range(DAYS):
            # 遅番配置
            if count_day_staff(schedule, d, ["遅"]) == 0:
                candidates = []
                for s in regulars:
                    name = s["name"]
                    if schedule[name][d] == "":
                        if check_rules(name, d, schedule, "遅"):
                            candidates.append(s)
                if candidates:
                    random.shuffle(candidates)
                    schedule[candidates[0]["name"]][d] = "遅"

            # 早番配置
            if count_day_staff(schedule, d, ["早"]) == 0:
                candidates = []
                for s in regulars:
                    name = s["name"]
                    if schedule[name][d] == "":
                        if check_rules(name, d, schedule, "早"):
                            candidates.append(s)
                for s in staff_dict_list:
                    if s["type"] == 2 and schedule[s["name"]][d] == "":
                        candidates.append(s)
                if candidates:
                    random.shuffle(candidates)
                    schedule[candidates[0]["name"]][d] = "早"

        # Phase 5: 日勤で埋める（勤務日数を考慮）
        for s in regulars:
            name = s["name"]
            empty_days = [d for d in range(DAYS) if schedule[name][d] == ""]
            random.shuffle(empty_days)
            for d in empty_days:
                curr_work = sum(1 for x in schedule[name] if is_work_shift(x))
                if curr_work >= work_limits[name]:
                    break
                if check_rules(name, d, schedule, "日"):
                    schedule[name][d] = "日"

        # Phase 6: 公休の最適配置（人員不足日を避ける）
        for s in regulars:
            name = s["name"]
            empty_days = [d for d in range(DAYS) if schedule[name][d] == ""]
            
            if not empty_days:
                continue

            day_scores = []
            for d in empty_days:
                day_cnt = count_day_staff(schedule, d, ["早", "日", "遅"])
                fixed_off = count_required_off(d, schedule)
                others_empty = sum(1 for s2 in regulars if s2["name"] != name and schedule[s2["name"]][d] == "")
                score = day_cnt + others_empty - fixed_off
                day_scores.append((d, score))

            day_scores.sort(key=lambda x: -x[1])
            for d, _ in day_scores:
                if check_rules(name, d, schedule, "◎"):
                    schedule[name][d] = "◎"

        # Phase 7: 人員調整（不足解消）
        for iteration in range(20):
            improved = False

            for d in range(DAYS):
                early_cnt = count_day_staff(schedule, d, ["早"])
                late_cnt = count_day_staff(schedule, d, ["遅"])
                day_total = count_day_staff(schedule, d, ["早", "日", "遅"])

                # 早番不足: 日勤者を早番に変更
                if early_cnt == 0:
                    for s in regulars:
                        name = s["name"]
                        if schedule[name][d] == "日":
                            schedule[name][d] = ""
                            if check_rules(name, d, schedule, "早"):
                                schedule[name][d] = "早"
                                improved = True
                                break
                            else:
                                schedule[name][d] = "日"

                # 遅番不足: 日勤者を遅番に変更
                if late_cnt == 0:
                    for s in regulars:
                        name = s["name"]
                        if schedule[name][d] == "日":
                            schedule[name][d] = ""
                            if check_rules(name, d, schedule, "遅"):
                                schedule[name][d] = "遅"
                                improved = True
                                break
                            else:
                                schedule[name][d] = "日"

                # 日勤帯不足 & 不要な公休がある場合
                if day_total < 3:
                    fixed_off_cnt = count_required_off(d, schedule)
                    total_staff = len(regulars)
                    night_cnt = count_day_staff(schedule, d, ["夜"])
                    ake_cnt = count_day_staff(schedule, d, ["・"])
                    min_off = night_cnt + ake_cnt + fixed_off_cnt
                    max_day_possible = total_staff - min_off

                    if max_day_possible >= 3 and day_total < 3:
                        for s in regulars:
                            name = s["name"]
                            if schedule[name][d] == "◎":
                                other_days = []
                                for od in range(DAYS):
                                    if od != d and schedule[name][od] == "◎":
                                        od_total = count_day_staff(schedule, od, ["早", "日", "遅"])
                                        if od_total >= 3:
                                            other_days.append(od)
                                
                                if other_days:
                                    schedule[name][d] = ""
                                    if check_rules(name, d, schedule, "日"):
                                        schedule[name][d] = "日"
                                        improved = True
                                        break
                                    else:
                                        schedule[name][d] = "◎"
                        if improved:
                            continue

            if not improved:
                break

        # Phase 8: 早番・遅番過多の調整
        for d in range(DAYS):
            early_cnt = count_day_staff(schedule, d, ["早"])
            late_cnt = count_day_staff(schedule, d, ["遅"])

            if early_cnt > 1:
                early_staff = [s for s in staff_dict_list if schedule[s["name"]][d] == "早" and s["type"] == 0]
                for s in early_staff[1:]:
                    name = s["name"]
                    schedule[name][d] = ""
                    if check_rules(name, d, schedule, "日"):
                        schedule[name][d] = "日"
                        break
                    else:
                        schedule[name][d] = "早"

            if late_cnt > 1:
                late_staff = [s for s in staff_dict_list if schedule[s["name"]][d] == "遅" and s["type"] == 0]
                for s in late_staff[1:]:
                    name = s["name"]
                    schedule[name][d] = ""
                    if check_rules(name, d, schedule, "日"):
                        schedule[name][d] = "日"
                        break
                    else:
                        schedule[name][d] = "遅"

        # スコアリング
        score = 0

        for s in staff_dict_list:
            if s["type"] == 0:
                cnt = sum(1 for x in schedule[s["name"]] if x.strip() == "◎")
                score -= abs(cnt - target_off_days) * 100

        for s in staff_dict_list:
            tgt = s["night_target"]
            if tgt > 0:
                cnt = schedule[s["name"]].count("夜")
                score -= abs(cnt - tgt) * 50

        early_missing = sum(1 for d in range(DAYS) if count_day_staff(schedule, d, ["早"]) == 0)
        late_missing = sum(1 for d in range(DAYS) if count_day_staff(schedule, d, ["遅"]) == 0)
        night_missing = sum(1 for d in range(DAYS) if count_day_staff(schedule, d, ["夜"]) == 0)
        day_shortage = sum(1 for d in range(DAYS) if count_day_staff(schedule, d, ["早", "日", "遅"]) < 3)

        score -= early_missing * 300
        score -= late_missing * 300
        score -= night_missing * 500
        score -= day_shortage * 100

        if score > best_score:
            best_score = score
            best_schedule = copy.deepcopy(schedule)

        if early_missing == 0 and late_missing == 0 and night_missing == 0 and day_shortage == 0 and score > -100:
            break

    # エラー収集
    if best_schedule:
        for d in range(DAYS):
            if not any(best_schedule[s["name"]][d] == "早" for s in staff_dict_list):
                errors.append(f"{d+1}日: 早番を配置できませんでした")
            if not any(best_schedule[s["name"]][d] == "遅" for s in staff_dict_list):
                errors.append(f"{d+1}日: 遅番を配置できませんでした")
            if not any(best_schedule[s["name"]][d] == "夜" for s in staff_dict_list):
                errors.append(f"{d+1}日: 夜勤を配置できませんでした")

    return best_schedule, errors


# ==========================================
# API Endpoints
# ==========================================

@app.post("/api/shift/solve", response_model=ShiftResponse)
async def create_shift(request: ShiftRequest):
    """
    シフトを作成する
    
    - **year**: 年 (2025-2030)
    - **month**: 月 (1-12)
    - **target_off_days**: 常勤スタッフの目標公休日数 (1-15)
    - **staff_data**: スタッフ設定のリスト
    - **max_attempts**: 最大試行回数 (デフォルト: 2500)
    """
    if not request.staff_data:
        raise HTTPException(status_code=400, detail="スタッフが登録されていません")
    
    try:
        schedule, errors = solve_shift(
            request.staff_data,
            request.year,
            request.month,
            request.target_off_days,
            request.max_attempts
        )
        
        if schedule is None:
            raise HTTPException(status_code=500, detail="シフトの作成に失敗しました")
        
        _, days = calendar.monthrange(request.year, request.month)
        
        return ShiftResponse(
            schedule=schedule,
            errors=errors,
            year=request.year,
            month=request.month,
            days=days
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"エラーが発生しました: {str(e)}")


@app.post("/api/shift/parse-days")
async def parse_days_endpoint(input_str: Optional[str] = None):
    """
    日付文字列をパースして整数リストに変換する
    
    - **input_str**: カンマ区切りの日付文字列 (例: "1,2,3" または "1，2，3")
    """
    result = parse_days(input_str)
    return {"days": result}


@app.get("/")
async def root():
    """APIのルートエンドポイント"""
    return {
        "message": "Shift Manager API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/shift/solve": "シフトを作成",
            "POST /api/shift/parse-days": "日付文字列をパース",
            "GET /docs": "APIドキュメント (Swagger UI)",
            "GET /redoc": "APIドキュメント (ReDoc)"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
