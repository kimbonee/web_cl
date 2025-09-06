#!/usr/bin/env python3
"""
Selenium을 사용한 웹페이지 스크래핑 (대안 방법)
JavaScript가 필요한 사이트나 연결 문제가 있는 사이트에 사용
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import time

class SeleniumWebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.driver = None
        
    def setup_driver(self):
        """Chrome 드라이버 설정"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # 백그라운드 실행
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            return True
        except Exception as e:
            print(f"Chrome 드라이버 설정 실패: {e}")
            return False
    
    def create_folder(self, folder_name):
        """데스크탑에 폴더 생성"""
        desktop_path = Path.home() / "Desktop"
        folder_path = desktop_path / folder_name
        
        print(f"폴더 생성 시도: {folder_path}")
        
        try:
            folder_path.mkdir(parents=True, exist_ok=True)
            print(f"폴더 생성 성공: {folder_path}")
            
            # images 하위 폴더도 생성
            images_folder = folder_path / "images"
            images_folder.mkdir(exist_ok=True)
            print(f"images 폴더 생성: {images_folder}")
            
        except Exception as e:
            print(f"폴더 생성 실패: {e}")
            # 대안 경로 시도
            alternative_path = Path.cwd() / "downloads" / folder_name
            alternative_path.mkdir(parents=True, exist_ok=True)
            (alternative_path / "images").mkdir(exist_ok=True)
            print(f"대안 경로로 폴더 생성: {alternative_path}")
            return alternative_path
        
        return folder_path
    
    def download_image(self, img_url, folder_path, img_name):
        """이미지 다운로드 (requests 사용)"""
        try:
            import requests
            
            # 절대 URL로 변환
            if img_url.startswith('//'):
                img_url = 'https:' + img_url
            elif img_url.startswith('/'):
                img_url = urljoin(self.base_url, img_url)
            elif not img_url.startswith(('http://', 'https://')):
                img_url = urljoin(self.base_url, '/' + img_url.lstrip('/'))
            
            print(f"이미지 다운로드 시도: {img_url}")
            
            # 세션 생성 및 헤더 설정
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
                'Referer': self.base_url
            })
            
            response = session.get(img_url, timeout=15, stream=True)
            response.raise_for_status()
            
            # Content-Type 확인
            content_type = response.headers.get('content-type', '')
            print(f"Content-Type: {content_type}")
            
            # 파일 확장자 결정
            if 'image/jpeg' in content_type or 'image/jpg' in content_type:
                file_ext = '.jpg'
            elif 'image/png' in content_type:
                file_ext = '.png'
            elif 'image/gif' in content_type:
                file_ext = '.gif'
            elif 'image/webp' in content_type:
                file_ext = '.webp'
            else:
                # URL에서 확장자 추출
                parsed_url = urlparse(img_url)
                file_ext = os.path.splitext(parsed_url.path)[1]
                if not file_ext:
                    file_ext = '.jpg'  # 기본값
            
            # 파일명 정리
            safe_name = re.sub(r'[^\w\-_\.]', '_', img_name)
            filename = f"{safe_name}{file_ext}"
            file_path = folder_path / "images" / filename
            
            # images 폴더 생성 확인
            images_folder = folder_path / "images"
            if not images_folder.exists():
                images_folder.mkdir(parents=True, exist_ok=True)
                print(f"images 폴더 생성: {images_folder}")
            
            # 이미지 데이터 저장
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 파일 크기 확인
            file_size = os.path.getsize(file_path)
            print(f"이미지 저장 완료: {file_path} (크기: {file_size} bytes)")
            
            if file_size == 0:
                print(f"경고: 이미지 파일이 비어있습니다: {file_path}")
                return None
            
            return str(file_path)
            
        except Exception as e:
            print(f"이미지 다운로드 실패: {img_url} - {e}")
            return None
    
    def extract_text_with_styling(self, page_source, url=None):
        """페이지 소스에서 텍스트 추출"""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(page_source, 'html.parser')
        styled_text = []
        
        # URL 정보 추가
        if url:
            styled_text.append(f"**원본 URL**: {url}")
            styled_text.append("")
        
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
        """Selenium을 사용한 웹페이지 스크래핑"""
        try:
            if not self.setup_driver():
                return {
                    'success': False,
                    'error': 'Chrome 드라이버를 설정할 수 없습니다. Chrome 브라우저가 설치되어 있는지 확인해주세요.'
                }
            
            # URL 검증 및 정규화
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            print(f"Selenium으로 요청 URL: {url}")
            
            # 페이지 로드
            self.driver.get(url)
            
            # 페이지 로딩 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # 추가 대기 (JavaScript 로딩)
            time.sleep(3)
            
            # 페이지 제목 추출
            page_title = self.driver.title
            if not page_title:
                page_title = "웹페이지_스크래핑"
            
            # 폴더명 생성
            safe_title = re.sub(r'[^\w\-_\.]', '_', page_title)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{safe_title}_{timestamp}"
            
            # 폴더 생성
            folder_path = self.create_folder(folder_name)
            
            # 페이지 소스 가져오기
            page_source = self.driver.page_source
            
            # 텍스트 정보 추출
            styled_text = self.extract_text_with_styling(page_source, url)
            
            # 텍스트 파일로 저장
            text_file = folder_path / "content.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(styled_text)
            
            # 마크다운 파일로도 저장
            md_file = folder_path / "content.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(styled_text)
            
            # 페이지 전체 스크린샷 캡처
            screenshot_path = folder_path / "page_screenshot.png"
            try:
                self.driver.save_screenshot(str(screenshot_path))
                print(f"페이지 스크린샷 저장: {screenshot_path}")
            except Exception as e:
                print(f"스크린샷 저장 실패: {e}")
                screenshot_path = None
            
            # 이미지 추출 및 다운로드
            images = self.driver.find_elements(By.TAG_NAME, "img")
            image_info = []
            
            for i, img in enumerate(images):
                try:
                    img_src = img.get_attribute('src')
                    if img_src:
                        img_alt = img.get_attribute('alt') or f'image_{i+1}'
                        img_path = self.download_image(img_src, folder_path, img_alt)
                        if img_path:
                            image_info.append({
                                'original_url': img_src,
                                'local_path': img_path,
                                'alt_text': img_alt
                            })
                except Exception as e:
                    print(f"이미지 처리 오류: {e}")
                    continue
            
            # 스크린샷 정보 추가
            if screenshot_path:
                image_info.append({
                    'original_url': 'page_screenshot',
                    'local_path': str(screenshot_path),
                    'alt_text': '페이지 전체 스크린샷'
                })
            
            # 메타데이터 저장
            metadata = {
                'url': url,
                'title': page_title,
                'scraped_at': datetime.now().isoformat(),
                'method': 'selenium',
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
                'images': image_info,
                'method': 'selenium'
            }
            
        except TimeoutException:
            return {
                'success': False,
                'error': '페이지 로딩 시간 초과: 페이지가 너무 오래 걸려 로드되지 않습니다.'
            }
        except WebDriverException as e:
            return {
                'success': False,
                'error': f'브라우저 오류: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'알 수 없는 오류: {str(e)}'
            }
        finally:
            if self.driver:
                self.driver.quit()

def main():
    import sys
    if len(sys.argv) != 2:
        print("사용법: python3 web_scraper_selenium.py <URL>")
        sys.exit(1)
    
    url = sys.argv[1]
    scraper = SeleniumWebScraper(url)
    result = scraper.scrape_page(url)
    
    if result['success']:
        print(f"스크래핑 완료!")
        print(f"폴더 위치: {result['folder_path']}")
        print(f"이미지 개수: {result['image_count']}")
        print(f"사용된 방법: {result['method']}")
    else:
        print(f"스크래핑 실패: {result['error']}")

if __name__ == "__main__":
    main()
