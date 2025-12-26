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

# --- サイドバー ---
with st.sidebar:
    st.title("🎙️ 配信コントロール")
    mode = st.radio("配信モードを選択", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    user_input = st.text_input("内容を入力してね", key="input_field")

    if st.button("🚀 LIVEスタート！"):
        if model and user_input:
            st.session_state.messages = [] # クリア
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            
            # 司会進行を含めたプロンプト
            # --- 司会進行・採点システム完全固定プロンプト ---
            full_prompt = f"""
            あなたは人気チャット番組の構成作家です。以下の内容で、視聴者が爆笑するような「会話劇」を書き上げてください。

            【本日のお題（ダジャレ）】: 「{user_input}」

            【登場人物と役割】:
            {mentor_prompts}

            【番組の進行ルール（厳守）】:
            1. [オープニング]: 司会（Gemini）が「さあ始まりました！本日のお題はこちら！」と元気よく登場し、お題を読み上げる。
            2. [メンター陣の反応]: 各メンターが順番に会話形式でリアクションする。発言の最後には必ず「キャラに合わせた基準での採点（100点満点）」を添えること。
            3. [師匠のトドメ]: 最後に「辛口師匠」が、メンターたちの甘さを一喝し、江戸っ子全開の毒舌でオチをつけた後、最終的な「番組認定スコア：〇〇点」をズバッと発表する。
            4. [エンディング]: 司会（Gemini）が、ひどいスコアに困惑したりフォローしたりしながら、視聴者に次回予告をして締める。

            【出力形式】:
            名前: セリフ
            （※必ずこの形式で、1行に一人の発言を書いてください）
            """
            
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
