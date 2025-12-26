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
# --- サイドバーのモード切替と入力部分を修正 ---
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
            # 1. 履歴をリセット
            st.session_state.messages = []
            
            # 2. 【ここが重要！】司会の第一声をAI生成の「前」に強制追加
            opening_text = f"さあ始まりました！シャレテールLive！本日のお題は「{user_input}」です！メンターの皆さん、いかがでしょうか？"
            st.session_state.messages.append({
                "role": "司会（Gemini）", 
                "content": opening_text, 
                "icon": CHARACTERS["司会（Gemini）"]["icon"]
            })

            # 3. AIには「続き」だけを書かせる
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            full_prompt = f"""
            あなたは番組の構成作家です。
            先ほど司会が「{opening_text}」と言って番組が開始されました。
            あなたは、その「続き」から台本を書いてください。司会の最初の挨拶は書かないでください。

            【本日のお題】: {user_input}
            【特別ルール】: {custom_instruction}

            【構成案】
            1. メンター5人（優しさ、ツンデレ、お姉さん、論理、ギャル）: 順に感想と採点。
            2. 司会（Gemini）: 5人の平均点を発表。
            3. 辛口師匠: 毒舌で総評し、最終点数を発表。
            4. 司会（Gemini）: 番組を締める。

            【形式】: 名前: セリフ
            """

            with st.spinner("スタジオ準備中..."):
                res = model.generate_content(full_prompt)
                lines = res.text.split('\n')
                for line in lines:
                    if ":" in line:
                        parts = line.split(":", 1)
                        name = parts[0].replace("*", "").strip()
                        # キャラクター名が一致する場合のみ追加
                        if name in CHARACTERS:
                            st.session_state.messages.append({
                                "role": name, 
                                "content": parts[1].strip(), 
                                "icon": CHARACTERS[name]["icon"]
                            })
                
                # 表示演出を開始
                st.session_state.is_typing = True

    if st.button("🗑️ ログ消去"):
        st.session_state.messages = []
        st.session_state.is_typing = False
        st.rerun()

# --- メイン画面 ---
# --- 6. メイン画面 ---
st.title(f"{mode}")

# チャット欄の枠（高さ）を固定する！
# height の数値（500）を調整すれば、お好みの高さにできます
chat_container = st.container(height=600, border=True)

with chat_container:
    # この中でメッセージを表示
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar=msg["icon"]):
            st.write(f"**{msg['role']}**")
            
            if st.session_state.is_typing:
                placeholder = st.empty()
                full_text = ""
                for char in msg["content"]:
                    full_text += char
                    placeholder.markdown(full_text + "▌")
                    time.sleep(0.03)
                placeholder.markdown(full_text)
                
                if i == len(st.session_state.messages) - 1:
                    st.session_state.is_typing = False
                
                wait = 1.2 if "師匠" in msg["role"] or "司会" in msg["role"] else 0.6
                time.sleep(wait)
            else:
                st.write(msg["content"])

if not st.session_state.messages:
    st.info("左のパネルから入力して『LIVEスタート！』を押してね。")
