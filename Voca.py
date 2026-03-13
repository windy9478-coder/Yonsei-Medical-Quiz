# ==========================================================
# Copyright (c) 2026 Inho Jung (windy9478-coder). All rights reserved.
# 본 프로그램의 저작권은 22학번 정인호에게 있습니다.
# 무단 복제, 수정 및 재배포를 금지하며, 적발 시 법적 책임을 물을 수 있습니다.
# ==========================================================

import csv
import os
import random
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import requests  # pip install requests


class MedicalVocaApp:
    # --- [ Configuration & Styling ] ---
    VERSION = "v1.2.4"
    REPO_URL = "https://api.github.com/repos/windy9478-coder/Yonsei-Medical-Quiz/releases/latest"
    DOWNLOAD_URL = "https://github.com/windy9478-coder/Yonsei-Medical-Quiz/releases"
    SECURITY_CODE = "yonseinursing"

    COLOR_PRIMARY = "#003876"  # 연세 블루
    COLOR_POINT = "#FFD700"  # 골드
    COLOR_BTN = "#0052A4"
    COLOR_TEXT = "#FFFFFF"
    COLOR_SUBTEXT = "#AAAAAA"
    COLOR_CORRECT = "#00FF7F"
    COLOR_WRONG = "#FF6347"

    def resource_path(self, relative_path):
        """ 실행 파일 내 임시 폴더에서 리소스 경로를 찾는 함수 """
        import sys
        try:
            # PyInstaller에 의해 생성된 임시 폴더 경로 (_MEIPASS)
            base_path = sys._MEIPASS
        except Exception:
            # 일반 파이썬 실행 시 현재 경로
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    def __init__(self, root):
        self.root = root
        self.root.title("연세대 간호학과 의학약어 퀴즈")
        self.root.geometry("800x900")
        self.root.configure(bg=self.COLOR_PRIMARY)
        #이미지 경로 찾아서 창 아이콘 설정
        try:
            icon_path = self.resource_path("icon.ico")
            if os.path.exists(icon_path):
                # 1. 제목 표시줄용 (전통적 방식)
                self.root.iconbitmap(icon_path)

                # 2. 작업표시줄 및 전체 시스템용 (이미지 객체 활용)
                from PIL import Image, ImageTk
                icon_img = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_img)
                # default=True로 설정하면 이후 생성되는 모든 서브창(Toplevel)에도 적용됩니다!
                self.root.iconphoto(True, icon_photo)
        except Exception as e:
            print(f"아이콘 로드 실패: {e}")

        # 상태 변수 초기화
        self.all_terms = []
        self.current_quiz = []
        self.wrong_answers = []
        self.current_index = 0
        self.score = 0
        self.auth_success = False

        # 폰트 설정
        # --- [ Font Handling (Multi-OS) ] ---
        import platform

        system_os = platform.system()
        if system_os == "Darwin":  # macOS 일 때
            main_font = "Apple SD Gothic Neo"
            title_font = "Apple SD Gothic Neo"
        else:  # Windows 또는 기타
            main_font = "Malgun Gothic"
            title_font = "Malgun Gothic"

        # 폰트 변수 적용
        self.font_title = (title_font, 24, "bold")
        self.font_main = (main_font, 15, "bold")
        self.font_desc = (main_font, 12)
        self.font_voca = ("Arial", 36, "bold")  # 약어는 Arial이 깔끔합니다.

        # 메인 컨테이너
        self.main_container = tk.Frame(self.root, bg=self.COLOR_PRIMARY)
        self.main_container.pack(fill="both", expand=True)

        # 초기 구동 프로세스
        self.run_pre_checks()

    # --- [ Pre-checks: Update & Security ] ---

    def run_pre_checks(self):
        """프로그램 시작 전 업데이트와 보안을 확인합니다."""
        self.check_for_updates()
        if self.check_security_code():
            self.show_welcome_screen()
        else:
            self.root.destroy()

    def check_for_updates(self):
        """GitHub API를 통해 최신 버전을 확인합니다."""
        try:
            response = requests.get(self.REPO_URL, timeout=3)
            if response.status_code == 200:
                latest_version = response.json().get('tag_name')
                if latest_version and latest_version != self.VERSION:
                    if messagebox.askyesno("업데이트 알림",
                                           f"새 버전({latest_version})이 출시되었습니다.\n다운로드 페이지로 이동할까요?"):
                        webbrowser.open(self.DOWNLOAD_URL)
                        self.root.destroy()
        except Exception as e:
            print(f"Update check failed: {e}")

    def check_security_code(self):
        """보안 인증 창을 실행합니다."""
        auth_win = tk.Toplevel(self.root)
        auth_win.title("Security Check")
        auth_win.geometry("450x350")
        auth_win.configure(bg=self.COLOR_PRIMARY)
        auth_win.resizable(False, False)
        auth_win.transient(self.root)
        auth_win.grab_set()
        try:
            icon_path = self.resource_path("icon.ico")
            if os.path.exists(icon_path):
                auth_win.iconbitmap(icon_path)
        except:
            pass
        # 보안 UI 구성
        self._build_auth_ui(auth_win)

        self.root.wait_window(auth_win)
        return self.auth_success

    def _build_auth_ui(self, win):
        """보안창 내부 UI 구성 (중복 버튼 제거 및 흰색 로고 적용)"""
        try:
            # 1. 로고를 선명한 흰색으로 처리 (누끼 + 화이트)
            img = Image.open("기본형_심볼-03.jpg").convert("RGBA")
            grayscale = img.convert("L")

            # 배경은 투명하게, 로고 부분만 추출하는 마스크
            mask = grayscale.point(lambda x: 0 if x > 235 else 255)

            # 순수한 흰색 배경 생성 후 마스크 입히기 (빨간색 방지)
            white_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
            white_img.putalpha(mask)

            white_img.thumbnail((150, 100))
            self.auth_logo = ImageTk.PhotoImage(white_img)
            tk.Label(win, image=self.auth_logo, bg=self.COLOR_PRIMARY).pack(pady=(30, 10))
        except:
            tk.Label(win, text="🛡️", font=("Arial", 40), bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT).pack(pady=(30, 10))

        tk.Label(win, text="Enter Password", font=("Arial", 12, "bold"),
                 bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT).pack()

        # 패스워드 입력창
        entry_pw = tk.Entry(win, font=("Arial", 16), show="●", width=20, justify="center", bd=0)
        entry_pw.pack(pady=20, ipady=5)
        entry_pw.focus()

        def validate():
            if entry_pw.get() == self.SECURITY_CODE:
                self.auth_success = True
                win.destroy()
            else:
                messagebox.showerror("Access Denied", "보안코드가 일치하지 않습니다.")
                entry_pw.delete(0, tk.END)

        # --- [ 버튼은 여기서 딱 한 번만 생성합니다 ] ---
        btn_verify = tk.Button(win, text="VERIFY ACCESS", command=validate,
                               font=("Arial", 10, "bold"), bg=self.COLOR_BTN, fg="white",
                               padx=20, pady=5, relief="flat", cursor="hand2")
        btn_verify.pack(pady=10)

        win.bind('<Return>', lambda e: validate())

    # --- [ UI Navigation Methods ] ---

    def clear_screen(self):
        """컨테이너의 모든 위젯을 제거합니다."""
        for widget in self.main_container.winfo_children():
            widget.destroy()

    def add_bottom_logo(self, parent):
        """하단 로고를 추가합니다."""
        try:
            img = Image.open("기본형_심볼-03.jpg").convert("RGBA")
            grayscale = img.convert("L")
            mask = grayscale.point(lambda x: 0 if x > 235 else 255)
            white_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
            white_img.putalpha(mask)
            white_img.thumbnail((400, 180))  # 또는 다른 원하는 크기
            self.logo_img = ImageTk.PhotoImage(white_img)
            logo_label = tk.Label(parent, image=self.logo_img, bg=self.COLOR_PRIMARY)
            logo_label.pack(side="bottom", pady=30)
        except Exception as e:
            print(f"Error loading logo: {e}")
            pass

    def show_welcome_screen(self):
        """1단계: 시작 화면"""
        self.clear_screen()

        tk.Label(self.main_container, text="🩺 의학용어 암기 마스터", font=self.font_title,
                 bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT).pack(pady=(60, 20))

        welcome_text = ("안녕하세요! 연세대학교 간호학과 학우 여러분.\n"
                        "의학용어 및 약어 암기를 돕기 위해 제작된 프로그램입니다.")
        tk.Label(self.main_container, text=welcome_text, font=self.font_desc,
                 bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT).pack(pady=10)

        dev_info = "개발자: 22학번 정인호 | windy9478@gmail.com"
        tk.Label(self.main_container, text=dev_info, font=self.font_desc,
                 bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT).pack(pady=10)

        tk.Button(self.main_container, text="START 🚀", command=self.show_setup_screen,
                  font=("Malgun Gothic", 16, "bold"), bg=self.COLOR_BTN, fg=self.COLOR_TEXT,
                  padx=50, pady=10).pack(pady=30)

        tk.Button(self.main_container, text="ℹ️ 프로그램 정보", command=self.show_about_info,
                  font=("Malgun Gothic", 10), bg=self.COLOR_PRIMARY, fg=self.COLOR_SUBTEXT,
                  relief="flat", cursor="hand2").pack()

        self.add_bottom_logo(self.main_container)

    def show_setup_screen(self):
        """2단계: 파일 로드 및 설정 화면"""
        self.clear_screen()

        tk.Label(self.main_container, text="📂 퀴즈 파일 등록 및 설정", font=self.font_title,
                 bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT).pack(pady=30)

        # 가이드 박스
        guide_frame = tk.LabelFrame(self.main_container, text="[ CSV 파일 등록 방법 ]",
                                    font=self.font_main, bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT, padx=20, pady=15)
        guide_frame.pack(pady=10, padx=40, fill="x")

        guide_text = ("1. 엑셀: [A:약어 / B:Full Term / C:한글뜻] 입력\n"
                      "2. 저장: 'CSV UTF-8 (쉼표로 분리)' 형식 권장\n"
                      "3. 아래 버튼을 클릭하여 파일 선택")
        tk.Label(guide_frame, text=guide_text, font=self.font_desc, bg=self.COLOR_PRIMARY,
                 fg=self.COLOR_TEXT, justify="left").pack()

        self.btn_csv = tk.Button(self.main_container, text="1. 의학용어 CSV 파일 선택하기", command=self.load_data,
                                 font=self.font_main, bg="#E1E1E1", fg="black", padx=20)
        self.btn_csv.pack(pady=(30, 5))

        self.file_label = tk.Label(self.main_container, text="아직 선택된 파일이 없습니다.",
                                   font=self.font_desc, bg=self.COLOR_PRIMARY, fg=self.COLOR_SUBTEXT)
        self.file_label.pack(pady=5)

        tk.Label(self.main_container, text="2. 이번 세트 문제 수:",
                 font=self.font_main, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT).pack(pady=(20, 10))

        self.entry_count = tk.Entry(self.main_container, font=self.font_main, width=10, justify="center")
        self.entry_count.insert(0, "20")
        self.entry_count.pack()

        tk.Button(self.main_container, text="퀴즈 시작하기!", command=self.prepare_quiz,
                  font=self.font_main, bg=self.COLOR_BTN, fg=self.COLOR_TEXT, padx=40, pady=10).pack(pady=40)

        self.add_bottom_logo(self.main_container)

    def show_quiz_screen(self):
        """3단계: 실제 퀴즈 진행 화면"""
        self.clear_screen()
        self.current_index = 0
        self.score = 0
        self.wrong_answers = []

        self.progress_label = tk.Label(self.main_container, text="", font=self.font_main,
                                       bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT)
        self.progress_label.pack(pady=20)

        self.abbr_label = tk.Label(self.main_container, text="", font=self.font_voca,
                                   bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT)
        self.abbr_label.pack(pady=30)

        # 입력 필드 프레임
        input_frame = tk.Frame(self.main_container, bg=self.COLOR_PRIMARY)
        input_frame.pack(pady=20)

        # Full Term 입력
        tk.Label(input_frame, text="Full Term:", font=self.font_main, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT).grid(
            row=0, column=0, sticky="e", pady=10)
        self.entry_full = tk.Entry(input_frame, font=self.font_main, width=35)
        self.entry_full.grid(row=0, column=1, padx=15)
        self.entry_full.bind('<Return>', lambda e: self.entry_mean.focus())

        # 한글 뜻 입력
        tk.Label(input_frame, text="한글 뜻:", font=self.font_main, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT).grid(row=1,
                                                                                                                 column=0,
                                                                                                                 sticky="e",
                                                                                                                 pady=10)
        self.entry_mean = tk.Entry(input_frame, font=self.font_main, width=35)
        self.entry_mean.grid(row=1, column=1, padx=15)
        self.entry_mean.bind('<Return>', lambda e: self.check_answer())

        self.btn_submit = tk.Button(self.main_container, text="정답 제출 (Enter)", command=self.check_answer,
                                    bg=self.COLOR_BTN, fg=self.COLOR_TEXT, font=self.font_main, padx=30, pady=5)
        self.btn_submit.pack(pady=20)

        tk.Button(self.main_container, text="중도 종료 및 채점", command=self.finish_early,
                  bg="#555555", fg="white", font=self.font_desc).pack()

        self.result_label = tk.Label(self.main_container, text="", font=self.font_main, bg=self.COLOR_PRIMARY)
        self.result_label.pack(pady=10)

        self.show_next_question()

    def show_summary_screen(self, early=False):
        """4단계: 결과 요약 화면"""
        self.clear_screen()
        total = self.current_index if early else len(self.current_quiz)

        tk.Label(self.main_container, text="📊 테스트 요약", font=self.font_title,
                 bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT).pack(pady=20)

        tk.Label(self.main_container, text=f"맞힌 개수: {self.score} / {total}",
                 font=self.font_main, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT).pack()

        if self.wrong_answers:
            tk.Label(self.main_container, text="[ 오답 리스트 ]", font=self.font_main,
                     bg=self.COLOR_PRIMARY, fg=self.COLOR_WRONG).pack(pady=(20, 5))

            txt = scrolledtext.ScrolledText(self.main_container, width=70, height=12, font=self.font_desc)
            txt.pack(pady=10)
            for abbr, full, mean in self.wrong_answers:
                txt.insert(tk.END, f"• {abbr}: {full} ({mean})\n")
            txt.config(state="disabled")

            tk.Button(self.main_container, text="틀린 문제만 다시 풀기 🔄", command=self.retry_wrong,
                      font=self.font_main, bg="#FF4500", fg="white", padx=20).pack(pady=5)
        else:
            tk.Label(self.main_container, text="🎉 완벽합니다! 모든 문제를 맞혔어요!",
                     font=self.font_main, bg=self.COLOR_PRIMARY, fg=self.COLOR_CORRECT).pack(pady=50)

        btn_frame = tk.Frame(self.main_container, bg=self.COLOR_PRIMARY)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="새로운 문제 세트", command=self.show_setup_screen,
                  font=self.font_main, bg=self.COLOR_BTN, fg="white", padx=10).grid(row=0, column=0, padx=10)

        tk.Button(btn_frame, text="처음으로", command=self.show_welcome_screen,
                  font=self.font_main, bg="#696969", fg="white", padx=10).grid(row=0, column=1, padx=10)

    # --- [ Logic Methods ] ---

    def load_data(self):
        """CSV 파일을 로드하여 메모리에 저장합니다."""
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
                    self.file_label.config(text=f"✅ 선택됨: {os.path.basename(file_path)}", fg=self.COLOR_POINT)
                    return
            except:
                continue
        messagebox.showerror("오류", "파일을 읽을 수 없습니다. 인코딩 형식을 확인해 주세요.")

    def prepare_quiz(self):
        """설정된 문제 수만큼 랜덤하게 퀴즈를 추출합니다."""
        if not self.all_terms:
            messagebox.showwarning("경고", "먼저 CSV 파일을 등록해주세요!")
            return
        try:
            count = int(self.entry_count.get())
            count = min(count, len(self.all_terms))
            self.current_quiz = random.sample(self.all_terms, count)
            self.show_quiz_screen()
        except ValueError:
            messagebox.showerror("오류", "문제 수는 숫자로 입력해주세요!")

    def show_next_question(self):
        """다음 문제를 표시하거나 요약 화면으로 넘어갑니다."""
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
        """입력된 정답을 확인하고 처리합니다."""
        if self.current_index >= len(self.current_quiz): return

        u_full = self.entry_full.get().strip().lower()
        u_mean = self.entry_mean.get().strip()
        abbr, c_full, c_mean = self.current_quiz[self.current_index]

        if u_full == c_full.lower() and u_mean == c_mean:
            self.score += 1
            self.result_label.config(text="정답입니다! ✅", fg=self.COLOR_CORRECT)
        else:
            self.result_label.config(text=f"오답! 정답: {c_full} / {c_mean}", fg=self.COLOR_WRONG)
            self.wrong_answers.append([abbr, c_full, c_mean])

        self.current_index += 1
        self.root.after(1000, self.show_next_question)

    def retry_wrong(self):
        """오답들만 모아서 다시 퀴즈를 시작합니다."""
        self.current_quiz = self.wrong_answers[:]
        random.shuffle(self.current_quiz)
        self.show_quiz_screen()

    def finish_early(self):
        """중도 종료 시 현재까지의 점수를 계산합니다."""
        if messagebox.askyesno("중도 종료", "지금까지 푼 문제만 채점할까요?"):
            self.show_summary_screen(early=True)

    def show_about_info(self):
        """프로그램 정보를 보여주는 팝업창"""
        about_win = tk.Toplevel(self.root)
        about_win.title("Information")
        about_win.geometry("400x450")
        about_win.configure(bg=self.COLOR_PRIMARY)
        about_win.transient(self.root)

        tk.Label(about_win, text="🩺", font=("Arial", 50), bg=self.COLOR_PRIMARY).pack(pady=(30, 10))
        tk.Label(about_win, text="연세 간호 의학용어 마스터", font=self.font_main, bg=self.COLOR_PRIMARY,
                 fg=self.COLOR_POINT).pack()
        tk.Label(about_win, text=f"Version {self.VERSION}", font=("Arial", 10), bg=self.COLOR_PRIMARY,
                 fg=self.COLOR_SUBTEXT).pack(pady=(0, 20))

        info = ("━━━━━━━━━━━━━━━━━━━━\n\n"
                "👨‍💻 Developer: 22학번 정인호\n"
                "📧 Contact: windy9478@gmail.com\n"
                "🏛️ Yonsei Univ. Nursing\n\n"
                "© 2026 Inho Jung. All rights reserved.")

        tk.Label(about_win, text=info, font=self.font_desc, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT).pack()
        tk.Button(about_win, text="닫기", command=about_win.destroy, bg=self.COLOR_BTN, fg="white", padx=30).pack(pady=20)


if __name__ == "__main__":
    import ctypes
    import platform

    # 윈도우 환경에서만 실행되도록 설정
    if platform.system() == "Windows":
        try:
            # 내 프로그램만의 고유 ID를 부여 (회사명.제품명.버전 등 자유롭게)
            myappid = 'yonsei.nursing.medicalvoca.1.2.4'
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            print(f"작업표시줄 설정 실패: {e}")

    root = tk.Tk()
    app = MedicalVocaApp(root)
    root.mainloop()
