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
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%) !important;
        border-right: 1px solid #334155;
        min-width: 320px !important;
        width: 320px !important;
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 1.5rem;
        width: 320px !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #e2e8f0;
    }
    
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #e2e8f0 !important;
    }
    
    /* サイドバー幅の強制 */
    [data-testid="stSidebar"][aria-expanded="true"] {
        min-width: 320px !important;
        max-width: 320px !important;
    }
    
    /* サイドバーヘッダー */
    .sidebar-header {
        font-family: 'Outfit', 'Noto Sans JP', sans-serif;
        font-size: 0.8rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #a5b4fc;
        padding: 0.75rem 0.5rem;
        margin-bottom: 1rem;
        background: linear-gradient(90deg, rgba(99, 102, 241, 0.2), transparent);
        border-left: 3px solid #6366f1;
        border-radius: 0 8px 8px 0;
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
        color: #f1f5f9 !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #1d4ed8 0%, #4338ca 100%);
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
    }
    
    .stButton > button:not([kind="primary"]) {
        background: #334155;
        color: #f1f5f9 !important;
        border: 1px solid #475569;
    }
    
    .stButton > button:not([kind="primary"]):hover {
        background: #475569;
        border-color: #6366f1;
        color: #ffffff !important;
    }
    
    /* 入力フィールド */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        border-radius: 10px !important;
        border: 1.5px solid #475569 !important;
        padding: 0.6rem 0.9rem !important;
        font-family: 'Noto Sans JP', sans-serif !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
        background: #1e293b !important;
        color: #f1f5f9 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #64748b !important;
    }
    
    /* セレクトボックス */
    .stSelectbox > div > div {
        background: #1e293b !important;
        color: #f1f5f9 !important;
    }
    
    div[data-baseweb="select"] > div {
        background: #1e293b !important;
        border-color: #475569 !important;
    }
    
    div[data-baseweb="select"] span {
        color: #f1f5f9 !important;
    }
    
    /* エキスパンダー */
    .streamlit-expanderHeader {
        font-family: 'Noto Sans JP', sans-serif !important;
        font-weight: 500 !important;
        font-size: 0.95rem !important;
        background: #334155 !important;
        border-radius: 12px !important;
        border: 1px solid #475569 !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease;
        color: #f1f5f9 !important;
    }
    
    .streamlit-expanderHeader p {
        color: #f1f5f9 !important;
        font-size: 0.95rem !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: #3f4f63 !important;
        border-color: #6366f1 !important;
    }
    
    details[open] > .streamlit-expanderHeader {
        border-bottom-left-radius: 0 !important;
        border-bottom-right-radius: 0 !important;
        border-bottom: none !important;
        background: #3730a3 !important;
    }
    
    .streamlit-expanderContent {
        background: #1e293b !important;
        border: 1px solid #475569 !important;
        border-top: none !important;
        border-radius: 0 0 12px 12px !important;
        padding: 1rem !important;
    }
    
    /* サイドバー内のすべてのテキストを見えるように */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stTextInput label,
    section[data-testid="stSidebar"] .stNumberInput label {
        color: #cbd5e1 !important;
        font-weight: 500 !important;
    }
    
    /* サイドバーのエキスパンダー内のテキスト */
    section[data-testid="stSidebar"] details summary span {
        color: #f1f5f9 !important;
    }
    
    /* アラートボックス */
    .alert-container {
        background: #1e293b;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        border-left: 4px solid #f59e0b;
    }
    
    .alert-title {
        font-family: 'Outfit', 'Noto Sans JP', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        color: #f1f5f9;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .alert-item {
        padding: 0.5rem 0;
        font-size: 0.9rem;
        color: #cbd5e1;
        border-bottom: 1px solid #334155;
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
        background: linear-gradient(90deg, transparent, #475569, transparent);
        margin: 1.5rem 0;
    }
    
    /* カード */
    .info-card {
        background: #1e293b;
        border-radius: 14px;
        padding: 1.25rem;
        box-shadow: var(--shadow-md);
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
    
    .info-card-header {
        font-size: 0.85rem;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .info-card-value {
        font-size: 1.75rem;
        font-weight: 700;
        color: #f1f5f9;
    }
    
    /* フォーム */
    .stForm {
        background: rgba(51, 65, 85, 0.5);
        border-radius: 14px;
        padding: 1rem;
        border: 1px solid #475569;
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
        border: 2px dashed #475569 !important;
        padding: 1rem !important;
        transition: all 0.2s ease !important;
        background: #1e293b !important;
    }
    
    .stFileUploader > div:hover {
        border-color: #6366f1 !important;
        background: #334155 !important;
    }
    
    .stFileUploader label {
        color: #cbd5e1 !important;
    }
    
    .stFileUploader small,
    .stFileUploader span {
        color: #94a3b8 !important;
    }
    
    /* ファイルアップローダー内のテキスト */
    [data-testid="stFileUploader"] section {
        color: #e2e8f0 !important;
    }
    
    [data-testid="stFileUploader"] section small {
        color: #94a3b8 !important;
    }
    
    [data-testid="stFileUploader"] button {
        color: #f1f5f9 !important;
        background: #475569 !important;
        border: none !important;
    }
    
    /* ラベル */
    .stTextInput > label,
    .stNumberInput > label,
    .stSelectbox > label,
    label {
        font-family: 'Noto Sans JP', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        color: #cbd5e1 !important;
    }
    
    /* マークダウンテキスト */
    .stMarkdown, .stMarkdown p {
        color: #e2e8f0 !important;
    }
    
    /* small タグ */
    small {
        color: #94a3b8 !important;
    }
    
    /* スクロールバー */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1e293b;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* アニメーション */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.4s ease-out forwards;
    }
    
    /* Streamlit固有の上書き */
    .stAlert {
        background: #1e293b !important;
        border: 1px solid #475569 !important;
        border-radius: 12px !important;
    }
    
    div[data-testid="stExpander"] details {
        border: none !important;
    }
</style>
""", unsafe_allow_html=True)

# ファイルアップローダーの日本語化（JavaScript注入）
import streamlit.components.v1 as components
components.html("""
<script>
function translateFileUploader() {
    const parent = window.parent.document;
    
    // ドロップゾーンのテキスト
    const spans = parent.querySelectorAll('[data-testid="stFileUploadDropzone"] span');
    spans.forEach(span => {
        if (span.textContent.includes('Drag and drop')) {
            span.textContent = 'ここにファイルをドロップ';
        }
    });
    
    // ファイルサイズ制限のテキスト
    const smalls = parent.querySelectorAll('[data-testid="stFileUploadDropzone"] small');
    smalls.forEach(small => {
        if (small.textContent.includes('Limit')) {
            small.textContent = '上限 200MB • JSON形式';
        }
    });
    
    // ボタンのテキスト
    const buttons = parent.querySelectorAll('[data-testid="stFileUploadDropzone"] button');
    buttons.forEach(btn => {
        if (btn.textContent.includes('Browse')) {
            btn.textContent = 'ファイルを選択';
        }
    });
}

// 初回実行と定期実行（DOMが読み込まれるまで待機）
setTimeout(translateFileUploader, 100);
setTimeout(translateFileUploader, 500);
setTimeout(translateFileUploader, 1000);
setInterval(translateFileUploader, 1500);
</script>
""", height=0)

# ヘッダー
st.markdown("""
<div class="main-header">
    <h1>✦ Shift Manager Pro</h1>
    <p>スマートなシフト自動作成ツール — 連勤ルール対応版</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. セッション状態の初期化
# ==========================================
if "staff_list" not in st.session_state:
    st.session_state.staff_list = [
        {"name": "スタッフA", "type": 0},
        {"name": "スタッフB", "type": 0}
    ]

if "input_year" not in st.session_state: st.session_state.input_year = 2026
if "input_month" not in st.session_state: st.session_state.input_month = 2
if "target_off" not in st.session_state: st.session_state.target_off = 9

# ==========================================
# 3. 設定の読込コールバック
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

# ==========================================
# 4. サイドバー構成
# ==========================================
with st.sidebar:
    # --- シフト作成ボタン（一番上） ---
    if st.button("🚀 シフトを作成", type="primary", use_container_width=True):
        st.session_state.run_solver = True
    else:
        st.session_state.run_solver = False
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # --- 設定ファイル ---
    st.markdown('<div class="sidebar-header">📂 設定ファイル</div>', unsafe_allow_html=True)
    st.file_uploader("ファイルをドラッグ＆ドロップ", type=["json"], key="setting_file_uploader", on_change=load_settings_callback)
    if st.session_state.get("load_success_flag", False):
        st.success("✓ 復元完了")
        st.session_state.load_success_flag = False
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # --- シフト設定 ---
    st.markdown('<div class="sidebar-header">📅 シフト設定</div>', unsafe_allow_html=True)

    col_y, col_m = st.columns(2)
    with col_y: YEAR = st.number_input("年", 2025, 2030, key="input_year")
    with col_m: MONTH = st.number_input("月", 1, 12, key="input_month")

    _, DAYS = calendar.monthrange(YEAR, MONTH)
    
    TARGET_OFF_DAYS = st.number_input("常勤の公休数", 1, 15, key="target_off", help="目標となる公休日数を設定")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

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

# ==========================================
# 6. スタッフ管理（個人設定の下）
# ==========================================
st.sidebar.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-header">👥 スタッフ管理</div>', unsafe_allow_html=True)

with st.sidebar.form("add_staff_form", clear_on_submit=True):
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
    del_name = st.sidebar.selectbox("削除対象", [s["name"] for s in st.session_state.staff_list], key="del_select")
    if st.sidebar.button("🗑️ このスタッフを削除", use_container_width=True):
        st.session_state.staff_list = [s for s in st.session_state.staff_list if s["name"] != del_name]
        st.rerun()

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
        # カスタムアラートボックス
        alert_html = '<div style="background: #1e293b; border-radius: 16px; padding: 1.25rem; margin-bottom: 1.5rem; border: 1px solid #475569; box-shadow: 0 4px 20px rgba(0,0,0,0.2);">'
        alert_html += '<div style="font-weight: 600; font-size: 1rem; color: #f1f5f9; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.5rem;">📋 確認ポイント</div>'
        
        for alert_type, msg in alerts:
            if alert_type == "error":
                icon = "🔴"
                bg = "rgba(239, 68, 68, 0.15)"
                border = "#ef4444"
                color = "#fca5a5"
            elif alert_type == "warning":
                icon = "⚠️"
                bg = "rgba(245, 158, 11, 0.15)"
                border = "#f59e0b"
                color = "#fcd34d"
            else:
                icon = "ℹ️"
                bg = "rgba(59, 130, 246, 0.15)"
                border = "#3b82f6"
                color = "#93c5fd"
            
            alert_html += f'<div style="background: {bg}; border-left: 3px solid {border}; padding: 0.6rem 1rem; margin-bottom: 0.5rem; border-radius: 0 8px 8px 0;"><span style="color: {color}; font-size: 0.9rem;">{icon} {msg}</span></div>'
        
        alert_html += '</div>'
        st.markdown(alert_html, unsafe_allow_html=True)

    # ------------------------------------------
    # テーブル表示（HTMLテーブルで高品質レンダリング）
    # ------------------------------------------
    _, current_days = calendar.monthrange(current_year, current_month)
    weekdays_ja = ["月", "火", "水", "木", "金", "土", "日"]
    
    def get_shift_style(val_str):
        val = val_str.strip() if val_str else ""
        if val == '◎' or val_str == '◎ ':
            if val_str == '◎ ':  # 希望休 - シアン/ターコイズで目立たせる
                return 'background: linear-gradient(135deg, #0891b2, #22d3ee); color: #0c1a1a; font-weight: 700; box-shadow: 0 0 8px rgba(34, 211, 238, 0.5);'
            return 'background: #10b981; color: white;'  # 通常公休
        elif val == '有':
            return 'background: linear-gradient(135deg, #ec4899, #f472b6); color: white; font-weight: 600;'
        elif val == 'リ休':
            return 'background: linear-gradient(135deg, #f97316, #fb923c); color: white; font-weight: 600;'
        elif val == '夜':
            return 'background: linear-gradient(135deg, #3730a3, #6366f1); color: white; font-weight: 700; text-shadow: 0 1px 2px rgba(0,0,0,0.3);'
        elif val == '・':
            return 'background: #818cf8; color: white; font-weight: 600;'
        elif val == '早':
            return 'background: linear-gradient(135deg, #eab308, #facc15); color: #1a1a1a; font-weight: 700;'
        elif val == '遅':
            return 'background: linear-gradient(135deg, #ea580c, #f97316); color: white; font-weight: 700;'
        elif val == '日':
            return 'background: #f8fafc; color: #1e293b; font-weight: 600;'
        return 'background: #334155; color: #94a3b8;'
    
    # HTMLテーブル構築
    html_parts = ['''
    <style>
    .shift-table-container {
        background: #1e293b;
        border-radius: 16px;
        padding: 1.5rem;
        overflow-x: auto;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
    }
    .shift-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 3px;
        font-family: 'Noto Sans JP', sans-serif;
    }
    .shift-table th {
        background: #334155;
        color: #e2e8f0;
        padding: 10px 6px;
        font-size: 0.75rem;
        font-weight: 600;
        text-align: center;
        border-radius: 6px;
        white-space: nowrap;
    }
    .shift-table th.name-header {
        background: linear-gradient(135deg, #4f46e5, #7c3aed);
        color: white;
        min-width: 80px;
        position: sticky;
        left: 0;
        z-index: 10;
    }
    .shift-table th.weekend {
        background: #475569;
        color: #fbbf24;
    }
    .shift-table th.sunday {
        background: #7f1d1d;
        color: #fca5a5;
    }
    .shift-table td {
        padding: 8px 4px;
        text-align: center;
        font-size: 0.85rem;
        border-radius: 6px;
        min-width: 38px;
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .shift-table td:hover {
        transform: scale(1.1);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 5;
        position: relative;
    }
    .shift-table td.name-cell {
        background: #1e293b;
        color: #f1f5f9;
        font-weight: 600;
        text-align: left;
        padding-left: 12px;
        position: sticky;
        left: 0;
        z-index: 5;
        min-width: 80px;
        border-left: 3px solid #6366f1;
    }
    .shift-table td.summary-cell {
        background: #475569;
        color: #f1f5f9;
        font-weight: 700;
    }
    .shift-table tr.total-row td {
        background: #0f172a;
        color: #94a3b8;
        font-weight: 600;
        border-top: 2px solid #475569;
    }
    .shift-table tr.total-row td.shortage {
        background: #991b1b;
        color: #fecaca;
        font-weight: 700;
    }
    .shift-table tr.total-row td.name-cell {
        background: #0f172a;
        color: #94a3b8;
        border-left: 3px solid #475569;
    }
    .legend-container {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 1rem;
        padding: 1rem;
        background: #1e293b;
        border-radius: 12px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 0.8rem;
        color: #cbd5e1;
    }
    .legend-badge {
        width: 28px;
        height: 22px;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 600;
    }
    </style>
    <div class="shift-table-container">
    <table class="shift-table">
    <thead><tr>
    <th class="name-header">スタッフ</th>
    ''']
    
    # ヘッダー行（日付）
    for d in range(1, current_days + 1):
        date_obj = datetime.date(current_year, current_month, d)
        wd_idx = date_obj.weekday()
        wd = weekdays_ja[wd_idx]
        
        th_class = ""
        if wd_idx == 6:  # 日曜
            th_class = ' class="sunday"'
        elif wd_idx == 5:  # 土曜
            th_class = ' class="weekend"'
        
        html_parts.append(f'<th{th_class}>{d}<br><span style="font-size:0.65rem">{wd}</span></th>')
    
    html_parts.append('<th>夜勤</th><th>公休</th></tr></thead><tbody>')
    
    # データ行
    for name in df_raw.index:
        html_parts.append('<tr>')
        html_parts.append(f'<td class="name-cell">{name}</td>')
        
        night_count = 0
        off_count = 0
        
        for d in range(current_days):
            val = df_raw.loc[name].iloc[d]
            val_str = str(val) if val else ""
            val_clean = val_str.strip()
            
            if val_clean == '夜':
                night_count += 1
            if val_clean == '◎':
                off_count += 1
            
            style = get_shift_style(val_str)
            display_val = val_clean if val_clean else ""
            html_parts.append(f'<td style="{style}">{display_val}</td>')
        
        # 集計列
        html_parts.append(f'<td class="summary-cell">{night_count}</td>')
        html_parts.append(f'<td class="summary-cell">{off_count}</td>')
        html_parts.append('</tr>')
    
    # 合計行
    html_parts.append('<tr class="total-row">')
    html_parts.append('<td class="name-cell">日勤計</td>')
    
    for d in range(current_days):
        cnt = day_shift_counts.get(d, 0)
        td_class = ' class="shortage"' if cnt < 3 else ''
        html_parts.append(f'<td{td_class}>{cnt}</td>')
    
    html_parts.append('<td></td><td></td></tr>')
    html_parts.append('</tbody></table></div>')
    
    # 凡例
    html_parts.append('''
    <div class="legend-container">
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #eab308, #facc15); color: #1a1a1a;">早</div>早番</div>
        <div class="legend-item"><div class="legend-badge" style="background: #f8fafc; color: #1e293b;">日</div>日勤</div>
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #ea580c, #f97316); color: white;">遅</div>遅番</div>
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #3730a3, #6366f1); color: white;">夜</div>夜勤</div>
        <div class="legend-item"><div class="legend-badge" style="background: #818cf8; color: white;">・</div>明け</div>
        <div class="legend-item"><div class="legend-badge" style="background: #10b981; color: white;">◎</div>公休</div>
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #0891b2, #22d3ee); color: #0c1a1a;">◎</div>希望休</div>
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #ec4899, #f472b6); color: white;">有</div>有休</div>
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #f97316, #fb923c); color: white;">リ</div>リフレッシュ休暇</div>
    </div>
    ''')
    
    st.markdown(''.join(html_parts), unsafe_allow_html=True)
    
    # ダウンロードボタン
    st.markdown('<div style="margin-top: 1.5rem;"></div>', unsafe_allow_html=True)
    
    # CSV用のデータフレーム作成
    df_csv = df_raw.copy()
    df_csv = df_csv.replace("◎ ", "◎")
    
    # 列名を日付形式に変更
    csv_cols = []
    for d in range(1, current_days + 1):
        wd = weekdays_ja[datetime.date(current_year, current_month, d).weekday()]
        csv_cols.append(f"{d}({wd})")
    df_csv.columns = csv_cols
    
    # 夜勤・公休列を追加
    df_csv['夜勤'] = [list(map(str.strip, r)).count('夜') for r in df_raw.values]
    df_csv['公休'] = [list(map(str.strip, r)).count('◎') for r in df_raw.values]
    
    csv = df_csv.to_csv(sep=",").encode('utf-8_sig')
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
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
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        margin-top: 2rem;
        border: 1px solid #475569;
    ">
        <div style="font-size: 4rem; margin-bottom: 1rem;">📋</div>
        <h2 style="color: #f1f5f9; font-weight: 600; margin-bottom: 0.5rem;">シフトを作成しましょう</h2>
        <p style="color: #94a3b8; font-size: 1rem;">
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
            background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(55, 48, 163, 0.3);
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">👥</div>
            <h4 style="color: #c7d2fe; font-weight: 600; margin: 0;">Step 1</h4>
            <p style="color: #a5b4fc; font-size: 0.9rem; margin: 0.5rem 0 0 0;">スタッフを登録</p>
        </div>
        <div style="
            background: linear-gradient(135deg, #854d0e 0%, #a16207 100%);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(161, 98, 7, 0.3);
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">⚙️</div>
            <h4 style="color: #fef3c7; font-weight: 600; margin: 0;">Step 2</h4>
            <p style="color: #fde68a; font-size: 0.9rem; margin: 0.5rem 0 0 0;">条件を設定</p>
        </div>
        <div style="
            background: linear-gradient(135deg, #065f46 0%, #047857 100%);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 4px 20px rgba(4, 120, 87, 0.3);
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">🚀</div>
            <h4 style="color: #d1fae5; font-weight: 600; margin: 0;">Step 3</h4>
            <p style="color: #a7f3d0; font-size: 0.9rem; margin: 0.5rem 0 0 0;">シフト作成</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
