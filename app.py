import streamlit as st
import random
import pandas as pd
import calendar
import datetime
import json
import copy
import streamlit_authenticator as stauth

# ==========================================
# 0. 認証設定 (ユーザー管理)
# ==========================================
# ユーザー名: admin / パスワード: abc123
config = {
    'credentials': {
        'usernames': {
            'admin': {
                'name': '管理者',
                'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
                'email': 'admin@example.com',
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'shift_manager_secure_key_2025',
        'name': 'shift_app_cookie'
    }
}

# ==========================================
# 1. アプリの設定 & デザイン
# ==========================================
st.set_page_config(page_title="Shift Manager Pro v56", layout="wide", page_icon="🗓️")

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

# 認証オブジェクトの作成 (0.4.2仕様)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# ログイン画面の表示 (引数なしで標準表示)
authenticator.login()

# 状態の取得
auth_status = st.session_state.get('authentication_status')
user_fullname = st.session_state.get('name')

if auth_status is False:
    st.error('ユーザー名、またはパスワードが違います。')
    st.info("【テスト用】ユーザー名: admin / パスワード: abc123")
    
elif auth_status is None:
    st.warning('ご利用にはログインをお願いいたします。')
    st.info("【テスト用】ユーザー名: admin / パスワード: abc123")
    
    st.markdown("---")
    st.subheader("💎 有料プランのお申し込み")
    st.write("継続的なご利用にはアカウント登録が必要です。")
    paypal_url = "https://www.paypal.com/jp/home" 
    st.link_button("PayPalで申し込む (月額 ¥1,000)", paypal_url)
    st.caption("※お支払い確認後、メールで案内を送付いたします。")

# ------------------------------------------
# ログイン成功後のメイン画面
# ------------------------------------------
if auth_status:
    with st.sidebar:
        st.write(f"ようこそ、**{user_fullname}** さん")
        authenticator.logout('ログアウト', 'sidebar')
        st.markdown("---")

    st.title("🗓️ Shift Manager Pro v56")
    st.caption("クラウド対応：認証修正・ロジック復旧版")

    # --- 2. スタッフ管理機能 ---
    if "staff_list" not in st.session_state:
        st.session_state.staff_list = [
            {"name": "スタッフA", "type": 0},
            {"name": "スタッフB", "type": 0}
        ]

    with st.sidebar:
        st.header("👥 スタッフ管理")
        with st.form("add_staff_form", clear_on_submit=True):
            new_name = st.text_input("名前を入力")
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

    # --- 3. 設定の読込・保存 ---
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
        st.header("📂 設定の復元")
        st.file_uploader("設定ファイル(.json)", type=["json"], key="setting_file_uploader", on_change=load_settings_callback)
        if st.session_state.get("load_success_flag", False):
            st.success("復元完了！")
            st.session_state.load_success_flag = False
        st.markdown("---")

    # --- 4. 年月・全体設定 ---
    with st.sidebar:
        st.header("📅 シフト設定")
        if "input_year" not in st.session_state: st.session_state.input_year = 2026
        if "input_month" not in st.session_state: st.session_state.input_month = 2
        col_y, col_m = st.columns(2)
        with col_y: YEAR = st.number_input("年", 2025, 2030, key="input_year")
        with col_m: MONTH = st.number_input("月", 1, 12, key="input_month")
        _, DAYS = calendar.monthrange(YEAR, MONTH)
        if "target_off" not in st.session_state: st.session_state.target_off = 9
        TARGET_OFF_DAYS = st.number_input("常勤の公休数", 1, 15, key="target_off")
        if st.button("シフトを作成する", type="primary"):
            st.session_state.run_solver = True
        else:
            st.session_state.run_solver = False

    # --- 5. 個人条件設定 ---
    SHIFT_OPTIONS = ["早", "日", "遅", "夜", "・", "◎", "有", "リ休"]
    staff_data_list = []
    def parse_days(input_str):
        if not input_str or not input_str.strip(): return []
        try:
            fixed_str = input_str.replace('，', ',').translate(str.maketrans('０１２３４５６７８９', '0123456789'))
            return sorted(list(set([int(x.strip()) for x in fixed_str.split(',') if x.strip().isdigit()])))
        except: return []

    st.sidebar.header("👤 個人条件設定")
    for idx, staff in enumerate(st.session_state.staff_list):
        name = staff["name"]
        stype = staff["type"]
        with st.sidebar.expander(f"{name}", expanded=False):
            type_labels = ["常勤", "パート(日勤のみ)", "パート(早番のみ)"]
            new_type_label = st.selectbox("属性変更", type_labels, index=stype, key=f"type_c_{name}_{idx}")
            stype = type_labels.index(new_type_label)
            staff["type"] = stype
            
            c1, c2 = st.columns(2)
            if f"prev_{name}" not in st.session_state: st.session_state[f"prev_{name}"] = "◎"
            with c1: prev_shift = st.selectbox("前月末", SHIFT_OPTIONS, key=f"prev_{name}")
            with c2:
                if f"streak_{name}" not in st.session_state: st.session_state[f"streak_{name}"] = 0
                prev_streak = st.number_input("連勤", 0, 10, key=f"streak_{name}")
            
            f1, f2, f3 = "", "", ""
            if st.checkbox("年始固定(1/1-3)", key=f"open_fix_{name}"):
                f1 = st.selectbox("1日", [""] + SHIFT_OPTIONS, key=f"f1_{name}")
                f2 = st.selectbox("2日", [""] + SHIFT_OPTIONS, key=f"f2_{name}")
                f3 = st.selectbox("3日", [""] + SHIFT_OPTIONS, key=f"f3_{name}")
            if stype == 0:
                if f"night_{name}" not in st.session_state: st.session_state[f"night_{name}"] = 4
                night_target_val = st.number_input("夜勤目標", 0, 10, key=f"night_{name}")
            else: night_target_val = 0
            req_n = st.text_input("夜勤希望", key=f"req_n_{name}")
            req_e = st.text_input("早番希望", key=f"req_e_{name}")
            req_l = st.text_input("遅番希望", key=f"req_l_{name}")
            req_d = st.text_input("日勤希望", key=f"req_d_{name}")
            off_in = st.text_input("希望休", key=f"off_{name}")
            ref_in = st.text_input("リ休", key=f"ref_{name}")
            paid_in = st.text_input("有休", key=f"paid_{name}")

        staff_data_list.append({
            "name": name, "type": stype, "night_target": night_target_val,
            "req_night": parse_days(req_n), "req_early": parse_days(req_e),
            "req_late": parse_days(req_l), "req_day": parse_days(req_d),
            "req_off": parse_days(off_in), "refresh_days": parse_days(ref_in), 
            "paid_leave_days": parse_days(paid_in), "prev_shift": prev_shift, 
            "prev_streak": prev_streak, "fixed_shifts": [f1, f2, f3]
        })

    # --- 6. 計算ロジック ---
    def solve_shift(staff_data):
        my_bar = st.progress(0, text="AIがシフトを作成中...")
        best_schedule = None
        best_score = -999999
        max_attempts = 1500 
        work_limits = {s["name"]: (99 if s["type"] != 0 else DAYS - (TARGET_OFF_DAYS + len(s["refresh_days"]) + len(s["paid_leave_days"]))) for s in staff_data}

        for attempt in range(max_attempts):
            schedule = {s["name"]: [""] * DAYS for s in staff_data}
            def check_rules(name, day_idx, current_sched, shift_type):
                staff_info = next(stf for stf in staff_data if stf["name"] == name)
                prev = staff_info["prev_shift"] if day_idx == 0 else current_sched[name][day_idx - 1]
                prev_clean = prev.strip()
                if prev_clean == "・" and shift_type.strip() not in ["◎", "リ休", "有"]: return False
                if prev_clean == "遅" and shift_type in ["早", "日"]: return False
                if prev_clean == "日" and shift_type == "早": return False
                if shift_type.strip() in ["◎", "リ休", "有", "・"]: return True
                streak = 0
                add = 2 if shift_type.strip() == "夜" else 1
                temp_d = day_idx - 1
                while temp_d >= 0:
                    val = current_sched[name][temp_d].strip()
                    if val not in ["", "◎", "リ休", "有"]: streak += 1; temp_d -= 1
                    else: break
                if temp_d < 0: streak += staff_info["prev_streak"]
                return (streak + add < 6)

            for s in staff_data:
                nm = s["name"]
                for i in range(3):
                    if s["fixed_shifts"][i]:
                        schedule[nm][i] = s["fixed_shifts"][i]
                        if s["fixed_shifts"][i] == "夜" and i + 1 < DAYS: schedule[nm][i+1] = "・"
                for d in s["req_off"]: schedule[nm][d-1] = "◎ " 
                for d in s["refresh_days"]: schedule[nm][d-1] = "リ休"
                for d in s["paid_leave_days"]: schedule[nm][d-1] = "有"
                for d in s["req_night"]:
                    if 0 < d <= DAYS:
                        schedule[nm][d-1] = "夜"
                        if d < DAYS: schedule[nm][d] = "・"
                for st_str, r_list in [("早","req_early"), ("遅","req_late"), ("日","req_day")]:
                    for d in s[r_list]:
                        if 0 < d <= DAYS and not schedule[nm][d-1]: schedule[nm][d-1] = st_str
                if s["type"] == 1:
                    for d in range(DAYS):
                        if not schedule[nm][d]: schedule[nm][d] = "日"
                elif s["type"] == 2:
                    for d in range(DAYS):
                        if not schedule[nm][d]: schedule[nm][d] = "早"

            for d in range(DAYS - 2):
                if any(schedule[x["name"]][d] == "夜" for x in staff_data): continue
                cands = [x for x in staff_data if x["type"] == 0 and schedule[x["name"]][d+2].strip() in ["◎", "有", "リ休"]]
                if cands:
                    cands.sort(key=lambda x: x["night_target"], reverse=True)
                    winner = cands[0]["name"]
                    if not schedule[winner][d] and not schedule[winner][d+1] and check_rules(winner, d, schedule, "夜"):
                        schedule[winner][d] = "夜"; schedule[winner][d+1] = "・"

            days_idx = list(range(DAYS)); random.shuffle(days_idx)
            for d in days_idx:
                if any(schedule[x["name"]][d] == "夜" for x in staff_data): continue
                cands = [x for x in staff_data if x["type"] == 0 and not schedule[x["name"]][d]]
                random.shuffle(cands)
                for s in cands:
                    if d < DAYS - 1 and not schedule[s["name"]][d+1] and check_rules(s["name"], d, schedule, "夜"):
                        schedule[s["name"]][d] = "夜"; schedule[s["name"]][d+1] = "・"; break
            
            regs = [s for s in staff_data if s["type"] == 0]
            for d in range(DAYS):
                for st_type in ["遅", "早"]:
                    if not any(schedule[x["name"]][d] == st_type for x in staff_data):
                        random.shuffle(regs)
                        for s in regs:
                            if not schedule[s["name"]][d]:
                                curr = sum(1 for x in schedule[s["name"]] if x.strip() in ["早","日","遅","夜","・"])
                                if curr < work_limits[s["name"]] and check_rules(s["name"], d, schedule, st_type):
                                    schedule[s["name"]][d] = st_type; break
                random.shuffle(regs)
                for s in regs:
                    if not schedule[s["name"]][d]:
                        curr = sum(1 for x in schedule[s["name"]] if x.strip() in ["早","日","遅","夜","・"])
                        if curr < work_limits[s["name"]] and check_rules(s["name"], d, schedule, "日"):
                            schedule[s["name"]][d] = "日"

            for s in staff_data:
                for d in range(DAYS):
                    if not schedule[s["name"]][d]: schedule[s["name"]][d] = "◎"

            for _ in range(5):
                d_counts = {d: sum(1 for x in staff_data if schedule[x["name"]][d].strip() in ["早","日","遅"]) for d in range(DAYS)}
                short, surp = [d for d, c in d_counts.items() if c < 3], [d for d, c in d_counts.items() if c > 3]
                if not short or not surp: break
                swapped = False
                for sd, ud in [(s, u) for s in short for u in surp]:
                    for s in regs:
                        nm = s["name"]
                        if schedule[nm][ud] in ["早","日","遅"] and schedule[nm][sd] == "◎" and check_rules(nm, sd, schedule, schedule[nm][ud]):
                            schedule[nm][sd] = schedule[nm][ud]; schedule[nm][ud] = "◎"; swapped = True; break
                    if swapped: break
                if not swapped: break

            sc = 0
            for s in staff_data:
                if s["type"] == 0: sc -= abs(sum(1 for x in schedule[s["name"]] if x.strip() == "◎") - TARGET_OFF_DAYS) * 100
            for d in range(DAYS):
                if sum(1 for x in staff_data if schedule[x["name"]][d].strip() in ["早","日","遅"]) < 3: sc -= 200
                if not any(schedule[x["name"]][d] == "夜" for x in staff_data): sc -= 500
            if sc > best_score: best_score = sc; best_schedule = copy.deepcopy(schedule)
            if sc > -50: break
        my_bar.progress(100, text="完了")
        return best_schedule

    if st.session_state.get('run_solver', False):
        res = solve_shift(staff_data_list)
        st.session_state.shift_result = res
        st.session_state.shift_success = True if res else False
        st.session_state.current_year, st.session_state.current_month = YEAR, MONTH
        st.session_state.run_solver = False
        st.rerun()

    if st.session_state.get('shift_success'):
        st.success(f"🎉 シフト案を作成しました（{st.session_state.current_year}年{st.session_state.current_month}月）")
        df_raw = pd.DataFrame(st.session_state.shift_result).T
        alerts = []
        for d_idx, col in enumerate(df_raw.columns):
            vals = [x.strip() for x in df_raw[col].values]
            cnt = sum(1 for x in vals if x in ['早','日','遅'])
            if cnt < 3: alerts.append(f"⚠️ {d_idx+1}日: 日勤帯が {cnt}名")
            if '夜' not in vals: alerts.append(f"🔴 {d_idx+1}日: 夜勤者なし")
        if alerts:
            with st.expander("🚨 要確認ポイント", expanded=True):
                for a in alerts: st.write(a)

        df_disp = df_raw.copy()
        df_disp['夜勤'] = [list(map(str.strip, r)).count('夜') for r in df_raw.values]
        df_disp['公休'] = [list(map(str.strip, r)).count('◎') for r in df_raw.values]
        cols = [f"{d+1}({['月','火','水','木','金','土','日'][datetime.date(st.session_state.current_year, st.session_state.current_month, d+1).weekday()]})" for d in range(calendar.monthrange(st.session_state.current_year, st.session_state.current_month)[1])]
        df_disp.columns = cols + ['夜勤', '公休']

        def color_shift(val):
            v = str(val); color, bg = 'black', ''
            if v == '◎ ': bg, color = '#15803d', 'white'
            elif v == '◎': bg = '#dcfce7'
            elif v == '有': bg = '#fbcfe8'
            elif v == 'リ休': bg = '#ffedd5'
            elif v == '夜': bg, color = '#1E3A8A', 'white'
            elif v == '・': bg = '#BFDBFE'
            elif v == '早': bg = '#FDE047'
            elif v == '遅': bg = '#FDBA74'
            elif v == '日': bg = '#FFFFFF'
            elif isinstance(val, (int, float)):
                bg = '#FECACA' if val < 3 else '#F0F0F0'
            return f'background-color: {bg}; color: {color}; border: 1px solid #ddd;'

        st.dataframe(df_disp.style.map(color_shift), use_container_width=True)
        csv = df_disp.replace("◎ ", "◎").to_csv(sep=",").encode('utf-8_sig')
        st.download_button("📥 CSVをダウンロード", csv, 'shift.csv', 'text/csv')
