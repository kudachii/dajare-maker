import streamlit as st
import google.generativeai as genai

# 他のアプリの設定と干渉しないよう、最小限の設定
st.set_page_config(page_title="AIダジャレメーカー")

def load_model():
    """
    他のアプリと共通のAPIキーを使用してモデルを初期化
    有料枠(Pay-as-you-go)で404が出る問題を回避する設定
    """
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            # 有料枠で最も安定する 'gemini-1.5-flash' を指定
            # もしこれで404が出る場合は 'models/gemini-1.5-flash' を自動試行
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                # 疎通テスト
                model.generate_content("Hi", generation_config={"max_output_tokens": 1})
                return model
            except:
                return genai.GenerativeModel('models/gemini-1.5-flash')
        else:
            st.error("SecretsにAPIキーが見つかりません。")
            return None
    except Exception as e:
        st.error(f"初期化エラー: {e}")
        return None

# モデルの読み込み
model = load_model()

# --- 画面構成 ---
st.title("🎤 AIダジャレメーカー")
st.write("お題を入力して、AIにダジャレを作ってもらいましょう。")

# 以前の入力と干渉しないよう、独自のkeyを設定
word = st.text_input("お題（例：電話、カレー）", key="dajare_word_input")

if st.button("ダジャレを生成する", key="dajare_gen_button"):
    if not word:
        st.warning("単語を入力してください。")
    elif model:
        with st.spinner('AIがネタを考えています...'):
            try:
                # シンプルなプロンプトでエラー率を下げる
                prompt = f"「{word}」を使った面白いダジャレを5つ、箇条書きで教えてください。"
                response = model.generate_content(prompt)
                
                if response.text:
                    st.success(f"「{word}」のダジャレが完成しました！")
                    st.write(response.text)
                else:
                    st.error("AIから空の返答がありました。")
                    
            except Exception as e:
                # エラーが出た場合、詳細を表示
                st.error("生成に失敗しました。")
                st.expander("エラー詳細を確認").write(e)
    else:
        st.error("モデルの初期化に失敗しています。")

# --- フッター ---
st.divider()
st.caption("© 2025 AIアプリ集 | 第4弾：ダジャレメーカー")
