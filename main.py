import streamlit as st
import google.generativeai as genai
import urllib.parse

# ページ設定
st.set_page_config(page_title="Shall Tell", page_icon="🎤")

# --- API初期化（リスト取得方式で安定化） ---
def init_dynamic_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        selected_name = next((t for t in target_models if t in available_models), None)
        if not selected_name and available_models:
            selected_name = available_models[0]
        return genai.GenerativeModel(selected_name) if selected_name else None
    except:
        return None

model = init_dynamic_model()

# --- リセット処理 ---
def reset_app():
    for key in st.session_state.keys():
        del st.session_state[key]
    st.rerun()

# --- メイン画面 ---
st.title("🎤 Shall Tell（シャレテール）")
st.subheader("〜ダジャレメーカー")
st.write("粋な大人は、解説しない。")

# 右上にリセットボタン
col1, col2 = st.columns([0.8, 0.2])
with col2:
    if st.button("🔄 Reset"):
        reset_app()

tab1, tab2 = st.tabs(["✨ Generate (作る)", "⚖️ Judge (判定)"])

# --- ① ネタ生成 ---
with tab1:
    word = st.text_input("お題を入力してください", key="gen_word")
    if st.button("Shall Tell !"):
        if word and model:
            with st.spinner('Thinking...'):
                # 解説禁止プロンプト
                prompt = f"「{word}」を使ったダジャレを5つ、箇条書きで出力してください。導入文や解説は一切不要。ダジャレだけをズバッと出力してください。"
                res = model.generate_content(prompt)
                st.success(f"『{word}』を冠した五選")
                st.write(res.text)

# --- ② 判定 ---
with tab2:
    user_input = st.text_area("自慢のダジャレをどうぞ", key="judge_input", placeholder="例：アルミ缶の上にあるみかん")
    if st.button("Judge Me"):
        if user_input and model:
            with st.spinner('Judging...'):
                prompt = f"""
                ユーザーのダジャレ「{user_input}」を、毒舌な落語家として短く判定してください。
                解説は絶対にせず、以下の3点のみを出力してください。
                
                【座布団】（0〜5枚の絵文字）
                【周囲の温度】（度数のみ）
                【師匠の一言】（20文字以内の短い毒舌）
                """
                res = model.generate_content(prompt)
                st.info("Shall Tell's Judgment")
                st.write(res.text)
                
                share_msg = f"【AIダジャレ判定：Shall Tell】\n「{user_input}」\n\n{res.text}\n#ShallTell #ダジャレメーカー"
                st.markdown(f'[𝕏で結果をシェアする](https://twitter.com/intent/tweet?text={urllib.parse.quote(share_msg)})')

st.divider()
st.caption("© 2025 Shall Tell | The Art of Puns.")
