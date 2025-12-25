import streamlit as st
import google.generativeai as genai
import time

# ページ設定
st.set_page_config(page_title="Shall Tell Live 3.0", page_icon="🎙️", layout="centered")

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

# キャラクター定義（司会 Gemini を追加！）
CHARACTERS = {
    "司会（Gemini）": {"icon": "🤖", "prompt": "番組の進行役。知的で明るく、メンターたちに話を振ったり、最後をきれいにまとめたりする。"},
    "優しさに溢れるメンター": {"icon": "🌈", "prompt": "全肯定で寄り添う。感動しやすく、くだちいさんの努力を涙ながらに称える。"},
    "ツンデレな指導員": {"icon": "💢", "prompt": "厳しくも愛があるツンデレ。毒舌だが、実は誰よりも期待している。"},
    "頼れるお姉さん": {"icon": "👩‍💼", "prompt": "包み込む大人の余裕がある女性。上品な口調で的確なアドバイスをくれる。"},
    "論理的コーチ": {"icon": "🧐", "prompt": "データに基づき論理的に分析する。効率を重視し、無駄な感情は排除する。"},
    "ギャル先生": {"icon": "✨", "prompt": "超ポジティブなアゲアゲ語。「マジ神」「優勝」が口癖のメンター。"},
    "辛口師匠": {"icon": "🍶", "prompt": "江戸っ子の毒舌落語家。最後に全員を黙らせる鋭いオチをつけ、座布団を全部持っていく。"}
}

# セッション状態の初期化
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- サイドバー：配信コントロールパネル ---
with st.sidebar:
    st.title("🎙️ ライブ配信操作盤")
    
    # モード切り替え
    mode = st.radio("配信モードを選択", ["🏆 ダジャレ公開処刑", "💬 戦略・10大ニュース会議"])
    
    st.divider()

    # モード別の入力設定
    if mode == "🏆 ダジャレ公開処刑":
        st.subheader("🔥 ネタ投稿スロット")
        user_input = st.text_input("いじり倒すネタを入力", placeholder="例：パンダのパンだ")
        instruction = "司会が場を盛り上げ、各メンターがこのダジャレをボコボコにいじり倒し、最後に師匠がトドメを刺し、司会が締める流れで。"
    else:
        st.subheader("📅 アジェンダ入力")
        user_input = st.text_area("議題・ニュースを入力", placeholder="例：今年の10大ニュースを発表します！")
        instruction = "司会が議題を提示し、各メンターがくだちいさんを労ったり未来を語ったりする。賑やかでエモい会議にし、最後に司会が締める流れで。"

    # 実行ボタン
    if st.button("🚀 LIVEスタート！", type="primary"):
        if model and user_input:
            st.session_state.messages = [] # 会議ごとにリセット
            mentor_prompts = "\n".join([f"- {name}: {info['prompt']}" for name, info in CHARACTERS.items()])
            
            full_prompt = f"""
            以下の内容について、司会を含む7人のメンバーでチャット番組形式の会話劇を作成してください。
            入力内容: 「{user_input}」
            
            各メンバーの設定:
            {mentor_prompts}
            
            構成指示:
            1. 最初に「司会（Gemini）」が登場し、本日の趣旨を説明してお題を振る。
            2. 各メンターが順番にリアクションし、会話を繋げる。
            3. 「辛口師匠」が最後にオチをつける。
            4. 最後に「司会（Gemini）」が全体をまとめて、視聴者に挨拶する。
            
            形式（厳守）:
            名前: セリフ
            """
            
            with st.spinner("スタジオの照明をオンにしています..."):
                try:
                    res = model.generate_content(full_prompt)
                    for line in res.text.split('\n'):
                        if ":" in line:
                            parts = line.split(":", 1)
                            name = parts[0].replace("*", "").strip()
                            content = parts[1].strip()
                            if name in CHARACTERS:
                                st.session_state.messages.append({"role": name, "content": content, "icon": CHARACTERS[name]["icon"]})
                    st.rerun()
                except Exception as e:
                    st.error(f"エラーが発生しました: {e}")

    if st.button("🗑️ チャット履歴をクリア"):
        st.session_state.messages = []
        st.rerun()

# --- メイン画面：ライブ配信ステージ ---
st.title(f"{mode}")
st.caption(f"配信中：くだちい × ポジティブメンター5人衆 ＋ 辛口師匠 ＋ 司会Gemini")

if not st.session_state.messages:
    st.info("左側のパネルでモードを選び、内容を入力して「LIVEスタート！」を押してください。")
else:
    # メッセージの表示
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"], avatar=msg["icon"]):
            st.write(f"**{msg['role']}**")
            
            # タイピング演出
            placeholder = st.empty()
            full_text = ""
            for char in msg["content"]:
                full_text += char
                placeholder.markdown(full_text + "▌")
                time.sleep(0.04) # タイピング速度
            placeholder.markdown(full_text)
        
        # 司会や師匠の後は少し長めに待つ演出
        wait_time = 1.2 if "司会" in msg["role"] or "師匠" in msg["role"] else 0.7
        time.sleep(wait_time)

# フッター演出
if st.session_state.messages:
    st.divider()
    st.center = st.write("🎙️ 本日のライブ配信は終了しました。")
    if mode == "🏆 ダジャレ公開処刑":
        st.balloons() # ダジャレボコられ完了のお祝い
