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
    /* メインエリア（チャット側）の背景と文字色 */
    .stApp {
        background-color: #1a1c24;
    }
    /* メインエリアのテキストだけを白くする（サイドバーを除外） */
    [data-testid="stHeader"], [data-testid="stChatMessage"] p, .stMarkdown p {
        color: #ffffff !important;
    }
    /* チャットボックスの枠 */
    [data-testid="stChatMessage"] {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    /* サイドバーの文字色は黒（デフォルト）のままにする */
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] label {
        color: #31333f !important;
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
            # --- 司会復活・台本固定プロンプト ---
            full_prompt = f"""
            # 【絶対厳守】書き出しは必ず「司会: 」という言葉から始めてください。
            # キャラクターのセリフ以外の解説文などは一切不要です。

            内容: 「{user_input}」についてのチャット番組「シャレテールLive」

            【登場人物】
            {mentor_prompts}

            【番組の進行（この順で1行ずつ出力）】
            1. 司会: 開始宣言とお題紹介（例：さあ始まりました！本日のお題は「{user_input}」です！）
            2. 各メンター（5人）: キャラ設定に基づいた感想と採点（100点満点）
            3. 司会: 5人の平均点を計算して発表
            4. 辛口師匠: 平均点をぶった斬る毒舌と、最終スコアの発表
            5. 司会: 締めの挨拶

            形式:
            名前: セリフ
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
