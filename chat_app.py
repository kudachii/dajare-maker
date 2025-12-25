import streamlit as st
import google.generativeai as genai
import time

# ページ設定
st.set_page_config(page_title="Shall Tell Live 3.0", page_icon="🎙️")

# --- API初期化 ---
@st.cache_resource
def init_model():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_priority = ['models/gemini-1.5-flash', 'models/gemini-pro']
            selected = next((m for m in target_priority if m in available_models), None)
            return genai.GenerativeModel(selected) if selected else None
        except: return None
    return None

model = init_model()

# キャラクター定義
CHARACTERS = {
    "司会（Gemini）": {"icon": "🤖", "prompt": "全体の進行役。知的で明るく、メンターに話を振る。"},
    "優しさに溢れるメンター": {"icon": "🌈", "prompt": "全肯定で寄り添う。"},
    "ツンデレな指導員": {"icon": "💢", "prompt": "厳しくも愛があるツンデレ。"},
    "頼れるお姉さん": {"icon": "👩‍💼", "prompt": "包み込む大人の余裕。"},
    "論理的コーチ": {"icon": "🧐", "prompt": "データに基づき論理分析。"},
    "ギャル先生": {"icon": "✨", "prompt": "超ポジティブなアゲアゲ語。"},
    "辛口師匠": {"icon": "🍶", "prompt": "江戸っ子の毒舌。最後にオチをつける。"}
}

# セッション状態
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- サイドバー ---
with st.sidebar:
    st.title("🎙️ 配信コントロール")
    mode = st.radio("配信モードを選択", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    
    if mode == "🏆 ダジャレ公開処刑":
        user_input = st.text_input("いじり倒すネタを入力")
        instruction = "司会がお題を出し、メンターがいじり、師匠がトドメ、最後に司会が締める。"
    else:
        user_input = st.text_area("議題・ニュースを入力")
        instruction = "司会がお題を出し、メンターが会議し、最後に司会が締める。"

    if st.button("🚀 LIVEスタート！", type="primary"):
        if model and user_input:
            # 1. 以前のログを消去
            st.session_state.messages = []
            
            # 2. AIにセリフを生成させる
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            full_prompt = f"内容:「{user_input}」\n設定:\n{mentor_prompts}\n指示: {instruction}\n形式: 名前: セリフ"
            
            with st.spinner("スタジオ準備中..."):
                res = model.generate_content(full_prompt)
                lines = res.text.split('\n')
                temp_messages = []
                for line in lines:
                    if ":" in line:
                        name, content = line.split(":", 1)
                        name = name.replace("*", "").strip()
                        if name in CHARACTERS:
                            temp_messages.append({"role": name, "content": content.strip(), "icon": CHARACTERS[name]["icon"]})
                
                # 3. 生成されたメッセージを一つずつセッションに追加して、その都度表示を更新する
                for msg in temp_messages:
                    st.session_state.messages.append(msg)
                    # ここで一度描画を走らせる
                    st.toast(f"{msg['role']}が発言中...")
                    time.sleep(1.0) # 思考してるような「間」
                    st.rerun()

    if st.button("🗑️ ログ消去"):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
st.title(f"{mode}")

# メッセージの表示（セッションにたまっているものを順に表示）
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg["icon"]):
        st.write(f"**{msg['role']}**")
        st.write(msg["content"])

if not st.session_state.messages:
    st.info("左のパネルからスタートしてね！")
