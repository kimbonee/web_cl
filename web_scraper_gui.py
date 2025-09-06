#!/usr/bin/env python3
"""
웹페이지 스크래핑 프로그램 - GUI 버전
URL을 입력받아 페이지의 텍스트 정보와 이미지를 추출하여 저장합니다.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import os
from pathlib import Path
from web_scraper import WebScraper

class WebScraperGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("웹페이지 스크래핑 프로그램")
        self.root.geometry("800x600")
        
        # 메인 프레임
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # URL 입력
        ttk.Label(main_frame, text="웹페이지 URL:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=80)
        url_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 버튼들
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(0, 10))
        
        self.scrape_button = ttk.Button(button_frame, text="스크래핑 시작", command=self.start_scraping)
        self.scrape_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.open_folder_button = ttk.Button(button_frame, text="결과 폴더 열기", command=self.open_result_folder)
        self.open_folder_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="화면 지우기", command=self.clear_output)
        self.clear_button.pack(side=tk.LEFT)
        
        # 진행률 표시
        self.progress_var = tk.StringVar(value="대기 중...")
        ttk.Label(main_frame, textvariable=self.progress_var).grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 결과 출력
        ttk.Label(main_frame, text="결과:").grid(row=5, column=0, sticky=tk.W, pady=(0, 5))
        
        self.output_text = scrolledtext.ScrolledText(main_frame, height=20, width=80)
        self.output_text.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # 그리드 가중치 설정
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.result_folder = None
        
    def start_scraping(self):
        """스크래핑 시작"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("오류", "URL을 입력해주세요.")
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # UI 비활성화
        self.scrape_button.config(state='disabled')
        self.progress_bar.start()
        self.progress_var.set("스크래핑 중...")
        
        # 별도 스레드에서 스크래핑 실행
        thread = threading.Thread(target=self.scrape_worker, args=(url,))
        thread.daemon = True
        thread.start()
    
    def scrape_worker(self, url):
        """스크래핑 작업자 스레드"""
        try:
            scraper = WebScraper(url)
            result = scraper.scrape_page(url)
            
            if result:
                self.result_folder = result
                self.root.after(0, self.scraping_success, result)
            else:
                self.root.after(0, self.scraping_error, "스크래핑에 실패했습니다.")
                
        except Exception as e:
            self.root.after(0, self.scraping_error, f"오류 발생: {str(e)}")
    
    def scraping_success(self, folder_path):
        """스크래핑 성공 처리"""
        self.progress_bar.stop()
        self.progress_var.set("스크래핑 완료!")
        self.scrape_button.config(state='normal')
        
        # 결과 출력
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"스크래핑 완료!\n")
        self.output_text.insert(tk.END, f"폴더 위치: {folder_path}\n\n")
        
        # 텍스트 파일 내용 읽어서 표시
        text_file = folder_path / "content.txt"
        if text_file.exists():
            with open(text_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.output_text.insert(tk.END, "추출된 내용:\n")
                self.output_text.insert(tk.END, "=" * 50 + "\n")
                self.output_text.insert(tk.END, content)
        
        messagebox.showinfo("완료", f"스크래핑이 완료되었습니다!\n폴더: {folder_path}")
    
    def scraping_error(self, error_msg):
        """스크래핑 오류 처리"""
        self.progress_bar.stop()
        self.progress_var.set("오류 발생")
        self.scrape_button.config(state='normal')
        
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"오류: {error_msg}\n")
        
        messagebox.showerror("오류", error_msg)
    
    def open_result_folder(self):
        """결과 폴더 열기"""
        if self.result_folder and self.result_folder.exists():
            os.system(f'open "{self.result_folder}"')
        else:
            messagebox.showwarning("경고", "결과 폴더가 없습니다. 먼저 스크래핑을 실행해주세요.")
    
    def clear_output(self):
        """출력 화면 지우기"""
        self.output_text.delete(1.0, tk.END)
        self.progress_var.set("대기 중...")

def main():
    root = tk.Tk()
    app = WebScraperGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
