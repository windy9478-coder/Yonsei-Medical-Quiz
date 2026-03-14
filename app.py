import streamlit as st
import pandas as pd
import random
import requests
import webbrowser
from PIL import Image
import time
import streamlit as st
import streamlit_analytics2 as streamlit_analytics

# ==========================================================
# [Copyright & About]
# Copyright (c) 2026 Inho Jung (windy9478-coder). All rights reserved.
# ==========================================================

CURRENT_VERSION = "v1.1.3"  # 대시보드 생성

# 1. 페이지 설정 (최상단 유지)
st.set_page_config(page_title="연세 간호 의학용어 테스트", page_icon="🩺", layout="centered")

# 2. 분석 트래킹 시작 (이 아래로 모든 코드 들여쓰기 완료)
with streamlit_analytics.track():
    # 2. 커스텀 CSS
    st.markdown("""
    <style>
    .stApp { background-color: #003876; }
    h1, h2, h3, p, label, .stMarkdown { color: white !important; }
    .stButton>button {
        background-color: #0052A4; color: white; border-radius: 8px;
        border: 2px solid #FFD700; font-weight: bold; width: 100%;
    }
    .stButton>button:hover { background-color: #FFD700; color: #003876; }
    @media (prefers-color-scheme: dark) {
        .stTextInput>div>div>input { color: black !important; background-color: white !important; }
    }
    @media (prefers-color-scheme: light) {
        .stTextInput>div>div>input { color: white !important; background-color: #003876 !important; }
    }
    .intro-box { text-align: center; margin-bottom: 30px; }
    .dev-badge {
        background-color: rgba(255, 215, 0, 0.15); padding: 12px;
        border-radius: 10px; border: 1px solid #FFD700; display: inline-block; margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    # 3. 세션 상태 초기화
    states = {
        'auth_success': False, 'quiz_data': None, 'current_index': 0,
        'score': 0, 'wrong_answers': [], 'quiz_started': False,
        'quiz_finished': False, 'quiz_mode': "유형 1: 약어 → Full Term + 뜻"
    }
    for key, value in states.items():
        if key not in st.session_state:
            st.session_state[key] = value


    def check_for_updates():
        repo_url = "https://api.github.com/repos/windy9478-coder/Yonsei-Medical-Quiz/releases/latest"
        try:
            response = requests.get(repo_url, timeout=3)
            if response.status_code == 200:
                latest_version = response.json()['tag_name']
                if latest_version != CURRENT_VERSION:
                    if st.sidebar.button(f"🆕 새 버전({latest_version}) 다운로드"):
                        webbrowser.open("https://github.com/windy9478-coder/Yonsei-Medical-Quiz/releases")
        except:
            pass


    # 4. 사이드바
    with st.sidebar:
        try:
            logo = Image.open("기본형_심볼-03.jpg")
            st.image(logo, use_container_width=True)
        except:
            st.markdown("### 🏛️ YONSEI NURSING")

        if not st.session_state.auth_success:
            pw = st.text_input("보안코드를 입력하세요", type="password")
            if st.button("인증하기"):
                if pw == "yonseinursing":
                    st.session_state.auth_success = True
                    st.rerun()
                else:
                    st.error("보안코드가 틀렸습니다.")
        else:
            st.success("✅ 인증 성공")
            check_for_updates()
            if st.button("로그아웃"):
                for key in states: st.session_state[key] = states[key]
                st.rerun()

        st.markdown("---")
        st.markdown(f"**Version:** {CURRENT_VERSION}\n**Dev:** 정인호\n© 2026 Inho Jung.")

    # 5. 메인 화면 안내
    st.markdown(f"""
        <div class='intro-box'>
            <h1 style='color: #FFD700;'>🩺 의학용어 테스트</h1>
            <p style='font-size: 17px;'>연세대학교 간호학과 테스트 솔루션</p>
            <div class='dev-badge'>
                <p style='color: #FFD700; margin: 0;'>👨‍💻 개발자: 정인호 | 📧 windy9478@gmail.com</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    if not st.session_state.auth_success:
        st.info("💡 사이드바에서 보안코드를 입력하면 시작할 수 있습니다.")
        st.stop()

    # 6. 설정 및 파일 업로드 화면
    if not st.session_state.quiz_started and not st.session_state.quiz_finished:
        st.subheader("📂 퀴즈 설정")

        with st.expander("📋 CSV 파일 작성 가이드 (필독)", expanded=True):
            st.markdown("""
                    학우분들이 직접 만든 단어장으로 공부할 수 있습니다! 아래 **예시 화면**처럼 파일을 구성해 주세요.
                    1. **엑셀 구성**: [A열: 약어] | [B열: Full Term] | [C열: 한글 뜻] 1행부터 단어 써주세요.
                    2. **일반 의학용어 퀴즈**: 약어 퀴즈가 아닌 일반 영단어 퀴즈를 보고 싶다면 **A열을 비우고** B열에 영어, C열에 한글을 적어주세요.
                    3. **저장 방식**: [다른 이름으로 저장] → 파일 형식을 **'CSV (쉼표로 분리)(*.csv)'**로 선택
                    4. **주의**: 한글 깨짐 방지를 위해 가급적 **'CSV UTF-8'** 형식을 사용해 주세요.
                    """)
            try:
                st.image(Image.open("csv_example.png"), use_container_width=True)
            except:
                pass

        uploaded_file = st.file_uploader("단어장(CSV) 업로드", type=["csv"])

        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file, encoding='utf-8-sig', header=None)
            except:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='cp949', header=None)

            if df.shape[1] < 3:
                st.error("CSV 열이 부족합니다.")
            else:
                st.success(f"✅ {len(df)}개의 단어 로드 완료 (1행 포함)")

                mode = st.selectbox("📝 문제 유형을 선택하세요:", [
                    "유형 1: 약어 → Full Term + 뜻",
                    "유형 2: Full Term → 뜻 (영->한)",
                    "유형 3: 뜻 → Full Term (한->영)"
                ])
                q_count = st.number_input("문제 수:", 1, len(df), min(20, len(df)))

                if st.button("퀴즈 시작하기! 🚀"):
                    st.session_state.quiz_data = df.sample(n=q_count).reset_index(drop=True)
                    st.session_state.quiz_mode = mode
                    st.session_state.quiz_started = True
                    st.rerun()

    # 7. 퀴즈 진행 화면
    elif st.session_state.quiz_started and not st.session_state.quiz_finished:
        df, idx = st.session_state.quiz_data, st.session_state.current_index
        mode, total = st.session_state.quiz_mode, len(df)

        st.markdown(f"### {mode} ({idx + 1} / {total})")
        st.progress((idx + 1) / total)

        if "유형 1" in mode:
            question_text = df.iloc[idx, 0]
            if pd.isna(question_text) or str(question_text).strip() == "":
                question_text = "(약어 없음 - B열 참고)"
        elif "유형 2" in mode:
            question_text = df.iloc[idx, 1]
        else:
            question_text = df.iloc[idx, 2]

        st.markdown(f"<h1 style='text-align: center; color: #FFD700;'>{question_text}</h1>", unsafe_allow_html=True)

        with st.form(key=f'q_{idx}', clear_on_submit=False):
            if "유형 1" in mode:
                ans_f = st.text_input("Full Term (영어)", key=f"f_{idx}")
                ans_m = st.text_input("한글 뜻", key=f"m_{idx}")
            elif "유형 2" in mode:
                ans_m = st.text_input("한글 뜻을 입력하세요", key=f"m_{idx}")
            else:
                ans_f = st.text_input("Full Term을 입력하세요 (영어)", key=f"f_{idx}")

            submitted = st.form_submit_button("정답 제출 (Enter)")

        if submitted:
            corr_f = str(df.iloc[idx, 1]).strip().lower().replace(" ", "")
            corr_m = str(df.iloc[idx, 2]).strip().replace(" ", "")

            user_f = ans_f.strip().lower().replace(" ", "") if "ans_f" in locals() or "ans_f" in globals() else ""
            user_m = ans_m.strip().replace(" ", "") if "ans_m" in locals() or "ans_m" in globals() else ""

            is_correct = False
            if "유형 1" in mode:
                if (user_f == corr_f) and (user_m == corr_m): is_correct = True
            elif "유형 2" in mode:
                if user_m == corr_m: is_correct = True
            else:
                if user_f == corr_f: is_correct = True

            if is_correct:
                st.session_state.score += 1
                st.success("✨ 정답입니다! 2초 뒤 이동합니다.")
            else:
                st.session_state.wrong_answers.append({
                    '약어': df.iloc[idx, 0],
                    'FullTerm': df.iloc[idx, 1],
                    '뜻': df.iloc[idx, 2]
                })
                st.error(f"오답! 정답: {df.iloc[idx, 1]} ({df.iloc[idx, 2]})")

            time.sleep(2)
            if idx + 1 < total:
                st.session_state.current_index += 1
            else:
                st.session_state.quiz_finished = True
            st.rerun()

    # 8. 결과 화면
    elif st.session_state.quiz_finished:
        st.subheader("📊 테스트 결과")
        score, total = st.session_state.score, len(st.session_state.quiz_data)
        st.metric("최종 점수", f"{score} / {total}", f"{(score / total) * 100:.1f} 점")

        if score == total: st.balloons()

        if st.session_state.wrong_answers:
            st.markdown("### ❌ 오답 리스트")
            display_wrong = pd.DataFrame(st.session_state.wrong_answers)
            st.table(display_wrong)

            if st.button("🔄 오답만 다시 풀기"):
                new_quiz_df = pd.DataFrame(st.session_state.wrong_answers)
                new_quiz_df.columns = [0, 1, 2]

                st.session_state.quiz_data = new_quiz_df.reset_index(drop=True)
                st.session_state.current_index = 0
                st.session_state.score = 0
                st.session_state.wrong_answers = []
                st.session_state.quiz_finished = False
                st.session_state.quiz_started = True
                st.rerun()

        if st.button("🏠 처음으로 돌아가기"):
            for key in ['quiz_data', 'current_index', 'score', 'wrong_answers', 'quiz_started', 'quiz_finished']:
                st.session_state[key] = states[key]
            st.rerun()
