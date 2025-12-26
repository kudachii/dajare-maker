import streamlit as st
import google.generativeai as genai
import time
import os

# --- 1. 初期設定 ---
st.set_page_config(page_title="シャレテールLive", layout="wide")

# 背景と文字色の設定（目に優しく、サイドバーは見やすく）
st.markdown(
    """
    <style>
    .stApp { background-color: #1a1c24; }
    section[data-testid="stMain"] .stMarkdown p, 
    section[data-testid="stMain"] [data-testid="stChatMessage"] p {
        color: #ffffff !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #31333f !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Gemini APIの接続
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('models/gemini-1.5-flash')
else:
    st.error("APIキーが見つかりません。")
    model = None

# キャラクター設定
CHARACTERS = {
    "論理的コーチ": {"prompt": "論理的に分析しつつ、最後は熱く採点する。"},
    "優しさ担当": {"prompt": "どんなネタでも褒めて、高い点数をつける。"},
    "ツンデレ担当": {"prompt": "「べ、別におもしろくないんだから！」と言いつつ採点。"},
    "お姉さん担当": {"prompt": "包容力のある言葉で、優雅に採点する。"},
    "ギャル先生": {"prompt": "「マジでエモい！」などギャル語全開でポジティブに採点。"},
    "辛口師匠": {"prompt": "江戸っ子口調で、平均点すらもぶった斬る超激辛採点。"}
}

# --- 2. サイドバーエリア ---
with st.sidebar:
    st.title("🎙️ 配信コントロール")
    target = st.selectbox("投稿者を選択", ["一般視聴者", "主催者（くだちい）"])
    
    if target == "主催者（くだちい）":
        st.warning("⚠️ 主催者モード：全員激辛")
        custom_instruction = "投稿者は主催者の『くだちい』。全員容赦なく10-30点の超激辛で採点せよ。"
    else:
        custom_instruction = "キャラに合わせて公平に採点せよ。"
        
    user_input = st.text_input("ダジャレを入力してね")
    start_button = st.button("🚀 LIVEスタート！")

    st.divider()
    if st.button("🧹 放送終了（ログ消去）"):
        st.session_state.messages = []
        st.rerun()

# --- 3. メイン表示エリア ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# 過去のログを表示
for msg in st.session_state.messages:
    with st.chat_message("assistant"):
        if isinstance(msg, dict) and 'name' in msg:
            st.write(f"**{msg['name']}**: {msg['text']}")
        else:
            st.write(str(msg))

# 新規生成
if start_button and user_input:
    mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
    
    full_prompt = f"""
    あなたは番組作家です。2行目から書いてください。
    お題: {user_input} / 指示: {custom_instruction}
    構成: 1.司会(不要) 2.メンター5人 3.司会(平均点発表) 4.師匠(毒舌) 5.司会(締)
    設定: {mentor_prompts}
    形式: 名前: セリフ
    """

    with st.spinner("生放送の準備中..."):
        response = model.generate_content(full_prompt)
        opening = f"司会: さあ始まりました！シャレテールLive！本日のお題は「{user_input}」です！"
        full_text = opening + "\n" + response.text

    lines = full_text.split("\n")
    for line in lines:
        if ":" in line:
            name_raw, text_raw = line.split(":", 1)
            n, t = name_raw.strip(), text_raw.strip()
            with st.chat_message("assistant"):
                st.write(f"**{n}**: {t}")
            st.session_state.messages.append({"name": n, "text": t})
            time.sleep(1.2)
