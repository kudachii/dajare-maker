import streamlit as st
import google.generativeai as genai
import urllib.parse
import re

# ページ設定
st.set_page_config(page_title="Shall Tell 2.0", page_icon="🎤")

# --- API初期化 (404エラー対策・自動モデル選択) ---
@st.cache_resource
def init_dynamic_model():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            # 利用可能なモデルをリストアップして、最適なものを選択
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # 優先順位をつけてモデルを選択
            target_priority = [
                'models/gemini-1.5-flash', 
                'models/gemini-pro', 
                'gemini-1.5-flash'
            ]
            
            selected_model = None
            for target in target_priority:
                if target in available_models:
                    selected_model = target
                    break
            
            if not selected_model and available_models:
                selected_model = available_models[0]
                
            if selected_model:
                return genai.GenerativeModel(selected_model)
        return None
    except Exception as e:
        st.error(f"API初期化エラー: {e}")
        return None

model = init_dynamic_model()

# --- 審査員（メンター）データ定義 ---
MENTORS = [
    {"name": "優しさに溢れるメンター", "icon": "🌈", "prompt": "精神的安全性を高める、温かく寄り添う口調で全肯定して。"},
    {"name": "ツンデレな指導員", "icon": "💢", "prompt": "「〜なんだからね」「〜しなさいよ」といったツンデレ口調で評価して。"},
    {"name": "頼れるお姉さん", "icon": "👩‍💼", "prompt": "落ち着いた大人の口調で包み込むように。「〜よ」「〜ね」を多用して。"},
    {"name": "論理的コーチ", "icon": "🧐", "prompt": "感情を排除し、ロジックでこのダジャレの有効性を分析して。「〜だ」「〜である」調。"},
    {"name": "カサネ・イズミ", "icon": "⚙️", "prompt": "システム維持AI。一人称「私」、二人称「あなた」。「〜である」「〜と判断する」調。ノイズの中に1%の奇跡を探して。"}
]

# --- サイドバー ---
with st.sidebar:
    st.title("Shall Tell 2.0")
    if st.button("🔄 アプリをリセット", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    if model:
        st.success(f"接続中: {model.model_name}")

# --- メイン UI ---
st.title("🎤 Shall Tell 2.0")
st.caption("2025-12-20 Update: メンター五人衆システム")

tab1, tab2, tab3 = st.tabs(["✨ Generate", "🏢 Situation", "⚖️ 大会公式 Judge"])

# --- ① ネタ生成 ---
with tab1:
    word = st.text_input("お題", key="word_input", placeholder="例：パンダ")
    if st.button("Shall Tell !", type="primary"):
        if word and model:
            res = model.generate_content(f"「{word}」のダジャレ5つ。解説不要。")
            st.success(f"『{word}』の五連発")
            st.write(res.text)

# --- ② シチュエーション ---
with tab2:
    sit_word = st.text_input("キーワード", key="sit_word")
    selected_context = st.selectbox("シチュエーション", ["会議", "デート", "謝罪", "飲み会", "その他（自由入力）"])
    final_context = st.text_input("詳細状況") if selected_context == "その他（自由入力）" else selected_context
    if st.button("一言を授かる", type="primary"):
        if sit_word and final_context and model:
            res = model.generate_content(f"{final_context}で「{sit_word}」を使ったダジャレ1つ。一言のみ。")
            st.subheader(f"「{res.text.strip()}」")

# --- ③ 大会公式判定 ---
with tab3:
    st.write("### 🏆 五人衆＋師匠による公式審判")
    user_input = st.text_area("ダジャレをエントリー", key="judge_input", placeholder="例：内科にないか？")
    
    if st.button("公式判定を開始", type="primary"):
        if user_input and model:
            with st.spinner('審査員たちが協議中...'):
                mentor_info = "\n".join([f"- {m['name']}: {m['prompt']}" for m in MENTORS])
                prompt = f"""
                ユーザーのダジャレ「{user_input}」を以下の6名で判定してください。
                {mentor_info}
                - 辛口師匠: 江戸っ子の毒舌落語家。

                出力形式：
                キャラ名: [スコア] | [講評]
                最後に「平均スコア: [数値]」「師匠のトドメ: [テキスト]」を含めてください。
                """
                try:
                    response = model.generate_content(prompt)
                    res_text = response.text
                    
                    st.write("#### 📝 審査員たちの判定一覧")
                    scores = []
                    lines = res_text.split('\n')
                    for line in lines:
                        if any(m['name'] in line for m in MENTORS) and '|' in line:
                            st.write(line)
                            s = re.search(r'(\d+)', line)
                            if s: scores.append(int(s.group(1)))
                    
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        st.divider()
                        st.metric("📊 メンター平均スコア", f"{avg_score:.1f} 点")
                        
                        st.write("#### 🍶 辛口師匠の総括")
                        shisho_summary = [l for l in lines if "師匠のトドメ:" in l or "辛口師匠:" in l]
                        if shisho_summary:
                            st.error(shisho_summary[-1].split(":")[-1].strip())
                except Exception as e:
                    st.error(f"判定中にエラーが発生しました: {e}")

st.divider()
st.caption("© 2025 Shall Tell 2.0 | 粋な大人は、解説しない。")
