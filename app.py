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
        padding: 0.6rem 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-md);
        color: #f1f5f9 !important;
        height: 42px;
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
    
    /* サイドバー上部のボタン行を揃える */
    section[data-testid="stSidebar"] .stButton {
        margin-bottom: 0;
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

# ヘッダー
st.markdown("""
<div class="main-header">
    <h1>✦ Shift Manager Pro</h1>
    <p>最適なシフトを、ワンクリックで。</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. セッション状態の初期化
# ==========================================
if "staff_list" not in st.session_state:
    st.session_state.staff_list = []

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
# 4. 使い方ダイアログ
# ==========================================
@st.dialog("📖 使い方ガイド", width="large")
def show_help_dialog():
    st.markdown("""
    ### 🚀 シフト作成の流れ
    
    **Step 1. 設定ファイルの読み込み（任意）**
    > 以前保存した設定ファイル(.json)がある場合、ドロップして復元できます。
    
    **Step 2. シフト設定**
    > 対象の年月と、常勤スタッフの公休日数を設定します。
    
    **Step 3. 個人設定**
    > 各スタッフの希望シフト・希望休・夜勤目標などを設定します。
    
    **Step 4. シフト作成**
    > 「シフトを作成」ボタンをクリックすると、自動でシフトを作成します。
    
    ---
    
    ### 📅 年始固定シフトについて
    
    1月のシフトを作成する際、**1/1〜1/3のシフトをあらかじめ決めておきたい**場合に使用します。
    
    **使い方：**
    1. 個人設定でスタッフを展開
    2. 「年始固定シフト」にチェックを入れる
    3. 1日・2日・3日それぞれのシフトを選択
    
    > 💡 例：1/1に夜勤、1/2に明け、1/3に公休を入れたい場合は、それぞれ「夜」「・」「◎」を選択します。
    
    ---
    
    ### 📋 シフト記号の意味
    
    | 記号 | 説明 |
    |:---:|:---|
    | 早 | 早番 |
    | 日 | 日勤 |
    | 遅 | 遅番 |
    | 夜 | 夜勤 |
    | ・ | 夜勤明け |
    | ◎ | 公休 |
    | 有 | 有給休暇 |
    | リ休 | リフレッシュ休暇 |
    
    ---
    
    ### 👤 スタッフ属性について
    
    | 属性 | アイコン | 説明 |
    |:---:|:---:|:---|
    | 常勤 | 🔵 | 全シフト対応可能 |
    | パート(日勤) | 🟢 | 日勤のみ対応 |
    | パート(早番) | 🟡 | 早番のみ対応 |
    
    ---
    
    ### ⚠️ 確認ポイントについて
    
    シフト作成後、以下の問題がある場合はアラートが表示されます：
    
    - 🔴 **夜勤者なし** - その日の夜勤担当がいません
    - ⚠️ **日勤帯不足** - 日勤帯（早・日・遅）のスタッフが3名未満です
    - ℹ️ **目標未達** - 公休数や夜勤回数が目標と異なります
    
    ---
    
    ### 💾 設定の保存
    
    サイドバー下部の「設定を保存」ボタンで、現在の設定をファイルに保存できます。
    次回以降、このファイルを読み込むことで設定を復元できます。
    """)
    
    if st.button("閉じる", use_container_width=True):
        st.rerun()

# ==========================================
# 5. サイドバー構成
# ==========================================

# --- 進捗状態の計算 ---
def get_progress_status():
    """各ステップの進捗状態を計算"""
    status = {
        "staff": {"done": False, "count": 0, "icon": "⬜", "color": "#64748b"},
        "settings": {"done": False, "icon": "⬜", "color": "#64748b"},
        "personal": {"done": False, "configured": 0, "total": 0, "icon": "⬜", "color": "#64748b"},
        "ready": False
    }
    
    # Step 1: スタッフ登録
    staff_count = len(st.session_state.staff_list)
    status["staff"]["count"] = staff_count
    if staff_count >= 1:
        status["staff"]["done"] = True
        status["staff"]["icon"] = "✅"
        status["staff"]["color"] = "#22c55e"
    
    # Step 2: シフト設定（年月と公休数が設定されているか）
    year_set = st.session_state.get('input_year', 2025) is not None
    month_set = st.session_state.get('input_month', 1) is not None
    off_set = st.session_state.get('target_off', 9) is not None
    if year_set and month_set and off_set:
        status["settings"]["done"] = True
        status["settings"]["icon"] = "✅"
        status["settings"]["color"] = "#22c55e"
    
    # Step 3: 個人設定（常勤スタッフの夜勤目標が設定されているか）
    regulars = [s for s in st.session_state.staff_list if s.get("type", 0) == 0]
    status["personal"]["total"] = len(regulars)
    configured = 0
    for s in regulars:
        nm = s["name"]
        night_target = st.session_state.get(f"night_{nm}", 0)
        if night_target > 0:
            configured += 1
    status["personal"]["configured"] = configured
    
    # 個人設定は1つでも設定があればチェックマーク、なければグレー
    if configured > 0:
        status["personal"]["done"] = True
        status["personal"]["icon"] = "✅"
        status["personal"]["color"] = "#22c55e"
    # スタッフがいない、または設定が一つもない場合はグレーのまま
    
    # 全体の準備状態
    status["ready"] = status["staff"]["done"] and status["settings"]["done"]
    
    return status

progress = get_progress_status()

with st.sidebar:
    # --- メインCTAボタン（状態に応じて変化）---
    if not progress["staff"]["done"]:
        btn_label = "👥 まずスタッフを登録"
        btn_disabled = True
    elif not progress["ready"]:
        btn_label = "⚙️ 設定を完了してください"
        btn_disabled = True
    else:
        btn_label = "🚀 シフトを作成"
        btn_disabled = False
    
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button(btn_label, type="primary", use_container_width=True, disabled=btn_disabled, key="sidebar_create_btn"):
            st.session_state.run_solver = True
            st.rerun()
    with col_btn2:
        if st.button("❓", use_container_width=True):
            show_help_dialog()
    
    # --- 不足項目の表示 ---
    if not progress["ready"]:
        missing_items = []
        if not progress["staff"]["done"]:
            missing_items.append("スタッフ未登録")
        if not progress["settings"]["done"]:
            missing_items.append("シフト設定")
        
        st.markdown(f'''
        <div style="background: rgba(245, 158, 11, 0.1); border-radius: 8px; padding: 0.5rem 0.75rem; margin-top: 0.5rem; border-left: 3px solid #f59e0b;">
            <span style="color: #fcd34d; font-size: 0.8rem;">⚠️ 不足: {" / ".join(missing_items)}</span>
        </div>
        ''', unsafe_allow_html=True)
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # --- シフト設定（最初に設定する基本情報）---
    settings_status = progress["settings"]
    st.markdown(f'''
    <div class="sidebar-header">
        <span style="color: {settings_status["color"]};">{settings_status["icon"]}</span> 
        📅 シフト設定
    </div>
    ''', unsafe_allow_html=True)

    col_y, col_m = st.columns(2)
    with col_y: YEAR = st.number_input("年", 2025, 2030, key="input_year")
    with col_m: MONTH = st.number_input("月", 1, 12, key="input_month")

    _, DAYS = calendar.monthrange(YEAR, MONTH)
    
    TARGET_OFF_DAYS = st.number_input("常勤の公休数", 1, 15, key="target_off", help="目標となる公休日数を設定")
    
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ==========================================
# 5. スタッフ管理（スタッフを追加）
# ==========================================
staff_status = progress["staff"]
staff_label = f'<span style="font-size: 0.75rem; color: #94a3b8;">({staff_status["count"]}名)</span>' if staff_status["count"] > 0 else ''
st.sidebar.markdown(f'''
<div class="sidebar-header">
    <span style="color: {staff_status["color"]};">{staff_status["icon"]}</span> 
    👥 スタッフ管理 {staff_label}
</div>
''', unsafe_allow_html=True)

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
        st.session_state.shift_result = None
        st.session_state.shift_success = False
        st.rerun()

st.sidebar.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

# ==========================================
# 6. 各スタッフ詳細設定
# ==========================================
personal_status = progress["personal"]
if personal_status["total"] > 0:
    personal_label = f'<span style="font-size: 0.75rem; color: #94a3b8;">({personal_status["configured"]}/{personal_status["total"]}名)</span>'
else:
    personal_label = ''
st.sidebar.markdown(f'''
<div class="sidebar-header">
    <span style="color: {personal_status["color"]};">{personal_status["icon"]}</span> 
    👤 個人設定 {personal_label}
</div>
''', unsafe_allow_html=True)
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
        
        key_f1, key_f2, key_f3 = f"f1_{name}", f"f2_{name}", f"f3_{name}"
        open_fix_key = f"open_fix_{name}"
        
        # 初期化
        if key_f1 not in st.session_state: st.session_state[key_f1] = ""
        if key_f2 not in st.session_state: st.session_state[key_f2] = ""
        if key_f3 not in st.session_state: st.session_state[key_f3] = ""
        
        if st.checkbox("年始固定シフト", key=open_fix_key):
            fix_opts = ["", "早", "日", "遅", "夜", "・", "◎", "有", "リ休"]
            cols = st.columns(3)
            with cols[0]: 
                idx1 = fix_opts.index(st.session_state[key_f1]) if st.session_state[key_f1] in fix_opts else 0
                st.selectbox("1日", fix_opts, index=idx1, key=key_f1)
            with cols[1]: 
                idx2 = fix_opts.index(st.session_state[key_f2]) if st.session_state[key_f2] in fix_opts else 0
                st.selectbox("2日", fix_opts, index=idx2, key=key_f2)
            with cols[2]: 
                idx3 = fix_opts.index(st.session_state[key_f3]) if st.session_state[key_f3] in fix_opts else 0
                st.selectbox("3日", fix_opts, index=idx3, key=key_f3)
        
        # チェックボックスがチェックされている場合のみ、セッション状態から値を取得
        if st.session_state.get(open_fix_key, False):
            f1 = st.session_state.get(key_f1, "")
            f2 = st.session_state.get(key_f2, "")
            f3 = st.session_state.get(key_f3, "")
        else:
            f1, f2, f3 = "", "", ""

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
# 7. 設定ファイル（読み込み・保存）
# ==========================================
st.sidebar.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-header">💾 設定の保存・読込</div>', unsafe_allow_html=True)

# 設定ファイル読み込み
st.sidebar.markdown('<p style="color: #94a3b8; font-size: 0.8rem; margin-bottom: 0.5rem;">過去の設定を復元</p>', unsafe_allow_html=True)
st.sidebar.file_uploader("設定ファイル", type=["json"], key="setting_file_uploader", on_change=load_settings_callback, label_visibility="collapsed")
if st.session_state.get("load_success_flag", False):
    st.sidebar.success("✓ 復元完了")
    st.session_state.load_success_flag = False

# 保存ボタン
st.sidebar.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
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
# 7. 計算ロジック
# ==========================================
def solve_shift(staff_data):
    progress_text = "✨ シフトを最適化中..."
    my_bar = st.progress(0, text=progress_text)
    
    errors = []
    best_schedule = None
    best_score = -999999
    max_attempts = 2500

    # 勤務日数の上限計算
    work_limits = {}
    for s in staff_data:
        if s["type"] != 0:
            work_limits[s["name"]] = 99
        else:
            extra_off = len(s["refresh_days"]) + len(s["paid_leave_days"])
            work_limits[s["name"]] = DAYS - (TARGET_OFF_DAYS + extra_off)

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
        staff_info = next(s for s in staff_data if s["name"] == name)
        if day_idx == 0:
            return staff_info["prev_shift"].strip()
        return current_sched[name][day_idx - 1].strip()

    def check_reverse(prev, next_shift):
        """逆行チェック: True=逆行あり（禁止）"""
        # 日→早、遅→日、遅→早 は禁止
        if prev == "日" and next_shift == "早":
            return True
        if prev == "遅" and next_shift in ["早", "日"]:
            return True
        return False

    def count_consecutive_work(name, day_idx, current_sched):
        """day_idxの前までの連勤数をカウント"""
        staff_info = next(s for s in staff_data if s["name"] == name)
        streak = 0
        d = day_idx - 1
        while d >= 0:
            val = current_sched[name][d].strip()
            if is_work_shift(val):
                streak += 1
                d -= 1
            else:
                break
        # 月初の場合は前月からの連勤を加算
        if d < 0:
            streak += staff_info["prev_streak"]
        return streak

    def has_night_in_streak(name, day_idx, current_sched):
        """連勤中に夜勤があるかチェック"""
        staff_info = next(s for s in staff_data if s["name"] == name)
        d = day_idx - 1
        while d >= 0:
            val = current_sched[name][d].strip()
            if is_work_shift(val):
                if val in ["夜", "・"]:
                    return True
                d -= 1
            else:
                break
        # 前月末が夜勤関連かチェック
        if d < 0 and staff_info["prev_shift"].strip() in ["夜", "・"]:
            return True
        return False

    def check_rules(name, day_idx, current_sched, shift_type):
        """シフトルールをチェック（前後両方向）"""
        staff_info = next(s for s in staff_data if s["name"] == name)
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
        # 前方向の連勤
        streak_before = count_consecutive_work(name, day_idx, current_sched)
        
        # 後方向の連勤（翌日以降で既に勤務が入っている場合）
        streak_after = 0
        d = day_idx + 1
        while d < DAYS:
            val = current_sched[name][d].strip()
            if is_work_shift(val):
                streak_after += 1
                d += 1
            else:
                break

        # 夜勤は翌日の明けと合わせて2日分
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
            # 前後の連勤中に夜勤があるかチェック
            has_night = has_night_in_streak(name, day_idx, current_sched)
            
            # 後方向に夜勤があるかもチェック
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
            
            # 日勤帯のみの連勤数をカウント
            day_streak = 0
            # 前方向
            d = day_idx - 1
            while d >= 0:
                val = current_sched[name][d].strip()
                if val in ["早", "日", "遅"]:
                    day_streak += 1
                    d -= 1
                elif val in ["夜", "・"]:
                    break  # 夜勤系があれば連勤は別カウント
                else:
                    break
            # 今回の追加
            day_streak += 1
            # 後方向
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
            
            # 日勤帯のみで5連勤以上は禁止（夜勤を含まない場合）
            if day_streak >= 5 and not has_night:
                return False

        return True

    def can_place_night(name, day_idx, current_sched):
        """夜勤を配置できるかチェック"""
        staff_info = next(s for s in staff_data if s["name"] == name)
        
        if staff_info["type"] != 0:
            return False
        if current_sched[name][day_idx] != "":
            return False
        
        # 翌日（明け）が空いているか
        if day_idx + 1 < DAYS:
            next_val = current_sched[name][day_idx + 1].strip()
            if next_val not in ["", "・"]:
                return False
        
        # 明け翌日は◎のみ（有休・リ休は不可）
        if day_idx + 2 < DAYS:
            next2_val = current_sched[name][day_idx + 2].strip()
            if next2_val in ["有", "リ休"]:
                return False
            if next2_val not in ["", "◎"]:
                return False

        return check_rules(name, day_idx, current_sched, "夜")

    def count_day_staff(schedule, day_idx, shift_types):
        """特定の日の特定シフトの人数をカウント"""
        return sum(1 for s in staff_data if schedule[s["name"]][day_idx].strip() in shift_types)

    def count_required_off(day_idx, schedule):
        """その日の希望休・有休・リ休の数"""
        cnt = 0
        for s in staff_data:
            val = schedule[s["name"]][day_idx]
            if val == "◎ " or val.strip() in ["有", "リ休"]:
                cnt += 1
        return cnt

    for attempt in range(max_attempts):
        if attempt % 200 == 0:
            my_bar.progress(min(attempt / max_attempts, 0.95), text=progress_text)

        schedule = {s["name"]: [""] * DAYS for s in staff_data}
        night_counts = {s["name"]: 0 for s in staff_data}
        regulars = [s for s in staff_data if s["type"] == 0]

        # ========================================
        # Phase 1: 固定シフトと希望の設定
        # ========================================
        for s in staff_data:
            name = s["name"]

            # 年始固定シフト
            for i in range(min(3, DAYS)):
                if s["fixed_shifts"][i] != "":
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

        # ========================================
        # Phase 2: 夜勤希望の配置
        # ========================================
        for s in staff_data:
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

        # ========================================
        # Phase 3: 毎日の夜勤配置
        # ========================================
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

        # ========================================
        # Phase 4: 早番・遅番の配置（毎日各1名）
        # ========================================
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
                # パート(早番)も候補に
                for s in staff_data:
                    if s["type"] == 2 and schedule[s["name"]][d] == "":
                        candidates.append(s)
                if candidates:
                    random.shuffle(candidates)
                    schedule[candidates[0]["name"]][d] = "早"

        # ========================================
        # Phase 5: 日勤で埋める（勤務日数を考慮）
        # ========================================
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

        # ========================================
        # Phase 6: 公休の最適配置（人員不足日を避ける）
        # ========================================
        for s in regulars:
            name = s["name"]
            empty_days = [d for d in range(DAYS) if schedule[name][d] == ""]
            
            if not empty_days:
                continue

            # 各空き日の「人員余裕度」を計算
            day_scores = []
            for d in empty_days:
                # その日の日勤帯人数（仮に公休を入れた場合）
                day_cnt = count_day_staff(schedule, d, ["早", "日", "遅"])
                # 希望休等の固定休みの数
                fixed_off = count_required_off(d, schedule)
                # 余裕度 = 日勤帯人数 + 他の空きがある人数
                others_empty = sum(1 for s2 in regulars if s2["name"] != name and schedule[s2["name"]][d] == "")
                score = day_cnt + others_empty - fixed_off
                day_scores.append((d, score))

            # 余裕度が高い日から公休を配置
            day_scores.sort(key=lambda x: -x[1])
            for d, _ in day_scores:
                if check_rules(name, d, schedule, "◎"):
                    schedule[name][d] = "◎"

        # ========================================
        # Phase 7: 人員調整（不足解消）
        # ========================================
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
                            # 一時的に空にしてcheck_rulesでチェック
                            schedule[name][d] = ""
                            if check_rules(name, d, schedule, "早"):
                                schedule[name][d] = "早"
                                improved = True
                                break
                            else:
                                schedule[name][d] = "日"  # 元に戻す

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
                                # 他の余裕日を探す
                                other_days = []
                                for od in range(DAYS):
                                    if od != d and schedule[name][od] == "◎":
                                        od_total = count_day_staff(schedule, od, ["早", "日", "遅"])
                                        if od_total >= 3:
                                            other_days.append(od)
                                
                                if other_days:
                                    # 元の日を日勤に変更可能かチェック
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

        # ========================================
        # Phase 8: 早番・遅番過多の調整
        # ========================================
        for d in range(DAYS):
            early_cnt = count_day_staff(schedule, d, ["早"])
            late_cnt = count_day_staff(schedule, d, ["遅"])

            # 早番2名以上 → 1名を日勤に
            if early_cnt > 1:
                early_staff = [s for s in staff_data if schedule[s["name"]][d] == "早" and s["type"] == 0]
                for s in early_staff[1:]:
                    name = s["name"]
                    schedule[name][d] = ""
                    if check_rules(name, d, schedule, "日"):
                        schedule[name][d] = "日"
                        break
                    else:
                        schedule[name][d] = "早"

            # 遅番2名以上 → 1名を日勤に
            if late_cnt > 1:
                late_staff = [s for s in staff_data if schedule[s["name"]][d] == "遅" and s["type"] == 0]
                for s in late_staff[1:]:
                    name = s["name"]
                    schedule[name][d] = ""
                    if check_rules(name, d, schedule, "日"):
                        schedule[name][d] = "日"
                        break
                    else:
                        schedule[name][d] = "遅"

        # ========================================
        # スコアリング
        # ========================================
        score = 0

        for s in staff_data:
            if s["type"] == 0:
                cnt = sum(1 for x in schedule[s["name"]] if x.strip() == "◎")
                score -= abs(cnt - TARGET_OFF_DAYS) * 100

        for s in staff_data:
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

    my_bar.progress(100, text="✓ 完了しました")

    # エラー収集
    if best_schedule:
        for d in range(DAYS):
            if not any(best_schedule[s["name"]][d] == "早" for s in staff_data):
                errors.append(f"{d+1}日: 早番を配置できませんでした")
            if not any(best_schedule[s["name"]][d] == "遅" for s in staff_data):
                errors.append(f"{d+1}日: 遅番を配置できませんでした")
            if not any(best_schedule[s["name"]][d] == "夜" for s in staff_data):
                errors.append(f"{d+1}日: 夜勤を配置できませんでした")

    return best_schedule, errors

# ==========================================
# 8. メイン画面表示
# ==========================================
if st.session_state.get('run_solver', False):
    if not staff_data_list:
        st.error("⚠️ スタッフが登録されていません。サイドバーからスタッフを追加してください。")
        st.session_state.run_solver = False
    else:
        result, errors = solve_shift(staff_data_list)
        st.session_state.shift_result = result
        st.session_state.shift_errors = errors
        st.session_state.shift_success = True if result else False
        st.session_state.current_year = YEAR
        st.session_state.current_month = MONTH
        st.session_state.run_solver = False
        st.rerun()

if st.session_state.get('shift_success', False):
    current_year = st.session_state.current_year
    current_month = st.session_state.current_month
    result = st.session_state.shift_result
    shift_errors = st.session_state.get('shift_errors', [])
    
    # サクセスメッセージ
    st.markdown(f"""
    <div class="success-banner">
        <span>🎉</span>
        <div>シフト案を作成しました — {current_year}年{current_month}月</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 配置エラーがあれば表示
    if shift_errors:
        error_html = '<div style="background: #450a0a; border-radius: 12px; padding: 1rem; margin-bottom: 1rem; border: 1px solid #dc2626;">'
        error_html += '<div style="font-weight: 600; font-size: 0.9rem; color: #fca5a5; margin-bottom: 0.5rem;">⚠️ 人員配置の警告</div>'
        error_html += '<div style="color: #fecaca; font-size: 0.85rem;">'
        for err in shift_errors[:10]:  # 最大10件表示
            error_html += f'<div style="margin-bottom: 0.25rem;">• {err}</div>'
        if len(shift_errors) > 10:
            error_html += f'<div style="margin-top: 0.5rem; color: #f87171;">...他 {len(shift_errors) - 10} 件</div>'
        error_html += '</div></div>'
        st.markdown(error_html, unsafe_allow_html=True)
    
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
        s_info = next((s for s in staff_data_list if s["name"] == name), None)
        if s_info is None:
            continue  # スタッフが見つからない場合はスキップ
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
                return 'background: linear-gradient(135deg, #67e8f9, #a5f3fc); color: #0e7490; font-weight: 700; box-shadow: 0 0 6px rgba(34, 211, 238, 0.4);'
            return 'background: #86efac; color: #166534;'  # 通常公休 - 明るい緑
        elif val == '有':
            return 'background: linear-gradient(135deg, #f9a8d4, #fbcfe8); color: #9d174d; font-weight: 600;'
        elif val == 'リ休':
            return 'background: linear-gradient(135deg, #fdba74, #fed7aa); color: #9a3412; font-weight: 600;'
        elif val == '夜':
            return 'background: linear-gradient(135deg, #818cf8, #a5b4fc); color: #1e1b4b; font-weight: 700;'
        elif val == '・':
            return 'background: #c7d2fe; color: #3730a3; font-weight: 600;'
        elif val == '早':
            return 'background: linear-gradient(135deg, #fde047, #fef08a); color: #713f12; font-weight: 700;'
        elif val == '遅':
            return 'background: linear-gradient(135deg, #fb923c, #fdba74); color: #7c2d12; font-weight: 700;'
        elif val == '日':
            return 'background: #f1f5f9; color: #334155; font-weight: 600;'
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
    
    # 日勤帯合計行
    html_parts.append('<tr class="total-row">')
    html_parts.append('<td class="name-cell">日勤計</td>')
    
    for d in range(current_days):
        cnt = day_shift_counts.get(d, 0)
        td_class = ' class="shortage"' if cnt < 3 else ''
        html_parts.append(f'<td{td_class}>{cnt}</td>')
    
    html_parts.append('<td></td><td></td></tr>')
    
    # 早番人数行
    html_parts.append('<tr class="total-row">')
    html_parts.append('<td class="name-cell" style="font-size: 0.75rem; color: #fbbf24;">┗ 早</td>')
    for d in range(current_days):
        col_vals = [str(df_raw.loc[name].iloc[d]).strip() for name in df_raw.index]
        early_cnt = col_vals.count('早')
        td_style = 'background: #0f172a; color: #fbbf24; font-size: 0.75rem;'
        if early_cnt == 0:
            td_style = 'background: #7f1d1d; color: #fecaca; font-size: 0.75rem; font-weight: 700;'
        html_parts.append(f'<td style="{td_style}">{early_cnt}</td>')
    html_parts.append('<td></td><td></td></tr>')
    
    # 日勤人数行
    html_parts.append('<tr class="total-row">')
    html_parts.append('<td class="name-cell" style="font-size: 0.75rem; color: #e2e8f0;">┗ 日</td>')
    for d in range(current_days):
        col_vals = [str(df_raw.loc[name].iloc[d]).strip() for name in df_raw.index]
        day_cnt = col_vals.count('日')
        td_style = 'background: #0f172a; color: #e2e8f0; font-size: 0.75rem;'
        html_parts.append(f'<td style="{td_style}">{day_cnt}</td>')
    html_parts.append('<td></td><td></td></tr>')
    
    # 遅番人数行
    html_parts.append('<tr class="total-row">')
    html_parts.append('<td class="name-cell" style="font-size: 0.75rem; color: #fb923c;">┗ 遅</td>')
    for d in range(current_days):
        col_vals = [str(df_raw.loc[name].iloc[d]).strip() for name in df_raw.index]
        late_cnt = col_vals.count('遅')
        td_style = 'background: #0f172a; color: #fb923c; font-size: 0.75rem;'
        if late_cnt == 0:
            td_style = 'background: #7f1d1d; color: #fecaca; font-size: 0.75rem; font-weight: 700;'
        html_parts.append(f'<td style="{td_style}">{late_cnt}</td>')
    html_parts.append('<td></td><td></td></tr>')
    
    html_parts.append('</tbody></table></div>')
    
    # 凡例
    html_parts.append('''
    <div class="legend-container">
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #fde047, #fef08a); color: #713f12;">早</div>早番</div>
        <div class="legend-item"><div class="legend-badge" style="background: #f1f5f9; color: #334155;">日</div>日勤</div>
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #fb923c, #fdba74); color: #7c2d12;">遅</div>遅番</div>
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #818cf8, #a5b4fc); color: #1e1b4b;">夜</div>夜勤</div>
        <div class="legend-item"><div class="legend-badge" style="background: #c7d2fe; color: #3730a3;">・</div>明け</div>
        <div class="legend-item"><div class="legend-badge" style="background: #86efac; color: #166534;">◎</div>公休</div>
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #67e8f9, #a5f3fc); color: #0e7490;">◎</div>希望休</div>
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #f9a8d4, #fbcfe8); color: #9d174d;">有</div>有休</div>
        <div class="legend-item"><div class="legend-badge" style="background: linear-gradient(135deg, #fdba74, #fed7aa); color: #9a3412;">リ</div>リフレッシュ休暇</div>
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
    # 初期状態の表示 - シンプルな進捗表示
    
    # 進捗状況
    s1_done = progress["staff"]["done"]
    s2_done = progress["settings"]["done"]
    s3_done = progress["personal"]["configured"] > 0
    
    staff_count = progress["staff"]["count"]
    personal_count = progress["personal"]["configured"]
    personal_total = progress["personal"]["total"]
    
    # メインカード
    if progress["ready"]:
        # 準備完了状態
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #065f46 0%, #047857 100%);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 8px 30px rgba(0,0,0,0.25);
            margin-top: 0.5rem;
            border: 1px solid #10b981;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">✨</div>
            <h2 style="color: #d1fae5; font-weight: 600; margin: 0; font-size: 1.3rem;">準備完了！</h2>
            <p style="color: #a7f3d0; font-size: 0.9rem; margin: 0.5rem 0 0 0;">
                下のボタンをクリックしてシフトを作成
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div style="height: 1rem;"></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 シフトを作成", type="primary", use_container_width=True, key="main_create_btn"):
                st.session_state.run_solver = True
                st.rerun()
    else:
        # 設定中状態
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border-radius: 16px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 8px 30px rgba(0,0,0,0.25);
            margin-top: 0.5rem;
            border: 1px solid #475569;
        ">
            <div style="font-size: 2rem; margin-bottom: 0.5rem;">📋</div>
            <h2 style="color: #f1f5f9; font-weight: 600; margin: 0; font-size: 1.3rem;">シフトを作成しましょう</h2>
            <p style="color: #94a3b8; font-size: 0.9rem; margin: 0.5rem 0 0 0;">
                サイドバーで設定を完了してください
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
    
    # 進捗チェックリスト（横並び・コンパクト）
    st.markdown(f"""
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
        <div style="
            background: {'rgba(34, 197, 94, 0.15)' if s1_done else 'rgba(100, 116, 139, 0.1)'};
            border-radius: 12px;
            padding: 1.25rem 1rem;
            text-align: center;
            border: 1px solid {'#22c55e' if s1_done else '#475569'};
        ">
            <div style="
                width: 40px; height: 40px;
                background: {'#22c55e' if s1_done else '#475569'};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 1rem;
                color: white;
                margin: 0 auto 0.75rem auto;
            ">{'✓' if s1_done else '1'}</div>
            <div style="color: {'#86efac' if s1_done else '#94a3b8'}; font-weight: 600; font-size: 0.9rem;">スタッフ登録</div>
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.25rem;">{f'{staff_count}名' if staff_count > 0 else '未登録'}</div>
        </div>
        <div style="
            background: {'rgba(34, 197, 94, 0.15)' if s2_done else 'rgba(100, 116, 139, 0.1)'};
            border-radius: 12px;
            padding: 1.25rem 1rem;
            text-align: center;
            border: 1px solid {'#22c55e' if s2_done else '#475569'};
        ">
            <div style="
                width: 40px; height: 40px;
                background: {'#22c55e' if s2_done else '#475569'};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 1rem;
                color: white;
                margin: 0 auto 0.75rem auto;
            ">{'✓' if s2_done else '2'}</div>
            <div style="color: {'#86efac' if s2_done else '#94a3b8'}; font-weight: 600; font-size: 0.9rem;">シフト設定</div>
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.25rem;">年月・公休数</div>
        </div>
        <div style="
            background: {'rgba(34, 197, 94, 0.15)' if s3_done else 'rgba(100, 116, 139, 0.1)'};
            border-radius: 12px;
            padding: 1.25rem 1rem;
            text-align: center;
            border: 1px solid {'#22c55e' if s3_done else '#475569'};
        ">
            <div style="
                width: 40px; height: 40px;
                background: {'#22c55e' if s3_done else '#475569'};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 700;
                font-size: 1rem;
                color: white;
                margin: 0 auto 0.75rem auto;
            ">{'✓' if s3_done else '3'}</div>
            <div style="color: {'#86efac' if s3_done else '#94a3b8'}; font-weight: 600; font-size: 0.9rem;">個人設定</div>
            <div style="color: #64748b; font-size: 0.8rem; margin-top: 0.25rem;">{f'{personal_count}/{personal_total}名' if personal_total > 0 else '—'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # ヘルプボタン
    st.markdown('<div style="height: 1.5rem;"></div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📖 使い方ガイド", use_container_width=True):
            show_help_dialog()
