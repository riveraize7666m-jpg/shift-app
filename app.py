import streamlit as st
import random
import pandas as pd
import calendar
import datetime
import json
import copy
import streamlit_authenticator as stauth

# ==========================================
# 0. 認証の設定 (v53 安定版)
# ==========================================
# ユーザー名: admin / パスワード: abc123
credentials = {
    'usernames': {
        'admin': {
            'name': '管理者',
            'password': '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW'
        }
    }
}

# 認証の準備
authenticator = stauth.Authenticate(
    credentials,
    'shift_cookie',
    'shift_key_2025',
    30
)

# ログイン画面の表示
# 戻り値を明示的に受け取ることで動作を安定させます
try:
    auth_result = authenticator.login('main')
except:
    # 古いバージョンの場合
    auth_result = authenticator.login('Login', 'main')

# ログイン状態をセッションから直接取得
status = st.session_state.get("authentication_status")

if status:
    # ------------------------------------------
    # ログイン成功
    # ------------------------------------------
    with st.sidebar:
        st.write(f"ようこそ {st.session_state.get('name')} さん")
        authenticator.logout('ログアウト', 'sidebar')
        st.markdown("---")

    st.title("🗓️ Shift Manager Pro v53")
    st.caption("ログイン機能・認証強化版")

    if "staff_list" not in st.session_state:
        st.session_state.staff_list = [
            {"name": "スタッフA", "type": 0},
            {"name": "スタッフB", "type": 0}
        ]

    with st.sidebar:
        st.header("👥 スタッフ管理")
        with st.form("add_staff", clear_on_submit=True):
            name_input = st.text_input("名前を入力")
            type_input = st.selectbox("属性", ["常勤", "パート(日勤のみ)", "パート(早番のみ)"])
            if st.form_submit_button("＋ 追加"):
                if name_input:
                    t_code = 0
                    if type_input == "パート(日勤のみ)": t_code = 1
                    elif type_input == "パート(早番のみ)": t_code = 2
                    st.session_state.staff_list.append({"name": name_input, "type": t_code})
                    st.rerun()

        if st.session_state.staff_list:
            del_target = st.selectbox("削除選択", [s["name"] for s in st.session_state.staff_list])
            if st.button("削除実行"):
                st.session_state.staff_list = [s for s in st.session_state.staff_list if s["name"] != del_target]
                st.rerun()
        st.markdown("---")

    with st.sidebar:
        st.header("📅 シフト設定")
        y_val = st.number_input("年", 2025, 2030, 2026)
        m_val = st.number_input("月", 1, 12, 2)
        if st.button("シフト案を作成", type="primary"):
            st.session_state.created = True

    if st.session_state.get("created"):
        st.success("シフト案を表示します")
        _, days_in_month = calendar.monthrange(y_val, m_val)
        dummy_data = {s["name"]: ["日"] * days_in_month for s in st.session_state.staff_list}
        st.dataframe(pd.DataFrame(dummy_data).T, use_container_width=True)

elif status is False:
    st.error('ユーザー名、またはパスワードが違います。')
    st.info("テスト用： admin / abc123")

else:
    st.warning('ログインをおねがいします。')
    st.info("テスト用： admin / abc123")
    
    st.markdown("---")
    st.subheader("💎 有料版の申し込み")
    st.write("継続して利用するには、登録がひつようです。")
    st.link_button("PayPalで月額 1,000円を支払う", "https://www.paypal.com/jp/home")
