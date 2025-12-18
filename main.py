import streamlit as st
import google.generativeai as genai
import urllib.parse

# 1. ページ設定
st.set_page_config(page_title="Shall Tell（シャレテール）", page_icon="🎤")

# --- API初期化 ---
def init_dynamic_model():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
            selected_name = next((t for t in target_models if t in available_models), None)
            if not selected_name and available_models:
                selected_name = available_models[0]
            return genai.GenerativeModel(selected_name)
        return None
    except:
        return None

model = init_dynamic_model()

# --- 2. サイドバー（リセット機能） ---
with st.sidebar:
    st.title("Shall Tell Menu")
    if st.button("🔄 アプリをリセット", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    st.info("入力をすべて消去します。")

# --- 3. メイン UI ---
st.title("🎤 Shall Tell（シャレテール）")
st.subheader("〜ダジャレメーカー")
st.write("粋な大人は、解説しない。")

tab1, tab2, tab3 = st.tabs(["✨ Generate", "🏢 Situation", "⚖️ Judge"])

# --- ① ネタ生成 ---
with tab1:
    word = st.text_input("お題を入力", key="word_input_key", placeholder="例：パンダ")
    if st.button("Shall Tell !", key="btn_gen", type="primary"):
        if word and model:
            with st.spinner('Thinking...'):
                prompt = f"「{word}」を使ったダジャレを5つ出力してください。解説・導入文は一切不要。ダジャレのみを箇条書きで出力してください。"
                res = model.generate_content(prompt)
                st.success(f"『{word}』の五連発")
                st.write(res.text)

# --- ② シチュエーション（NEW!） ---
with tab2:
    st.write("特定の状況で使える「空気を変える一言」を提案します。")
    sit_word = st.text_input("使いたいキーワード", key="sit_word_key", placeholder="例：お茶")
    context = st.selectbox("シチュエーション", 
                           ["会議で煮詰まった時", "デートの沈黙", "謝罪のあと", "飲み会の締め", "エレベーターの中"], 
                           key="sit_context_key")
    if st.button("一言を授かる", key="btn_sit", type="primary"):
        if sit_word and model:
            with st.spinner('Preparing...'):
                prompt = f"{context}という状況で、「{sit_word}」を使ったダジャレを1つだけ提案してください。解説や前置きは一切せず、その「一言」だけを出力してください。"
                res = model.generate_content(prompt)
                st.info("放たれるべき一言")
                st.subheader(f"「{res.text.strip()}」")

# --- ③ 判定 ---
with tab3:
    user_input = st.text_area("自慢のダジャレをどうぞ", key="judge_input_key", placeholder="例：アルミ缶の上にあるみかん")
    if st.button("Judge Me", key="btn_judge", type="primary"):
        if user_input and model:
            with st.spinner('Judging...'):
                prompt = f"ユーザーのダジャレ「{user_input}」を毒舌な落語家として判定。解説なしで【座布団(0-5)】【周囲の温度】【師匠の一言(20字以内)】のみ出力して。"
                res = model.generate_content(prompt)
                st.info("Judgment")
                st.write(res.text)
                
                share_msg = f"【AIダジャレ判定：Shall Tell】\n「{user_input}」\n\n{res.text}\n#ShallTell"
                st.markdown(f'[𝕏で結果をシェアする](https://twitter.com/intent/tweet?text={urllib.parse.quote(share_msg)})')

st.divider()
st.caption("© 2025 Shall Tell | 粋な大人は、解説しない。")
