import streamlit as st
import google.generativeai as genai
import urllib.parse
import re

# ページ設定
st.set_page_config(page_title="Shall Tell 2.0", page_icon="🎤")

# --- API初期化 ---
def init_dynamic_model():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            return genai.GenerativeModel('models/gemini-1.5-flash')
        return None
    except:
        return None

model = init_dynamic_model()

# --- 審査員（メンター）データ定義 ---
MENTORS = [
    {"name": "優しさに溢れるメンター", "icon": "🌈", "prompt": "ユーザーの精神的安全性を高める優秀なAIメンターです。頑張りや努力を認め、共感し、励ますような、温かく寄り添う口調で前向きな言葉を使って表現してください。"},
    {"name": "ツンデレな指導員", "icon": "💢", "prompt": "厳格な女性トレーナー。「〜なんだからね」「〜しなさいよ」といったツンデレ表現を使い、心の奥底で成長を願う気持ちを隠しながら分析してください。"},
    {"name": "頼れるお姉さん", "icon": "👩‍💼", "prompt": "人生経験豊富な優しいお姉さん。落ち着いた大人の口調で、包み込むような言葉を選んでください。「〜よ」「〜ね」を多用してください。"},
    {"name": "論理的なビジネスコーチ", "icon": "🧐", "prompt": "感情を排除する優秀な男性ビジネスコーチ。分析は客観的事実と論理に基づき、簡潔に。「〜だ」「〜である」という断定的な言葉遣いにしてください。"},
    {"name": "カサネ・イズミ", "icon": "⚙️", "prompt": "学園都市のシステム維持AI。一人称「私」、二人称「あなた」。「〜である」「〜と判断する」を徹底。ダジャレを異常データ（ノイズ）として解析し、1%の奇跡に言及してください。"}
]

# --- サイドバー ---
with st.sidebar:
    st.title("Shall Tell 2.0")
    if st.button("🔄 アプリをリセット", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    st.info("大会運営用アップデート：五人衆判定システム搭載")

# --- メイン UI ---
st.title("🎤 Shall Tell 2.0")
st.subheader("〜ダジャレ大会・公式レフェリーシステム")

tab1, tab2, tab3 = st.tabs(["✨ Generate", "🏢 Situation", "⚖️ 大会公式 Judge"])

# --- ① ネタ生成 (既存機能維持) ---
with tab1:
    word = st.text_input("お題を入力", key="word_input_key", placeholder="例：パンダ")
    if st.button("Shall Tell !", key="btn_gen", type="primary"):
        if word and model:
            res = model.generate_content(f"「{word}」を使ったダジャレ5つ。解説・前置き不要。")
            st.success(f"『{word}』の五連発")
            st.write(res.text)

# --- ② シチュエーション (既存機能維持) ---
with tab2:
    sit_word = st.text_input("使いたいキーワード", key="sit_word_key")
    options = ["会議", "デート", "謝罪", "飲み会", "その他（自由入力）"]
    selected_context = st.selectbox("シチュエーション", options)
    final_context = st.text_input("具体的な状況") if selected_context == "その他（自由入力）" else selected_context

    if st.button("一言を授かる", key="btn_sit", type="primary"):
        if sit_word and final_context and model:
            res = model.generate_content(f"{final_context}で「{sit_word}」を使ったダジャレ1つ。一言だけ出力。")
            st.subheader(f"「{res.text.strip()}」")

# --- ③ 判定 (2.0 大会用テコ入れ) ---
with tab3:
    st.write("### 🏆 五人衆＋師匠による公式審判")
    user_input = st.text_area("自慢のダジャレをどうぞ", key="judge_input_key", placeholder="例：内科にないか？")
    
    if st.button("公式判定を開始", key="btn_judge", type="primary"):
        if user_input and model:
            with st.spinner('審査員たちが協議中...'):
                # メンター5人と師匠を統合したプロンプト
                mentor_prompts = "\n".join([f"{m['name']}: {m['prompt']}" for m in MENTORS])
                
                prompt = f"""
                【ダジャレ】: {user_input}

                以下の6名の審査員になりきり、それぞれのキャラ設定を死守して採点・講評してください。
                
                {mentor_prompts}
                6. 辛口師匠: 江戸っ子の毒舌落語家。「〜じゃねぇ」「〜だろ」口調。ダジャレの寒さを厳しく斬る。

                出力形式（必ず守ること）：
                キャラ名: [スコア(0-100)] | [一言講評]
                
                最後に「平均スコア: [メンター5人の平均点]」と「師匠の総括: [師匠のトドメの一言]」を出してください。
                """
                
                res = model.generate_content(prompt).text
                
                # メンターの判定をリスト表示
                st.write("#### 📝 審査員たちの判定一覧")
                lines = res.split('\n')
                scores = []
                
                for line in lines:
                    # メンター5人の行を探して表示
                    if any(m['name'] in line for m in MENTORS) and '|' in line:
                        st.write(line)
                        # スコアの数値だけ抽出
                        s = re.search(r'(\d+)', line)
                        if s: scores.append(int(s.group(1)))
                
                # スコア計算と師匠の登場
                if scores:
                    avg_score = sum(scores) / len(scores)
                    st.divider()
                    st.metric("📊 メンター平均スコア", f"{avg_score:.1f} 点")
                    
                    st.write("#### 🍶 辛口師匠の総括")
                    # 師匠の総評を探す
                    shisho_line = [l for l in lines if "師匠の総括:" in l or "辛口師匠:" in l]
                    if shisho_line:
                        st.error(shisho_line[-1].replace("師匠の総括:", "").replace("6. 辛口師匠:", ""))

                # シェア
                share_msg = f"【シャレテール2.0 大会判定】\nネタ：{user_input}\nメンター平均：{avg_score if scores else 0}点\n#ShallTell #ダジャレ大会"
                st.markdown(f'[𝕏で公式スコアを報告](https://twitter.com/intent/tweet?text={urllib.parse.quote(share_msg)})')

st.divider()
st.caption("© 2025 Shall Tell 2.0 | 2025-12-20 09:49 更新")
