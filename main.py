import streamlit as st
import google.generativeai as genai
import urllib.parse

# --- ページ基本設定 ---
st.set_page_config(
    page_title="AIダジャレ判定メーカー",
    page_icon="🎤",
    layout="centered"
)

# --- スタイル調整 ---
st.markdown("""
    <style>
    .main { background-color: #f5f5f5; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3em; background-color: #ff4b4b; color: white; font-weight: bold; }
    .judge-result { padding: 20px; border: 2px solid #333; border-radius: 10px; background-color: white; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

# --- API初期化関数 (自動モデル選択ロジック) ---
def init_gemini():
    try:
        # 1. APIキーの取得
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
        elif "temp_api_key" in st.session_state:
            api_key = st.session_state["temp_api_key"]
        else:
            return None, "APIキーが設定されていません。"

        genai.configure(api_key=api_key)
        
        # 2. 利用可能なモデルを順に試行 (404エラー対策)
        # 環境によって 'gemini-1.5-flash' か 'models/gemini-1.5-flash' かが分かれるため
        candidate_models = [
            'gemini-1.5-flash', 
            'models/gemini-1.5-flash', 
            'gemini-1.5-flash-latest', 
            'gemini-pro'
        ]
        
        for model_name in candidate_models:
            try:
                model = genai.GenerativeModel(model_name)
                # 疎通確認のためのテストリクエスト
                model.generate_content("test", generation_config={"max_output_tokens": 1})
                return model, None
            except:
                continue
        
        return None, "有効なGeminiモデルが見つかりませんでした。APIキーの有効期限や権限を確認してください。"
    except Exception as e:
        return None, str(e)

# --- サイドバー ---
with st.sidebar:
    st.title("⚙️ 設定")
    if "GEMINI_API_KEY" not in st.secrets:
        temp_key = st.text_input("Gemini API Keyを入力", type="password")
        if temp_key:
            st.session_state["temp_api_key"] = temp_key
    st.write("---")
    st.caption("Ver 1.1.0 (Auto-Model Recovery)")

# モデルの準備
model, error_msg = init_gemini()

# --- メインコンテンツ ---
st.title("🎤 AIダジャレ判定メーカー")
st.write("プロのAI落語家が、あなたのダジャレを厳しくプロデュース。")

if error_msg and "GEMINI_API_KEY" not in st.secrets and "temp_api_key" not in st.session_state:
    st.warning("👈 左側のサイドバーからGemini APIキーを入力して開始してください。")
elif error_msg:
    st.error(f"初期化エラー: {error_msg}")
else:
    tab1, tab2, tab3 = st.tabs(["✨ ダジャレを作る", "🏢 シチュエーション", "⚖️ 判定してもらう"])

    # --- ① 単語から生成 ---
    with tab1:
        word = st.text_input("キーワードを入力（例：電話）", key="word_input")
        if st.button("5つのネタを生成！"):
            if word and model:
                with st.spinner('ネタ帳をめくっています...'):
                    try:
                        prompt = f"「{word}」を使ったダジャレを5つ、箇条書きで出力してください。"
                        res = model.generate_content(prompt)
                        st.balloons()
                        st.success(f"「{word}」のネタが整いました！")
                        st.write(res.text)
                    except Exception as e:
                        st.error(f"生成エラー: {e}")

    # --- ② シチュエーション生成 ---
    with tab2:
        sit_word = st.text_input("使いたい単語", key="sit_word")
        context = st.selectbox("シチュエーション", ["会議の沈黙を破る", "デートの緊張をほぐす", "謝罪の場を和ませる", "深夜のテンション"])
        if st.button("状況に合わせてボケる"):
            if sit_word and model:
                with st.spinner('空気を読んでいます...'):
                    try:
                        prompt = f"「{context}」という状況で「{sit_word}」を使ったダジャレを1つ作り、その場の空気感も一言添えてください。"
                        res = model.generate_content(prompt)
                        st.info(res.text)
                    except Exception as e:
                        st.error(f"シチュエーションエラー: {e}")

    # --- ③ ダジャレ判定 ---
    with tab3:
        st.subheader("あなたの渾身のネタを評価")
        user_input = st.text_area("ダジャレを入力", placeholder="例：アルミ缶の上にあるみかん")
        
        if st.button("審査員に提出"):
            if user_input and model:
                with st.spinner('審査員が真剣に評価中...'):
                    prompt = f"""
                    あなたは毒舌な落語家です。ユーザーのダジャレ「{user_input}」を判定し、以下の形式で答えてください。
                    【座布団】（0〜5枚の絵文字で評価）
                    【周囲の温度】（マイナス273度〜100度の間で表現）
                    【師匠のコメント】（辛口ながらも愛のあるコメント）
                    """
                    try:
                        res = model.generate_content(prompt)
                        result_text = res.text
                        st.markdown(f'<div class="judge-result">{result_text}</div>', unsafe_allow_html=True)
                        
                        # SNSシェア用URL
                        st.write("---")
                        share_msg = f"【AIダジャレ判定結果】\n「{user_input}」\n\n{result_text}\n#ダジャレメーカー #AI判定"
                        encoded_msg = urllib.parse.quote(share_msg)
                        share_url = f"https://twitter.com/intent/tweet?text={encoded_msg}"
                        st.markdown(f'[𝕏(Twitter)で結果をシェアする]({share_url})')
                    except Exception as e:
                        st.error(f"判定エラー: {e}")

# --- フッター ---
st.write("---")
st.caption("© 2025 ダジャレ・ラボ | 全国の寒がりな皆様へ捧ぐ")
