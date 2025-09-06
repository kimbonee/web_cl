# GitHub 저장소 설정 가이드

## 1. GitHub에서 새 저장소 생성

1. [GitHub.com](https://github.com)에 로그인
2. "New repository" 버튼 클릭
3. 저장소 이름: `web-scraper` (또는 원하는 이름)
4. 설명: "웹페이지 스크래핑 프로그램 - 텍스트와 이미지를 추출하여 데스크탑에 저장"
5. Public 또는 Private 선택
6. "Create repository" 클릭

## 2. 로컬 저장소와 GitHub 연결

GitHub에서 저장소를 생성한 후, 다음 명령어를 실행하세요:

```bash
# GitHub 저장소 URL을 원격 저장소로 추가
git remote add origin https://github.com/YOUR_USERNAME/web-scraper.git

# 메인 브랜치로 설정
git branch -M main

# 코드를 GitHub에 푸시
git push -u origin main
```

## 3. 사용법

```bash
# 저장소 클론
git clone https://github.com/YOUR_USERNAME/web-scraper.git
cd web-scraper

# 의존성 설치
pip3 install -r requirements.txt

# 프로그램 실행
python3 web_scraper.py "웹페이지_URL"
```

## 4. 예시

```bash
python3 web_scraper.py "https://r.yongsanyouthtown.or.kr/modules/board/bd_view.html?no=132&id=apply&p=1&or=bd_order&al=asc"
```
