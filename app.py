import streamlit as st
import random
import pandas as pd
import calendar
import datetime
import json
import copy
import streamlit_authenticator as stauth

# ==========================================
# 0. 認証設定
# ==========================================
# ユーザー名: admin
# パスワード: abc123
# 下の文字列はパスワードを暗号化したものです。
config = {
    'credentials': {
        'usernames': {
            'admin': {
                'name': '管理者',
                'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW',
            }
        }
    },
    'cookie': {
        'expiry_days': 30,
        'key': 'shift_manager_key_2025',
        'name': 'shift_cookie'
    }
}

# ==========================================
# 1. デザインの設定
# ==========================================
st.set_page_config(page_title="Shift Manager Pro v51", layout="wide", page_icon="🗓️")

st.markdown("""
    <style>
    .stApp { font-family: 'Helvetica Neue', Arial, sans-serif; }
    .stButton>button {
        width: 100%; border-radius: 12px; font-weight: bold;
        background-color: #FF4B4B; color: white; height: 3em;
    }
    section[data-testid="stSidebar"] { background-color: #f8f9fa; }
    </style>
""", unsafe_allow_html=True)

# 認証の準備
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# ログイン画面を表示
authenticator.login('main')

# 状態を確認
if st.session_state["authentication_status"]:
    # ログイン成功時の画面
    with st.sidebar:
        st.write(f"こんにちは、{st.session_state['name']} さん")
        authenticator.logout('ログアウト', 'sidebar')
        st.markdown("---")

    st.title("🗓️ Shift Manager Pro v51")
    st.caption("ログイン機能・PayPal決済リンク実装版")

    # ==========================================
    # 2. スタッフ管理
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
            new_type = st.selectbox("属性", ["常勤", "パート(日勤のみ)", "パート(早番のみ)"], index=0)
            submitted = st.form_submit_button("＋ 追加")
            if submitted and new_name:
                type_code = 0
                if new_type == "パート(日勤のみ)": type_code = 1
                elif new_type == "パート(早番のみ)": type_code = 2
                st.session_state.staff_list.append({"name": new_name, "type": type_code})
                st.success(f"{new_name}さんを追加しました")
                st.rerun()

        if st.session_state.staff_list:
            del_name = st.selectbox("削除対象", [s["name"] for s in st.session_state.staff_list])
            if st.button("削除を実行"):
                st.session_state.staff_list = [s for s in st.session_state.staff_list if s["name"] != del_name]
                st.rerun()
        st.markdown("---")

    # シフト設定
    with st.sidebar:
        st.header("📅 シフト設定")
        if "input_year" not in st.session_state: st.session_state.input_year = 2026
        if "input_month" not in st.session_state: st.session_state.input_month = 2
        col_y, col_m = st.columns(2)
        with col_y: YEAR = st.number_input("年", 2025, 2030, key="input_year")
        with col_m: MONTH = st.number_input("月", 1, 12, key="input_month")
        _, DAYS = calendar.monthrange(YEAR, MONTH)
        if "target_off" not in st.session_state: st.session_state.target_off = 9
        TARGET_OFF_DAYS = st.number_input("公休目標", 1, 15, key="target_off")
        if st.button("シフト案を作成", type="primary"):
            st.session_state.run_solver = True

    # 個別条件の設定
    SHIFT_OPTIONS = ["早", "日", "遅", "夜", "・", "◎", "有", "リ休"]
    staff_data_list = []
    def parse_days(input_str):
        if not input_str or not input_str.strip(): return []
        try:
            fixed = input_str.replace('，', ',').translate(str.maketrans('０１２３４５６７８９', '0123456789'))
            return sorted(list(set([int(x.strip()) for x in fixed.split(',') if x.strip().isdigit()])))
        except: return []

    for idx, staff in enumerate(st.session_state.staff_list):
        name = staff["name"]
        stype = staff["type"]
        with st.sidebar.expander(f"{name}", expanded=False):
            type_labels = ["常勤", "パート(日勤のみ)", "パート(早番のみ)"]
            new_type_label = st.selectbox("属性変更", type_labels, index=stype, key=f"t_{name}_{idx}")
            stype = type_labels.index(new_type_label)
            staff["type"] = stype
            
            c1, c2 = st.columns(2)
            if f"p_{name}" not in st.session_state: st.session_state[f"p_{name}"] = "◎"
            with c1: prev_shift = st.selectbox("前月末", SHIFT_OPTIONS, key=f"p_{name}")
            with c2:
                if f"s_{name}" not in st.session_state: st.session_state[f"s_{name}"] = 0
                prev_streak = st.number_input("連勤", 0, 10, key=f"s_{name}")
            
            if stype == 0:
                if f"n_{name}" not in st.session_state: st.session_state[f"n_{name}"] = 4
                night_tgt = st.number_input("夜勤目標", 0, 10, key=f"n_{name}")
            else: night_tgt = 0

            req_n = st.text_input("夜勤希望", key=f"rn_{name}")
            req_e = st.text_input("早番希望", key=f"re_{name}")
            req_l = st.text_input("遅番希望", key=f"rl_{name}")
            req_d = st.text_input("日勤希望", key=f"rd_{name}")
            off_in = st.text_input("希望休", key=f"of_{name}")

        staff_data_list.append({
            "name": name, "type": stype, "night_target": night_tgt,
            "req_night": parse_days(req_n), "req_early": parse_days(req_e),
            "req_late": parse_days(req_l), "req_day": parse_days(req_d),
            "req_off": parse_days(off_in), "prev_shift": prev_shift, 
            "prev_streak": prev_streak
        })

    # シフト計算
    def solve_shift(staff_data):
        my_bar = st.progress(0, text="計算中...")
        best_schedule = None
        best_score = -999999
        
        for attempt in range(1000):
            schedule = {s["name"]: [""] * DAYS for s in staff_data}
            # 簡易ロジック
            for s in staff_data:
                nm = s["name"]
                for d in s["req_off"]: schedule[nm][d-1] = "◎ "
                if s["type"] == 1:
                    for d in range(DAYS):
                        if not schedule[nm][d]: schedule[nm][d] = "日"
                elif s["type"] == 2:
                    for d in range(DAYS):
                        if not schedule[nm][d]: schedule[nm][d] = "早"
            
            for s in staff_data:
                for d in range(DAYS):
                    if not schedule[s["name"]][d]: schedule[s["name"]][d] = "◎"
            
            best_schedule = schedule
            break
        my_bar.progress(100, text="完了")
        return best_schedule

    if st.session_state.get('run_solver', False):
        res = solve_shift(staff_data_list)
        st.session_state.shift_result = res
        st.session_state.shift_success = True
        st.session_state.run_solver = False
        st.rerun()

    if st.session_state.get('shift_success'):
        st.success("シフト案を作成しました")
        df = pd.DataFrame(st.session_state.shift_result).T
        
        def color_shift(val):
            v = str(val)
            if v == '◎ ': return 'background-color: #15803d; color: white;'
            if v == '◎': return 'background-color: #dcfce7; color: black;'
            return 'background-color: white; color: black;'
            
        st.dataframe(df.style.applymap(color_shift), use_container_width=True)

elif st.session_state["authentication_status"] is False:
    st.error('ユーザー名またはパスワードが正しくありません')
    st.info("テスト用： admin / abc123")
    
elif st.session_state["authentication_status"] is None:
    st.warning('利用するにはログインをお願いします')
    st.info("テスト用： admin / abc123")
    
    # 決済への導線
    st.markdown("---")
    st.subheader("💎 有料プランのお申し込み")
    st.write("このツールを継続して利用するには、登録が必要です。")
    paypal_url = "https://www.paypal.com/jp/home" 
    st.link_button("PayPalで支払う (月額 ¥1,000)", paypal_url)
    st.caption("※お支払い後に、ログイン情報を送付します。")
