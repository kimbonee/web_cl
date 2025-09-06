#!/usr/bin/env python3
"""
웹 기반 웹페이지 스크래핑 애플리케이션
Flask를 사용하여 웹 브라우저에서 사용할 수 있는 GUI 제공
"""

from flask import Flask, render_template, request, jsonify, send_file
import os
import re
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import json
from datetime import datetime
from pathlib import Path
import threading
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

app = Flask(__name__)

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        
        # 재시도 전략 설정
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        # 타임아웃 설정 조정 (더 짧게)
        self.timeout = (3, 10)  # (연결 타임아웃, 읽기 타임아웃)
        
    def create_folder(self, folder_name):
        """데스크탑에 폴더 생성"""
        desktop_path = Path.home() / "Desktop"
        folder_path = desktop_path / folder_name
        
        if not folder_path.exists():
            folder_path.mkdir(parents=True, exist_ok=True)
        
        return folder_path
    
    def download_image(self, img_url, folder_path, img_name):
        """이미지 다운로드"""
        try:
            # 절대 URL로 변환
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = urljoin(self.base_url, img_url)
            
            response = self.session.get(img_url, timeout=self.timeout)
            response.raise_for_status()
            
            # 파일 확장자 추출
            parsed_url = urlparse(img_url)
            file_ext = os.path.splitext(parsed_url.path)[1]
            if not file_ext:
                file_ext = '.jpg'
            
            # 파일명 정리
            safe_name = re.sub(r'[^\w\-_\.]', '_', img_name)
            filename = f"{safe_name}{file_ext}"
            file_path = folder_path / "images" / filename
            
            # images 폴더 생성
            (folder_path / "images").mkdir(exist_ok=True)
            
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
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
            styled_text.append(f"# {title.get_text().strip()}")
        
        # 테이블 정보 추출
        tables = soup.find_all('table')
        for table in tables:
            styled_text.append("## 프로그램 정보")
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    key = cells[0].get_text().strip()
                    value = cells[1].get_text().strip()
                    styled_text.append(f"**{key}**: {value}")
            styled_text.append("")
        
        # 본문 내용 추출
        content_divs = soup.find_all(['div', 'p'], class_=re.compile(r'content|body|main'))
        for div in content_divs:
            text = div.get_text().strip()
            if text and len(text) > 10:
                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        styled_text.append(line)
                styled_text.append("")
        
        return '\n'.join(styled_text)
    
    def scrape_page(self, url):
        """웹페이지 스크래핑"""
        try:
            # URL 검증 및 정규화
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            print(f"요청 URL: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 페이지 제목 추출
            page_title = soup.find('title')
            if page_title:
                title = page_title.get_text().strip()
            else:
                title = "웹페이지_스크래핑"
            
            # 폴더명 생성
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
            
            return {
                'success': True,
                'folder_path': str(folder_path),
                'text_content': styled_text,
                'image_count': len(image_info),
                'images': image_info
            }
            
        except requests.exceptions.ConnectTimeout:
            return {
                'success': False,
                'error': '연결 시간 초과: 서버에 연결할 수 없습니다. 네트워크 연결을 확인하거나 잠시 후 다시 시도해주세요.'
            }
        except requests.exceptions.ReadTimeout:
            return {
                'success': False,
                'error': '읽기 시간 초과: 서버 응답이 너무 느립니다. 잠시 후 다시 시도해주세요.'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': '연결 오류: 서버에 연결할 수 없습니다. URL을 확인하거나 네트워크 연결을 점검해주세요.'
            }
        except requests.exceptions.HTTPError as e:
            return {
                'success': False,
                'error': f'HTTP 오류 ({e.response.status_code}): {e.response.reason}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'알 수 없는 오류: {str(e)}'
            }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    url = request.json.get('url', '').strip()
    use_selenium = request.json.get('use_selenium', False)
    
    if not url:
        return jsonify({'success': False, 'error': 'URL을 입력해주세요.'})
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    if use_selenium:
        try:
            from web_scraper_selenium import SeleniumWebScraper
            scraper = SeleniumWebScraper(url)
            result = scraper.scrape_page(url)
        except ImportError:
            return jsonify({
                'success': False, 
                'error': 'Selenium이 설치되지 않았습니다. pip install selenium을 실행해주세요.'
            })
    else:
        scraper = WebScraper(url)
        result = scraper.scrape_page(url)
        
        # 일반 방법이 실패하면 자동으로 Selenium 시도
        if not result['success'] and 'ConnectTimeoutError' in str(result.get('error', '')):
            try:
                from web_scraper_selenium import SeleniumWebScraper
                print("일반 방법 실패, Selenium으로 재시도...")
                selenium_scraper = SeleniumWebScraper(url)
                result = selenium_scraper.scrape_page(url)
                if result['success']:
                    result['method'] = 'selenium_auto_fallback'
            except ImportError:
                pass  # Selenium이 없으면 원래 오류 반환
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
