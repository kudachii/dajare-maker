import streamlit as st
import google.generativeai as genai
import urllib.parse
import re

# ページ設定
st.set_page_config(page_title="Shall Tell 2.0", page_icon="🎤", layout="centered")

# --- API初期化 (自動モデル選択・キャッシュ対応) ---
@st.cache_resource
def init_dynamic_model():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            # 利用可能なモデルを動的に取得
            available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            target_priority = [
                'models/gemini-1.5-flash', 
                'models/gemini-pro', 
                'gemini-1.5-flash'
            ]
            
            selected_model = next((t for t in target_priority if t in available_models), None)
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
    {"name": "優しさに溢れるメンター", "icon": "🌈", "prompt": "ユーザーの精神的安全性を高める、温かく寄り添う口調で全肯定。頑張りを認め、励ます。"},
    {"name": "ツンデレな指導員", "icon": "💢", "prompt": "「〜なんだからね」「〜しなさいよ」といったツンデレ表現。厳しくも愛がある評価。"},
    {"name": "頼れるお姉さん", "icon": "👩‍💼", "prompt": "落ち着いた大人の口調。「〜よ」「〜ね」を多用し、包み込むように励ます。"},
    {"name": "論理的コーチ", "icon": "🧐", "prompt": "感情を排除。論理とデータに基づき「〜だ」「〜である」調でダジャレを分析。"},
    {"name": "カサネ・イズミ", "icon": "⚙️", "prompt": "システム維持AI。一人称「私」、二人称「あなた」。「〜である」調。1%の奇跡を観測。"}
]

# --- サイドバー ---
with st.sidebar:
    st.title("Shall Tell 2.0")
    if st.button("🔄 アプリをリセット", use_container_width=True):
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()
    if model:
        st.success(f"System: {model.model_name}")

# --- メイン UI ---
st.title("🎤 Shall Tell 2.0")
st.caption("2025-12-20 Update: ポジティブメンター五人衆システム搭載")

tab1, tab2, tab3 = st.tabs(["✨ Generate", "🏢 Situation", "⚖️ 大会公式 Judge"])

# --- ① ネタ生成 (1.1維持) ---
with tab1:
    word = st.text_input("お題を入力", key="word_input", placeholder="例：パンダ")
    if st.button("Shall Tell !", type="primary"):
        if word and model:
            res = model.generate_content(f"「{word}」のダジャレ5つ。解説・前置き不要。")
            st.success(f"『{word}』の五連発")
            st.write(res.text)

# --- ② シチュエーション (1.1維持) ---
with tab2:
    sit_word = st.text_input("キーワード", key="sit_word")
    selected_context = st.selectbox("シチュエーション", ["会議", "デート", "謝罪", "飲み会", "その他（自由入力）"])
    final_context = st.text_input("詳細状況") if selected_context == "その他（自由入力）" else selected_context
    if st.button("一言を授かる", type="primary"):
        if sit_word and final_context and model:
            res = model.generate_content(f"{final_context}で「{sit_word}」を使ったダジャレ1つ。一言のみ。")
            st.subheader(f"「{res.text.strip()}」")

# --- ③ 大会公式判定 (2.0 目玉) ---
with tab3:
    st.write("### 🏆 五人衆＋師匠による公式審判")
    user_input = st.text_area("ダジャレをエントリー", key="judge_input", placeholder="例：内科にないか？")
    
    if st.button("公式判定を開始", type="primary"):
        if user_input and model:
            with st.spinner('審査員たちが協議中...'):
                mentor_info = "\n".join([f"- {m['name']}: {m['prompt']}" for m in MENTORS])
                prompt = f"""
                ユーザーのダジャレ「{user_input}」を以下の6名で個別に判定してください。
                
                {mentor_info}
                - 辛口師匠: 江戸っ子の毒舌落語家。厳しく斬る。

                出力形式：
                キャラ名: [スコア(0-100)] | [一言講評]
                最後に必ず「師匠のトドメ: [テキスト]」を含めてください。
                """
                try:
                    response = model.generate_content(prompt)
                    res_text = response.text
                    
                    st.write("### 🏁 判定リザルト")
                    
                    # データの抽出と表示
                    lines = res_text.split('\n')
                    scores = []
                    
                    # メンター判定をカード形式で表示（2列）
                    cols = st.columns(2)
                    m_count = 0
                    
                    for line in lines:
                        for m in MENTORS:
                            if m['name'] in line and '|' in line:
                                s_match = re.search(r'(\d+)', line)
                                comment = line.split('|')[-1].strip()
                                
                                if s_match:
                                    val = int(s_match.group(1))
                                    scores.append(val)
                                    
                                    with cols[m_count % 2]:
                                        with st.container(border=True):
                                            st.markdown(f"**{m['icon']} {m['name']}**")
                                            st.progress(val / 100)
                                            st.write(f"**{val}点** : {comment}")
                                    m_count += 1
                    
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        st.divider()
                        
                        # 平均スコアの強調表示
                        c1, c2, c3 = st.columns([1, 2, 1])
                        with c2:
                            st.metric("📊 メンター平均スコア", f"{avg_score:.1f} 点")
                        
                        # 師匠のトドメ
                        st.write("#### 🍶 辛口師匠の総括")
                        shisho_summary = [l for l in lines if "師匠のトドメ:" in l or "辛口師匠:" in l]
                        shisho_text = shisho_summary[-1].split(":")[-1].strip() if shisho_summary else "....（絶句）"
                        st.error(f"**師匠：** 「{shisho_text}」")

                        # Xシェア
                        share_text = f"【シャレテール2.0 大会判定】\n「{user_input}」\nメンター平均：{avg_score:.1f}点！\n#ShallTell #ダジャレ大会"
                        st.markdown(f'[𝕏で公式スコアを報告](https://twitter.com/intent/tweet?text={urllib.parse.quote(share_text)})')
                
                except Exception as e:
                    st.error(f"判定エラー: {e}")

st.divider()
st.caption("© 2025 Shall Tell 2.0 | 粋な大人は、解説しない。")
