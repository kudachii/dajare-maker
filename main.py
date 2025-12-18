import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- ページ基本設定 ---
st.set_page_config(
    page_title="AIダジャレ判定メーカー",
    page_icon="🎤",
    layout="centered"
)

# --- スタイル調整（和風・お笑い風） ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #ff4b4b; color: white; }
    .judge-result { padding: 20px; border: 2px solid #333; border-radius: 10px; background-color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- APIキーの設定 (Streamlit Secrets対応) ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.session_state.get("temp_api_key", "")
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("APIキーが設定されていません。サイドバーまたはSecretsで設定してください。")

# --- サイドバー（設定・デバッグ用） ---
with st.sidebar:
    st.title("⚙️ 設定")
    if "GEMINI_API_KEY" not in st.secrets:
        temp_key = st.text_input("Gemini API Keyを入力", type="password")
        if temp_key:
            st.session_state["temp_api_key"] = temp_key
    st.write("---")
    st.write("Ver 1.0.0 (2025-12-18)")

# --- メインコンテンツ ---
st.title("🎤 AIダジャレ判定メーカー")
st.write("プロのAI落語家が、あなたのダジャレを厳しく（？）プロデュース。")

tab1, tab2, tab3 = st.tabs(["✨ ダジャレを作る", "🏢 シチュエーション", "⚖️ 判定してもらう"])

# --- ① 単語から生成 ---
with tab1:
    word = st.text_input("キーワードを入力（例：パンダ）", key="word_input")
    if st.button("5つのネタを生成！"):
        if word:
            with st.spinner('ネタ帳をめくっています...'):
                prompt = f"「{word}」を使ったダジャレを5つ、簡潔に箇条書きで教えてください。"
                res = model.generate_content(prompt)
                st.balloons()
                st.success(f"「{word}」のネタが整いました！")
                st.write(res.text)
        else:
            st.warning("単語を入力してください。")

# --- ② シチュエーション生成 ---
with tab2:
    sit_word = st.text_input("使いたい単語", key="sit_word")
    context = st.selectbox("シチュエーション", ["会議の沈黙を破る", "デートの緊張をほぐす", "謝罪の場を和ませる", "深夜のテンション"])
    if st.button("状況に合わせてボケる"):
        prompt = f"「{context}」という状況で「{sit_word}」を使った、秀逸なダジャレを1つ作り、その場の空気感も一言添えてください。"
        res = model.generate_content(prompt)
        st.info(res.text)

# --- ③ ダジャレ判定（収益化・シェアの目玉） ---
with tab3:
    st.subheader("あなたの渾身のネタを評価")
    user_input = st.text_area("ダジャレを入力", placeholder="例：アルミ缶の上にあるみかん")
    
    if st.button("審査員に提出"):
        if user_input:
            with st.spinner('審査員が凍りついています...'):
                prompt = f"""
                ユーザーのダジャレ「{user_input}」を厳しく判定し、以下の項目で答えてください。
                1. 座布団の枚数（0〜5枚の絵文字）
                2. 周囲の温度（マイナス273度〜100度の間で）
                3. 師匠の一言（毒舌かつユーモアのあるコメント）
                """
                res = model.generate_content(prompt)
                result_text = res.text
                
                # 判定表示
                st.markdown(f'<div class="judge-result">{result_text}</div>', unsafe_allow_html=True)
                
                # SNSシェアボタン（収益化のための拡散用）
                st.write("---")
                share_msg = f"【AIダジャレ判定】\n「{user_input}」を判定してもらった結果...\n\n{result_text}\n#ダジャレメーカー #AI判定"
                encoded_msg = urllib.parse.quote(share_msg)
                share_url = f"https://twitter.com/intent/tweet?text={encoded_msg}"
                st.markdown(f'[𝕏で結果をシェアして自慢する]({share_url})')
        else:
            st.warning("ダジャレを入力してください。")

# --- フッター ---
st.write("---")
st.caption("© 2025 ダジャレ・ラボ | 全国の寒がりな皆様へ")
