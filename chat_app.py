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
            selected = next((m for m in target_priority if m in available_models), available_models[0] if available_models else None)
            return genai.GenerativeModel(selected) if selected else None
        except: return None
    return None

model = init_model()

# キャラクター定義
CHARACTERS = {
    "優しさに溢れるメンター": {"icon": "🌈", "prompt": "全肯定で寄り添う"},
    "ツンデレな指導員": {"icon": "💢", "prompt": "厳しくも愛があるツンデレ"},
    "頼れるお姉さん": {"icon": "👩‍💼", "prompt": "包み込む大人の余裕"},
    "論理적コーチ": {"icon": "🧐", "prompt": "データに基づき論理分析"},
    "ギャル先生": {"icon": "✨", "prompt": "超ポジティブなアゲアゲ語"},
    "辛口師匠": {"icon": "🍶", "prompt": "江戸っ子の毒舌。最後に全員を黙らせるオチを"}
}

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- サイドバー：ここですべてをコントロール ---
with st.sidebar:
    st.title("🎙️ 配信コントロールパネル")
    
    # 【切り替えスイッチ】
    mode = st.radio("配信モードを選択", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    
    st.divider()

    # モードによって入力欄を動的に切り替え
    if mode == "🏆 ダジャレ公開処刑":
        st.subheader("🔥 ネタ投稿スロット")
        user_input = st.text_input("いじり倒すネタを入力", key="dajare_in")
        sys_prompt = "このダジャレを6人でチャット形式でボコボコにいじり倒して。最後に師匠がトドメを刺して。"
    else:
        st.subheader("📅 アジェンダ入力")
        user_input = st.text_area("議題やニュースを入力", key="meeting_in")
        sys_prompt = "この議題（ニュース）について、6人がチャット形式で賑やかに会議して。くだちいさんへの労いや未来への希望を語って。"

    # 実行ボタン
    if st.button("🚀 LIVEスタート！", type="primary"):
        if model and user_input:
            st.session_state.messages = [] # 会議のたびにログをリセット
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            
            full_prompt = f"以下の内容で6人のチャット会議を作成して。\n内容:「{user_input}」\nキャラ設定:\n{mentor_prompts}\n指示: {sys_prompt}\n形式: 名前: セリフ"
            
            with st.spinner("AIたちがスタジオに集結中..."):
                try:
                    res = model.generate_content(full_prompt)
                    for line in res.text.split('\n'):
                        if ":" in line:
                            name, content = line.split(":", 1)
                            name = name.replace("*", "").strip()
                            if name in CHARACTERS:
                                st.session_state.messages.append({"role": name, "content": content.strip(), "icon": CHARACTERS[name]["icon"]})
                    st.rerun()
                except Exception as e: st.error(f"エラー: {e}")

    if st.button("🗑️ ログを全消去"):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面 ---
st.title(f"{mode}")
st.write(f"現在のステージ： **{mode}**")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg["icon"]):
        st.write(f"**{msg['role']}**")
        placeholder = st.empty()
        full_text = ""
        for char in msg["content"]:
            full_text += char
            placeholder.markdown(full_text + "▌")
            time.sleep(0.04)
        placeholder.markdown(full_text)
    time.sleep(0.7)
