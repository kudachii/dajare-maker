import streamlit as st
import google.generativeai as genai
import time
import os

# --- 1. ページ設定 ---
st.set_page_config(page_title="Shall Tell Live 4.0", page_icon="🎙️", layout="wide")

# --- 音声合成用のJavaScript関数（キャラ別設定） ---
def speak_text(text, char_name):
    # キャラクターごとの声のパラメータ
    voice_settings = {
        "司会（Gemini）": {"pitch": 1.1, "rate": 1.1},
        "優しさに溢れるメンター": {"pitch": 1.3, "rate": 0.9},
        "ツンデレな指導員": {"pitch": 0.9, "rate": 1.1},
        "頼れるお姉さん": {"pitch": 1.0, "rate": 0.8},
        "論理적コーチ": {"pitch": 0.8, "rate": 1.0},
        "ギャル先生": {"pitch": 1.5, "rate": 1.3},
        "辛口師匠": {"pitch": 0.5, "rate": 0.8},
    }
    s = voice_settings.get(char_name, {"pitch": 1.0, "rate": 1.0})
    
    # JavaScriptを生成して実行（ブラウザの音声合成API）
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance();
    msg.text = "{text}";
    msg.lang = 'ja-JP';
    msg.pitch = {s['pitch']};
    msg.rate = {s['rate']};
    window.speechSynthesis.speak(msg);
    </script>
    """
    # 非表示のコンテナにJavaScriptを流し込む
    st.components.v1.html(js_code, height=0)

# --- 2. モデル初期化 (エラー回避の自動探索) ---
def init_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("APIキーが見つかりません。")
        return None
    
    genai.configure(api_key=api_key)
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_models = ["models/gemini-1.5-flash", "models/gemini-pro"]
        for target in target_models:
            for m in available_models:
                if target in m: return genai.GenerativeModel(m)
        if available_models: return genai.GenerativeModel(available_models[0])
    except:
        return genai.GenerativeModel("gemini-pro")
    return None

model = init_gemini()

# --- 3. キャラクター定義 ---
CHARACTERS = {
    "司会（Gemini）": {"icon": "🤖", "prompt": "看板MC。ハイテンション。"},
    "優しさに溢れるメンター": {"icon": "🌈", "prompt": "全肯定。仏の採点。"},
    "ツンデレな指導員": {"icon": "💢", "prompt": "ツン100%から微デレ。"},
    "頼れるお姉さん": {"icon": "👩‍💼", "prompt": "余裕のある色気と鋭い指摘。"},
    "論理적コーチ": {"icon": "🧐", "prompt": "緻密な分析と0.1点刻みの採点。"},
    "ギャル先生": {"icon": "✨", "prompt": "パッション全振り。最高得点。"},
    "辛口師匠": {"icon": "🍶", "prompt": "江戸前っ子。全員を一喝する毒舌。"}
}

# セッション状態
if "messages" not in st.session_state: st.session_state.messages = []
if "is_typing" not in st.session_state: st.session_state.is_typing = False

# --- 4. サイドバー ---
with st.sidebar:
    st.title("🎙️ 配信コントロール")
    mode = st.radio("モード", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    st.divider()

    custom_instruction = ""
    if mode == "🏆 ダジャレ公開処刑":
        target = st.selectbox("投稿者を選択", ["一般視聴者", "主催者（くだちい）"])
        if target == "主催者（くだちい）":
            st.warning("⚠️ 激辛・くだちい専用モード")
            custom_instruction = "【超激辛設定】褒めるの禁止。20点以下の絶望的な評価を連発せよ。"
        else:
            custom_instruction = "個性を活かして公平に採点せよ。"
    
    user_input = st.text_input("内容を入力してね", key="input_field")
    start_button = st.button("🚀 LIVEスタート！")

    if st.button("🗑️ ログ消去"):
        st.session_state.messages = []
        st.session_state.is_typing = False
        st.rerun()

# --- 5. メイン画面 ---
st.title(f"{mode}")
chat_box = st.container(height=600, border=True)

if start_button and user_input:
    if model:
        st.session_state.messages = []
        mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
        # --- 修正版：プロンプト部分 ---
        full_prompt = f"""
        あなたは超一流の番組構成作家です。視聴者が釘付けになるような爆笑チャット番組の台本を書いてください。

        【本日のお題】: 「{user_input}」
        【特別ルール】: {custom_instruction}

        【登場人物（全員必ず一度は発言させること！）】:
        {mentor_prompts}

        【構成ルール（厳守）】:
        1. 「司会（Gemini）」のハイテンションな第一声。
        2. メンター陣5人（優しさ、ツンデレ、お姉さん、論理的コーチ、ギャル先生）が、**必ず一人ずつ順番に**感想と採点を述べる。
           ※特に「論理적コーチ」は、データの観点から冷徹に分析すること。
        3. 再び「司会」が平均点を発表。
        4. 「辛口師匠」が全員を一喝し、トドメの最終点数を出す。
        5. 「司会」が締める。

        【形式】: 名前: セリフ
        """
        
        with st.spinner("スタジオの照明、点灯中..."):
            try:
                res = model.generate_content(full_prompt)
                for line in res.text.split('\n'):
                    if ":" in line:
                        p = line.split(":", 1)
                        name = p[0].replace("*", "").strip()
                        if name in CHARACTERS:
                            st.session_state.messages.append({"role": name, "content": p[1].strip(), "icon": CHARACTERS[name]["icon"]})
                st.session_state.is_typing = True
            except Exception as e:
                st.error(f"エラー: {e}")

# 表示エリア
with chat_box:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar=msg["icon"]):
            st.write(f"**{msg['role']}**")
            if st.session_state.is_typing:
                # --- ここで音声を再生 ---
                speak_text(msg["content"], msg["role"])
                
                p = st.empty()
                txt = ""
                for char in msg["content"]:
                    txt += char
                    p.markdown(txt + "▌")
                    time.sleep(0.16) # 音声の長さに合わせ少し調整
                p.markdown(txt)
                if i == len(st.session_state.messages) - 1:
                    st.session_state.is_typing = False
                time.sleep(0.8) # 次の人が喋るまでの「間」
            else:
                st.write(msg["content"])
