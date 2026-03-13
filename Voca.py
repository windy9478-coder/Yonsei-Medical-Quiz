# ==========================================================
# Copyright (c) 2026 Inho Jung (windy9478-coder). All rights reserved.
# 본 프로그램의 저작권은 22학번 정인호에게 있습니다.
# 무단 복제, 수정 및 재배포를 금지하며, 적발 시 법적 책임을 물을 수 있습니다.
# ==========================================================

import csv
import os
import sys
import random
import webbrowser
import platform
import ctypes
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

    def __init__(self, root):
        self.root = root
        self.root.title("연세대 간호학과 의학약어 퀴즈")
        self.root.geometry("800x900")
        self.root.configure(bg=self.COLOR_PRIMARY)

        # 1. 시스템 리소스 및 아이콘 설정
        self._setup_fonts()
        self._set_window_icon(self.root)

        # 2. 상태 변수 초기화
        self.all_terms = []
        self.current_quiz = []
        self.wrong_answers = []
        self.current_index = 0
        self.score = 0
        self.auth_success = False

        # 3. 메인 컨테이너 설정
        self.main_container = tk.Frame(self.root, bg=self.COLOR_PRIMARY)
        self.main_container.pack(fill="both", expand=True)

        # 4. 초기 구동 (업데이트 & 보안)
        self.run_pre_checks()

    # --- [ Utility Methods ] ---

    def resource_path(self, relative_path):
        """ PyInstaller 빌드 후에도 리소스를 찾을 수 있게 경로를 변환 (파이참 경고 해결) """
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def _setup_fonts(self):
        """ OS 환경에 따른 폰트 최적화 설정 """
        sys_os = platform.system()
        m_font = "Apple SD Gothic Neo" if sys_os == "Darwin" else "Malgun Gothic"

        self.font_title = (m_font, 24, "bold")
        self.font_main = (m_font, 15, "bold")
        self.font_desc = (m_font, 12)
        self.font_voca = ("Arial", 36, "bold")

    def _set_window_icon(self, window):
        """ 메인 및 서브 창의 아이콘을 일괄 설정 (작업표시줄 포함) """
        try:
            icon_path = self.resource_path("icon.ico")
            if os.path.exists(icon_path):
                # 윈도우 타이틀바
                window.iconbitmap(icon_path)
                # 작업표시줄 및 범용 아이콘 (참조 유지를 위해 self에 저장)
                icon_img = Image.open(icon_path)
                self.tk_icon = ImageTk.PhotoImage(icon_img)
                window.iconphoto(True, self.tk_icon)
        except Exception as e:
            print(f"Icon load error: {e}")

    def _process_white_logo(self, size):
        """ 원본 로고를 흰색 누끼 이미지로 변환하는 통합 함수 """
        try:
            img_path = self.resource_path("기본형_심볼-03.jpg")
            img = Image.open(img_path).convert("RGBA")
            grayscale = img.convert("L")
            mask = grayscale.point(lambda x: 0 if x > 235 else 255)

            white_img = Image.new("RGBA", img.size, (255, 255, 255, 255))
            white_img.putalpha(mask)
            white_img.thumbnail(size)
            return ImageTk.PhotoImage(white_img)
        except:
            return None

    # --- [ Pre-checks & Auth ] ---

    def run_pre_checks(self):
        self._check_for_updates()
        if self._show_security_dialog():
            self.show_welcome_screen()
        else:
            self.root.destroy()

    def _check_for_updates(self):
        try:
            res = requests.get(self.REPO_URL, timeout=3)
            if res.status_code == 200:
                latest = res.json().get('tag_name')
                if latest and latest != self.VERSION:
                    if messagebox.askyesno("업데이트", f"새 버전({latest})이 있습니다. 이동할까요?"):
                        webbrowser.open(self.DOWNLOAD_URL)
                        self.root.destroy()
        except:
            pass

    def _show_security_dialog(self):
        auth_win = tk.Toplevel(self.root)
        auth_win.title("Security Check")
        auth_win.geometry("450x350")
        auth_win.configure(bg=self.COLOR_PRIMARY)
        auth_win.resizable(False, False)
        auth_win.transient(self.root)
        auth_win.grab_set()
        self._set_window_icon(auth_win)

        # 로고 표시
        logo = self._process_white_logo((150, 100))
        if logo:
            self.auth_logo_img = logo  # 참조 유지
            tk.Label(auth_win, image=self.auth_logo_img, bg=self.COLOR_PRIMARY).pack(pady=(30, 10))
        else:
            tk.Label(auth_win, text="🛡️", font=("Arial", 40), bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT).pack(
                pady=(30, 10))

        tk.Label(auth_win, text="Enter Password", font=("Arial", 12, "bold"), bg=self.COLOR_PRIMARY,
                 fg=self.COLOR_POINT).pack()

        pw_entry = tk.Entry(auth_win, font=("Arial", 16), show="●", width=20, justify="center", bd=0)
        pw_entry.pack(pady=20, ipady=5)
        pw_entry.focus()

        def validate():
            if pw_entry.get() == self.SECURITY_CODE:
                self.auth_success = True
                auth_win.destroy()
            else:
                messagebox.showerror("Access Denied", "보안코드가 일치하지 않습니다.")
                pw_entry.delete(0, tk.END)

        tk.Button(auth_win, text="VERIFY ACCESS", command=validate, font=("Arial", 10, "bold"),
                  bg=self.COLOR_BTN, fg="white", padx=20, pady=5, relief="flat", cursor="hand2").pack(pady=10)
        auth_win.bind('<Return>', lambda e: validate())
        self.root.wait_window(auth_win)
        return self.auth_success

    # --- [ UI Screens ] ---

    def clear_screen(self):
        for widget in self.main_container.winfo_children(): widget.destroy()

    def add_bottom_logo(self, parent):
        logo = self._process_white_logo((400, 180))
        if logo:
            self.footer_logo_img = logo  # 참조 유지
            tk.Label(parent, image=self.footer_logo_img, bg=self.COLOR_PRIMARY).pack(side="bottom", pady=30)

    def show_welcome_screen(self):
        self.clear_screen()
        tk.Label(self.main_container, text="🩺 의학용어 암기 마스터", font=self.font_title, bg=self.COLOR_PRIMARY,
                 fg=self.COLOR_POINT).pack(pady=(60, 20))
        tk.Label(self.main_container, text="안녕하세요! 연세대학교 간호학과 학우 여러분.\n의학용어 암기를 돕기 위한 프로그램입니다.",
                 font=self.font_desc, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT).pack(pady=10)
        tk.Label(self.main_container, text="개발자: 22학번 정인호 | windy9478@gmail.com", font=self.font_desc,
                 bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT).pack(pady=10)

        tk.Button(self.main_container, text="START 🚀", command=self.show_setup_screen,
                  font=("Malgun Gothic", 16, "bold"),
                  bg=self.COLOR_BTN, fg=self.COLOR_TEXT, padx=50, pady=10).pack(pady=30)

        tk.Button(self.main_container, text="ℹ️ 프로그램 정보", command=self.show_about_info, font=self.font_desc,
                  bg=self.COLOR_PRIMARY, fg=self.COLOR_SUBTEXT, relief="flat", cursor="hand2").pack()
        self.add_bottom_logo(self.main_container)

    def show_setup_screen(self):
        self.clear_screen()
        tk.Label(self.main_container, text="📂 퀴즈 파일 등록 및 설정", font=self.font_title, bg=self.COLOR_PRIMARY,
                 fg=self.COLOR_POINT).pack(pady=30)

        guide_frame = tk.LabelFrame(self.main_container, text="[ CSV 파일 등록 방법 ]", font=self.font_main,
                                    bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT, padx=20, pady=15)
        guide_frame.pack(pady=10, padx=40, fill="x")
        tk.Label(guide_frame, text="1. 엑셀: [A:약어 / B:Full Term / C:한글뜻]\n2. 저장: 'CSV UTF-8 (쉼표로 분리)'\n3. 파일 선택 버튼 클릭",
                 font=self.font_desc, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT, justify="left").pack()

        self.btn_csv = tk.Button(self.main_container, text="1. 의학용어 CSV 파일 선택", command=self.load_data,
                                 font=self.font_main, bg="#E1E1E1", padx=20)
        self.btn_csv.pack(pady=(30, 5))
        self.file_label = tk.Label(self.main_container, text="선택된 파일 없음", font=self.font_desc, bg=self.COLOR_PRIMARY,
                                   fg=self.COLOR_SUBTEXT)
        self.file_label.pack(pady=5)

        tk.Label(self.main_container, text="2. 문제 수 설정:", font=self.font_main, bg=self.COLOR_PRIMARY,
                 fg=self.COLOR_TEXT).pack(pady=(20, 10))
        self.cnt_entry = tk.Entry(self.main_container, font=self.font_main, width=10, justify="center")
        self.cnt_entry.insert(0, "20")
        self.cnt_entry.pack()

        tk.Button(self.main_container, text="퀴즈 시작하기!", command=self.prepare_quiz, font=self.font_main,
                  bg=self.COLOR_BTN, fg=self.COLOR_TEXT, padx=40, pady=10).pack(pady=40)
        self.add_bottom_logo(self.main_container)

    def show_quiz_screen(self):
        self.clear_screen()
        self.current_index = 0;
        self.score = 0;
        self.wrong_answers = []

        self.prog_lbl = tk.Label(self.main_container, font=self.font_main, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT)
        self.prog_lbl.pack(pady=20)
        self.abbr_lbl = tk.Label(self.main_container, font=self.font_voca, bg=self.COLOR_PRIMARY, fg=self.COLOR_POINT)
        self.abbr_lbl.pack(pady=30)

        f_node = tk.Frame(self.main_container, bg=self.COLOR_PRIMARY)
        f_node.pack(pady=20)

        tk.Label(f_node, text="Full Term:", font=self.font_main, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT).grid(row=0,
                                                                                                                 column=0,
                                                                                                                 pady=10)
        self.ent_f = tk.Entry(f_node, font=self.font_main, width=30);
        self.ent_f.grid(row=0, column=1, padx=10)
        self.ent_f.bind('<Return>', lambda e: self.ent_m.focus())

        tk.Label(f_node, text="한글 뜻:", font=self.font_main, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT).grid(row=1,
                                                                                                            column=0,
                                                                                                            pady=10)
        self.ent_m = tk.Entry(f_node, font=self.font_main, width=30);
        self.ent_m.grid(row=1, column=1, padx=10)
        self.ent_m.bind('<Return>', lambda e: self.check_answer())

        tk.Button(self.main_container, text="정답 제출 (Enter)", command=self.check_answer, bg=self.COLOR_BTN,
                  fg=self.COLOR_TEXT, font=self.font_main, padx=30).pack(pady=20)
        tk.Button(self.main_container, text="중도 종료", command=self.finish_early, bg="#555555", fg="white",
                  font=self.font_desc).pack()
        self.res_lbl = tk.Label(self.main_container, font=self.font_main, bg=self.COLOR_PRIMARY);
        self.res_lbl.pack(pady=10)
        self.show_next_question()

    def show_summary_screen(self, early=False):
        self.clear_screen()
        total = self.current_index if early else len(self.current_quiz)
        tk.Label(self.main_container, text="📊 테스트 요약", font=self.font_title, bg=self.COLOR_PRIMARY,
                 fg=self.COLOR_POINT).pack(pady=20)
        tk.Label(self.main_container, text=f"맞힌 개수: {self.score} / {total}", font=self.font_main, bg=self.COLOR_PRIMARY,
                 fg=self.COLOR_TEXT).pack()

        if self.wrong_answers:
            tk.Label(self.main_container, text="[ 오답 리스트 ]", font=self.font_main, bg=self.COLOR_PRIMARY,
                     fg=self.COLOR_WRONG).pack(pady=(20, 5))
            txt = scrolledtext.ScrolledText(self.main_container, width=70, height=12, font=self.font_desc)
            txt.pack(pady=10)
            for a, f, m in self.wrong_answers: txt.insert(tk.END, f"• {a}: {f} ({m})\n")
            txt.config(state="disabled")
            tk.Button(self.main_container, text="틀린 문제 다시 풀기 🔄", command=self.retry_wrong, bg="#FF4500", fg="white",
                      font=self.font_main).pack(pady=5)
        else:
            tk.Label(self.main_container, text="🎉 완벽합니다!", font=self.font_main, bg=self.COLOR_PRIMARY,
                     fg=self.COLOR_CORRECT).pack(pady=50)

        f_btn = tk.Frame(self.main_container, bg=self.COLOR_PRIMARY);
        f_btn.pack(pady=20)
        tk.Button(f_btn, text="새 퀴즈", command=self.show_setup_screen, bg=self.COLOR_BTN, fg="white",
                  font=self.font_main).grid(row=0, column=0, padx=10)
        tk.Button(f_btn, text="처음으로", command=self.show_welcome_screen, bg="#696969", fg="white",
                  font=self.font_main).grid(row=0, column=1, padx=10)

    # --- [ Logic ] ---

    def load_data(self):
        f_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not f_path: return
        self.all_terms = []
        for enc in ['utf-8-sig', 'cp949', 'euc-kr', 'utf-8']:
            try:
                with open(f_path, 'r', encoding=enc, errors='replace') as f:
                    self.all_terms = [[c.strip() for c in r] for r in csv.reader(f) if r and len(r) >= 3]
                if self.all_terms:
                    self.file_label.config(text=f"✅ {os.path.basename(f_path)}", fg=self.COLOR_POINT)
                    return
            except:
                continue
        messagebox.showerror("오류", "파일 로드 실패")

    def prepare_quiz(self):
        if not self.all_terms: return messagebox.showwarning("경고", "CSV 파일을 먼저 등록하세요.")
        try:
            num = min(int(self.cnt_entry.get()), len(self.all_terms))
            self.current_quiz = random.sample(self.all_terms, num)
            self.show_quiz_screen()
        except:
            messagebox.showerror("오류", "숫자를 입력하세요.")

    def show_next_question(self):
        self.ent_f.delete(0, tk.END);
        self.ent_m.delete(0, tk.END);
        self.res_lbl.config(text="")
        self.ent_f.focus()
        if self.current_index < len(self.current_quiz):
            a, _, _ = self.current_quiz[self.current_index]
            self.prog_lbl.config(text=f"Q {self.current_index + 1} / {len(self.current_quiz)}")
            self.abbr_lbl.config(text=a)
        else:
            self.show_summary_screen()

    def check_answer(self):
        if self.current_index >= len(self.current_quiz): return
        u_f, u_m = self.ent_f.get().strip().lower(), self.ent_m.get().strip()
        a, c_f, c_m = self.current_quiz[self.current_index]
        if u_f == c_f.lower() and u_m == c_m:
            self.score += 1;
            self.res_lbl.config(text="정답! ✅", fg=self.COLOR_CORRECT)
        else:
            self.res_lbl.config(text=f"오답! 정답: {c_f} / {c_m}", fg=self.COLOR_WRONG)
            self.wrong_answers.append([a, c_f, c_m])
        self.current_index += 1
        self.root.after(1000, self.show_next_question)

    def retry_wrong(self):
        self.current_quiz = self.wrong_answers[:]
        random.shuffle(self.current_quiz)
        self.show_quiz_screen()

    def finish_early(self):
        if messagebox.askyesno("중도 종료", "채점할까요?"): self.show_summary_screen(early=True)

    def show_about_info(self):
        win = tk.Toplevel(self.root)
        win.title("About")
        win.geometry("400x450")
        win.configure(bg=self.COLOR_PRIMARY);
        self._set_window_icon(win)
        tk.Label(win, text="🩺", font=("Arial", 50), bg=self.COLOR_PRIMARY).pack(pady=20)
        info = f"연세 간호 의학용어 마스터\nVersion {self.VERSION}\n\nDeveloper: 22학번 정인호\nwindy9478@gmail.com\n\n© 2026 Inho Jung."
        tk.Label(win, text=info, font=self.font_desc, bg=self.COLOR_PRIMARY, fg=self.COLOR_TEXT).pack()
        tk.Button(win, text="닫기", command=win.destroy, bg=self.COLOR_BTN, fg="white", padx=20).pack(pady=20)


if __name__ == "__main__":
    if platform.system() == "Windows":
        try:
            # 작업표시줄 아이콘 고정 (파이참 경고 회피용 getattr 사용)
            shell32 = getattr(ctypes.windll, 'shell32')
            shell32.SetCurrentProcessExplicitAppUserModelID('yonsei.nursing.quiz.1.2.4')
        except:
            pass
    root = tk.Tk()
    app = MedicalVocaApp(root)
    root.mainloop()
