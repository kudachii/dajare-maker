import streamlit as st
import google.generativeai as genai
import time

# ページ設定
st.set_page_config(page_title="Shall Tell Live 3.0", page_icon="🎙️")

# --- API初期化 (自動探索) ---
@st.cache_resource
def init_model():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    return genai.GenerativeModel(m.name)
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

if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

# これをメイン画面の st.title の前に入れるだけで、背景に躍動感が出ます
# --- 背景を落ち着いた「深夜のラジオ局」風の色に修正 ---
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(-45deg, #0f172a, #1e293b, #334155);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #f8fafc;
    }
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    /* チャット枠を少しだけ明るくして読みやすく */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- サイドバー ---
with st.sidebar:
    st.title("🎙️ 配信コントロール")
    
    # 1. メインモードの選択
    mode = st.radio("配信モードを選択", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    
    st.divider()

    # 2. ダジャレモードの時だけ「誰が投稿したか」を選択
    custom_instruction = ""
    if mode == "🏆 ダジャレ公開処刑":
        target = st.selectbox("投稿者を選択", ["一般視聴者", "主催者（くだちい）"])
        if target == "主催者（くだちい）":
            st.warning("⚠️ 主催者モード：メンターが全員【辛口】になります")
            custom_instruction = "【特別ルール】投稿者は主催者の「くだちい」です。身内への厳しさとして、メンター全員が容赦ない『超辛口』で採点（10点〜30点台）してください。"
        else:
            custom_instruction = "通常のキャラ設定に合わせた採点を行ってください。"
    
    user_input = st.text_input("内容を入力してね", key="input_field")

    if st.button("🚀 LIVEスタート！"):
        if model and user_input:
            st.session_state.messages = [] 
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            
            # --- ここでプロンプトを組み立て！ ---
            # --- 司会・平均点・主催者激辛モード完全統合プロンプト ---
            full_prompt = f"""
            あなたはチャット番組「シャレテールLive」の司会兼・構成作家です。
            必ず以下の【構成】に従って、1人ずつの名前とセリフを生成してください。

            【本日のお題】: {user_input}
            【投稿者】: {target if 'target' in locals() else '一般'}
            【特別指示】: {custom_instruction}

            【構成ルール（絶対守ってください）】:
            1. 最初に必ず「司会: 」から始めて、元気よく番組をスタートさせてください。
            2. 次に、5人のメンターが順に「名前: セリフ」の形式で採点（100点満点）を行ってください。
            3. その後、必ず「司会: 」が全員の平均点を算出して発表してください。
            4. 次に「辛口師匠: 」が江戸っ子口調で平均点をぶった斬り、最終スコアをズバッと言ってください。
            5. 最後に必ず「司会: 」が番組を締めて終わってください。

            【設定】:
            {mentor_prompts}
            """
            
            # (以下、生成と表示のロジック...)
            
            with st.spinner("スタジオ準備中..."):
                res = model.generate_content(full_prompt)
                lines = res.text.split('\n')
                for line in lines:
                    if ":" in line:
                        parts = line.split(":", 1)
                        name = parts[0].replace("*", "").strip()
                        if name in CHARACTERS:
                            st.session_state.messages.append({"role": name, "content": parts[1].strip(), "icon": CHARACTERS[name]["icon"]})
                st.session_state.is_typing = True # 演出開始！

    if st.button("🗑️ ログ消去"):
        st.session_state.messages = []
        st.session_state.is_typing = False
        st.rerun()

# --- メイン画面 ---
st.title(f"{mode}")

# メッセージ表示ロジック
for i, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"], avatar=msg["icon"]):
        st.write(f"**{msg['role']}**")
        
        # 演出フラグが立っている場合、タイピング風に表示
        if st.session_state.is_typing:
            placeholder = st.empty()
            full_text = ""
            for char in msg["content"]:
                full_text += char
                placeholder.markdown(full_text + "▌")
                time.sleep(0.04) # タイピング速度
            placeholder.markdown(full_text)
            
            # 最後の人まで終わったら演出終了
            if i == len(st.session_state.messages) - 1:
                st.session_state.is_typing = False
            
            # 次の人が喋るまでの「間」
            wait = 1.5 if "師匠" in msg["role"] or "司会" in msg["role"] else 0.8
            time.sleep(wait)
        else:
            # 演出が終わっている、またはログ表示の場合は一気に
            st.write(msg["content"])

if not st.session_state.messages:
    st.info("左のパネルから入力して『LIVEスタート！』を押してね。")
