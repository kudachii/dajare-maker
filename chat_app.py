import streamlit as st
import time

# ページ設定
st.set_page_config(page_title="Shall Tell Live!", page_icon="🎙️")

# メンター設定（ギャル先生を先行追加！）
CHARACTERS = {
    "くだちい": {"icon": "👨‍💻", "color": "#f0f2f6"},
    "優しさに溢れるメンター": {"icon": "🌈", "color": "#fff4f4"},
    "ツンデレな指導員": {"icon": "💢", "color": "#f4f4ff"},
    "頼れるお姉さん": {"icon": "👩‍💼", "color": "#fff9f4"},
    "論理的コーチ": {"icon": "🧐", "color": "#f0f0f0"},
    "カサネ・イズミ": {"icon": "⚙️", "color": "#e0f7fa"},
    "ギャル先生": {"icon": "✨", "color": "#fff0f5"},
    "辛口師匠": {"icon": "🍶", "color": "#f5f5dc"}
}

st.title("🎙️ Shall Tell ライブ配信会場")
st.caption("2025-12-26: シャレテール杯 緊急公開処刑（？）会場")

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# サイドバー：発言者の選択
with st.sidebar:
    st.title("配信コントロール")
    speaker = st.selectbox("次に発言する人を選んでね", list(CHARACTERS.keys()))
    user_text = st.text_area("セリフを入力", placeholder="ここに喋らせたい内容を書くよ")
    
    if st.button("発言する！"):
        if user_text:
            st.session_state.messages.append({
                "role": speaker,
                "content": user_text,
                "icon": CHARACTERS[speaker]["icon"]
            })
            st.rerun()

    if st.button("ログをクリア"):
        st.session_state.messages = []
        st.rerun()

# チャット画面の表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg["icon"]):
        st.write(f"**{msg['role']}**")
        st.write(msg["content"])

# --- 使い方アドバイス ---
st.divider()
st.info("💡 使い方：左のサイドバーでキャラを選んで喋らせるだけ！一人で何役もこなして、爆笑の対談シーンを作ってスクショを撮ろう！")
