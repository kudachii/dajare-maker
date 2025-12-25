import streamlit as st
import google.generativeai as genai
import time

# ページ設定
st.set_page_config(page_title="Shall Tell Live!", page_icon="🎙️")

# --- API初期化 (自動探索版) ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_priority = ['models/gemini-1.5-flash', 'models/gemini-pro', 'gemini-1.5-flash']
        selected_model_name = next((m for m in target_priority if m in available_models), None)
        model = genai.GenerativeModel(selected_model_name) if selected_model_name else None
    except:
        model = None
else:
    model = None

# キャラクター定義
CHARACTERS = {
    "優しさに溢れるメンター": {"icon": "🌈", "prompt": "温かく寄り添う全肯定"},
    "ツンデレな指導員": {"icon": "💢", "prompt": "厳しくも愛があるツンデレ"},
    "頼れるお姉さん": {"icon": "👩‍💼", "prompt": "包み込むように励ます大人の女性"},
    "論理的コーチ": {"icon": "🧐", "prompt": "感情を排除し論理的に分析する"},
    "ギャル先生": {"icon": "✨", "prompt": "超ポジティブにアゲるギャル語"},
    "辛口師匠": {"icon": "🍶", "prompt": "江戸っ子の毒舌落語家。最後にオチをつける"}
}

st.title("🎙️ Shall Tell オート会議システム")

if "messages" not in st.session_state:
    st.session_state.messages = []

# サイドバー
with st.sidebar:
    st.title("大会進行パネル")
    target_dajare = st.text_input("いじり倒すダジャレを入力")
    
    if st.button("AI会議スタート！"):
        if model and target_dajare:
            st.session_state.messages = [] # 会議ごとにリセット
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            prompt = f"「{target_dajare}」について、以下の6人でチャット会話。形式「名前: セリフ」。\n{mentor_prompts}"
            
            with st.spinner("AIたちが作戦会議中..."):
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                for line in lines:
                    if ":" in line:
                        parts = line.split(":", 1)
                        name = parts[0].replace("*", "").strip()
                        content = parts[1].strip()
                        if name in CHARACTERS:
                            st.session_state.messages.append({"role": name, "content": content, "icon": CHARACTERS[name]["icon"]})

# --- チャット表示（ここが演出の肝！） ---
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar=msg["icon"]):
        st.write(f"**{msg['role']}**")
        
        # 1文字ずつ表示するアニメーション
        placeholder = st.empty()
        full_text = ""
        for char in msg["content"]:
            full_text += char
            placeholder.markdown(full_text + "▌") # カーソル風の記号
            time.sleep(0.05) # 1文字ごとの速さ（ここを調整してね）
        placeholder.markdown(full_text)
    
    # 次の人が喋り出すまでの「間」
    time.sleep(1.0) # 1秒待機（ここが「間」だよ！）
