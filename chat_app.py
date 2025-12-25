import streamlit as st
import google.generativeai as genai

# ページ設定
st.set_page_config(page_title="Shall Tell Live 3.0", page_icon="🎙️")

# --- API初期化 (ここが修正ポイント！) ---
@st.cache_resource
def init_model():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        try:
            # モデル名の指定を一番シンプルな形にする、
            # または利用可能なモデルをリストから直接取得する
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # 最初に見つかった「生成可能」なモデル（通常は flash や pro）を返す
                    return genai.GenerativeModel(m.name)
        except Exception as e:
            st.error(f"モデル探索エラー: {e}")
            return None
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

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- サイドバー ---
with st.sidebar:
    st.title("🎙️ 配信コントロール")
    mode = st.radio("配信モードを選択", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    user_input = st.text_input("内容を入力してね", key="input_field")

    if st.button("🚀 LIVEスタート！"):
        if not model:
            st.error("モデルの初期化に失敗しています。APIキーを確認してください。")
        elif user_input:
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            full_prompt = f"内容:「{user_input}」について、以下のキャラで会話劇を作って。形式「名前: セリフ」\n{mentor_prompts}"
            
            with st.spinner("AIがスタジオ入りしています..."):
                try:
                    res = model.generate_content(full_prompt)
                    new_messages = []
                    for line in res.text.split('\n'):
                        if ":" in line:
                            parts = line.split(":", 1)
                            name = parts[0].replace("*", "").strip()
                            content = parts[1].strip()
                            if name in CHARACTERS:
                                new_messages.append({"role": name, "content": content, "icon": CHARACTERS[name]["icon"]})
                    st.session_state.messages = new_messages
                except Exception as e:
                    st.error(f"生成エラーが発生しました: {e}")

# --- メイン画面 ---
st.title(f"{mode}")

if st.session_state.messages:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg["icon"]):
            st.write(f"**{msg['role']}**")
            st.write(msg["content"])
else:
    st.info("左のパネルから入力してボタンを押してね。")
