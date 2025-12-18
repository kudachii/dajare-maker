import streamlit as st
import google.generativeai as genai

# 1. ページ設定
st.set_page_config(page_title="シンプル・ダジャレ", page_icon="🎤")

# 2. API初期化（有料枠を想定）
def init_gemini():
    try:
        # 他のアプリで使用しているSecretsのキー名に合わせてください
        api_key = st.secrets["GEMINI_API_KEY"]
        genai.configure(api_key=api_key)
        # 有料枠で最も確実な指定
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"接続設定エラー: {e}")
        return None

model = init_gemini()

# 3. メイン画面
st.title("🎤 シンプル・ダジャレ")
st.write("キーワードから、AIがダジャレを生成します。")

word = st.text_input("お題となる単語を入力", placeholder="例：パンダ")

if st.button("ダジャレを作る"):
    if word and model:
        with st.spinner('作成中...'):
            try:
                # 非常にシンプルなプロンプト
                prompt = f"「{word}」を使った面白いダジャレを5つ考えて、箇条書きで教えてください。"
                response = model.generate_content(prompt)
                
                # 結果表示
                st.success(f"「{word}」の結果です：")
                st.write(response.text)
                
            except Exception as e:
                st.error(f"生成中にエラーが発生しました: {e}")
    elif not word:
        st.warning("単語を入力してください。")

# 4. フッター
st.divider()
st.caption("2025 Dajare Maker - Simple Mode")
