import streamlit as st
import google.generativeai as genai
import time
import os

# --- 1. ページ設定 ---
st.set_page_config(page_title="Shall Tell Live 3.0", page_icon="🎙️", layout="wide")

# --- 2. モデル初期化 (エラー回避の自動探索) ---
def init_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("APIキーが見つかりません。")
        return None
    
    genai.configure(api_key=api_key)
    try:
        # 使えるモデルを自動で見つける
        available_models = [m.name for m in genai.list_models() 
                           if 'generateContent' in m.supported_generation_methods]
        
        # 1.5-flashを最優先、次にproを探す
        target_models = ["models/gemini-1.5-flash", "models/gemini-pro", "gemini-1.5-flash", "gemini-pro"]
        for target in target_models:
            if target in available_models:
                return genai.GenerativeModel(target)
        
        # 見つからなければ最初にあるものを使う
        if available_models:
            return genai.GenerativeModel(available_models[0])
    except Exception as e:
        # 万が一リスト取得に失敗したら一番標準的な名前を試す
        return genai.GenerativeModel("gemini-pro")
    return None

# 変数 "model" をここで確実に作成する
model = init_gemini()

# --- 3. キャラクター定義 ---
# --- 3. キャラクター定義（性格をパワーアップ！） ---
CHARACTERS = {
    "司会（Gemini）": {
        "icon": "🤖", 
        "prompt": "番組の看板MC。ハイテンションで『さあ盛り上がってまいりました！』『拍手！』など観客を煽り、メンターに熱く話を振る。平均点発表もドラマチックに行う。"
    },
    "優しさに溢れるメンター": {"icon": "🌈", "prompt": "仏のような全肯定。何を言っても『天才ですね！』と涙を流して喜ぶ採点。"},
    "ツンデレな指導員": {
        "icon": "💢", 
        "prompt": "最初は『ハァ？何これ、意味わかんないんだけど』と冷たく突き放すが、最後は顔を赤らめながら『……ま、まあ、少しはセンスあるんじゃない？フンッ！』とデレて、意外と高得点を出す採点。"
    },
    "頼れるお姉さん": {"icon": "👩‍💼", "prompt": "大人の色気と余裕。優しく耳元で囁くような口調で、鋭い指摘を混ぜながら採点。"},
    "論理적コーチ": {"icon": "🧐", "prompt": "メガネをクイッと上げながら、AIの計算速度を凌駕する超緻密な分析を行い、0.1点刻みで厳しく採点。"},
    "ギャル先生": {"icon": "✨", "prompt": "『マジ卍！』『それな！』と語彙力低めに、でも圧倒的なパッションで場をアゲる。常に最高得点に近い採点。"},
    "辛口師匠": {"icon": "🍶", "prompt": "江戸前っ子。メンター全員を『甘いんだよ！』と一喝し、ネタを木っ端微塵に砕く。オチとしての衝撃の点数を出す。"}
}
# セッション状態
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
            st.warning("⚠️ 主催者モード：全員激辛")
            custom_instruction = "投稿者は『くだちい』。全員10-30点の超激辛で採点せよ。忖度不要。"
        else:
            custom_instruction = "キャラに合わせた採点を行え。"
    
    user_input = st.text_input("内容を入力してね", key="input_field")
    start_button = st.button("🚀 LIVEスタート！")

    st.divider()
    if st.button("🗑️ ログ消去"):
        st.session_state.messages = []
        st.session_state.is_typing = False
        st.rerun()

# --- 5. メイン画面 ---
st.title(f"{mode}")

# 放送用コンテナ
chat_box = st.container(height=600, border=True)

# 実行処理
if start_button and user_input:
    if model:
        st.session_state.messages = [] # 初期化
        
        # 司会の第一声を即時追加
        opening = f"さあ始まりました！シャレテールLive！本日のお題は「{user_input}」です！メンター陣の皆さん、いかがでしょうか？"
        st.session_state.messages.append({"role": "司会（Gemini）", "content": opening, "icon": CHARACTERS["司会（Gemini）"]["icon"]})
        
        # プロンプト作成
        mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
        full_prompt = f"あなたは番組作家です。司会の「{opening}」に続く台本を書いて。構成：メンター5人採点、司会平均点発表、辛口師匠総評、司会締。形式：名前: セリフ\n設定：\n{mentor_prompts}\n指示：{custom_instruction}"
        
        try:
            res = model.generate_content(full_prompt)
            for line in res.text.split('\n'):
                if ":" in line:
                    p = line.split(":", 1)
                    name = p[0].replace("*", "").strip()
                    if name in CHARACTERS and name != "司会（Gemini）":
                        st.session_state.messages.append({"role": name, "content": p[1].strip(), "icon": CHARACTERS[name]["icon"]})
            st.session_state.is_typing = True
        except Exception as e:
            st.error(f"生成エラー: {e}")
    else:
        st.error("AIモデルの準備ができていません。APIキーを確認してください。")

# 表示エリア
with chat_box:
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"], avatar=msg["icon"]):
            st.write(f"**{msg['role']}**")
            if st.session_state.is_typing:
                p = st.empty()
                txt = ""
                for char in msg["content"]:
                    txt += char
                    p.markdown(txt + "▌")
                    time.sleep(0.02) # 少し速めに設定
                p.markdown(txt)
                if i == len(st.session_state.messages) - 1:
                    st.session_state.is_typing = False
                time.sleep(0.5)
            else:
                st.write(msg["content"])

if not st.session_state.messages:
    st.info("左から入力して『LIVEスタート！』を押してね。")
