import streamlit as st
import random
import pandas as pd
import calendar
import datetime
import json
import copy

# ★追加：認証ライブラリ
import streamlit_authenticator as stauth

# ==========================================
# 1. アプリの設定 & デザイン
# ==========================================
st.set_page_config(page_title="Shift Manager Pro v40", layout="wide", page_icon="🗓️")

# ==========================================
# 0. ログイン（ここが「st.set_page_config直後」です）
# ==========================================
# 初心者向け：まずは最小構成で動く形（ベタ書き）にしています。
# 本番運用では st.secrets や config.yaml に移してください。

AUTH_CONFIG = {
    "credentials": {
        "usernames": {
            "admin": {
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                # ★必ず変更してください（最初は動作確認のため平文でもOK）
                "password": "change-me",
                "roles": ["admin"],
            }
        }
    },
    "cookie": {
        "name": "shift_manager_pro",
        # ★必ず変更：長くてランダムな文字列にしてください
        "key": "PLEASE_REPLACE_WITH_RANDOM_LONG_SECRET",
        "expiry_days": 30,
    },
}

authenticator = stauth.Authenticate(
    AUTH_CONFIG["credentials"],
    AUTH_CONFIG["cookie"]["name"],
    AUTH_CONFIG["cookie"]["key"],
    AUTH_CONFIG["cookie"]["expiry_days"],
)

# ログインフォーム
try:
    authenticator.login(
        location="main",
        fields={
            "Form name": "ログイン",
            "Username": "ユーザー名",
            "Password": "パスワード",
            "Login": "ログイン",
        },
        key="login_widget",
    )
except Exception as e:
    st.error(e)
    st.stop()

# 認証状態で分岐（未ログイン時はここで止める）
if st.session_state.get("authentication_status") is True:
    with st.sidebar:
        authenticator.logout(location="sidebar", key="logout_btn")
        st.caption(f"ログイン中：{st.session_state.get('name') or st.session_state.get('username')}")
elif st.session_state.get("authentication_status") is False:
    st.error("ユーザー名またはパスワードが違います。")
    st.stop()
else:
    st.warning("ユーザー名とパスワードを入力してください。")
    st.stop()

# ==========================================
# 以降：ログイン成功した人だけが見えるUI
# ==========================================

st.markdown("""
    <style>
    .stApp { font-family: 'Helvetica Neue', Arial, sans-serif; }
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: bold;
        background-color: #FF4B4B; color: white; height: 3em;
    }
    .alert-box {
        padding: 1rem; background-color: #fef2f2; border: 1px solid #f87171; 
        border-radius: 8px; color: #991b1b; margin-bottom: 1rem;
    }
    section[data-testid="stSidebar"] { background-color: #f8f9fa; }
    @media (prefers-color-scheme: dark) {
        section[data-testid="stSidebar"] { background-color: #262730; }
    }
    </style>
""", unsafe_allow_html=True)

st.title("🗓️ Shift Manager Pro v40")
st.caption("クラウド対応：汎用ロジック＆アラート機能搭載版")

# ==========================================
# 2. スタッフ管理機能
# ==========================================
if "staff_list" not in st.session_state:
    st.session_state.staff_list = [
        {"name": "スタッフA", "type": 0},
        {"name": "スタッフB", "type": 0}
    ]

with st.sidebar:
    st.header("👥 スタッフ管理")
    
    with st.form("add_staff_form", clear_on_submit=True):
        new_name = st.text_input("名前を入力")
        # 属性から「夜勤専従」を削除し、3種類に整理
        new_type = st.selectbox("属性", ["常勤", "パート(日勤のみ)", "パート(早番のみ)"], index=0)
        submitted = st.form_submit_button("＋ スタッフを追加")
        
        if submitted and new_name:
            type_code = 0
            if new_type == "パート(日勤のみ)": type_code = 1
            elif new_type == "パート(早番のみ)": type_code = 2
            
            st.session_state.staff_list.append({"name": new_name, "type": type_code})
            st.success(f"{new_name}さんを追加しました")
            st.rerun()

    if st.session_state.staff_list:
        del_name = st.selectbox("削除するスタッフ", [s["name"] for s in st.session_state.staff_list], key="del_select")
        if st.button("削除実行"):
            st.session_state.staff_list = [s for s in st.session_state.staff_list if s["name"] != del_name]
            st.rerun()
    
    st.markdown("---")

# ==========================================
# 3. 設定の読込・保存
# ==========================================
def load_settings_callback():
    uploaded = st.session_state.setting_file_uploader
    if uploaded is not None:
        try:
            data = json.load(uploaded)
            if "staff_list_save" in data:
                st.session_state.staff_list = data["staff_list_save"]
            for key, value in data.items():
                if key != "staff_list_save":
                    st.session_state[key] = value
            st.session_state.load_success_flag = True
        except Exception as e:
            st.session_state.load_error = f"エラー: {e}"

with st.sidebar:
    st.header("📂 設定の保存・復元")
    st.file_uploader("設定ファイル(.json)", type=["json"], key="setting_file_uploader", on_change=load_settings_callback)
    if st.session_state.get("load_success_flag", False):
        st.success("復元完了！")
        st.session_state.load_success_flag = False
    st.markdown("---")

# ==========================================
# 4. 年月・全体設定
# ==========================================
with st.sidebar:
    st.header("📅 シフト設定")
    if "input_year" not in st.session_state: st.session_state.input_year = 2026
    if "input_month" not in st.session_state: st.session_state.input_month = 2

    col_y, col_m = st.columns(2)
    with col_y: YEAR = st.number_input("年", 2025, 2030, key="input_year")
    with col_m: MONTH = st.number_input("月", 1, 12, key="input_month")

    _, DAYS = calendar.monthrange(YEAR, MONTH)
    
    if "target_off" not in st.session_state: st.session_state.target_off = 9
    TARGET_OFF_DAYS = st.number_input("常勤の公休数 (目標)", 1, 15, key="target_off")
    
    st.markdown("---")
    if st.button("シフトを作成する", type="primary"):
        st.session_state.run_solver = True
    else:
        st.session_state.run_solver = False

# ==========================================
# 5. 各スタッフ詳細設定
# ==========================================
st.sidebar.header("👤 個人条件設定")
SHIFT_OPTIONS = ["早", "日", "遅", "夜", "・", "◎", "有", "リ休"]
staff_data_list = []

def parse_days(input_str):
    if not input_str or not input_str.strip(): return []
    try:
        fixed_str = input_str.replace('，', ',').translate(str.maketrans('０１２３４５６７８９', '0123456789'))
        return sorted(list(set([int(x.strip()) for x in fixed_str.split(',') if x.strip().isdigit()])))
    except: return []

for idx, staff in enumerate(st.session_state.staff_list):
    name = staff["name"]
    stype = staff["type"]
    
    with st.sidebar.expander(f"{name}", expanded=False):
        # 属性変更
        type_labels = ["常勤", "パート(日勤のみ)", "パート(早番のみ)"]
        current_idx = 0
        if stype == 1: current_idx = 1
        elif stype == 2: current_idx = 2
        
        new_type_label = st.selectbox("属性変更", type_labels, index=current_idx, key=f"type_c_{name}_{idx}")
        new_code = 0
        if new_type_label == "パート(日勤のみ)": new_code = 1
        elif new_type_label == "パート(早番のみ)": new_code = 2
        staff["type"] = new_code
        stype = new_code

        c1, c2 = st.columns(2)
        key_prev = f"prev_{name}"
        if key_prev not in st.session_state: st.session_state[key_prev] = SHIFT_OPTIONS[5]
        with c1: prev_shift = st.selectbox("前月末", SHIFT_OPTIONS, key=key_prev)
        
        with c2:
            key_streak = f"streak_{name}"
            if key_streak not in st.session_state: st.session_state[key_streak] = 0
            prev_streak = st.number_input("連勤", 0, 10, key=key_streak)
        
        # 固定シフト(年始)
        f1, f2, f3 = "", "", ""
        if st.checkbox("年始固定(1/1-3)", key=f"open_fix_{name}"):
            fix_opts = [""] + SHIFT_OPTIONS
            key_f1, key_f2, key_f3 = f"f1_{name}", f"f2_{name}", f"f3_{name}"
            if key_f1 not in st.session_state: st.session_state[key_f1] = ""
            if key_f2 not in st.session_state: st.session_state[key_f2] = ""
            if key_f3 not in st.session_state: st.session_state[key_f3] = ""
            f1 = st.selectbox("1日", fix_opts, key=key_f1)
            f2 = st.selectbox("2日", fix_opts, key=key_f2)
            f3 = st.selectbox("3日", fix_opts, key=key_f3)

        night_target_val = 0
        if stype != 0: st.info("夜勤なし")
        else:
            key_night = f"night_{name}"
            if key_night not in st.session_state: st.session_state[key_night] = 4
            night_target_val = st.number_input("夜勤目標", 0, 10, key=key_night)

        req_n_in = st.text_input("夜勤希望 (例:7,20)", key=f"req_n_{name}")
        req_e_in = st.text_input("早番希望", key=f"req_e_{name}")
        req_l_in = st.text_input("遅番希望", key=f"req_l_{name}")
        req_d_in = st.text_input("日勤希望", key=f"req_d_{name}")
        off_in = st.text_input("希望休", key=f"off_{name}")
        work_in = st.text_input("出勤希望", key=f"work_{name}")
        ref_in = st.text_input("リ休", key=f"ref_{name}")
        paid_in = st.text_input("有休", key=f"paid_{name}")

    staff_data_list.append({
        "name": name, "type": stype, "night_target": night_target_val,
        "req_night": parse_days(req_n_in),
        "req_early": parse_days(req_e_in),
        "req_late": parse_days(req_l_in),
        "req_day": parse_days(req_d_in),
        "req_off": parse_days(off_in), "req_work": parse_days(work_in),
        "refresh_days": parse_days(ref_in), "paid_leave_days": parse_days(paid_in),
        "prev_shift": prev_shift, "prev_streak": prev_streak,
        "fixed_shifts": [f1, f2, f3]
    })

# 保存ボタン
st.sidebar.markdown("---")
export_data = {
    'input_year': st.session_state.get('input_year'),
    'input_month': st.session_state.get('input_month'),
    'target_off': st.session_state.get('target_off'),
    'staff_list_save': st.session_state.staff_list 
}
for s in st.session_state.staff_list:
    nm = s["name"]
    keys = [
        f"prev_{nm}", f"streak_{nm}", f"open_fix_{nm}", 
        f"f1_{nm}", f"f2_{nm}", f"f3_{nm}", f"night_{nm}", 
        f"req_n_{nm}", f"req_e_{nm}", f"req_l_{nm}", f"req_d_{nm}",
        f"off_{nm}", f"work_{nm}", f"ref_{nm}", f"paid_{nm}"
    ]
    for k in keys:
        if k in st.session_state: export_data[k] = st.session_state[k]
st.sidebar.download_button("💾 設定を保存", json.dumps(export_data, indent=2, ensure_ascii=False), 'shift_settings.json', 'application/json')

# ==========================================
# 6. 計算ロジック (v40 汎用・厳格化版)
# ==========================================
def solve_shift(staff_data):
    progress_text = "AIがシフトを作成中..."
    my_bar = st.progress(0, text=progress_text)

    best_schedule = None
    best_score = -999999
    max_attempts = 1500 

    # 各スタッフの労働可能日数の計算
    work_limits = {}
    for s in staff_data:
        if s["type"] != 0: 
            work_limits[s["name"]] = 99 # パートは制限なし（希望休以外出る）
        else:
            # 常勤は [月の日数 - 公休 - 有休 - リ休] が出勤日数
            extra_off = len(s["refresh_days"]) + len(s["paid_leave_days"])
            work_limits[s["name"]] = DAYS - (TARGET_OFF_DAYS + extra_off)

    for attempt in range(max_attempts):
        schedule = {s["name"]: [""] * DAYS for s in staff_data}
        night_counts = {s["name"]: 0 for s in staff_data}
        
        # インターバル制御用のランダム要素
        interval_factor = 0.6
        night_intervals = {}
        for s in staff_data:
            if s["night_target"] > 0:
                calc = (DAYS / s["night_target"]) * interval_factor
                night_intervals[s["name"]] = int(calc)
            else:
                night_intervals[s["name"]] = 0

        # ルールチェック関数
        def check_rules(name, day_idx, current_sched, shift_type):
            staff_info = next(s for s in staff_data if s["name"] == name)
            
            # 前日データの取得
            if day_idx == 0: prev = staff_info["prev_shift"]
            else: prev = current_sched[name][day_idx - 1]
            
            # 【ルール1】 夜勤明け(・)の翌日は、必ず休み系(◎,リ休,有)
            # ※ここで「日勤」などを入れようとしたらNG
            if prev == "・" and shift_type not in ["◎", "リ休", "有"]: return False
            
            # 【ルール2】 インターバル（遅番の翌日は早/日NG、日勤の翌日は早NG）
            if prev == "遅" and shift_type in ["早", "日"]: return False
            if prev == "日" and shift_type == "早": return False
            
            is_off_type = (shift_type in ["◎", "リ休", "有", "・"])
            if is_off_type: return True
            
            # 【ルール3】 連勤制限（5連勤までOK、6連勤NG）
            streak = 0
            current_add = 1
            temp_d = day_idx - 1
            while temp_d >= 0:
                if current_sched[name][temp_d] not in ["", "◎", "リ休", "有"]: 
                    streak += 1; temp_d -= 1
                else: break
            if temp_d < 0: streak += staff_info["prev_streak"]
            
            if streak + current_add >= 6: return False
            
            return True

        # ---------------------------------------------------
        # Phase 1: ベース作成（固定・希望・パート自動埋め）
        # ---------------------------------------------------
        for s in staff_data:
            name = s["name"]
            
            # (1) 年始固定
            for i in range(3):
                if s["fixed_shifts"][i] != "":
                    schedule[name][i] = s["fixed_shifts"][i]
                    # もし固定で夜勤が入っていたら、翌日・翌々日を予約
                    if s["fixed_shifts"][i] == "夜":
                        night_counts[name] += 1
                        if i + 1 < DAYS: schedule[name][i+1] = "・"
                        if i + 2 < DAYS: schedule[name][i+2] = "◎"

            # (2) 休み希望 (◎, リ休, 有)
            for d in s["req_off"]: 
                if schedule[name][d-1] == "": schedule[name][d-1] = "◎"
            for d in s["refresh_days"]:
                if schedule[name][d-1] == "": schedule[name][d-1] = "リ休"
            for d in s["paid_leave_days"]:
                if schedule[name][d-1] == "": schedule[name][d-1] = "有"
            
            # (3) 勤務希望 (早, 日, 遅, 夜)
            # 夜勤希望の場合、セットで翌日(・)と翌々日(◎)を確保する
            if "req_night" in s:
                for d_idx in s["req_night"]:
                    d = d_idx - 1
                    if 0 <= d < DAYS and schedule[name][d] == "":
                        schedule[name][d] = "夜"
                        night_counts[name] += 1
                        if d < DAYS - 1: schedule[name][d+1] = "・"
                        if d + 2 < DAYS: schedule[name][d+2] = "◎"
            
            for shifts, req_list in [("早", "req_early"), ("遅", "req_late"), ("日", "req_day")]:
                if req_list in s:
                    for d_idx in s[req_list]:
                        d = d_idx - 1
                        if 0 <= d < DAYS and schedule[name][d] == "":
                            schedule[name][d] = shifts
            
            # (4) パートの自動埋め（最優先）
            if s["type"] == 1: # パート(日勤のみ)
                for d in range(DAYS):
                    if schedule[name][d] == "": schedule[name][d] = "日"
            elif s["type"] == 2: # パート(早番のみ)
                for d in range(DAYS):
                    if schedule[name][d] == "": schedule[name][d] = "早"

        # ---------------------------------------------------
        # Phase 2: 夜勤の割り当て（常勤のみ）
        # ---------------------------------------------------
        cands_night = [s for s in staff_data if s["type"] == 0 and s["night_target"] > 0]
        days_indices = list(range(DAYS))
        random.shuffle(days_indices)
        
        for d in days_indices:
            if any(schedule[s["name"]][d] == "夜" for s in staff_data): continue
            
            random.shuffle(cands_night)
            for s in cands_night:
                name = s["name"]
                if schedule[name][d] == "":
                    if d < DAYS - 1 and schedule[name][d+1] != "": continue
                    if d + 2 < DAYS and schedule[name][d+2] not in ["", "◎", "有", "リ休"]: continue

                    if check_rules(name, d, schedule, "夜"):
                        schedule[name][d] = "夜"
                        night_counts[name] += 1
                        if d < DAYS - 1: schedule[name][d+1] = "・"
                        if d + 2 < DAYS and schedule[name][d+2] == "": schedule[name][d+2] = "◎"
                        break

        # ---------------------------------------------------
        # Phase 3: 日勤帯の埋め合わせ（常勤のみ）
        # ---------------------------------------------------
        regulars = [s for s in staff_data if s["type"] == 0]
        
        for d in range(DAYS):
            # 1. 遅番がいないなら、可能な常勤を入れる
            if not any(schedule[s["name"]][d] == "遅" for s in staff_data):
                random.shuffle(regulars)
                for s in regulars:
                    if schedule[s["name"]][d] == "":
                        curr_work = sum([1 for x in schedule[s["name"]] if x in ["早","日","遅","夜","・"]])
                        if curr_work < work_limits[s["name"]]:
                            if check_rules(s["name"], d, schedule, "遅"):
                                schedule[s["name"]][d] = "遅"
                                break
            
            # 2. 早番がいないなら、可能な常勤を入れる
            if not any(schedule[s["name"]][d] == "早" for s in staff_data):
                random.shuffle(regulars)
                for s in regulars:
                    if schedule[s["name"]][d] == "":
                        curr_work = sum([1 for x in schedule[s["name"]] if x in ["早","日","遅","夜","・"]])
                        if curr_work < work_limits[s["name"]]:
                            if check_rules(s["name"], d, schedule, "早"):
                                schedule[s["name"]][d] = "早"
                                break

            # 3. 残りの枠を日勤などで埋める（労働日数上限まで）
            random.shuffle(regulars)
            for s in regulars:
                if schedule[s["name"]][d] == "":
                    curr_work = sum([1 for x in schedule[s["name"]] if x in ["早","日","遅","夜","・"]])
                    if curr_work < work_limits[s["name"]]:
                        fill = "日"
                        if check_rules(s["name"], d, schedule, fill):
                            schedule[s["name"]][d] = fill

        # ---------------------------------------------------
        # Phase 4: 最終調整
        # ---------------------------------------------------
        for s in staff_data:
            for d in range(DAYS):
                if schedule[s["name"]][d] == "": schedule[s["name"]][d] = "◎"

        # ---------------------------------------------------
        # スコアリング
        # ---------------------------------------------------
        score = 0
        
        # 公休数のズレ（常勤のみ）
        for s in staff_data:
            if s["type"] == 0:
                cnt = schedule[s["name"]].count("◎")
                score -= abs(cnt - TARGET_OFF_DAYS) * 100
        
        # 夜勤数のズレ
        for s in staff_data:
            tgt = s["night_target"]
            if tgt > 0:
                cnt = schedule[s["name"]].count("夜")
                score -= abs(cnt - tgt) * 50
        
        # 人員不足ペナルティ
        shortage_penalty = 0
        for d in range(DAYS):
            day_cnt = sum([1 for s in staff_data if schedule[s["name"]][d] in ["早", "日", "遅"]])
            if day_cnt < 3: shortage_penalty += 1
        score -= shortage_penalty * 200

        # 夜勤不在ペナルティ
        night_missing = 0
        for d in range(DAYS):
            if not any(schedule[s["name"]][d] == "夜" for s in staff_data):
                night_missing += 1
        score -= night_missing * 500

        if score > best_score:
            best_score = score
            best_schedule = copy.deepcopy(schedule)
            
        if shortage_penalty == 0 and night_missing == 0 and score > -50:
            break

    my_bar.progress(100, text="完了！")
    return best_schedule

# ==========================================
# 7. メイン画面表示
# ==========================================
if st.session_state.get('run_solver', False):
    if not staff_data_list:
        st.error("スタッフが登録されていません。")
        st.session_state.run_solver = False
    else:
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
    
    st.success(f"🎉 シフト案を作成しました（{current_year}年{current_month}月）")
    
    # ------------------------------------------
    # アラート生成機能
    # ------------------------------------------
    df_raw = pd.DataFrame(result).T
    alerts = []
    
    # 日ごとのチェック
    day_shift_counts = {}
    for d_idx, col in enumerate(df_raw.columns):
        col_values = df_raw[col].values
        day_cnt = sum([1 for x in col_values if x in ['早', '日', '遅']])
        day_shift_counts[col] = day_cnt
        
        date_obj = datetime.date(current_year, current_month, d_idx + 1)
        wd_ja = ["月","火","水","木","金","土","日"][date_obj.weekday()]
        date_str = f"{current_month}/{d_idx+1}({wd_ja})"

        if day_cnt < 3:
            alerts.append(f"⚠️ {date_str}: 日勤帯が {day_cnt}名 しかいません")
        
        if '夜' not in col_values:
            alerts.append(f"🔴 {date_str}: 夜勤者がいません")

    # 個人ごとのチェック
    for name in df_raw.index:
        s_info = next(s for s in staff_data_list if s["name"] == name)
        row = df_raw.loc[name]
        
        if s_info["type"] == 0:
            off_cnt = list(row).count("◎")
            if off_cnt != TARGET_OFF_DAYS:
                alerts.append(f"⚠️ {name}: 公休が {off_cnt}日 (目標{TARGET_OFF_DAYS})")
        
        if s_info["night_target"] > 0:
            n_cnt = list(row).count("夜")
            if n_cnt != s_info["night_target"]:
                alerts.append(f"ℹ️ {name}: 夜勤 {n_cnt}回 (目標{s_info['night_target']})")

    # アラート表示
    if alerts:
        with st.expander("🚨 シフトの要確認ポイント (クリックで開閉)", expanded=True):
            for a in alerts:
                st.write(a)

    # ------------------------------------------
    # テーブル表示
    # ------------------------------------------
    df_display = df_raw.copy()
    df_display['夜勤'] = [list(r).count('夜') for r in df_raw.values]
    df_display['公休'] = [list(r).count('◎') for r in df_raw.values]
    
    total_row = pd.Series(day_shift_counts, name="日勤計")
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
        elif isinstance(val, (int, float)):
            if val < 3: bg_color = '#FECACA'; font_weight='bold'
            else: bg_color = '#F0F0F0'; font_weight='normal'
            return f'background-color: {bg_color}; color: black; font-weight: {font_weight}; border: 1px solid #ddd;'
        return f'background-color: {bg_color}; color: {color}; border: 1px solid #ddd;'

    st.dataframe(df_display.style.map(color_shift), use_container_width=True)
    
    csv = df_display.to_csv(sep=",").encode('utf-8_sig')
    st.download_button("📥 CSVをダウンロード", csv, f'shift_{current_year}_{current_month}.csv', 'text/csv')
