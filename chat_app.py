import streamlit as st
import google.generativeai as genai
import time

# ページ設定
st.set_page_config(page_title="Shall Tell Live!", page_icon="🎙️")

# API初期化（secretsから読み込み）
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')

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

# お題の入力
with st.sidebar:
    st.title("大会進行パネル")
    target_dajare = st.text_input("いじり倒すダジャレを入力", placeholder="例：内科にないか？")
    
    if st.button("AI会議スタート！"):
        if target_dajare:
            # プロンプト作成
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            prompt = f"""
            ユーザーのダジャレ「{target_dajare}」について、以下の6人がチャットで会話しています。
            
            {mentor_prompts}

            条件：
            - チャット形式の台本を作成してください。
            - 1人1〜2発言程度。
            - お互いの発言に反応し合ってください。
            - 最後に辛口師匠が全員を黙らせるような毒舌で締めてください。
            
            出力形式：
            名前: セリフ
            """
            
            with st.spinner("AIたちが作戦会議中..."):
                response = model.generate_content(prompt)
                lines = response.text.split('\n')
                
                # 1行ずつ解析してセッションに追加
                for line in lines:
                    if ":" in line:
                        name, content = line.split(":", 1)
                        name = name.strip()
                        if name in CHARACTERS:
                            st.session_state.messages.append({
                                "role": name,
                                "content": content.strip(),
                                "icon": CHARACTERS[name]["icon"]
                            })

# チャット表示
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg["icon"]):
        st.write(f"**{msg['role']}**")
        st.write(msg["content"])
        time.sleep(0.5) # 少しだけディレイを入れてライブ感を出す
