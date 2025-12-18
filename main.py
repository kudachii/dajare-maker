import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="シンプル・ダジャレ", page_icon="🎤")

def init_gemini():
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        
        # 有料枠で 404 エラーが出る場合、このフルパス指定が最も有効です
        model_name = 'models/gemini-1.5-flash'
        model = genai.GenerativeModel(model_name)
        
        # 404かどうかをここでテスト
        try:
            model.generate_content("test", generation_config={"max_output_tokens": 1})
        except:
            # もしダメなら旧安定版を試す
            model = genai.GenerativeModel('gemini-pro')
            
        return model, None
    except Exception as e:
        return None, str(e)

model, err = init_gemini()

st.title("🎤 シンプル・ダジャレ")

if err:
    st.error(f"初期化に失敗しました。APIキーを確認してください: {err}")
else:
    word = st.text_input("お題を入力してください")
    if st.button("ダジャレを作る"):
        if word:
            with st.spinner('AIが必死に考えています...'):
                try:
                    # モデル名を明示的に指定して実行
                    res = model.generate_content(f"「{word}」でダジャレを5つ作ってください。")
                    st.success("整いました！")
                    st.write(res.text)
                except Exception as e:
                    # ここでエラーが出たら詳細を表示
                    st.error(f"生成エラー詳細: {e}")
                    st.info("ヒント: Google AI Studioで新しいAPIキーを『デフォルトプロジェクト』で作成し直すと解決することがあります。")

st.divider()
st.caption("2025.12.18 Stable Build")
