import streamlit as st
import google.generativeai as genai
import time
import os
import requests
import json
import base64

# --- 1. ページ設定 ---
st.set_page_config(page_title="Shall Tell Live 5.0", page_icon="🎙️", layout="wide")

# --- VOICEVOX連携設定 ---
# 起動しているVOICEVOXの各キャラIDを定義
VOX_CHARACTERS = {
    "司会（Gemini）": 3,          # ずんだもん（ノーマル）
    "優しさに溢れるメンター": 28,     # 四国めたん（ささやき）
    "ツンデレな指導員": 10,        # 雨晴はう（クールな女性）
    "頼れるお姉さん": 2,          # 四国めたん（ノーマル）
    "論理的なビジネスコーチ": 13,    # 青山龍星（熱血系だが低音）
    "ギャル先生": 0,              # 四国めたん（あまあま）
    "辛口師匠": 11,               # 玄野武宏（渋いおじさん）
}

def speak_text(text, char_name):
    # VOICEVOXのスピーカーIDを取得
    speaker_id = VOX_CHARACTERS.get(char_name, 3)
    base_url = "http://127.0.0.1:50021"
    
    try:
        # 1. 音声合成用のクエリを作成
        query_res = requests.post(
            f"{base_url}/audio_query",
            params={'text': text, 'speaker': speaker_id},
            timeout=10
        )
        query_res.raise_for_status()

        # 2. 音声データを生成
        synthesis_res = requests.post(
            f"{base_url}/synthesis",
            params={'speaker': speaker_id},
            data=json.dumps(query_res.json()),
            timeout=20
        )
        synthesis_res.raise_for_status()
        
        # 3. 再生用のHTMLタグを生成（controlsを付けて見えるようにします）
        audio_base64 = base64.b64encode(synthesis_res.content).decode("utf-8")
        # プレイヤーを見えるようにし、自動再生(autoplay)もセット
        audio_tag = f"""
            <audio autoplay="true" controls style="width: 100%; height: 30px;">
                <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
            </audio>
        """
        # プレイヤーを表示するためにheightを少し持たせる
        st.components.v1.html(audio_tag, height=50)
        
    except Exception as e:
        # エラーが出た場合のみ表示
        st.error(f"VOICEVOXエラー: {e}")

# --- 2. モデル初期化 ---
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
    "論理的なビジネスコーチ": {"icon": "🧐", "prompt": "緻密な分析と0.1点刻みの採点。"},
    "ギャル先生": {"icon": "✨", "prompt": "パッション全振り。最高得点。"},
    "辛口師匠": {"icon": "🍶", "prompt": "江戸前っ子。全員を一喝する毒舌。"}
}

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
            custom_instruction = """
            【最優先事項】投稿者は主催者の「くだちい」さんです。
            1. キャラクターは全員、積極的に「くだちいさん」と名前を呼んでください。
            2. 「ツンデレな指導員」は女性です。一切のデレを捨て、徹底的に冷たく、見下すような「ツン」100%で「くだちいさん、本気で言ってるの？」と罵倒してください。
            3. 「優しさに溢れるメンター」は、全人類の母のような全肯定。くだちいさんのどんなネタも「くだちいさん、あなたは神か仏か…！」と涙を流して拝んでください。
            4. くだちいさんは生ぬるい評価を嫌うので、師心の最終得点も含め、合計点は20点台以下の超絶激辛にしてください。
            """
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
        full_prompt = f"""
        あなたは超一流の番組構成作家です。視聴者が釘付けになるような爆笑チャット番組の台本を書いてください。

        【本日のお題】: 「{user_input}」
        【特別ルール】: {custom_instruction}

        【登場人物（全員必ず一度は発言させること！）】:
        {mentor_prompts}

        【構成ルール（厳守）】:
        1. 「司会（Gemini）」のハイテンションな第一声。
        2. メンター陣5人（優しさ、ツンデレ、お姉さん、論理的なビジネスコーチ、ギャル先生）が、**必ず一人ずつ順番に**感想と採点を述べる。
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
                # --- VOICEVOX再生を実行 ---
                speak_text(msg["content"], msg["role"])
                
                p = st.empty()
                txt = ""
                # VOICEVOXの生成時間を考慮し、タイピングを少しゆったりめに
                for char in msg["content"]:
                    txt += char
                    p.markdown(txt + "▌")
                    time.sleep(0.12)
                p.markdown(txt)
                if i == len(st.session_state.messages) - 1:
                    st.session_state.is_typing = False
                time.sleep(0.8) # 次の人が喋るまでの間隔
            else:
                st.write(msg["content"])
