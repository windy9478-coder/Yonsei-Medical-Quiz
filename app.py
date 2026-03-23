import streamlit as st
import pandas as pd
import random
import requests
import webbrowser
from PIL import Image
import time
import streamlit_analytics2 as streamlit_analytics
import re

# ==========================================================
# [Copyright & About]
# Copyright (c) 2026 Inho Jung (windy9478-coder). All rights reserved.
# ==========================================================

CURRENT_VERSION = "v1.1.5"

st.set_page_config(page_title="연세 간호 의학용어 테스트", page_icon="🩺", layout="centered")

def normalize_text(text):
    if pd.isna(text): return ""
    return str(text).replace(" ", "").replace("-", "").replace("/", "").lower()

def check_answer(user_ans, correct_ans):
    u, c = normalize_text(user_ans), normalize_text(correct_ans)
    if u == c: return True
    if "(" in str(correct_ans):
        base = normalize_text(re.sub(r'\(.*\)', '', str(correct_ans)))
        inner = normalize_text(re.search(r'\((.*)\)', str(correct_ans)).group(1)) if re.search(r'\((.*)\)', str(correct_ans)) else ""
        if u == base or u == inner: return True
    return False

with streamlit_analytics.track():
    st.markdown("""
    <style>
    .stApp { background-color: #003876; }
    h1, h2, h3, p, label, .stMarkdown { color: white !important; }
    .stButton>button {
        background-color: #0052A4; color: white; border-radius: 8px;
        border: 2px solid #FFD700; font-weight: bold; width: 100%;
    }
    .stButton>button:hover { background-color: #FFD700; color: #003876; }
    .intro-box { text-align: center; margin-bottom: 30px; }
    .dev-badge {
        background-color: rgba(255, 215, 0, 0.15); padding: 12px;
        border-radius: 10px; border: 1px solid #FFD700; display: inline-block; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    states = {
        'auth_success': False, 'master_pool': None, 'quiz_data': None, 
        'current_index': 0, 'score': 0, 'wrong_answers': [], 
        'quiz_started': False, 'quiz_finished': False, 
        'quiz_mode': "유형 1: 약어 → Full Term + 뜻",
        'user_responses': {}
    }
    for key, value in states.items():
        if key not in st.session_state:
            st.session_state[key] = value

    with st.sidebar:
        try:
            st.image(Image.open("기본형_심볼-03.jpg"), use_container_width=True)
        except:
            st.markdown("### 🏛️ YONSEI NURSING")

        # --- 수정된 인증 로직 ---
        if not st.session_state.auth_success:
            pw = st.text_input("보안코드", type="password")
            if st.button("인증"):
                if pw == "yonseinursing":
                    st.session_state.auth_success = True
                    st.rerun()
                else:
                    st.error("보안코드가 틀렸습니다.")
        else:
            st.success("✅ 인증 완료")
            if st.button("로그아웃"):
                for key in states: st.session_state[key] = states[key]
                st.rerun()

        st.markdown("---")
        st.markdown(f"**Version:** {CURRENT_VERSION}\n**Dev:** 정인호\n© 2026 Inho Jung.")

    st.markdown("<div class='intro-box'><h1 style='color: #FFD700;'>🩺 의학용어 테스트</h1><p>연세대학교 간호학과 스마트 테스트 솔루션</p></div>", unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.auth_success:
        st.info("💡 사이드바에서 보안코드를 입력해 주세요.")
        st.stop()

    # 6. 설정 및 파일 업로드
    if not st.session_state.quiz_started and not st.session_state.quiz_finished:
        st.subheader("📂 퀴즈 설정")
        uploaded_file = st.file_uploader("단어장(CSV) 업로드", type=["csv"])

        if uploaded_file:
            if st.session_state.master_pool is None:
                try: df = pd.read_csv(uploaded_file, encoding='utf-8-sig', header=None)
                except: 
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding='cp949', header=None)
                st.session_state.master_pool = df
            
            pool = st.session_state.master_pool
            st.success(f"✅ 현재 학습 가능: {len(pool)}개")
            
            if len(pool) == 0:
                st.warning("모든 문제를 다 풀었습니다!")
                if st.button("전체 문제 초기화"):
                    st.session_state.master_pool = None
                    st.rerun()
            else:
                mode = st.selectbox("📝 문제 유형:", ["유형 1: 약어 → Full Term + 뜻", "유형 2: Full Term → 뜻", "유형 3: 뜻 → Full Term"])
                q_count = st.number_input("문제 수:", 1, len(pool), min(20, len(pool)))

                if st.button("퀴즈 시작하기! 🚀"):
                    st.session_state.quiz_data = pool.sample(n=q_count)
                    st.session_state.master_pool = pool.drop(st.session_state.quiz_data.index)
                    st.session_state.quiz_data = st.session_state.quiz_data.reset_index(drop=True)
                    st.session_state.quiz_mode, st.session_state.quiz_started = mode, True
                    st.session_state.user_responses = {}
                    st.rerun()

    # 7. 퀴즈 진행
    elif st.session_state.quiz_started and not st.session_state.quiz_finished:
        df, idx = st.session_state.quiz_data, st.session_state.current_index
        mode, total = st.session_state.quiz_mode, len(df)
        st.markdown(f"### {mode} ({idx + 1} / {total})")
        st.progress((idx + 1) / total)

        q_text = df.iloc[idx, 0] if "유형 1" in mode else (df.iloc[idx, 1] if "유형 2" in mode else df.iloc[idx, 2])
        st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>{q_text}</h1>", unsafe_allow_html=True)

        prev_f = st.session_state.user_responses.get(f"f_{idx}", "")
        prev_m = st.session_state.user_responses.get(f"m_{idx}", "")

        with st.form(key=f'q_{idx}', clear_on_submit=False):
            ans_f, ans_m = None, None
            if "유형 1" in mode:
                ans_f = st.text_input("Full Term (영어)", value=prev_f, key=f"f_in_{idx}")
                ans_m = st.text_input("한글 뜻", value=prev_m, key=f"m_in_{idx}")
            elif "유형 2" in mode: ans_m = st.text_input("한글 뜻", value=prev_m, key=f"m_in_{idx}")
            else: ans_f = st.text_input("Full Term (영어)", value=prev_f, key=f"f_in_{idx}")
            
            col1, col2 = st.columns(2)
            with col2: submitted = st.form_submit_button("정답 제출 (Enter) ➡️")
            with col1: back = st.form_submit_button("⬅️ 이전 문제")

        if back:
            if idx > 0:
                st.session_state.current_index -= 1
                st.rerun()
            else: st.warning("첫 번째 문제입니다.")

        if submitted:
            if ans_f: st.session_state.user_responses[f"f_{idx}"] = ans_f
            if ans_m: st.session_state.user_responses[f"m_{idx}"] = ans_m
            
            correct_f, correct_m = df.iloc[idx, 1], df.iloc[idx, 2]
            res_f = check_answer(ans_f, correct_f) if ans_f is not None else True
            res_m = check_answer(ans_m, correct_m) if ans_m is not None else True

            if res_f and res_m:
                st.session_state.score += 1
                st.success("✨ 정답입니다!")
            else:
                st.session_state.wrong_answers.append({
                    '문제': q_text, '내 답변(영)': ans_f if ans_f else "-", '정답(영)': correct_f,
                    '내 답변(한)': ans_m if ans_m else "-", '정답(한)': correct_m
                })
                st.error(f"오답! 정답: {correct_f} ({correct_m})")

            time.sleep(2)
            if idx + 1 < total:
                st.session_state.current_index += 1
                st.rerun()
            else:
                st.session_state.quiz_finished = True
                st.rerun()

    # 8. 결과 화면
    elif st.session_state.quiz_finished:
        st.subheader("📊 테스트 결과")
        score, total = st.session_state.score, len(st.session_state.quiz_data)
        st.metric("최종 점수", f"{score} / {total}")
        
        if st.session_state.wrong_answers:
            st.table(pd.DataFrame(st.session_state.wrong_answers))
            if st.button("🔄 오답만 다시 풀기"):
                wrong_list = [[w['문제'], w['정답(영)'], w['정답(한)']] for w in st.session_state.wrong_answers]
                new_df = pd.DataFrame(wrong_list).sample(frac=1)
                new_df.columns = [0, 1, 2]
                st.session_state.quiz_data = new_df.reset_index(drop=True)
                st.session_state.current_index, st.session_state.score = 0, 0
                st.session_state.wrong_answers, st.session_state.quiz_finished, st.session_state.quiz_started = [], False, True
                st.rerun()

        if st.button("🏠 다음 세트 풀러 가기"):
            for key in ['quiz_data', 'current_index', 'score', 'wrong_answers', 'quiz_started', 'quiz_finished', 'user_responses']:
                st.session_state[key] = states[key]
            st.rerun()
