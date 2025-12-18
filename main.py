import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="AIダジャレメーカー")

def init_dynamic_model():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 利用可能なモデルをAPIから直接リストアップ
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # リストの中から優先順位をつけて選択
        target_models = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro']
        
        selected_name = None
        for target in target_models:
            if target in available_models:
                selected_name = target
                break
        
        # 万が一見つからなければリストの最初の一つを使う
        if not selected_name and available_models:
            selected_name = available_models[0]
            
        if selected_name:
            return genai.GenerativeModel(selected_name), selected_name
        else:
            return None, "利用可能なモデルがリストに見つかりません。"
    except Exception as e:
        return None, str(e)

model, model_info = init_dynamic_model()

st.title("🎤 AIダジャレメーカー")
if model_info:
    st.caption(f"接続モデル: {model_info}")

if not model:
    st.error(f"モデル接続エラー: {model_info}")
else:
    word = st.text_input("お題を入力", key="final_test_input")
    if st.button("生成"):
        try:
            # 安全フィルターをOFFにしてNotFoundを回避する（有料枠なら可能）
            res = model.generate_content(
                f"「{word}」でダジャレを5つ作って",
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ]
            )
            st.write(res.text)
        except Exception as e:
            st.error(f"実行エラー: {e}")
            # リストアップされた全モデルを表示（デバッグ用）
            with st.expander("利用可能なモデルリストを確認"):
                st.write([m.name for m in genai.list_models()])
