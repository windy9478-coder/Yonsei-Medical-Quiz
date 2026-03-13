# ==========================================================
# Copyright (c) 2026 Inho Jung (windy9478-coder). All rights reserved.
# 본 프로그램의 저작권은 22학번 정인호에게 있습니다.
# 무단 복제, 수정 및 재배포를 금지하며, 적발 시 법적 책임을 물을 수 있습니다.
# ==========================================================
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import csv
import random
import os
from PIL import Image, ImageTk
import webbrowser
import requests # 터미널에서 pip install requests 필요


class MedicalVocaApp:
    def __init__(self, root):
        self.root = root
        self.current_version = "v1.2.3"  # 현재 프로그램 버전

        # 1. 보안코드 확인 전 업데이트부터 체크!
        self.check_for_updates()

        if not self.check_security_code():
            self.root.destroy()
            return

        # 2. 기본 UI 및 설정
        self.root.title("연세대 간호학과 의학약어 퀴즈")
        self.root.geometry("800x900")  # 안내 문구가 늘어남에 따라 높이 조절

        # --- 시각적 최적화 테마 ---
        self.bg_color = "#003876"  # 연세 블루
        self.text_color = "#FFFFFF"
        self.point_color = "#FFD700"  # 골드 (강조색)
        self.entry_bg = "#FFFFFF"
        self.btn_bg = "#0052A4"

        self.font_title = ("Malgun Gothic", 22, "bold")
        self.font_desc = ("Malgun Gothic", 11)  # 설명용 폰트
        self.font_main = ("Malgun Gothic", 14, "bold")
        self.font_voca = ("Arial", 32, "bold")

        self.root.configure(bg=self.bg_color)

        self.all_terms = []
        self.current_quiz = []
        self.wrong_answers = []
        self.current_index = 0
        self.score = 0

        self.main_container = tk.Frame(self.root, bg=self.bg_color)
        self.main_container.pack(fill="both", expand=True)

        self.show_welcome_screen()

    def check_for_updates(self):
        """깃허브에서 최신 릴리즈 버전을 확인하는 함수"""
        # 인호의 실제 깃허브 아이디와 저장소 이름으로 확인해줘!
        repo_url = "https://api.github.com/repos/windy9478-coder/Yonsei-Medical-Quiz/releases/latest"
        try:
            response = requests.get(repo_url, timeout=5)  # 5초 안에 응답 없으면 패스
            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release['tag_name']  # 예: v1.0.0

                if latest_version != self.current_version:
                    if messagebox.askyesno("업데이트 알림",
                                           f"새로운 버전({latest_version})이 출시되었습니다!\n지금 업데이트를 위해 다운로드 페이지로 이동할까요?"):
                        webbrowser.open("https://github.com/windy9478-coder/Yonsei-Medical-Quiz/releases")
                        self.root.destroy()
        except Exception as e:
            print(f"업데이트 체크 실패: {e}")
            pass  # 인터넷 연결이 안 된 경우 그냥 진행

    def check_security_code(self):
        """커스텀 디자인된 보안 확인 창"""
        self.auth_success = False

        # 1. 보안용 서브 윈도우 설정
        auth_win = tk.Toplevel(self.root)
        auth_win.title("Security Check")
        auth_win.geometry("450x350")
        auth_win.configure(bg="#003876")  # 연세 블루
        auth_win.resizable(False, False)

        # 메인 창이 뜨기 전에 이 창이 최상단에 오도록 설정
        auth_win.transient(self.root)
        auth_win.grab_set()

        # 2. 로고 및 텍스트 (간지 포인트)
        try:
            # 기존 로고 재활용 (사이즈만 작게)
            img = Image.open("기본형_심볼-03.jpg").convert("RGBA")
            grayscale = img.convert("L")
            mask = grayscale.point(lambda x: 0 if x > 235 else 255)
            img.putalpha(mask)
            img.thumbnail((150, 100))
            self.auth_logo = ImageTk.PhotoImage(img)
            tk.Label(auth_win, image=self.auth_logo, bg="#003876").pack(pady=(30, 10))
        except:
            tk.Label(auth_win, text="🛡️", font=("Arial", 40), bg="#003876", fg="#FFD700").pack(pady=(30, 10))

        tk.Label(auth_win, text="AUTHORIZED PERSONNEL ONLY",
                 font=("Arial", 12, "bold"), bg="#003876", fg="#FFD700").pack()
        tk.Label(auth_win, text="연세 간호 의학용어 마스터 보안 인증",
                 font=("Malgun Gothic", 10), bg="#003876", fg="#FFFFFF").pack(pady=(5, 20))

        # 3. 입력 필드
        entry_pw = tk.Entry(auth_win, font=("Arial", 16), show="●", width=20, justify="center", bd=0)
        entry_pw.pack(pady=10, ipady=5)
        entry_pw.focus()

        # 4. 검증 로직
        def validate():
            if entry_pw.get() == "yonseinursing":
                self.auth_success = True
                auth_win.destroy()
            else:
                messagebox.showerror("Access Denied", "보안코드가 일치하지 않습니다.")
                entry_pw.delete(0, tk.END)

        # 5. 버튼 (세련된 블루 버튼)
        btn_verify = tk.Button(auth_win, text="VERIFY ACCESS", command=validate,
                               font=("Arial", 10, "bold"), bg="#0052A4", fg="white",
                               padx=20, pady=5, relief="flat", cursor="hand2")
        btn_verify.pack(pady=20)

        # 엔터 키 바인딩
        auth_win.bind('<Return>', lambda e: validate())

        # 창이 닫힐 때까지 대기
        self.root.wait_window(auth_win)
        return self.auth_success

    def show_about_info(self):
        """프로그램 정보를 보여주는 커스텀 팝업"""
        about_win = tk.Toplevel(self.root)
        about_win.title("Program Information")
        about_win.geometry("400x450")
        about_win.configure(bg=self.bg_color)
        about_win.resizable(False, False)

        # 메인 창 중앙에 오도록 설정
        about_win.transient(self.root)
        about_win.grab_set()

        # 1. 아이콘/로고 (텍스트로 대체 가능)
        tk.Label(about_win, text="🩺", font=("Arial", 50), bg=self.bg_color).pack(pady=(30, 10))

        # 2. 프로그램 제목 및 버전
        tk.Label(about_win, text="연세 간호 의학용어 마스터",
                 font=("Malgun Gothic", 16, "bold"), bg=self.bg_color, fg=self.point_color).pack()
        tk.Label(about_win, text=f"Version {self.current_version}",
                 font=("Arial", 10), bg=self.bg_color, fg="#AAAAAA").pack(pady=(0, 20))

        # 3. 상세 정보 (저작권 강조)
        info_text = (
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "👨‍💻 Developer: 22학번 정인호\n"
            "📧 Contact: windy9478@gmail.com\n"
            "🏛️ Affiliation: Yonsei Univ. College of Nursing\n\n"
            "━━━━━━━━━━━━━━━━━━━━\n\n"
            "© 2026 Inho Jung. All rights reserved.\n"
            "본 프로그램의 모든 저작권은 제작자에게 있습니다.\n"
            "무단 전재 및 재배포를 금지합니다."
        )

        tk.Label(about_win, text=info_text, font=("Malgun Gothic", 10),
                 bg=self.bg_color, fg=self.text_color, justify="center").pack()

        # 4. 닫기 버튼
        tk.Button(about_win, text="확인", command=about_win.destroy,
                  bg=self.btn_bg, fg="white", font=("Malgun Gothic", 10, "bold"),
                  padx=30, pady=5, relief="flat", cursor="hand2").pack(pady=30)
    def clear_screen(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def add_bottom_logo(self, parent):
        """밝기 기반 마스크를 활용해 로고 배경을 투명하게 처리"""
        try:
            img = Image.open("기본형_심볼-03.jpg").convert("RGBA")
            grayscale = img.convert("L")
            mask = grayscale.point(lambda x: 0 if x > 235 else 255)
            img.putalpha(mask)
            img.thumbnail((400, 180))
            self.logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(parent, image=self.logo_img, bg=self.bg_color)
            logo_label.pack(side="bottom", pady=30)
        except:
            pass

    # --- 1. 초기 시작 화면 ---
    def show_welcome_screen(self):
        self.clear_screen()

        welcome_text = (
            "안녕하세요! 연세대학교 간호학과 학우 여러분.\n"
            "의학용어 및 약어 암기를 돕기 위해 제작된 프로그램입니다.\n"
            "자유롭게 배포 가능하며, 문의 사항은 아래 메일로 연락 주세요."
        )

        tk.Label(self.main_container, text="🩺 의학용어 암기 마스터", font=self.font_title,
                 bg=self.bg_color, fg=self.point_color).pack(pady=(60, 20))

        tk.Label(self.main_container, text=welcome_text, font=self.font_desc,
                 bg=self.bg_color, fg=self.text_color, justify="center").pack(pady=10)

        dev_info = "개발자: 22학번 정인호\nEmail: windy9478@gmail.com"
        tk.Label(self.main_container, text=dev_info, font=self.font_desc,
                 bg=self.bg_color, fg=self.point_color).pack(pady=10)

        tk.Button(self.main_container, text="START 🚀", command=self.show_setup_screen,
                  font=("Malgun Gothic", 16, "bold"), bg=self.btn_bg, fg=self.text_color,
                  padx=50, pady=10).pack(pady=30)
        # 정보(About) 버튼 추가 (작고 깔끔하게)
        tk.Button(self.main_container, text="ℹ️ 프로그램 정보", command=self.show_about_info,
                  font=("Malgun Gothic", 10), bg=self.bg_color, fg="#AAAAAA",
                  relief="flat", cursor="hand2").pack(pady=5)

        self.add_bottom_logo(self.main_container)

    # --- 2. CSV 등록 및 친절한 가이드 화면 ---
    def show_setup_screen(self):
        self.clear_screen()

        tk.Label(self.main_container, text="📂 퀴즈 파일 등록 및 설정", font=self.font_title,
                 bg=self.bg_color, fg=self.point_color).pack(pady=30)

        # --- 친절한 가이드 텍스트 박스 ---
        guide_frame = tk.LabelFrame(self.main_container, text="[ CSV 파일 등록 방법 ]",
                                    font=self.font_main, bg=self.bg_color, fg=self.point_color, padx=20, pady=15)
        guide_frame.pack(pady=10, padx=40, fill="x")

        guide_text = (
            "1. 엑셀을 열고 [A열: 약어 / B열: Full Term / C열: 한글 뜻]을 입력하세요.\n"
            "2. [다른 이름으로 저장] → 파일 형식을 'CSV (쉼표로 분리)'로 선택해 저장하세요.\n"
            "   (한글이 깨진다면 'CSV UTF-8' 형식을 권장합니다.)\n"
            "3. 아래 버튼을 눌러 저장한 파일을 등록하면 퀴즈 준비 끝!\n"
            "※ 파일 확장자(.csv)가 보이지 않는다면 탐색기 '보기'에서 체크해주세요."
        )
        tk.Label(guide_frame, text=guide_text, font=self.font_desc, bg=self.bg_color,
                 fg=self.text_color, justify="left").pack()

        # 파일 선택 버튼
        self.btn_csv = tk.Button(self.main_container, text="1. 의학용어 CSV 파일 선택하기", command=self.load_data,
                                 font=self.font_main, bg="#E1E1E1", fg="black", padx=20)
        self.btn_csv.pack(pady=(30, 5))

        self.file_label = tk.Label(self.main_container, text="아직 선택된 파일이 없습니다.",
                                   font=self.font_desc, bg=self.bg_color, fg="#AAAAAA")
        self.file_label.pack(pady=5)

        # 문제 수 설정
        tk.Label(self.main_container, text="2. 이번 세트에서 풀고 싶은 문제 수:",
                 font=self.font_main, bg=self.bg_color, fg=self.text_color).pack(pady=(20, 10))

        self.entry_count = tk.Entry(self.main_container, font=self.font_main, width=10, justify="center")
        self.entry_count.insert(0, "20")
        self.entry_count.pack()

        tk.Button(self.main_container, text="퀴즈 시작하기!", command=self.prepare_quiz,
                  font=self.font_main, bg=self.btn_bg, fg=self.text_color, padx=40, pady=10).pack(pady=40)

        self.add_bottom_logo(self.main_container)

    # --- (이하 load_data, prepare_quiz, quiz_screen 등 기존 로직 유지) ---
    def load_data(self):
        file_path = filedialog.askopenfilename(title="CSV 파일 선택", filetypes=[("CSV Files", "*.csv")])
        if not file_path: return
        self.all_terms = []
        encodings = ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']
        for enc in encodings:
            try:
                with open(file_path, 'r', encoding=enc, errors='replace') as f:
                    reader = csv.reader(f)
                    self.all_terms = [[c.strip() for c in row] for row in reader if row and len(row) >= 3]
                if self.all_terms:
                    self.file_label.config(text=f"✅ 선택됨: {os.path.basename(file_path)}", fg=self.point_color)
                    break
            except:
                continue

    def prepare_quiz(self):
        if not self.all_terms:
            messagebox.showwarning("경고", "먼저 CSV 파일을 등록해주세요!")
            return
        try:
            count = int(self.entry_count.get())
            count = min(count, len(self.all_terms))
            self.current_quiz = random.sample(self.all_terms, count)
            self.show_quiz_screen()
        except:
            messagebox.showerror("오류", "문제 수는 숫자로 입력해주세요!")

    # --- (기존 show_quiz_screen, check_answer, show_summary_screen 등 생략) ---
    # (위의 로직들은 이전 버전과 동일하게 유지하면 됩니다.)

    # --- 3. 퀴즈 진행 화면 ---
    def show_quiz_screen(self):
        self.clear_screen()
        self.current_index = 0
        self.score = 0
        self.wrong_answers = []

        self.progress_label = tk.Label(self.main_container, text="", font=self.font_main, bg=self.bg_color,
                                       fg=self.text_color)
        self.progress_label.pack(pady=20)

        self.abbr_label = tk.Label(self.main_container, text="", font=self.font_voca, bg=self.bg_color,
                                   fg=self.point_color)
        self.abbr_label.pack(pady=30)

        input_frame = tk.Frame(self.main_container, bg=self.bg_color)
        input_frame.pack(pady=20)

        tk.Label(input_frame, text="Full Term:", font=self.font_main, bg=self.bg_color, fg=self.text_color).grid(row=0,
                                                                                                                 column=0,
                                                                                                                 sticky="e",
                                                                                                                 pady=10)
        self.entry_full = tk.Entry(input_frame, font=self.font_main, width=35)
        self.entry_full.grid(row=0, column=1, padx=15)
        self.entry_full.bind('<Return>', lambda e: self.entry_mean.focus())

        tk.Label(input_frame, text="한글 뜻:", font=self.font_main, bg=self.bg_color, fg=self.text_color).grid(row=1,
                                                                                                            column=0,
                                                                                                            sticky="e",
                                                                                                            pady=10)
        self.entry_mean = tk.Entry(input_frame, font=self.font_main, width=35)
        self.entry_mean.grid(row=1, column=1, padx=15)
        self.entry_mean.bind('<Return>', lambda e: self.check_answer())

        self.btn_submit = tk.Button(self.main_container, text="정답 제출 (Enter)", command=self.check_answer,
                                    bg=self.btn_bg, fg=self.text_color, font=self.font_main, padx=30, pady=5)
        self.btn_submit.pack(pady=20)

        tk.Button(self.main_container, text="중도 종료 및 채점", command=self.finish_early,
                  bg="#555555", fg="white", font=self.font_desc).pack()

        self.result_label = tk.Label(self.main_container, text="", font=self.font_main, bg=self.bg_color)
        self.result_label.pack(pady=10)

        self.show_next_question()

    def show_next_question(self):
        self.entry_full.delete(0, tk.END)
        self.entry_mean.delete(0, tk.END)
        self.result_label.config(text="")
        self.entry_full.focus()

        if self.current_index < len(self.current_quiz):
            abbr, _, _ = self.current_quiz[self.current_index]
            self.progress_label.config(text=f"Q {self.current_index + 1} / {len(self.current_quiz)}")
            self.abbr_label.config(text=abbr)
        else:
            self.show_summary_screen()

    def check_answer(self):
        if self.current_index >= len(self.current_quiz): return

        u_full = self.entry_full.get().strip().lower()
        u_mean = self.entry_mean.get().strip()
        abbr, c_full, c_mean = self.current_quiz[self.current_index]

        if u_full == c_full.lower() and u_mean == c_mean:
            self.score += 1
            self.result_label.config(text="정답입니다! ✅", fg="#00FF7F")
        else:
            self.result_label.config(text=f"오답! 정답: {c_full} / {c_mean}", fg="#FF6347")
            self.wrong_answers.append([abbr, c_full, c_mean])

        self.current_index += 1
        self.root.after(1000, self.show_next_question)

    def finish_early(self):
        if messagebox.askyesno("중도 종료", "지금까지 푼 문제만 채점할까요?"):
            self.show_summary_screen(early=True)

    # --- 4. 오답 요약 및 선택 화면 ---
    def show_summary_screen(self, early=False):
        self.clear_screen()
        total = self.current_index if early else len(self.current_quiz)

        tk.Label(self.main_container, text="📊 테스트 요약", font=self.font_title,
                 bg=self.bg_color, fg=self.point_color).pack(pady=20)

        tk.Label(self.main_container, text=f"맞힌 개수: {self.score} / {total}",
                 font=self.font_main, bg=self.bg_color, fg=self.text_color).pack()

        if self.wrong_answers:
            tk.Label(self.main_container, text="[ 오답 리스트 ]", font=self.font_main,
                     bg=self.bg_color, fg="#FF6347").pack(pady=(20, 5))

            # 오답 목록 스크롤 뷰
            txt = scrolledtext.ScrolledText(self.main_container, width=70, height=12, font=self.font_desc)
            txt.pack(pady=10)
            for abbr, full, mean in self.wrong_answers:
                txt.insert(tk.END, f"• {abbr}: {full} ({mean})\n")
            txt.config(state=tk.DISABLED)

            tk.Button(self.main_container, text="틀린 문제만 다시 풀기 🔄", command=self.retry_wrong,
                      font=self.font_main, bg="#FF4500", fg="white", padx=20).pack(pady=5)
        else:
            tk.Label(self.main_container, text="🎉 완벽합니다! 틀린 문제가 없어요!",
                     font=self.font_main, bg=self.bg_color, fg="#00FF7F").pack(pady=50)

        btn_frame = tk.Frame(self.main_container, bg=self.bg_color)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="새로운 문제 세트 풀기", command=self.show_setup_screen,
                  font=self.font_main, bg=self.btn_bg, fg="white", padx=10).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="처음으로", command=self.show_welcome_screen,
                  font=self.font_main, bg="#696969", fg="white", padx=10).grid(row=0, column=1, padx=10)

    def retry_wrong(self):
        self.current_quiz = self.wrong_answers
        random.shuffle(self.current_quiz)
        self.show_quiz_screen()


if __name__ == "__main__":
    root = tk.Tk()
    app = MedicalVocaApp(root)

    root.mainloop()

