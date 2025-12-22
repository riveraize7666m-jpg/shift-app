import streamlit as st
import random
import pandas as pd
import calendar
import datetime
import json
import copy
import re

# ==========================================
# 1. アプリの設定 & デザイン
# ==========================================
st.set_page_config(
    page_title="Shift Manager Pro", 
    layout="wide", 
    page_icon="✦",
    initial_sidebar_state="expanded"
)

# モダンでリッチなカスタムCSS
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* ルート変数 */
    :root {
        --primary: #2563eb;
        --primary-light: #3b82f6;
        --primary-dark: #1d4ed8;
        --accent: #f59e0b;
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --neutral-50: #fafafa;
        --neutral-100: #f5f5f5;
        --neutral-200: #e5e5e5;
        --neutral-300: #d4d4d4;
        --neutral-600: #525252;
        --neutral-700: #404040;
        --neutral-800: #262626;
        --neutral-900: #171717;
        --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
        --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
    }
    
    /* ベーススタイル */
    .stApp {
        font-family: 'Noto Sans JP', 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* ヘッダータイトル */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #6d28d9 100%);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-xl);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 100%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 60%);
        animation: shimmer 3s ease-in-out infinite;
    }
    
    @keyframes shimmer {
        0%, 100% { transform: rotate(0deg); }
        50% { transform: rotate(5deg); }
    }
    
    .main-header h1 {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
        position: relative;
        z-index: 1;
    }
    
    .main-header p {
        color: rgba(255,255,255,0.8);
        font-size: 0.95rem;
        margin: 0.5rem 0 0 0;
        font-weight: 400;
        position: relative;
        z-index: 1;
    }
    
    /* サイドバー */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid var(--neutral-200);
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
    }
    
    /* サイドバーヘッダー */
    .sidebar-header {
        font-family: 'Outfit', 'Noto Sans JP', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--neutral-600);
        padding: 0.75rem 0;
        border-bottom: 2px solid var(--primary);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* ボタンスタイル */
    .stButton > button {
        width: 100%;
        border: none;
        border-radius: 12px;
        font-family: 'Noto Sans JP', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-md);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
        color: white;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #4338ca 100%);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .stButton > button:not([kind="primary"]) {
        background: white;
        color: var(--neutral-700);
        border: 1px solid var(--neutral-200);
    }
    
    .stButton > button:not([kind="primary"]):hover {
        background: var(--neutral-50);
        border-color: var(--primary-light);
        color: var(--primary);
    }
    
    /* 入力フィールド */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: 10px !important;
        border: 1.5px solid var(--neutral-200) !important;
        padding: 0.6rem 0.9rem !important;
        font-family: 'Noto Sans JP', sans-serif !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    }
    
    /* エキスパンダー */
    .streamlit-expanderHeader {
        font-family: 'Noto Sans JP', sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
        background: white;
        border-radius: 12px !important;
        border: 1px solid var(--neutral-200);
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease;
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--neutral-50);
        border-color: var(--primary-light);
    }
    
    details[open] > .streamlit-expanderHeader {
        border-bottom-left-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
        border-bottom: none;
    }
    
    .streamlit-expanderContent {
        background: white;
        border: 1px solid var(--neutral-200);
        border-top: none;
        border-radius: 0 0 12px 12px;
        padding: 1rem !important;
    }
    
    /* アラートボックス */
    .alert-container {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        box-shadow: var(--shadow-md);
        border-left: 4px solid var(--warning);
    }
    
    .alert-title {
        font-family: 'Outfit', 'Noto Sans JP', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        color: var(--neutral-800);
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .alert-item {
        padding: 0.5rem 0;
        font-size: 0.9rem;
        color: var(--neutral-700);
        border-bottom: 1px solid var(--neutral-100);
    }
    
    .alert-item:last-child {
        border-bottom: none;
    }
    
    /* サクセスメッセージ */
    .success-banner {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 1.25rem 1.5rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        box-shadow: var(--shadow-lg);
    }
    
    .success-banner span {
        font-size: 1.5rem;
    }
    
    /* データフレームコンテナ */
    .dataframe-container {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: var(--shadow-lg);
        margin-top: 1rem;
    }
    
    /* セクション区切り */
    .section-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--neutral-200), transparent);
        margin: 1.5rem 0;
    }
    
    /* カード */
    .info-card {
        background: white;
        border-radius: 14px;
        padding: 1.25rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--neutral-100);
        margin-bottom: 1rem;
    }
    
    .info-card-header {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--neutral-600);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .info-card-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--neutral-900);
    }
    
    /* フォーム */
    .stForm {
        background: var(--neutral-50);
        border-radius: 14px;
        padding: 1rem;
        border: 1px solid var(--neutral-200);
    }
    
    /* ダウンロードボタン */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        padding: 0.75rem 1.5rem !important;
        transition: all 0.3s ease !important;
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* プログレスバー */
    .stProgress > div > div > div {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
        border-radius: 10px;
    }
    
    /* チェックボックス */
    .stCheckbox > label {
        font-family: 'Noto Sans JP', sans-serif;
        font-size: 0.9rem;
    }
    
    /* ファイルアップローダー */
    .stFileUploader > div {
        border-radius: 12px !important;
        border: 2px dashed var(--neutral-300) !important;
        padding: 1rem !important;
        transition: all 0.2s ease !important;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--primary) !important;
        background: var(--neutral-50) !important;
    }
    
    /* ラベル */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label {
        font-family: 'Noto Sans JP', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: var(--neutral-700) !important;
    }
    
    /* スクロールバー */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--neutral-100);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--neutral-300);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--neutral-400);
    }
    
    /* ダークモード対応 */
    @media (prefers-color-scheme: dark) {
        .stApp {
            background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        }
        
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            border-right: 1px solid #334155;
        }
        
        .streamlit-expanderHeader,
        .streamlit-expanderContent,
        .alert-container,
        .dataframe-container,
        .info-card {
            background: #1e293b;
            border-color: #334155;
        }
        
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            background: #1e293b !important;
            color: #f1f5f9 !important;
            border-color: #334155 !important;
        }
    }
    
    /* アニメーション */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.4s ease-out forwards;
    }
</style>
""", unsafe_allow_html=True)

# ヘッダー
st.markdown("""
<div class="main-header">
    <h1>✦ Shift Manager Pro</h1>
    <p>スマートなシフト自動作成ツール — 連勤ルール対応版</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. スタッフ管理機能
# ==========================================
if "staff_list" not in st.session_state:
    st.session_state.staff_list = [
        {"name": "スタッフA", "type": 0},
        {"name": "スタッフB", "type": 0}
    ]

with st.sidebar:
    st.markdown('<div class="sidebar-header">👥 スタッフ管理</div>', unsafe_allow_html=True)
    
    with st.form("add_staff_form", clear_on_submit=True):
        new_name = st.text_input("名前", placeholder="新しいスタッフ名")
        new_type = st.selectbox("属性", ["常勤", "パート(日勤のみ)", "パート(早番のみ)"], index=0)
        submitted = st.form_submit_button("➕ スタッフを追加", type="primary")
        
        if submitted and new_name:
            type_code = 0
            if new_type == "パート(日勤のみ)": type_code = 1
            elif new_type == "パート(早番のみ)": type_code = 2
            
            st.session_state.staff_list.append({"name": new_name, "type": type_code})
            st.success(f"✓ {new_name}さんを追加しました")
            st.rerun()

    if st.session_state.staff_list:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        del_name = st.selectbox("削除対象", [s["name"] for s in st.session_state.staff_list], key="del_select")
        if st.button("🗑️ 削除する"):
            st.session_state.staff_list = [s for s in st.session_state.staff_list if s["name"] != del_name]
            st.rerun()
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

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
    st.markdown('<div class="sidebar-header">📂 設定ファイル</div>', unsafe_allow_html=True)
    st.file_uploader("設定を復元", type=["json"], key="setting_file_uploader", on_change=load_settings_callback, label_visibility="collapsed")
    if st.session_state.get("load_success_flag", False):
        st.success("✓ 復元完了")
        st.session_state.load_success_flag = False
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ==========================================
# 4. 年月・全体設定
# ==========================================
with st.sidebar:
    st.markdown('<div class="sidebar-header">📅 シフト設定</div>', unsafe_allow_html=True)
    if "input_year" not in st.session_state: st.session_state.input_year = 2026
    if "input_month" not in st.session_state: st.session_state.input_month = 2

    col_y, col_m = st.columns(2)
    with col_y: YEAR = st.number_input("年", 2025, 2030, key="input_year")
    with col_m: MONTH = st.number_input("月", 1, 12, key="input_month")

    _, DAYS = calendar.monthrange(YEAR, MONTH)
    
    if "target_off" not in st.session_state: st.session_state.target_off = 9
    TARGET_OFF_DAYS = st.number_input("常勤の公休数", 1, 15, key="target_off", help="目標となる公休日数を設定")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    if st.button("🚀 シフトを作成", type="primary", use_container_width=True):
        st.session_state.run_solver = True
    else:
        st.session_state.run_solver = False

# ==========================================
# 5. 各スタッフ詳細設定
# ==========================================
st.sidebar.markdown('<div class="sidebar-header">👤 個人設定</div>', unsafe_allow_html=True)
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
    
    type_emoji = "🔵" if stype == 0 else "🟢" if stype == 1 else "🟡"
    
    with st.sidebar.expander(f"{type_emoji} {name}", expanded=False):
        type_labels = ["常勤", "パート(日勤のみ)", "パート(早番のみ)"]
        current_idx = 0
        if stype == 1: current_idx = 1
        elif stype == 2: current_idx = 2
        
        new_type_label = st.selectbox("属性", type_labels, index=current_idx, key=f"type_c_{name}_{idx}")
        new_code = 0
        if new_type_label == "パート(日勤のみ)": new_code = 1
        elif new_type_label == "パート(早番のみ)": new_code = 2
        staff["type"] = new_code
        stype = new_code

        c1, c2 = st.columns(2)
        key_prev = f"prev_{name}"
        if key_prev not in st.session_state: st.session_state[key_prev] = SHIFT_OPTIONS[5]
        with c1: prev_shift = st.selectbox("前月末シフト", SHIFT_OPTIONS, key=key_prev)
        
        with c2:
            key_streak = f"streak_{name}"
            if key_streak not in st.session_state: st.session_state[key_streak] = 0
            prev_streak = st.number_input("連勤日数", 0, 10, key=key_streak)
        
        f1, f2, f3 = "", "", ""
        if st.checkbox("年始固定シフト", key=f"open_fix_{name}"):
            fix_opts = [""] + SHIFT_OPTIONS
            key_f1, key_f2, key_f3 = f"f1_{name}", f"f2_{name}", f"f3_{name}"
            if key_f1 not in st.session_state: st.session_state[key_f1] = ""
            if key_f2 not in st.session_state: st.session_state[key_f2] = ""
            if key_f3 not in st.session_state: st.session_state[key_f3] = ""
            cols = st.columns(3)
            with cols[0]: f1 = st.selectbox("1日", fix_opts, key=key_f1)
            with cols[1]: f2 = st.selectbox("2日", fix_opts, key=key_f2)
            with cols[2]: f3 = st.selectbox("3日", fix_opts, key=key_f3)

        night_target_val = 0
        if stype != 0:
            st.info("💡 このスタッフは夜勤対象外です")
        else:
            key_night = f"night_{name}"
            if key_night not in st.session_state: st.session_state[key_night] = 4
            night_target_val = st.number_input("🌙 夜勤目標回数", 0, 10, key=key_night)

        st.markdown("**希望シフト** <small style='color:#666'>（例: 7,20）</small>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            req_n_in = st.text_input("夜勤希望", key=f"req_n_{name}", label_visibility="collapsed", placeholder="夜勤希望日")
            req_l_in = st.text_input("遅番希望", key=f"req_l_{name}", label_visibility="collapsed", placeholder="遅番希望日")
        with c2:
            req_e_in = st.text_input("早番希望", key=f"req_e_{name}", label_visibility="collapsed", placeholder="早番希望日")
            req_d_in = st.text_input("日勤希望", key=f"req_d_{name}", label_visibility="collapsed", placeholder="日勤希望日")
        
        st.markdown("**休暇設定**", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            off_in = st.text_input("希望休", key=f"off_{name}", label_visibility="collapsed", placeholder="希望休")
            ref_in = st.text_input("リ休", key=f"ref_{name}", label_visibility="collapsed", placeholder="リフレッシュ休暇")
        with c2:
            work_in = st.text_input("出勤希望", key=f"work_{name}", label_visibility="collapsed", placeholder="出勤希望日")
            paid_in = st.text_input("有休", key=f"paid_{name}", label_visibility="collapsed", placeholder="有給休暇")

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
st.sidebar.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
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
st.sidebar.download_button("💾 設定を保存", json.dumps(export_data, indent=2, ensure_ascii=False), 'shift_settings.json', 'application/json', use_container_width=True)

# ==========================================
# 6. 計算ロジック
# ==========================================
def solve_shift(staff_data):
    progress_text = "✨ AIがシフトを最適化中..."
    my_bar = st.progress(0, text=progress_text)

    best_schedule = None
    best_score = -999999
    max_attempts = 1500 

    work_limits = {}
    for s in staff_data:
        if s["type"] != 0: 
            work_limits[s["name"]] = 99 
        else:
            extra_off = len(s["refresh_days"]) + len(s["paid_leave_days"])
            work_limits[s["name"]] = DAYS - (TARGET_OFF_DAYS + extra_off)

    for attempt in range(max_attempts):
        if attempt % 100 == 0:
            my_bar.progress(min(attempt / max_attempts, 0.95), text=progress_text)
            
        schedule = {s["name"]: [""] * DAYS for s in staff_data}
        night_counts = {s["name"]: 0 for s in staff_data}
        
        def check_rules(name, day_idx, current_sched, shift_type):
            staff_info = next(s for s in staff_data if s["name"] == name)
            
            if day_idx == 0: prev = staff_info["prev_shift"]
            else: prev = current_sched[name][day_idx - 1]
            
            prev_clean = prev.strip()
            
            if prev_clean == "・" and shift_type.strip() not in ["◎", "リ休", "有"]: return False
            if prev_clean == "遅" and shift_type in ["早", "日"]: return False
            if prev_clean == "日" and shift_type == "早": return False
            
            is_off_type = (shift_type.strip() in ["◎", "リ休", "有", "・"])
            if is_off_type: return True
            
            streak = 0
            current_add = 2 if shift_type.strip() == "夜" else 1
            
            temp_d = day_idx - 1
            while temp_d >= 0:
                val = current_sched[name][temp_d].strip()
                if val not in ["", "◎", "リ休", "有"]: 
                    streak += 1; temp_d -= 1
                else: break
            if temp_d < 0: streak += staff_info["prev_streak"]
            
            if streak + current_add >= 6: return False
            
            return True

        # Phase 1: ベース作成
        for s in staff_data:
            name = s["name"]
            for i in range(3):
                if s["fixed_shifts"][i] != "":
                    schedule[name][i] = s["fixed_shifts"][i]
                    if s["fixed_shifts"][i] == "夜":
                        night_counts[name] += 1
                        if i + 1 < DAYS: schedule[name][i+1] = "・"
                        if i + 2 < DAYS: schedule[name][i+2] = "◎" 
            for d in s["req_off"]: 
                if schedule[name][d-1] == "": schedule[name][d-1] = "◎ " 
            for d in s["refresh_days"]:
                if schedule[name][d-1] == "": schedule[name][d-1] = "リ休"
            for d in s["paid_leave_days"]:
                if schedule[name][d-1] == "": schedule[name][d-1] = "有"
            if "req_night" in s:
                for d_idx in s["req_night"]:
                    d = d_idx - 1
                    if 0 <= d < DAYS and schedule[name][d] == "":
                        schedule[name][d] = "夜"
                        night_counts[name] += 1
                        if d < DAYS - 1: schedule[name][d+1] = "・"
                        if d + 2 < DAYS and schedule[name][d+2] == "": schedule[name][d+2] = "◎"
            for shifts, req_list in [("早", "req_early"), ("遅", "req_late"), ("日", "req_day")]:
                if req_list in s:
                    for d_idx in s[req_list]:
                        d = d_idx - 1
                        if 0 <= d < DAYS and schedule[name][d] == "":
                            schedule[name][d] = shifts
            if s["type"] == 1: 
                for d in range(DAYS):
                    if schedule[name][d] == "": schedule[name][d] = "日"
            elif s["type"] == 2:
                for d in range(DAYS):
                    if schedule[name][d] == "": schedule[name][d] = "早"

        # Phase 1.5: 希望休前の夜勤優先配置
        for d in range(DAYS - 2):
            if any(schedule[s["name"]][d] == "夜" for s in staff_data): continue
            candidates = []
            for s in staff_data:
                if s["type"] != 0: continue
                name = s["name"]
                val_next2 = schedule[name][d+2].strip()
                if val_next2 in ["◎", "有", "リ休"]:
                    if schedule[name][d] == "" and schedule[name][d+1] == "":
                         if check_rules(name, d, schedule, "夜"):
                            candidates.append(s)
            if candidates:
                random.shuffle(candidates)
                candidates.sort(key=lambda x: x["night_target"], reverse=True)
                w_name = candidates[0]["name"]
                schedule[w_name][d] = "夜"
                schedule[w_name][d+1] = "・"
                night_counts[w_name] += 1

        # Phase 2: 残りの夜勤割り当て
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
                    if d + 2 < DAYS:
                        val_next2 = schedule[name][d+2].strip()
                        if val_next2 != "" and val_next2 not in ["◎", "有", "リ休"]: continue

                    if check_rules(name, d, schedule, "夜"):
                        schedule[name][d] = "夜"
                        night_counts[name] += 1
                        if d < DAYS - 1: schedule[name][d+1] = "・"
                        if d + 2 < DAYS and schedule[name][d+2] == "": schedule[name][d+2] = "◎"
                        break

        # Phase 3: 日勤埋め合わせ
        regulars = [s for s in staff_data if s["type"] == 0]
        
        for d in range(DAYS):
            if not any(schedule[s["name"]][d] == "遅" for s in staff_data):
                random.shuffle(regulars)
                for s in regulars:
                    if schedule[s["name"]][d] == "":
                        curr_work = sum([1 for x in schedule[s["name"]] if x.strip() in ["早","日","遅","夜","・"]])
                        if curr_work < work_limits[s["name"]]:
                            if check_rules(s["name"], d, schedule, "遅"):
                                schedule[s["name"]][d] = "遅"
                                break
            if not any(schedule[s["name"]][d] == "早" for s in staff_data):
                random.shuffle(regulars)
                for s in regulars:
                    if schedule[s["name"]][d] == "":
                        curr_work = sum([1 for x in schedule[s["name"]] if x.strip() in ["早","日","遅","夜","・"]])
                        if curr_work < work_limits[s["name"]]:
                            if check_rules(s["name"], d, schedule, "早"):
                                schedule[s["name"]][d] = "早"
                                break

        for s in regulars:
            empty_days = [d for d in range(DAYS) if schedule[s["name"]][d] == ""]
            random.shuffle(empty_days)
            for d in empty_days:
                curr_work = sum([1 for x in schedule[s["name"]] if x.strip() in ["早","日","遅","夜","・"]])
                if curr_work >= work_limits[s["name"]]: break
                if check_rules(s["name"], d, schedule, "日"):
                    schedule[s["name"]][d] = "日"

        # Phase 4: 最終調整
        for s in staff_data:
            for d in range(DAYS):
                if schedule[s["name"]][d] == "": schedule[s["name"]][d] = "◎"

        for _ in range(10): 
            day_counts = {}
            for d in range(DAYS):
                cnt = sum(1 for s in staff_data if schedule[s["name"]][d].strip() in ["早", "日", "遅"])
                day_counts[d] = cnt
            
            short_days = [d for d, c in day_counts.items() if c < 3]
            surplus_days = [d for d, c in day_counts.items() if c > 3]
            
            if not short_days: break 
            
            random.shuffle(short_days)
            random.shuffle(surplus_days)
            
            swapped = False
            for short_d in short_days:
                if swapped: break
                for surp_d in surplus_days:
                    if swapped: break
                    
                    random.shuffle(regulars)
                    for staff in regulars:
                        name = staff["name"]
                        shift_src = schedule[name][surp_d]
                        shift_dst = schedule[name][short_d]
                        
                        if shift_src not in ["早", "日", "遅"]: continue
                        if shift_dst != "◎": continue 
                        
                        if not check_rules(name, short_d, schedule, shift_src): continue
                        
                        valid_forward = True
                        if short_d < DAYS - 1:
                            next_shift = schedule[name][short_d+1].strip()
                            if shift_src == "遅" and next_shift in ["早", "日"]: valid_forward = False
                            if shift_src == "日" and next_shift == "早": valid_forward = False
                        if not valid_forward: continue

                        schedule[name][short_d] = shift_src
                        schedule[name][surp_d] = "◎"
                        swapped = True
                        break 
            
            if not swapped: break

        # スコアリング
        score = 0
        
        for s in staff_data:
            if s["type"] == 0:
                cnt = sum([1 for x in schedule[s["name"]] if x.strip() == "◎"])
                score -= abs(cnt - TARGET_OFF_DAYS) * 100
        
        for s in staff_data:
            tgt = s["night_target"]
            if tgt > 0:
                cnt = schedule[s["name"]].count("夜")
                score -= abs(cnt - tgt) * 50
        
        shortage_penalty = 0
        for d in range(DAYS):
             day_cnt = sum([1 for s in staff_data if schedule[s["name"]][d].strip() in ["早", "日", "遅"]])
             if day_cnt < 3: shortage_penalty += 1
        score -= shortage_penalty * 200

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

    my_bar.progress(100, text="✓ 完了しました")
    return best_schedule

# ==========================================
# 7. メイン画面表示
# ==========================================
if st.session_state.get('run_solver', False):
    if not staff_data_list:
        st.error("⚠️ スタッフが登録されていません。サイドバーからスタッフを追加してください。")
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
    
    # サクセスメッセージ
    st.markdown(f"""
    <div class="success-banner">
        <span>🎉</span>
        <div>シフト案を作成しました — {current_year}年{current_month}月</div>
    </div>
    """, unsafe_allow_html=True)
    
    # ------------------------------------------
    # アラート
    # ------------------------------------------
    df_raw = pd.DataFrame(result).T
    alerts = []
    
    day_shift_counts = {}
    for d_idx, col in enumerate(df_raw.columns):
        col_values = [x.strip() for x in df_raw[col].values]
        day_cnt = sum([1 for x in col_values if x in ['早', '日', '遅']])
        day_shift_counts[col] = day_cnt
        
        date_obj = datetime.date(current_year, current_month, d_idx + 1)
        wd_ja = ["月","火","水","木","金","土","日"][date_obj.weekday()]
        date_str = f"{current_month}/{d_idx+1}({wd_ja})"

        if day_cnt < 3:
            alerts.append(("warning", f"{date_str}: 日勤帯が {day_cnt}名"))
        
        if '夜' not in col_values:
             alerts.append(("error", f"{date_str}: 夜勤者なし"))

    for name in df_raw.index:
        s_info = next(s for s in staff_data_list if s["name"] == name)
        row = [x.strip() for x in df_raw.loc[name]]
        
        if s_info["type"] == 0:
            off_cnt = row.count("◎")
            if off_cnt != TARGET_OFF_DAYS:
                alerts.append(("info", f"{name}: 公休 {off_cnt}日 (目標{TARGET_OFF_DAYS})"))
        
        if s_info["night_target"] > 0:
            n_cnt = row.count("夜")
            if n_cnt != s_info["night_target"]:
                alerts.append(("info", f"{name}: 夜勤 {n_cnt}回 (目標{s_info['night_target']})"))

    if alerts:
        with st.expander("📋 確認ポイント", expanded=True):
            for alert_type, msg in alerts:
                if alert_type == "error":
                    st.markdown(f"🔴 {msg}")
                elif alert_type == "warning":
                    st.markdown(f"⚠️ {msg}")
                else:
                    st.markdown(f"ℹ️ {msg}")

    # ------------------------------------------
    # テーブル表示
    # ------------------------------------------
    st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
    
    df_display = df_raw.copy()
    df_display['夜勤'] = [list(map(str.strip, r)).count('夜') for r in df_raw.values]
    df_display['公休'] = [list(map(str.strip, r)).count('◎') for r in df_raw.values]
    
    total_row = pd.Series(day_shift_counts, name="日勤計")
    total_row['夜勤'] = ''
    total_row['公休'] = ''
    df_display = pd.concat([df_display, total_row.to_frame().T])

    _, current_days = calendar.monthrange(current_year, current_month)
    cols = []
    weekdays_ja = ["月", "火", "水", "木", "金", "土", "日"]
    for d in range(1, current_days + 1):
        wd = weekdays_ja[datetime.date(current_year, current_month, d).weekday()]
        cols.append(f"{d}({wd})")
    df_display.columns = cols + ['夜勤', '公休']
    
    def color_shift(val):
        val_str = str(val)
        style = 'text-align: center; font-weight: 500; border-radius: 4px; '
        
        if val_str == '◎ ': 
            return style + 'background: linear-gradient(135deg, #059669, #10b981); color: white;'
        elif val_str == '◎': 
            return style + 'background: #d1fae5; color: #065f46;'
        elif val_str == '有':
            return style + 'background: linear-gradient(135deg, #db2777, #ec4899); color: white;'
        elif val_str == 'リ休':
            return style + 'background: linear-gradient(135deg, #ea580c, #f97316); color: white;'
        elif val_str == '夜': 
            return style + 'background: linear-gradient(135deg, #1e3a8a, #3730a3); color: white;'
        elif val_str == '・': 
            return style + 'background: #dbeafe; color: #1e40af;'
        elif val_str == '早': 
            return style + 'background: linear-gradient(135deg, #ca8a04, #eab308); color: #422006;'
        elif val_str == '遅': 
            return style + 'background: linear-gradient(135deg, #c2410c, #ea580c); color: white;'
        elif val_str == '日': 
            return style + 'background: #fafafa; color: #171717; border: 1px solid #e5e5e5;'
        elif isinstance(val, (int, float)):
            if val < 3: 
                return style + 'background: #fecaca; color: #991b1b; font-weight: 700;'
            else: 
                return style + 'background: #f5f5f5; color: #525252;'
        
        return style + 'background: white; color: #525252;'

    st.dataframe(
        df_display.style.map(color_shift),
        use_container_width=True,
        height=400
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ダウンロードボタン
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        df_csv = df_display.replace("◎ ", "◎")
        csv = df_csv.to_csv(sep=",").encode('utf-8_sig')
        st.download_button(
            "📥 CSVダウンロード", 
            csv, 
            f'shift_{current_year}_{current_month}.csv', 
            'text/csv',
            use_container_width=True
        )

else:
    # 初期状態の表示
    st.markdown("""
    <div style="
        background: white;
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        margin-top: 2rem;
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
        <h2 style="color: #171717; font-weight: 600; margin-bottom: 0.5rem;">シフトを作成しましょう</h2>
        <p style="color: #525252; font-size: 1rem;">
            サイドバーでスタッフと条件を設定し、<br>
            「シフトを作成」ボタンをクリックしてください
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # クイックガイド
    st.markdown("""
    <div style="
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1.5rem;
        margin-top: 2rem;
    ">
        <div style="
            background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">👥</div>
            <h4 style="color: #1e40af; font-weight: 600; margin: 0;">Step 1</h4>
            <p style="color: #3730a3; font-size: 0.9rem; margin: 0.5rem 0 0 0;">スタッフを登録</p>
        </div>
        <div style="
            background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚙️</div>
            <h4 style="color: #92400e; font-weight: 600; margin: 0;">Step 2</h4>
            <p style="color: #a16207; font-size: 0.9rem; margin: 0.5rem 0 0 0;">条件を設定</p>
        </div>
        <div style="
            background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🚀</div>
            <h4 style="color: #065f46; font-weight: 600; margin: 0;">Step 3</h4>
            <p style="color: #047857; font-size: 0.9rem; margin: 0.5rem 0 0 0;">シフト作成</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
