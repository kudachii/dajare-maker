import streamlit as st
import google.generativeai as genai
import time

# ページ設定
st.set_page_config(page_title="Shall Tell Live 3.0", page_icon="🎙️", layout="centered")

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
    "司会（Gemini）": {"icon": "🤖", "prompt": "全体の進行役。知的で明るく、メンターたちに話を振ったり最後をまとめたりする。"},
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
if "playing" not in st.session_state:
    st.session_state.playing = False

# --- サイドバー ---
with st.sidebar:
    st.title("🎙️ 配信コントロール")
    mode = st.radio("配信モードを選択", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    st.divider()

    if mode == "🏆 ダジャレ公開処刑":
        user_input = st.text_input("いじり倒すネタを入力", key="dajare_key")
        instruction = "司会がお題を出し、各メンターがいじり、師匠がトドメを刺し、最後に司会が締める流れ。"
    else:
        user_input = st.text_area("議題・ニュースを入力", key="meeting_key")
        instruction = "司会が議題を出し、各メンターが賑やかに会議し、最後に司会がエモく締める流れ。"

    if st.button("🚀 LIVEスタート！", type="primary"):
        if model and user_input:
            st.session_state.messages = [] # 初期化
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            full_prompt = f"内容:「{user_input}」\n設定:\n{mentor_prompts}\n指示: {instruction}\n形式: 名前: セリフ"
            
            with st.spinner("スタジオ準備中..."):
                res = model.generate_content(full_prompt)
                for line in res.text.split('\n'):
                    if ":" in line:
                        name, content = line.split(":", 1)
                        name = name.replace("*", "").strip()
                        if name in CHARACTERS:
                            st.session_state.messages.append({"role": name, "content": content.strip(), "icon": CHARACTERS[name]["icon"]})
            st.session_state.playing = True # 演出開始フラグ

    if st.button("🗑️ ログ消去"):
        st.session_state.messages = []
        st.session_state.playing = False
        st.rerun()

# --- メイン画面 ---
st.title(f"{mode}")

# メッセージの表示（ここが演出ロジック）
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar=msg["icon"]):
        st.write(f"**{msg['role']}**")
        
        # 新しいメッセージ（まだ演出してないもの）だけタイピング風にする
        if st.session_state.playing:
            placeholder = st.empty()
            full_text = ""
            for char in msg["content"]:
                full_text += char
                placeholder.markdown(full_text + "▌")
                time.sleep(0.03)
            placeholder.markdown(full_text)
            
            # 全員の演出が終わったらフラグを折るための処理（最後の人までいったら）
            if i == len(st.session_state.messages) - 1:
                st.session_state.playing = False
            
            time.sleep(0.8) # 次の人が喋るまでの間
        else:
            # すでに表示済みのものは一気に表示
            st.write(msg["content"])

if not st.session_state.messages:
    st.info("左のパネルからスタートしてね！")
elif not st.session_state.playing:
    st.success("🏁 配信終了！")
