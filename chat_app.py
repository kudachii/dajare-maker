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
            st.warning("⚠️ 激辛・くだちい専用モード発動中")
            # ここでAIへの圧力を強めます
            custom_instruction = """
            【最優先事項】投稿者は主催者の「くだちい」です。
            彼は生ぬるい評価を嫌います。メンター全員、プロとして一切の手加減を捨て、
            「寒い」「時間の無駄」「やり直し」レベルの超激辛評価（0点〜20点台）を連発してください。
            褒めることは禁止です。ツンデレ指導員は「ツン」100%で突き放してください。
            """
        else:
            custom_instruction = "各キャラクターの個性を活かしつつ、一般視聴者向けに公平に採点してください。"
    
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
        st.session_state.messages = [] # まっさらにして放送開始
        
        # キャラクター設定をAIに叩き込む
        mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
        
        full_prompt = f"""
        あなたは超一流の番組構成作家です。視聴者が釘付けになるような爆笑チャット番組の台本を書いてください。

        【本日のお題】: 「{user_input}」
        【特別ルール】: {custom_instruction}

        【登場人物】:
        {mentor_prompts}

        【構成ルール（厳守）】:
        1. 必ず「司会（Gemini）」のハイテンションな第一声から書き始めること。
        2. 次にメンター陣5人が、それぞれの個性を爆発させて感想と採点を述べる。
        3. 再び「司会（Gemini）」が登場し、5人の平均点（0.1点刻み）をドラマチックに発表。
        4. 「辛口師匠」が登場。メンター全員を一喝し、毒舌の総評とともに衝撃の最終点数を出す。
        5. 最後に「司会（Gemini）」がタジタジになりながら番組を締める。

        【形式】: 名前: セリフ
        """
        
        with st.spinner("スタジオの照明、点灯中..."):
            try:
                res = model.generate_content(full_prompt)
                # 司会から始まる全ての台本をログに格納
                for line in res.text.split('\n'):
                    if ":" in line:
                        p = line.split(":", 1)
                        name = p[0].replace("*", "").strip()
                        if name in CHARACTERS:
                            st.session_state.messages.append({
                                "role": name, 
                                "content": p[1].strip(), 
                                "icon": CHARACTERS[name]["icon"]
                            })
                
                # これで1行目からタイピング演出が始まる！
                st.session_state.is_typing = True
                
            except Exception as e:
                st.error(f"生放送トラブル発生（生成エラー）: {e}")

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
                    time.sleep(0.1) # 少し速めに設定
                p.markdown(txt)
                if i == len(st.session_state.messages) - 1:
                    st.session_state.is_typing = False
                time.sleep(0.5)
            else:
                st.write(msg["content"])

if not st.session_state.messages:
    st.info("左から入力して『LIVEスタート！』を押してね。")
