import streamlit as st
import google.generativeai as genai
import time

# ページ設定
st.set_page_config(page_title="Shall Tell Live 3.0", page_icon="🎙️")

# --- API初期化 (自動探索システム) ---
@st.cache_resource
def init_model():
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        try:
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            target_priority = ['models/gemini-1.5-flash', 'models/gemini-pro', 'gemini-1.5-flash']
            selected = next((m for m in target_priority if m in available_models), None)
            return genai.GenerativeModel(selected) if selected else None
        except:
            return None
    return None

model = init_model()

# キャラクター定義
CHARACTERS = {
    "優しさに溢れるメンター": {"icon": "🌈", "prompt": "温かく寄り添う全肯定。感動しやすい。"},
    "ツンデレな指導員": {"icon": "💢", "prompt": "厳しくも愛があるツンデレ。口が悪いが実は応援している。"},
    "頼れるお姉さん": {"icon": "👩‍💼", "prompt": "包み込むように励ます大人の女性。上品な口調。"},
    "論理的コーチ": {"icon": "🧐", "prompt": "感情を排除し論理的に分析する。効率とデータを重視。"},
    "ギャル先生": {"icon": "✨", "prompt": "超ポジティブにアゲるギャル語。「マジ神」「優勝」が口癖。"},
    "辛口師匠": {"icon": "🍶", "prompt": "江戸っ子の毒舌落語家。最後にオチをつけ、全員を黙らせる。"}
}

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- サイドバー：コントロールパネル ---
with st.sidebar:
    st.title("🎙️ ライブ配信操作盤")
    
    # モード選択
    mode = st.radio("配信モードを選択", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    
    st.divider()
    
    if mode == "🏆 ダジャレ公開処刑":
        st.subheader("ダジャレ入力欄")
        user_input = st.text_input("いじり倒すネタを入力", placeholder="例：パンダのパンだ")
        instruction = "このダジャレを、それぞれのキャラでボコボコにいじり倒して笑いに変えてください。最後に師匠が毒舌で締めて。"
    else:
        st.subheader("議題入力欄")
        user_input = st.text_area("議題・ニュースを入力", placeholder="例：今年の10大ニュースを発表します！")
        instruction = "この議題について、それぞれのキャラがリアクションしつつ会議してください。くだちいさんを労ったり、未来を語ったり、賑やかに！"

    if st.button("AI会議・スタート！", type="primary"):
        if model and user_input:
            st.session_state.messages = [] # クリアして開始
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            
            full_prompt = f"""
            以下の入力について、6人のメンバーでチャット会議を行ってください。
            入力内容: 「{user_input}」
            
            メンバー設定:
            {mentor_prompts}
            
            指示:
            {instruction}
            
            出力形式（必ず守ってください）:
            名前: セリフ
            """
            
            with st.spinner("AIたちがスタジオ入りしています..."):
                try:
                    response = model.generate_content(full_prompt)
                    lines = response.text.split('\n')
                    for line in lines:
                        if ":" in line:
                            parts = line.split(":", 1)
                            name = parts[0].replace("*", "").strip()
                            content = parts[1].strip()
                            if name in CHARACTERS:
                                st.session_state.messages.append({"role": name, "content": content, "icon": CHARACTERS[name]["icon"]})
                    st.rerun()
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

    if st.button("チャットをリセット"):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面：チャット表示 ---
st.title(f"🎙️ {mode}会場")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=msg["icon"]):
        st.write(f"**{msg['role']}**")
        
        # タイピング演出
        placeholder = st.empty()
        full_text = ""
        for char in msg["content"]:
            full_text += char
            placeholder.markdown(full_text + "▌")
            time.sleep(0.03) # 少し速めに設定
        placeholder.markdown(full_text)
    
    time.sleep(0.8) # 次の人が喋るまでの「間」

if not st.session_state.messages:
    st.info("左のパネルから入力して、会議を始めてください！")
