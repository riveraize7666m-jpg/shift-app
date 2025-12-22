import streamlit as st
import random
import pandas as pd
import calendar
import datetime
import json
import copy

# ==========================================
# 1. アプリの設定 & デザインカスタマイズ
# ==========================================
st.set_page_config(page_title="Shift Manager Pro", layout="wide", page_icon="🗓️")

st.markdown("""
    <style>
    .stApp { font-family: 'Helvetica Neue', Arial, sans-serif; }
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: bold;
        background-color: #FF4B4B; color: white; height: 3em;
    }
    section[data-testid="stSidebar"] { background-color: #f8f9fa; }
    @media (prefers-color-scheme: dark) {
        section[data-testid="stSidebar"] { background-color: #262730; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗓️ Shift Manager Pro v35")
st.caption("AI Assisted Shift Scheduling System (Standard View + Day Request)")

# ==========================================
# 2. 設定の読込・保存ロジック
# ==========================================
STAFF_NAMES = [
    "若山 慎吾", "金子 紗愛", "小野寺 龍雅", "菅原 佳子",
    "佐藤 成子", "小林 和", "林 小太郎", "トン"
]

def load_settings_callback():
    uploaded = st.session_state.setting_file_uploader
    if uploaded is not None:
        try:
            data = json.load(uploaded)
            for key, value in data.items():
                st.session_state[key] = value
            st.session_state.load_success_flag = True
        except Exception as e:
            st.session_state.load_error = f"エラー: {e}"

with st.sidebar:
    st.header("📂 設定の読込")
    
    st.file_uploader(
        "設定ファイル(.json)", 
        type=["json"], 
        key="setting_file_uploader", 
        on_change=load_settings_callback
    )

    if st.session_state.get("load_success_flag", False):
        st.success("復元完了！")
        st.session_state.load_success_flag = False
    
    if "load_error" in st.session_state:
        st.error(st.session_state.load_error)
        del st.session_state.load_error

    st.markdown("---")

# ==========================================
# 3. シフト作成ロジック
# ==========================================
with st.sidebar:
    st.header("📅 設定")
    
    if "input_year" not in st.session_state:
        st.session_state.input_year = 2026
    if "input_month" not in st.session_state:
        st.session_state.input_month = 2

    col_y, col_m = st.columns(2)
    with col_y: YEAR = st.number_input("年", 2025, 2030, key="input_year")
    with col_m: MONTH = st.number_input("月", 1, 12, key="input_month")

    _, DAYS = calendar.monthrange(YEAR, MONTH)
    SUNDAYS = [d for d in range(1, DAYS + 1) if datetime.date(YEAR, MONTH, d).weekday() == 6]

    st.markdown(f"<h3 style='text-align: center;'>{YEAR}年 {MONTH}月</h3>", unsafe_allow_html=True)
    
    if st.button("シフトを作成する", type="primary"):
        st.session_state.run_solver = True
    else:
        st.session_state.run_solver = False

    if "target_off" not in st.session_state:
        st.session_state.target_off = 9
    TARGET_OFF_DAYS = st.number_input("今月の公休数 (目標)", 1, 15, key="target_off")
    st.markdown("---")

# ==========================================
# 4. スタッフ・条件設定
# ==========================================
st.sidebar.header("👥 スタッフ条件")
STAFF_TYPES = [0, 1, 0, 2, 0, 0, 0, 3]
SHIFT_OPTIONS = ["早", "日", "遅", "夜", "・", "◎", "有", "リ休"]
staff_data_list = []

def parse_days(input_str):
    if not input_str.strip(): return []
    try:
        fixed_str = input_str.replace('，', ',').translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        return sorted(list(set([int(x.strip()) for x in fixed_str.split(',') if x.strip().isdigit()])))
    except: return []

for name, stype in zip(STAFF_NAMES, STAFF_TYPES):
    with st.sidebar.expander(f"👤 {name}", expanded=False):
        c1, c2 = st.columns(2)
        
        key_prev = f"prev_{name}"
        if key_prev not in st.session_state:
            st.session_state[key_prev] = SHIFT_OPTIONS[5]
        with c1: prev_shift = st.selectbox("前月末", SHIFT_OPTIONS, key=key_prev)
        
        with c2:
            prev_streak = 0
            if prev_shift not in ["◎", "有", "リ休"]:
                key_streak = f"streak_{name}"
                if key_streak not in st.session_state:
                    st.session_state[key_streak] = 0
                prev_streak = st.number_input("連勤", 0, 10, key=key_streak)
        
        f1, f2, f3 = "", "", ""
        if st.checkbox("🎍 年始(1/1-3)固定", key=f"open_fix_{name}"):
            fix_opts = [""] + SHIFT_OPTIONS
            key_f1 = f"f1_{name}"
            key_f2 = f"f2_{name}"
            key_f3 = f"f3_{name}"
            
            if key_f1 not in st.session_state: st.session_state[key_f1] = ""
            if key_f2 not in st.session_state: st.session_state[key_f2] = ""
            if key_f3 not in st.session_state: st.session_state[key_f3] = ""

            f1 = st.selectbox("1日", fix_opts, key=key_f1)
            f2 = st.selectbox("2日", fix_opts, key=key_f2)
            f3 = st.selectbox("3日", fix_opts, key=key_f3)

        st.markdown("**▼ 夜勤目標回数**")
        night_target_val = 0
        if stype in [1, 2]: st.info("夜勤なし (0回)")
        else:
            default_val = 4 if name in ["林 小太郎", "トン"] else 5
            key_night = f"night_{name}"
            if key_night not in st.session_state:
                st.session_state[key_night] = default_val
            night_target_val = st.number_input("回数 (目標)", 0, 10, key=key_night)

        st.markdown("**▼ 休日・希望**")
        if stype in [1, 2]: st.info("★固定シフト：休みを全て入力")
        
        # --- 追加機能: 各種シフト希望入力 ---
        night_req_input = st.text_input(f"夜勤希望 (例: 7,20)", key=f"req_night_{name}")
        early_req_input = st.text_input(f"早番希望 (例: 1,5)", key=f"req_early_{name}")
        late_req_input = st.text_input(f"遅番希望 (例: 10,12)", key=f"req_late_{name}")
        day_req_input = st.text_input(f"日勤希望 (例: 3,25)", key=f"req_day_{name}") # 【追加】日勤希望
        # ----------------------------------

        off_input = st.text_input(f"希望休 (例: 10,15)", key=f"off_{name}")
        work_input = st.text_input(f"出勤希望 (例: 5,20)", key=f"work_{name}")
        refresh_input = st.text_input(f"リ休 (例: 15,16)", key=f"refresh_{name}")
        paid_leave_input = st.text_input(f"有休 (例: 20)", key=f"paid_{name}")

    req_night = parse_days(night_req_input)
    req_early = parse_days(early_req_input)
    req_late = parse_days(late_req_input)
    req_day = parse_days(day_req_input) # 【追加】
    req_off = parse_days(off_input)
    req_work = parse_days(work_input)
    refresh_days = parse_days(refresh_input)
    paid_leave_days = parse_days(paid_leave_input)

    staff_data_list.append({
        "name": name, "type": stype, "night_target": [night_target_val, night_target_val],
        "req_night": req_night,
        "req_early": req_early,
        "req_late": req_late,
        "req_day": req_day, # 【追加】
        "req_off": req_off, "req_work": req_work,
        "refresh_days": refresh_days, "paid_leave_days": paid_leave_days,
        "prev_shift": prev_shift, "prev_streak": prev_streak,
        "fixed_shifts": [f1, f2, f3]
    })

# 設定保存ボタン
st.sidebar.markdown("---")
export_data = {
    'input_year': st.session_state.get('input_year'),
    'input_month': st.session_state.get('input_month'),
    'target_off': st.session_state.get('target_off')
}
for name in STAFF_NAMES:
    # 保存キーに新しい項目を追加
    keys_to_save = [
        f"prev_{name}", f"streak_{name}", f"open_fix_{name}", 
        f"f1_{name}", f"f2_{name}", f"f3_{name}", f"night_{name}", 
        f"req_night_{name}", f"req_early_{name}", f"req_late_{name}", 
        f"req_day_{name}", # 【追加】
        f"off_{name}", f"work_{name}", f"refresh_{name}", f"paid_{name}"
    ]
    for k in keys_to_save:
        if k in st.session_state: export_data[k] = st.session_state[k]

st.sidebar.download_button("💾 設定をファイルに保存", json.dumps(export_data, indent=2, ensure_ascii=False), 'shift_settings.json', 'application/json')

# ==========================================
# 5. 計算ロジック
# ==========================================
def solve_shift(staff_data):
    progress_text = "AIがシフトを作成中... (機能フル装備)"
    my_bar = st.progress(0, text=progress_text)

    best_schedule = None
    best_score = -9999
    
    max_attempts = 3000

    target_work_days_map = {}
    for s in staff_data:
        if s["type"] in [1, 2]: 
            target_work_days_map[s["name"]] = 99
        else:
            extra_off = len(s["refresh_days"]) + len(s["paid_leave_days"])
            target_work_days_map[s["name"]] = DAYS - (TARGET_OFF_DAYS + extra_off)

    for attempt in range(max_attempts):
        schedule = {s["name"]: [""] * DAYS for s in staff_data}
        night_counts = {s["name"]: 0 for s in staff_data}
        last_night_day = {s["name"]: -99 for s in staff_data}
        
        difficulty_level = 0 if attempt < 1000 else (1 if attempt < 2000 else 2)
        interval_factor = 0.60 - (difficulty_level * 0.2)
        if interval_factor < 0: interval_factor = 0
        
        night_intervals = {}
        for s in staff_data:
            if s["night_target"][1] > 0:
                night_intervals[s["name"]] = int((DAYS / s["night_target"][1]) * interval_factor)
            else:
                night_intervals[s["name"]] = 0

        def check_rules(name, day_idx, current_sched, shift_type):
            staff_info = next(s for s in staff_data if s["name"] == name)
            if name == "若山 慎吾":
                if shift_type == "日": return False
                if shift_type == "早" and (day_idx + 1) not in SUNDAYS: return False

            if day_idx == 0: prev = staff_info["prev_shift"]
            else: prev = current_sched[name][day_idx - 1]
            
            if prev == "・" and shift_type not in ["◎", "リ休", "有"]: return False
            if prev == "遅" and shift_type in ["早", "日"]: return False
            if prev == "日" and shift_type == "早": return False

            is_off_type = (shift_type in ["◎", "リ休", "有"])
            if difficulty_level == 0 and is_off_type:
                if day_idx >= 3:
                    s = current_sched[name]
                    p1 = (s[day_idx-1] in ["◎", "リ休", "有"])
                    p2 = (s[day_idx-2] in ["◎", "リ休", "有"])
                    p3 = (s[day_idx-3] in ["◎", "リ休", "有"])
                    if (not p1) and p2 and (not p3): return False
            
            if is_off_type: return True
            
            streak = 0
            current_add = 2 if shift_type == "夜" else 1
            temp_d = day_idx - 1
            while temp_d >= 0:
                if current_sched[name][temp_d] not in ["", "◎", "リ休", "有"]: 
                    streak += 1; temp_d -= 1
                else: break
            if temp_d < 0: streak += staff_info["prev_streak"]
            
            total = streak + current_add
            if total >= 6: return False 
            if total == 5 and staff_info["type"] not in [1, 2] and shift_type != "夜": return False
            if staff_info["type"] in [0, 3] and staff_info["night_target"][1] > 4 and shift_type != "夜" and total >= 4: return False
            
            future_streak = 0
            check_d = day_idx + 1
            if shift_type == "夜": check_d = day_idx + 2
            
            while check_d < DAYS:
                if current_sched[name][check_d] in ["早", "日", "遅", "夜", "・"]:
                    future_streak += 1; check_d += 1
                else: break
            if total + future_streak >= 6: return False

            return True

        # Phase 1: 固定・希望シフトの反映
        for s in staff_data:
            name = s["name"]
            # 年始固定
            for i in range(3):
                if s["fixed_shifts"][i] != "":
                    schedule[name][i] = s["fixed_shifts"][i]
                    if s["fixed_shifts"][i] == "夜":
                        night_counts[name] += 1
                        last_night_day[name] = i
                        if i + 1 < DAYS: schedule[name][i+1] = "・"
            # 休日系
            for d in s["req_off"]:
                if schedule[name][d-1] == "": schedule[name][d-1] = "◎"
            for d in s["refresh_days"]:
                if schedule[name][d-1] == "": schedule[name][d-1] = "リ休"
            for d in s["paid_leave_days"]:
                if schedule[name][d-1] == "": schedule[name][d-1] = "有"
            
            # --- 早番・遅番・日勤の希望反映 ---
            if "req_early" in s:
                for d_idx in s["req_early"]:
                    d = d_idx - 1
                    if 0 <= d < DAYS and schedule[name][d] == "":
                        schedule[name][d] = "早"
            
            if "req_late" in s:
                for d_idx in s["req_late"]:
                    d = d_idx - 1
                    if 0 <= d < DAYS and schedule[name][d] == "":
                        schedule[name][d] = "遅"

            if "req_day" in s: # 【追加】日勤希望ロジック
                for d_idx in s["req_day"]:
                    d = d_idx - 1
                    if 0 <= d < DAYS and schedule[name][d] == "":
                        schedule[name][d] = "日"
            # --------------------------

            if s["type"] == 1:
                for d in range(DAYS):
                    if schedule[name][d] == "": schedule[name][d] = "日"
            elif s["type"] == 2:
                for d in range(DAYS):
                    if schedule[name][d] == "": schedule[name][d] = "早"
            
            if "req_night" in s:
                for d_idx in s["req_night"]:
                    d = d_idx - 1
                    if 0 <= d < DAYS:
                        schedule[name][d] = "夜"
                        night_counts[name] += 1
                        last_night_day[name] = d
                        if d < DAYS - 1: schedule[name][d+1] = "・"
                        if d + 2 < DAYS and schedule[name][d+2] == "": schedule[name][d+2] = "◎"

            if s["type"] not in [1, 2]:
                fill_shift = "遅" if name == "若山 慎吾" else "日"
                for d_idx in s["req_work"]:
                    d = d_idx - 1
                    if 0 <= d < DAYS and schedule[name][d] == "":
                        if check_rules(name, d, schedule, fill_shift):
                            schedule[name][d] = fill_shift

        # Phase 2
        cands_night = [s for s in staff_data if s["night_target"][1] > 0]
        
        for d in range(DAYS):
            curr_nights = [s["name"] for s in staff_data if schedule[s["name"]][d]=="夜"]
            if curr_nights: continue 

            anchor_candidates = []
            for s in cands_night:
                name = s["name"]
                if schedule[name][d] != "": continue
                if d < DAYS - 1 and schedule[name][d+1] != "": continue
                if (d + 2 + 1) in s["req_off"]:
                    if check_rules(name, d, schedule, "夜"):
                        anchor_candidates.append(s)
            
            if anchor_candidates:
                anchor_candidates.sort(key=lambda x: (night_counts[x["name"]] < x["night_target"][1]), reverse=True)
                chosen = anchor_candidates[0]["name"]
                schedule[chosen][d] = "夜"
                if d < DAYS - 1: schedule[chosen][d+1] = "・"
                night_counts[chosen] += 1
                last_night_day[chosen] = d

        for d in range(DAYS):
            curr_nights = [s["name"] for s in staff_data if schedule[s["name"]][d]=="夜"]
            if curr_nights: continue
            
            valid_candidates = []
            for s in cands_night:
                name = s["name"]
                if schedule[name][d] != "": continue
                if d < DAYS - 1 and schedule[name][d+1] != "": continue 
                
                is_anchor = ((d + 2 + 1) in s["req_off"])
                is_perfect = False
                if d + 2 < DAYS:
                    if schedule[name][d+2] == "◎": is_perfect = True
                else: is_perfect = True
                
                if not is_anchor and d+2 < DAYS and schedule[name][d+2] != "" and schedule[name][d+2] != "◎":
                    continue

                if check_rules(name, d, schedule, "夜"):
                    current = night_counts[name]
                    target = s["night_target"][1]
                    is_under = current < target
                    if d > 20 and is_under: interval_ok = True 
                    else: interval_ok = (d - last_night_day[name] >= night_intervals[name])
                    valid_candidates.append({"data": s, "score": (is_anchor, is_under, max(0, target - current), is_perfect, interval_ok)})
            
            if valid_candidates:
                valid_candidates.sort(key=lambda x: x["score"], reverse=True)
                chosen = valid_candidates[0]["data"]["name"]
                schedule[chosen][d] = "夜"
                if d < DAYS - 1: schedule[chosen][d+1] = "・"
                if d+2 < DAYS and schedule[chosen][d+2] == "": schedule[chosen][d+2] = "◎"
                night_counts[chosen] += 1
                last_night_day[chosen] = d
        
        for d in range(DAYS):
            curr_nights = [s["name"] for s in staff_data if schedule[s["name"]][d]=="夜"]
            if curr_nights: continue
            
            best_cand = None
            cut_target_day = -1
            
            for s in cands_night:
                name = s["name"]
                if schedule[name][d] != "": continue
                if d < DAYS - 1 and schedule[name][d+1] != "": continue
                
                streak = 0
                temp_d = d - 1
                while temp_d >= 0:
                    if schedule[name][temp_d] not in ["", "◎", "リ休", "有"]: 
                        streak += 1; temp_d -= 1
                    else: break
                if temp_d < 0: streak += next(st for st in staff_data if st["name"]==name)["prev_streak"]
                if streak + 2 >= 6: continue
                
                future_streak = 0
                check_d = d + 2
                limit_day = -1
                
                while check_d < DAYS:
                    if schedule[name][check_d] in ["早", "日", "遅", "夜", "・"]:
                        future_streak += 1
                        if streak + 2 + future_streak >= 6:
                            limit_day = check_d
                            break
                        check_d += 1
                    else: break
                
                best_cand = s
                cut_target_day = limit_day
                break
            
            if best_cand:
                name = best_cand["name"]
                schedule[name][d] = "夜"
                if d < DAYS - 1: schedule[name][d+1] = "・"
                if cut_target_day != -1: schedule[name][cut_target_day] = "◎" 
                elif d + 2 < DAYS and schedule[name][d+2] == "": schedule[name][d+2] = "◎"
                night_counts[name] += 1
                last_night_day[name] = d

        # Phase 3-5
        for d in range(DAYS):
            if not any(schedule[s["name"]][d] == "遅" for s in staff_data):
                cands = [s["name"] for s in staff_data if s["type"] not in [1, 2] and schedule[s["name"]][d] == "" and check_rules(s["name"], d, schedule, "遅")]
                if cands: schedule[random.choice(cands)][d] = "遅"
            if not any(schedule[s["name"]][d] == "早" for s in staff_data):
                cands = [s["name"] for s in staff_data if s["type"] not in [1, 2] and schedule[s["name"]][d] == "" and check_rules(s["name"], d, schedule, "早")]
                if cands: schedule[random.choice(cands)][d] = "早"

        regulars = [s for s in staff_data if s["type"] in [0, 3]]
        for s in regulars:
            fill_shift = "遅" if s["name"] == "若山 慎吾" else "日"
            available_days = [d for d in range(DAYS) if schedule[s["name"]][d] == ""]
            random.shuffle(available_days)
            for d in available_days:
                curr_work = sum([1 for x in schedule[s["name"]] if x not in ["","◎", "リ休", "有"]])
                if curr_work >= target_work_days_map[s["name"]]: break
                if check_rules(s["name"], d, schedule, fill_shift):
                    schedule[s["name"]][d] = fill_shift
        
        min_target = 3
        for d in range(DAYS):
            current_staff = sum([1 for s in staff_data if schedule[s["name"]][d] in ["早", "日", "遅"]])
            if current_staff < min_target:
                needed = min_target - current_staff
                candidates = []
                for s in regulars:
                    if schedule[s["name"]][d] == "":
                        fill_shift = "遅" if s["name"] == "若山 慎吾" else "日"
                        if check_rules(s["name"], d, schedule, fill_shift):
                             candidates.append(s["name"])
                for i in range(min(needed, len(candidates))):
                    name = candidates[i]
                    fill_shift = "遅" if name == "若山 慎吾" else "日"
                    schedule[name][d] = fill_shift

        for s in staff_data:
            for d in range(DAYS):
                if schedule[s["name"]][d] == "": schedule[s["name"]][d] = "◎"

        # Phase 6
        min_target = 3 
        for _ in range(10): 
            shortage_days = []
            surplus_days = []
            for d in range(DAYS):
                cnt = sum([1 for s in staff_data if schedule[s["name"]][d] in ["早", "日", "遅"]])
                if cnt < min_target: shortage_days.append(d)
                elif cnt > min_target: surplus_days.append(d)
            if not shortage_days: break 
            
            for d_short in shortage_days:
                swapped = False
                for s in regulars:
                    if schedule[s["name"]][d_short] == "◎" and (d_short + 1) not in s["req_off"]: 
                        fill_shift = "遅" if s["name"] == "若山 慎吾" else "日"
                        if not check_rules(s["name"], d_short, schedule, fill_shift): continue
                        for d_surplus in surplus_days:
                            if schedule[s["name"]][d_surplus] in ["早", "日", "遅"]:
                                prev_shift_surplus = schedule[s["name"]][d_surplus]
                                schedule[s["name"]][d_short] = fill_shift
                                schedule[s["name"]][d_surplus] = "◎"
                                if check_rules(s["name"], d_short, schedule, fill_shift):
                                    swapped = True
                                    surplus_days.remove(d_surplus) 
                                    break
                                else:
                                    schedule[s["name"]][d_short] = "◎"
                                    schedule[s["name"]][d_surplus] = prev_shift_surplus
                        if swapped: break

        # Scoring
        score = 0
        for s in staff_data:
            if s["type"] not in [1, 2]:
                cnt = schedule[s["name"]].count("◎")
                diff = abs(cnt - TARGET_OFF_DAYS)
                if diff == 0: score += 50
                else: score -= diff * 50
        for s in staff_data:
            tgt = s["night_target"][0]
            if tgt > 0:
                cnt = schedule[s["name"]].count("夜")
                diff = abs(cnt - tgt)
                if diff == 0: score += 50
                else: score -= diff * 50
        night_missing = sum([1 for d in range(DAYS) if not any(schedule[s["name"]][d] == "夜" for s in staff_data)])
        score -= night_missing * 500
        shortage = 0
        for d in range(DAYS):
             day_cnt = sum([1 for s in staff_data if schedule[s["name"]][d] in ["早", "日", "遅"]])
             if day_cnt < 3: shortage += 1
        score -= shortage * 100
        for s in staff_data:
            if s["type"] in [1, 2]: continue
            has_2off = False
            sl = schedule[s["name"]]
            for i in range(DAYS - 1):
                if sl[i] in ["◎","リ休","有"] and sl[i+1] in ["◎","リ休","有"]: has_2off = True; break
            if has_2off: score += 20
            else: score -= 10

        if score > best_score:
            best_score = score
            best_schedule = copy.deepcopy(schedule)
        
        if night_missing == 0 and shortage == 0 and score > 600:
            break

    my_bar.progress(100, text="完了！")
    return best_schedule

# ==========================================
# 6. メイン画面
# ==========================================
if st.session_state.get('run_solver', False):
    result = solve_shift(staff_data_list)
    st.session_state.shift_result = result
    st.session_state.shift_success = True if result else False
    st.session_state.current_year = YEAR
    st.session_state.current_month = MONTH
    st.session_state.run_solver = False
    st.rerun()

if st.session_state.get('shift_success', False):
    current_year = st.session_state.current_year
    current_month = st.session_state.current_month
    result = st.session_state.shift_result
    
    st.success(f"🎉 シフト案を作成しました！（{current_year}年{current_month}月）")
    
    warnings = []
    df_raw = pd.DataFrame(result).T
    df_display = df_raw.copy()
    
    night_counts = []
    off_counts = []
    
    for name in df_raw.index:
        row = df_raw.loc[name].tolist()
        n_night = row.count('夜')
        n_off = row.count('◎')
        night_counts.append(n_night)
        off_counts.append(n_off)
        
        staff_info = next(s for s in staff_data_list if s["name"] == name)
        
        if staff_info['type'] not in [1, 2]:
            if n_off != TARGET_OFF_DAYS:
                warnings.append(f"⚠️ {name}: 公休が {n_off}日 です (目標: {TARGET_OFF_DAYS}日)")
        
        tgt = staff_info['night_target'][0]
        if tgt > 0 and n_night != tgt:
            warnings.append(f"⚠️ {name}: 夜勤が {n_night}回 です (目標: {tgt}回)")

    for d in range(len(df_raw.columns)):
        col = df_raw.iloc[:, d]
        if '夜' not in col.values:
            warnings.append(f"🔴 {d+1}日: 夜勤がいません！")
            
    for d in range(len(df_raw.columns)):
        col = df_raw.iloc[:, d]
        cnt = sum([1 for x in col.values if x in ["早", "日", "遅"]])
        if cnt < 3: 
             warnings.append(f"⚠️ {d+1}日: 日勤帯が {cnt}人しかいません")

    if warnings:
        with st.expander("⚠️ 条件未達のアラートがあります", expanded=True):
            for w in warnings: st.write(w)

    df_display['夜勤'] = night_counts
    df_display['公休'] = off_counts

    day_shift_counts = {}
    for col in df_raw.columns:
        count = df_raw[col].apply(lambda x: 1 if x in ['早', '日', '遅'] else 0).sum()
        day_shift_counts[col] = count
    
    total_row = pd.Series(day_shift_counts, name="日勤帯合計")
    total_row['夜勤'] = ''
    total_row['公休'] = ''
    df_display = pd.concat([df_display, total_row.to_frame().T])

    _, current_days = calendar.monthrange(current_year, current_month)
    weekdays_ja = ["月", "火", "水", "木", "金", "土", "日"]
    cols = []
    for d in range(1, current_days + 1):
        wd = weekdays_ja[datetime.date(current_year, current_month, d).weekday()]
        cols.append(f"{d}({wd})")
    df_display.columns = cols + ['夜勤', '公休']
    
    def color_shift(val):
        color = 'black'; bg_color = ''
        if val == '夜': bg_color = '#1E3A8A'; color = 'white'
        elif val == '・': bg_color = '#BFDBFE'
        elif val == '早': bg_color = '#FDE047'
        elif val == '遅': bg_color = '#FDBA74'
        elif val == '日': bg_color = '#FFFFFF'
        elif val in ['◎', 'リ休', '有']: bg_color = '#DCFCE7'
        elif isinstance(val, (int, float)) and val > 0:
            if val < 3: bg_color = '#FECACA' 
            else: bg_color = '#F0F0F0'
            return f'background-color: {bg_color}; color: black; font-weight: bold; border: 1px solid #ddd;'
        return f'background-color: {bg_color}; color: {color}; border: 1px solid #ddd;'

    st.subheader("📅 シフト作成結果")
    st.dataframe(df_display.style.map(color_shift), use_container_width=True)
    
    csv = df_display.to_csv(sep=",").encode('utf-8_sig')
    st.download_button("📥 CSVをダウンロード", csv, f'shift_{current_year}_{current_month}.csv', 'text/csv')

elif st.session_state.get('shift_success') is False:
    st.error("エラーが発生しました。再試行してください。")