# HI 면접 MASTER (Interview Training Platform)

이 프로젝트는 면접관 교육을 위한 동영상 학습 플랫폼입니다.
프론트엔드는 HTML/JS로 구성되어 있으며, 백엔드는 Python FastAPI를 사용합니다.

## 🚀 배포 가이드 (Deployment Guide)

### 1. 백엔드 (Backend) - Render
Render.com을 사용하여 백엔드 API를 배포합니다.

#### 설정 (Settings)
- **Name**: (원하는 이름)
- **Runtime**: Python 3
- **Root Directory**: `backend`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port 10000`

#### 중요: CORS 설정
Render 배포 후, `backend/main.py`의 `origins` 리스트에 **프론트엔드 배포 주소(GitHub Pages URL)**를 추가해야 할 수 있습니다.

### 2. 프론트엔드 (Frontend) - GitHub Pages
이 저장소 자체를 GitHub Pages로 호스팅하여 프론트엔드를 배포합니다.

#### 설정 (Settings)
1. GitHub 저장소의 **Settings** -> **Pages** 메뉴로 이동합니다.
2. **Source**를 `Deploy from a branch`로 선택합니다.
3. **Branch**를 `main` (또는 배포할 브랜치), 폴더를 `/ (root)`로 선택하고 **Save**를 클릭합니다.
4. 잠시 후 상단에 배포된 URL이 표시됩니다. (예: `https://your-username.github.io/repo-name/`)

#### API 연결 (API Connection)
1. `js/config.js` 파일을 엽니다.
2. `API_BASE_URL` 값을 위에서 배포한 **Render 백엔드 URL**로 변경합니다.
   ```javascript
   const CONFIG = {
       // API_BASE_URL: 'http://localhost:8000/api',
       API_BASE_URL: 'https://your-render-app-name.onrender.com/api' 
   };
   ```
3. 변경 사항을 커밋하고 푸시합니다.

## 📁 프로젝트 구조 (Project Structure)

```
.
├── admin.html          # 관리자 대시보드
├── index.html          # 메인(학습자) 대시보드
├── learning.html       # 나의 학습 현황
├── login.html          # 로그인 페이지
├── videos.html         # 강의 목록
├── watch.html          # 강의 시청 페이지
├── css/
│   └── style.css       # 스타일시트
├── js/
│   ├── app.js          # 공통 UI 로직
│   ├── auth.js         # 인증 관리
│   ├── config.js       # [NEW] API URL 설정
│   └── data.js         # 데이터/API 관리
├── assets/
│   └── videos/         # (데모용) 로컬 비디오 파일
└── backend/            # 백엔드 서버 코드
    ├── main.py         # FastAPI 앱 진입점
    ├── database.py     # DB 설정
    ├── models.py       # 데이터 모델
    └── requirements.txt
```

## 🛠 로컬 개발 (Local Development)

1. **백엔드 실행**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. **프론트엔드 실행**
   - Live Server 등을 사용하여 `index.html`을 엽니다.
   - `js/config.js`에서 `localhost` 주소 주석을 해제하여 사용합니다.