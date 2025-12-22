import streamlit as st
import pandas as pd
import calendar
import streamlit_authenticator as stauth

# ==========================================
# 0. 認証の設定 (v55 ログ解析に基づく修正版)
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

# ログイン画面の表示 (v55修正: エラー回避のためキーワード引数を使用)
# ログに出ていた ValueError を解消するための書き方です。
authenticator.login(location='main')

# ログイン状態の確認
status = st.session_state.get("authentication_status")

if status:
    # ------------------------------------------
    # ログイン成功時
    # ------------------------------------------
    with st.sidebar:
        st.write(f"ようこそ {st.session_state.get('name')} さん")
        authenticator.logout('ログアウト', 'sidebar')
        st.markdown("---")

    st.title("🗓️ Shift Manager Pro v55")
    st.success("ログインに成功しました。")
    
    # 以前のシフト作成画面がここに入ります（動作確認のため一旦メッセージのみ）
    st.write("この画面が表示されていれば、認証システムは正常に稼働しています。")

elif status is False:
    st.error('ユーザー名、またはパスワードが違います。')
    st.info("テスト用： admin / abc123")

else:
    st.warning('ご利用にはログインが必要です。')
    st.info("テスト用： admin / abc123")
    
    st.markdown("---")
    st.subheader("💎 有料版の申し込み")
    st.write("継続して利用するには、アカウントの登録が必要です。")
    paypal_url = "https://www.paypal.com/jp/home" 
    st.link_button("PayPalで月額 1,000円を支払う", paypal_url)
