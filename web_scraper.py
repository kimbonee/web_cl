#!/usr/bin/env python3
"""
웹페이지 스크래핑 프로그램
URL을 입력받아 페이지의 텍스트 정보와 이미지를 추출하여 저장합니다.
"""

import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
from datetime import datetime
import argparse
from pathlib import Path

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def create_folder(self, folder_name):
        """데스크탑에 폴더 생성"""
        desktop_path = Path.home() / "Desktop"
        folder_path = desktop_path / folder_name
        
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"폴더 생성: {folder_path}")
        
        return folder_path
    
    def download_image(self, img_url, folder_path, img_name):
        """이미지 다운로드"""
        try:
            # 절대 URL로 변환
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = urljoin(self.base_url, img_url)
            
            response = self.session.get(img_url, timeout=30)
            response.raise_for_status()
            
            # 파일 확장자 추출
            parsed_url = urlparse(img_url)
            file_ext = os.path.splitext(parsed_url.path)[1]
            if not file_ext:
                file_ext = '.jpg'  # 기본 확장자
            
            # 파일명 정리
            safe_name = re.sub(r'[^\w\-_\.]', '_', img_name)
            filename = f"{safe_name}{file_ext}"
            file_path = folder_path / "images" / filename
            
            # images 폴더 생성
            (folder_path / "images").mkdir(exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"이미지 저장: {file_path}")
            return str(file_path)
            
        except Exception as e:
            print(f"이미지 다운로드 실패: {img_url} - {e}")
            return None
    
    def extract_text_with_styling(self, soup):
        """텍스트를 스타일과 함께 추출"""
        styled_text = []
        
        # 제목 추출
        title = soup.find('h1') or soup.find('h2') or soup.find('h3')
        if title:
            styled_text.append(f"# {title.get_text().strip()}\n")
        
        # 테이블 정보 추출
        tables = soup.find_all('table')
        for table in tables:
            styled_text.append("## 프로그램 정보\n")
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    styled_text.append(f"**{key}**: {value}\n")
            styled_text.append("\n")
        
        # 본문 내용 추출
        content_divs = soup.find_all(['div', 'p'], class_=re.compile(r'content|body|main'))
        for div in content_divs:
            text = div.get_text().strip()
            if text and len(text) > 10:  # 의미있는 텍스트만
                # 줄바꿈 처리
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        styled_text.append(f"{line}\n")
                styled_text.append("\n")
        
        return '\n'.join(styled_text)
    
    def scrape_page(self, url):
        """웹페이지 스크래핑"""
        try:
            print(f"페이지 로딩 중: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 페이지 제목 추출
            page_title = soup.find('title')
            if page_title:
                title = page_title.get_text().strip()
            else:
                title = "웹페이지_스크래핑"
            
            # 폴더명 생성 (특수문자 제거)
            safe_title = re.sub(r'[^\w\-_\.]', '_', title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{safe_title}_{timestamp}"
            
            # 폴더 생성
            folder_path = self.create_folder(folder_name)
            
            # 텍스트 정보 추출
            styled_text = self.extract_text_with_styling(soup)
            
            # 텍스트 파일로 저장
            text_file = folder_path / "content.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(styled_text)
            
            # 마크다운 파일로도 저장
            md_file = folder_path / "content.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(styled_text)
            
            # 이미지 추출 및 다운로드
            images = soup.find_all('img')
            image_info = []
            
            for i, img in enumerate(images):
                img_src = img.get('src')
                if img_src:
                    img_alt = img.get('alt', f'image_{i+1}')
                    img_path = self.download_image(img_src, folder_path, img_alt)
                    if img_path:
                        image_info.append({
                            'original_url': img_src,
                            'local_path': img_path,
                            'alt_text': img_alt
                        })
            
            # 메타데이터 저장
            metadata = {
                'url': url,
                'title': title,
                'scraped_at': datetime.now().isoformat(),
                'images': image_info,
                'text_file': str(text_file),
                'markdown_file': str(md_file)
            }
            
            metadata_file = folder_path / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"\n스크래핑 완료!")
            print(f"폴더 위치: {folder_path}")
            print(f"텍스트 파일: {text_file}")
            print(f"마크다운 파일: {md_file}")
            print(f"이미지 개수: {len(image_info)}")
            
            return folder_path
            
        except Exception as e:
            print(f"스크래핑 실패: {e}")
            return None

def main():
    parser = argparse.ArgumentParser(description='웹페이지 스크래핑 프로그램')
    parser.add_argument('url', help='스크래핑할 웹페이지 URL')
    
    args = parser.parse_args()
    
    scraper = WebScraper(args.url)
    result = scraper.scrape_page(args.url)
    
    if result:
        print(f"\n복사할 텍스트:")
        print("=" * 50)
        text_file = result / "content.txt"
        if text_file.exists():
            with open(text_file, 'r', encoding='utf-8') as f:
                print(f.read())

if __name__ == "__main__":
    main()
