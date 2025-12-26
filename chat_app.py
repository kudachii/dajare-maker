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
    .stApp { background-color: #1a1c24; }
    /* メインエリアの文字色（白） */
    section[data-testid="stMain"] .stMarkdown p, 
    section[data-testid="stMain"] [data-testid="stChatMessage"] p {
        color: #ffffff !important;
    }
    /* サイドバーの文字色（黒） */
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label {
        color: #31333f !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- サイドバーの設定エリア ---
with st.sidebar:
    st.title("🎙️ 配信コントロール")
    mode = st.radio("モード", ["🏆 ダジャレ公開処刑", "💬 戦略会議"])
    target = st.selectbox("投稿者", ["一般視聴者", "主催者（くだちい）"])
    
    if target == "主催者（くだちい）":
        custom_instruction = "【主催者モード】全員、超辛口（10-30点）で採点せよ！"
    else:
        custom_instruction = "各キャラらしく採点せよ。"
        
    user_input = st.text_input("内容を入力してね")
    start_button = st.button("🚀 LIVEスタート！")

    st.divider()
    if st.button("🧹 放送終了（ログ消去）"):
        st.session_state.messages = []
        st.rerun()
# --- ここからメインエリア（インデントを一番左に戻す） ---

# 1. ログの初期化と表示（安全装置付き）
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message("assistant"):
        if isinstance(msg, dict) and 'name' in msg:
            st.write(f"**{msg['name']}**: {msg['text']}")
        else:
            st.write(str(msg))

# 2. 「LIVEスタート！」が押された時の処理
if start_button and user_input:
    # メンター設定の準備
    mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
    
    full_prompt = f"""
    あなたは番組構成作家です。2行目（論理的コーチ）から台本を書いてください。
    【お題】: {user_input}
    【指示】: {custom_instruction}
    【構成】: 1.司会(不要) 2.メンター5人 3.司会(平均点) 4.師匠(毒舌) 5.司会(締)
    【設定】: {mentor_prompts}
    形式: 名前: セリフ
    """

    with st.spinner("生放送の準備中..."):
        response = model.generate_content(full_prompt)
        opening = f"司会: さあ始まりました！シャレテールLive！本日のお題は「{user_input}」です！"
        full_text = opening + "\n" + response.text

    # 1行ずつ表示して保存する
    lines = full_text.split("\n")
    for line in lines:
        if ":" in line:
            name, text = line.split(":", 1)
            name_clean = name.strip()
            text_clean = text.strip()
            
            # 画面に「間」を持って表示
            with st.chat_message("assistant"):
                st.write(f"**{name_clean}**: {text_clean}")
            
            # セッション（記録）に保存
            st.session_state.messages.append({"name": name_clean, "text": text_clean})
            
            # 1.2秒待機してライブ感を出す
            time.sleep(1.2)
# --- メイン画面での実行エリア（ここをサイドバーの外に出す） ---
if start_button:
    if model and user_input:
        st.session_state.messages = [] 
        mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
        
        # AIへの完全な指示書
        full_prompt = f"""
        あなたは人気チャット番組「シャレテールLive」の構成作家です。
        以下の指示に従い、一字一句、台本を書き出してください。
        1行目の司会の開始宣言はシステム側で用意するので、あなたは「2行目の論理的コーチ」から書き始めてください。

        【本日のお題】: 「{user_input}」
        【特別指示】: {custom_instruction}

        【台本作成ルール（厳守）】:
        1. 出力の1行目は「論理的コーチ: 」から始めてください。
        2. 各メンターは、今回の追加指示（特に主催者の場合は超辛口）を最優先して、手加減なしに「〇〇点」と採点してください。
        3. 5人の採点後、司会が必ず「計算した平均点は〇〇点です」と発表してください。
        4. 辛口師匠は、平均点すらも「甘ぇ！」とぶった斬り、さらに低い「最終スコア」を叩き出してください。
        5. 最後は司会が、ボコボコにされた現場を必死にまとめて締めてください。

        【名前リスト】: 論理的コーチ, 優しさ担当, ツンデレ担当, お姉さん担当, ギャル先生, 司会, 辛口師匠

        【キャラクター設定】:
        {mentor_prompts}

        【出力形式】: 名前: セリフ
        """

        # AI生成と司会の第一声を強制合体
        with st.spinner("生放送の準備中..."):
            response = model.generate_content(full_prompt)
            # 司会の第一声をプログラムで先頭に挿入
            opening = f"司会: さあ始まりました！シャレテールLive！本日のお題は「{user_input}」です！\n"
            full_text = opening + response.text

        # 1行ずつチャット形式でメイン画面に表示
        lines = full_text.split("\n")
        for line in lines:
            if ":" in line:
                name, text = line.split(":", 1)
                with st.chat_message("assistant"):
                    # メイン画面に「名前: セリフ」の形式で表示
                    st.write(f"**{name.strip()}**: {text.strip()}")
                time.sleep(1.0) # 1秒のディレイでライブ感を演出
                
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
