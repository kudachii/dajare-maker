import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- ページ基本設定 ---
st.set_page_config(page_title="AIダジャレ判定メーカー", page_icon="🎤")

# --- API初期化 (有料枠向け最適化) ---
def init_gemini():
    try:
        # Secretsから取得
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        elif "temp_api_key" in st.session_state:
            api_key = st.session_state["temp_api_key"]
        else:
            return None, "APIキーをサイドバーに入力してください。"

        genai.configure(api_key=api_key)
        
        # 有料枠の場合、models/ プレフィックスを付けるのが最も確実です
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        # 起動確認（1トークンだけ生成して疎通を確認）
        model.generate_content("Hi", generation_config={"max_output_tokens": 1})
        return model, None
    except Exception as e:
        # エラーメッセージを詳細に表示して原因を突き止める
        return None, f"接続エラー: {str(e)}"

# --- サイドバー ---
with st.sidebar:
    st.title("⚙️ 設定")
    if "GEMINI_API_KEY" not in st.secrets:
        temp_key = st.text_input("Gemini API Keyを入力", type="password")
        if temp_key:
            st.session_state["temp_api_key"] = temp_key
    st.write("---")
    st.info("有料枠アカウントとして接続中")

model, error_msg = init_gemini()

# --- メイン UI ---
st.title("🎤 AIダジャレ判定メーカー")

if error_msg:
    st.error(error_msg)
    st.info("💡 Google AI Studioで新しいAPIキーを発行し直すと解決する場合があります。")
else:
    tab1, tab2, tab3 = st.tabs(["✨ 生成", "🏢 シチュエーション", "⚖️ 判定"])

    with tab1:
        word = st.text_input("キーワードを入力")
        if st.button("生成"):
            res = model.generate_content(f"「{word}」でダジャレを5つ作って。")
            st.write(res.text)

    with tab2:
        sit_word = st.text_input("使いたい単語")
        context = st.selectbox("シチュエーション", ["会議", "デート", "謝罪"])
        if st.button("シチュエーション生成"):
            res = model.generate_content(f"{context}の状況で「{sit_word}」を使ったダジャレを1つ。")
            st.write(res.text)

    with tab3:
        user_input = st.text_area("ダジャレを入力")
        if st.button("判定"):
            prompt = f"落語家としてダジャレ「{user_input}」を【座布団】【温度】【コメント】で判定して。"
            res = model.generate_content(prompt)
            st.success("判定完了！")
            st.write(res.text)
            
            # シェア機能
            share_msg = f"【AIダジャレ判定】\n「{user_input}」を判定した結果...\n\n{res.text}\n#ダジャレメーカー"
            st.markdown(f'[𝕏でシェアする](https://twitter.com/intent/tweet?text={urllib.parse.quote(share_msg)})')
