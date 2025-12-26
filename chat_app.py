import streamlit as st
import google.generativeai as genai
import time

# --- 1. ページ設定 ---
st.set_page_config(page_title="Shall Tell Live 3.0", page_icon="🎙️", layout="wide")

# --- 2. API初期化 ---
# --- 2. API初期化 (確実に動くモデルを自動探索) ---
@st.cache_resource
def init_model():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        try:
            # 使えるモデルをリストアップして、適切なものを選ぶ
            models = [m.name for m in genai.list_models() 
                     if 'generateContent' in m.supported_generation_methods]
            
            # 優先順位をつけて選択
            for target in ["models/gemini-1.5-flash", "models/gemini-pro", "gemini-1.5-flash", "gemini-pro"]:
                if target in models:
                    return genai.GenerativeModel(target)
            
            # どれも見つからなければ最初に見つかったものを使う
            if models:
                return genai.GenerativeModel(models[0])
        except Exception as e:
            st.error(f"モデルの取得中にエラーが発生しました: {e}")
            return None
    return None
    
# --- 3. キャラクター定義 ---
CHARACTERS = {
    "司会（Gemini）": {"icon": "🤖", "prompt": "進行役。知的で明るくメンターに振る。"},
    "優しさに溢れるメンター": {"icon": "🌈", "prompt": "全肯定で寄り添う採点。"},
    "ツンデレな指導員": {"icon": "💢", "prompt": "厳しくも愛があるツンデレ採点。"},
    "頼れるお姉さん": {"icon": "👩‍💼", "prompt": "大人の余裕で採点。"},
    "論理的コーチ": {"icon": "🧐", "prompt": "データに基づき論理分析して採点。"},
    "ギャル先生": {"icon": "✨", "prompt": "超ポジティブなアゲアゲ語で採点。"},
    "辛口師匠": {"icon": "🍶", "prompt": "毒舌で全てをぶった斬る。最後にオチ。"}
}

if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_typing" not in st.session_state:
    st.session_state.is_typing = False

# --- 4. サイドバー ---
with st.sidebar:
    st.title("🎙️ 配信コントロール")
    mode = st.radio("モード", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    st.divider()

    custom_instruction = ""
    if mode == "🏆 ダジャレ公開処刑":
        target = st.selectbox("投稿者を選択", ["一般視聴者", "主催者（くだちい）"])
        if target == "主催者（くだちい）":
            st.warning("⚠️ 主催者モード：全員激辛評価")
            custom_instruction = "【特別】投稿者は『くだちい』。全員10-30点の超激辛で採点せよ。"
        else:
            custom_instruction = "キャラに合わせた採点を行え。"
    
    user_input = st.text_input("内容を入力してね", key="input_field")

    if st.button("🚀 LIVEスタート！"):
        if model and user_input:
            st.session_state.messages = [] # リセット
            
            # --- 【重要】AIを呼ぶ前に司会の第一声を強制追加！ ---
            opening = f"さあ始まりました！シャレテールLive！本日のお題は「{user_input}」です！メンターの皆さん、いかがでしょうか？"
            st.session_state.messages.append({
                "role": "司会（Gemini）", "content": opening, "icon": CHARACTERS["司会（Gemini）"]["icon"]
            })

            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            full_prompt = f"あなたは番組作家です。司会の「{opening}」に続く台本を書いて。構成：メンター5人採点、司会平均点発表、辛口師匠総評、司会締。形式：名前: セリフ\n設定：\n{mentor_prompts}\n指示：{custom_instruction}"
            
            with st.spinner("スタジオ準備中..."):
                res = model.generate_content(full_prompt)
                for line in res.text.split('\n'):
                    if ":" in line:
                        p = line.split(":", 1)
                        name = p[0].replace("*", "").strip()
                        if name in CHARACTERS and name != "司会（Gemini）" or "司会" in name: # 司会が重複してもOKなように
                            st.session_state.messages.append({
                                "role": name, "content": p[1].strip(), "icon": CHARACTERS.get(name, CHARACTERS["司会（Gemini）"])["icon"]
                            })
                st.session_state.is_typing = True

    if st.button("🗑️ ログ消去"):
        st.session_state.messages = []
        st.session_state.is_typing = False
        st.rerun()

# --- 5. メイン画面（枠固定スクロール版） ---
st.title(f"{mode}")

# 枠の高さを固定（600px）して、その中でチャットを動かす
chat_box = st.container(height=600, border=True)

with chat_box:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar=msg["icon"]):
            st.write(f"**{msg['role']}**")
            if st.session_state.is_typing:
                p = st.empty()
                txt = ""
                for c in msg["content"]:
                    txt += c
                    p.markdown(txt + "▌")
                    time.sleep(0.03)
                p.markdown(txt)
                if i == len(st.session_state.messages) - 1:
                    st.session_state.is_typing = False
                time.sleep(0.8)
            else:
                st.write(msg["content"])

if not st.session_state.messages:
    st.info("左から入力して『LIVEスタート！』を押してね。")
