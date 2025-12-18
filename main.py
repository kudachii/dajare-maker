import streamlit as st
import google.generativeai as genai
import urllib.parse

st.set_page_config(page_title="AIダジャレメーカー", page_icon="🎤")

# --- API初期化（OKが出た動的な方法を維持） ---
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

# --- メイン画面 ---
st.title("🎤 AIダジャレ判定メーカー")
st.write("解説不要。笑い（と寒さ）は、その一言に宿る。")

tab1, tab2 = st.tabs(["✨ ネタを作る", "⚖️ 判定してもらう"])

# --- ① ネタ生成（解説を禁止） ---
with tab1:
    word = st.text_input("お題を入力", key="gen_word")
    if st.button("ネタを5つ出す"):
        if word and model:
            with st.spinner('作成中...'):
                # 「解説禁止」を強調したプロンプト
                prompt = f"「{word}」を使ったダジャレを5つ、箇条書きで出力してください。余計な解説、説明、導入文は一切不要です。ダジャレのみをズバッと出力してください。"
                res = model.generate_content(prompt)
                st.success(f"「{word}」の五連発")
                st.write(res.text)

# --- ② 判定（野暮な説明を排除） ---
with tab2:
    user_input = st.text_area("自慢のダジャレを入力", placeholder="例：アルミ缶の上にあるみかん")
    if st.button("審査員に提出"):
        if user_input and model:
            with st.spinner('審査中...'):
                # 判定も「解説」ではなく「評価」に特化
                prompt = f"""
                ユーザーのダジャレ「{user_input}」を、毒舌な落語家として短く判定してください。
                以下の3点のみを出力し、ダジャレの構造の解説などは絶対にしないでください。
                
                【座布団】（0〜5枚の絵文字）
                【周囲の温度】（度数のみ）
                【師匠の一言】（20文字以内の短い毒舌）
                """
                res = model.generate_content(prompt)
                st.info("判定結果")
                st.write(res.text)
                
                # シェアボタン
                share_msg = f"【AIダジャレ判定】\n「{user_input}」\n\n{res.text}\n#ダジャレメーカー"
                st.markdown(f'[𝕏で結果をシェアする](https://twitter.com/intent/tweet?text={urllib.parse.quote(share_msg)})')

st.divider()
st.caption("© 2025 ダジャレ・ラボ | 解説しないのが、一番面白い。")
