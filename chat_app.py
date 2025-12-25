import streamlit as st
import google.generativeai as genai

# ページ設定
st.set_page_config(page_title="Shall Tell Live 3.0", page_icon="🎙️")

# --- API初期化 ---
@st.cache_resource
def init_model():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        try:
            # 安全にモデルを選択
            return genai.GenerativeModel('gemini-1.5-flash')
        except: return None
    return None

model = init_model()

# キャラクター定義
CHARACTERS = {
    "司会（Gemini）": {"icon": "🤖", "prompt": "全体の進行役。"},
    "優しさに溢れるメンター": {"icon": "🌈", "prompt": "全肯定。"},
    "ツンデレな指導員": {"icon": "💢", "prompt": "ツンデレ。"},
    "頼れるお姉さん": {"icon": "👩‍💼", "prompt": "大人。"},
    "論理的コーチ": {"icon": "🧐", "prompt": "論理。"},
    "ギャル先生": {"icon": "✨", "prompt": "ギャル。"},
    "辛口師匠": {"icon": "🍶", "prompt": "毒舌。"}
}

# 1. セッションにメッセージを保存する場所を作る
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- サイドバー ---
with st.sidebar:
    st.title("🎙️ 配信コントロール")
    mode = st.radio("配信モードを選択", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    user_input = st.text_input("内容を入力してね")

    if st.button("🚀 LIVEスタート！"):
        if model and user_input:
            # AIへの命令（プロンプト）
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            full_prompt = f"内容:「{user_input}」について、以下のキャラで会話劇を作って。形式「名前: セリフ」\n{mentor_prompts}"
            
            # AIが生成
            with st.spinner("AIが考え中..."):
                res = model.generate_content(full_prompt)
                
                # いったんメッセージをリセット
                new_messages = []
                for line in res.text.split('\n'):
                    if ":" in line:
                        name, content = line.split(":", 1)
                        name = name.replace("*", "").strip()
                        if name in CHARACTERS:
                            new_messages.append({"role": name, "content": content.strip(), "icon": CHARACTERS[name]["icon"]})
                
                # セッションに保存
                st.session_state.messages = new_messages

# --- メイン画面 ---
st.title(f"{mode}")

# 2. 保存されているメッセージをすべて表示する
if st.session_state.messages:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg["icon"]):
            st.write(f"**{msg['role']}**")
            st.write(msg["content"])
else:
    st.info("左のパネルから入力してボタンを押してね。")
