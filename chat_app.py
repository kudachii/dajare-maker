import streamlit as st
import google.generativeai as genai
import time

# ページ設定
st.set_page_config(page_title="Shall Tell Live!", page_icon="🎙️")

# --- API初期化 (エラー対策版) ---
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    
    # モデル名を 'gemini-1.5-flash' に固定せず、
    # 互換性のある名前（models/gemini-1.5-flash）を試す設定
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        # テスト実行して確認（エラーが出たら予備のモデル名に切り替え）
        # ※ここでは定義だけにして、実際の生成時にトライする形にするよ
    except:
        model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("APIキーが見つからないよ！ .streamlit/secrets.toml を確認してね。")
    model = None

# キャラクター定義 (変更なし)
CHARACTERS = {
    "優しさに溢れるメンター": {"icon": "🌈", "prompt": "温かく寄り添う全肯定"},
    "ツンデレな指導員": {"icon": "💢", "prompt": "厳しくも愛があるツンデレ"},
    "頼れるお姉さん": {"icon": "👩‍💼", "prompt": "包み込むように励ます大人の女性"},
    "論理的コーチ": {"icon": "🧐", "prompt": "感情を排除し論理的に分析する"},
    "ギャル先生": {"icon": "✨", "prompt": "超ポジティブにアゲるギャル語"},
    "辛口師匠": {"icon": "🍶", "prompt": "江戸っ子の毒舌落語家。最後にオチをつける"}
}

st.title("🎙️ Shall Tell オート会議システム")

# メッセージをクリアするボタンをサイドバーに追加
with st.sidebar:
    if st.button("チャットをリセット"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

# お題の入力
with st.sidebar:
    st.title("大会進行パネル")
    target_dajare = st.text_input("いじり倒すダジャレを入力", placeholder="例：内科にないか？")
    
    if st.button("AI会議スタート！"):
        if not model:
            st.warning("APIの準備ができてないみたい...")
        elif target_dajare:
            # プロンプト作成 (変更なし)
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            prompt = f"""
            ユーザーのダジャレ「{target_dajare}」について、以下の6人がチャットで会話しています。
            {mentor_prompts}
            条件：チャット形式の台本を作成。1人1〜2発言。互いに反応し合う。最後に辛口師匠が毒舌で締める。
            出力形式：名前: セリフ
            """
            
            with st.spinner("AIたちが作戦会議中..."):
                try:
                    # ここでモデル名を微調整して再トライする仕組み
                    try:
                        response = model.generate_content(prompt)
                    except:
                        # 予備のモデル名でリトライ
                        alt_model = genai.GenerativeModel('gemini-1.5-flash')
                        response = alt_model.generate_content(prompt)

                    lines = response.text.split('\n')
                    for line in lines:
                        if ":" in line:
                            parts = line.split(":", 1)
                            name = parts[0].replace("*", "").strip() # 太字装飾などを除去
                            content = parts[1].strip()
                            if name in CHARACTERS:
                                st.session_state.messages.append({
                                    "role": name, "content": content, "icon": CHARACTERS[name]["icon"]
                                })
                    st.rerun() # 画面を更新して表示を安定させる
                except Exception as e:
                    st.error(f"生成エラー: {e}\n(モデル名 models/gemini-1.5-flash が見つからないようです)")

# チャット表示 (変更なし)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg["icon"]):
        st.write(f"**{msg['role']}**")
        st.write(msg["content"])
