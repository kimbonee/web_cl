# 웹페이지 스크래핑 프로그램

웹페이지에서 텍스트 정보와 이미지를 추출하여 데스크탑에 저장하는 Python 프로그램입니다.

## 기능

- 웹페이지의 텍스트 정보 추출 (스타일 적용)
- 이미지 자동 다운로드 및 저장
- 데스크탑에 자동 폴더 생성
- 마크다운 및 텍스트 파일로 저장
- 메타데이터 JSON 파일 생성

## 설치

1. 저장소 클론:
```bash
git clone <repository-url>
cd web_scraper_project
```

2. 의존성 설치:
```bash
pip install -r requirements.txt
```

## 사용법

### 명령줄 버전

```bash
python3 web_scraper.py <URL>
```

예시:
```bash
python3 web_scraper.py "https://r.yongsanyouthtown.or.kr/modules/board/bd_view.html?no=132&id=apply&p=1&or=bd_order&al=asc"
```

### GUI 버전

```bash
python3 web_scraper_gui.py
```

GUI 버전에서는:
1. URL을 입력창에 입력
2. "스크래핑 시작" 버튼 클릭
3. 결과를 화면에서 확인
4. "결과 폴더 열기" 버튼으로 저장된 파일 확인

## 출력 파일

프로그램 실행 시 데스크탑에 다음 구조로 폴더가 생성됩니다:

```
프로그램명_타임스탬프/
├── content.txt          # 추출된 텍스트 (일반 텍스트)
├── content.md           # 추출된 텍스트 (마크다운)
├── metadata.json        # 메타데이터
└── images/              # 다운로드된 이미지들
    ├── image1.jpg
    └── image2.png
```

## 특징

- **스타일 적용**: 텍스트가 마크다운 형식으로 저장되어 복사-붙여넣기 시 서식이 유지됩니다.
- **이미지 자동 다운로드**: 페이지의 모든 이미지를 자동으로 다운로드합니다.
- **메타데이터 저장**: 원본 URL, 추출 시간, 이미지 정보 등을 JSON으로 저장합니다.
- **안전한 파일명**: 특수문자를 자동으로 처리하여 안전한 파일명을 생성합니다.

## 요구사항

- Python 3.7+
- 인터넷 연결
- 필요한 Python 패키지들 (requirements.txt 참조)
