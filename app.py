import streamlit as st
import random
import pandas as pd
import calendar
import datetime
import json
import copy

# ==========================================
# 1. アプリの設定 & デザイン
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

st.title("🗓️ Shift Manager Pro v36")
st.caption("クラウド対応：スタッフ登録機能つき")

# ==========================================
# 2. スタッフ管理機能（新規追加）
# ==========================================
if "staff_list" not in st.session_state:
    # 初期データ（最初は空でもよいが、例として入れておく）
    st.session_state.staff_list = [
        {"name": "スタッフA", "type": 0},
        {"name": "スタッフB", "type": 0}
    ]

with st.sidebar:
    st.header("👥 スタッフ管理")
    
    # スタッフ追加フォーム
    with st.form("add_staff_form", clear_on_submit=True):
        new_name = st.text_input("名前を入力")
        new_type = st.selectbox("属性", ["常勤", "パート(日勤のみ)", "パート(早番のみ)", "夜勤専従"], index=0)
        submitted = st.form_submit_button("＋ スタッフを追加")
        
        if submitted and new_name:
            # 属性を数値コードに変換（ロジック用）
            type_code = 0
            if new_type == "パート(日勤のみ)": type_code = 1
            elif new_type == "パート(早番のみ)": type_code = 2
            elif new_type == "夜勤専従": type_code = 3
            
            st.session_state.staff_list.append({"name": new_name, "type": type_code})
            st.success(f"{new_name}さんを追加しました")
            st.rerun()

    # スタッフ削除
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
            # スタッフリストの復元
            if "staff_list_save" in data:
                st.session_state.staff_list = data["staff_list_save"]
            # その他の設定復元
            for key, value in data.items():
                if key != "staff_list_save":
                    st.session_state[key] = value
            st.session_state.load_success_flag = True
        except Exception as e:
            st.session_state.load_error = f"エラー: {e}"

with st.sidebar:
    st.header("📂 設定の保存・復元")
    st.caption("※ブラウザを閉じるとデータが消えるため、必ず保存をお願いします。")
    
    st.file_uploader(
        "設定ファイル(.json)", 
        type=["json"], 
        key="setting_file_uploader", 
        on_change=load_settings_callback
    )

    if st.session_state.get("load_success_flag", False):
        st.success("復元完了！")
        st.session_state.load_success_flag = False
    
    st.markdown("---")

# ==========================================
# 4. 年月・全体設定
# ==========================================
with st.sidebar:
    st.header("📅 シフト設定")
    
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
    
    if "target_off" not in st.session_state:
        st.session_state.target_off = 9
    TARGET_OFF_DAYS = st.number_input("公休数 (目標)", 1, 15, key="target_off")
    
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
        # 属性変更（保存用）
        type_labels = ["常勤", "パート(日勤のみ)", "パート(早番のみ)", "夜勤専従"]
        current_idx = 0
        if stype == 1: current_idx = 1
        elif stype == 2: current_idx = 2
        elif stype == 3: current_idx = 3
        
        new_type_label = st.selectbox("属性変更", type_labels, index=current_idx, key=f"type_c_{name}_{idx}")
        # 変更があれば反映
        new_code = 0
        if new_type_label == "パート(日勤のみ)": new_code = 1
        elif new_type_label == "パート(早番のみ)": new_code = 2
        elif new_type_label == "夜勤専従": new_code = 3
        staff["type"] = new_code
        stype = new_code

        c1, c2 = st.columns(2)
        key_prev = f"prev_{name}"
        if key_prev not in st.session_state: st.session_state[key_prev] = SHIFT_OPTIONS[5]
        with c1: prev_shift = st.selectbox("前月末", SHIFT_OPTIONS, key=key_prev)
        
        with c2:
            prev_streak = 0
            if prev_shift not in ["◎", "有", "リ休"]:
                key_streak = f"streak_{name}"
                if key_streak not in st.session_state: st.session_state[key_streak] = 0
                prev_streak = st.number_input("連勤", 0, 10, key=key_streak)
        
        # 固定シフト
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

        # 夜勤回数
        night_target_val = 0
        if stype in [1, 2]: st.info("夜勤なし")
        else:
            default_val = 4
            key_night = f"night_{name}"
            if key_night not in st.session_state: st.session_state[key_night] = default_val
            night_target_val = st.number_input("夜勤目標", 0, 10, key=key_night)

        # 希望シフト入力
        req_n_in = st.text_input("夜勤希望 (例:7,20)", key=f"req_n_{name}")
        req_e_in = st.text_input("早番希望", key=f"req_e_{name}")
        req_l_in = st.text_input("遅番希望", key=f"req_l_{name}")
        req_d_in = st.text_input("日勤希望", key=f"req_d_{name}")
        off_in = st.text_input("希望休", key=f"off_{name}")
        work_in = st.text_input("出勤希望", key=f"work_{name}")
        ref_in = st.text_input("リ休", key=f"ref_{name}")
        paid_in = st.text_input("有休", key=f"paid_{name}")

    # データ整形
    staff_data_list.append({
        "name": name, "type": stype, "night_target": [night_target_val, night_target_val],
        "req_night": parse_days(req_n_in),
        "req_early": parse_days(req_e_in),
        "req_late": parse_days(req_l_in),
        "req_day": parse_days(req_d_in),
        "req_off": parse_days(off_in), "req_work": parse_days(work_in),
        "refresh_days": parse_days(ref_in), "paid_leave_days": parse_days(paid_in),
        "prev_shift": prev_shift, "prev_streak": prev_streak,
        "fixed_shifts": [f1, f2, f3]
    })

# 保存ボタン用データ生成
st.sidebar.markdown("---")
export_data = {
    'input_year': st.session_state.get('input_year'),
    'input_month': st.session_state.get('input_month'),
    'target_off': st.session_state.get('target_off'),
    'staff_list_save': st.session_state.staff_list 
}
# 各入力項目の保存
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

st.sidebar.download_button(
    "💾 設定をファイルに保存", 
    json.dumps(export_data, indent=2, ensure_ascii=False), 
    'shift_settings.json', 
    'application/json'
)

# ==========================================
# 6. 計算ロジック (コア機能)
# ==========================================
def solve_shift(staff_data):
    progress_text = "AIがシフトを作成中..."
    my_bar = st.progress(0, text=progress_text)

    best_schedule = None
    best_score = -99999
    
    # 試行回数（多いほど精度が上がるが遅くなる）
    max_attempts = 1000 

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
        
        # 難易度調整パラメータ
        interval_factor = 0.6
        night_intervals = {}
        for s in staff_data:
            if s["night_target"][1] > 0:
                night_intervals[s["name"]] = int((DAYS / s["night_target"][1]) * interval_factor)
            else:
                night_intervals[s["name"]] = 0

        def check_rules(
