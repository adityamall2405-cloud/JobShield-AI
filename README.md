# JobShield AI - Fake Job Posting Prediction Platform

JobShield AI is a full-stack platform that detects fraudulent job postings using:
- ML-based fraud probability prediction
- Trust score (`1 - fraud probability`)
- Scam indicator analysis (missing details, unrealistic salary, phishing signals)

## Tech Stack
- Backend: FastAPI + scikit-learn
- Frontend: React + Vite
- Model: TF-IDF + Logistic Regression (class-balanced)

## Project Structure
- `fake_job_postings.csv` - training dataset
- `backend/train_model.py` - model training script
- `backend/app/main.py` - API server
- `frontend/` - web client

## Backend Setup
```powershell
cd "c:\Users\adity\OneDrive\Desktop\fake job postings\backend"
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Train model:
```powershell
cd "c:\Users\adity\OneDrive\Desktop\fake job postings"
python .\backend\train_model.py --data .\fake_job_postings.csv --output .\backend\models\jobshield_model.joblib
```

Run API:
```powershell
cd "c:\Users\adity\OneDrive\Desktop\fake job postings"
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

## Frontend Setup
```powershell
cd "c:\Users\adity\OneDrive\Desktop\fake job postings\frontend"
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## One-Click Local Startup
From project root:
```powershell
powershell -ExecutionPolicy Bypass -File .\start_backend.ps1
```

In a second terminal:
```powershell
powershell -ExecutionPolicy Bypass -File .\start_frontend.ps1
```

Helper script:
```powershell
.\start_all.ps1
```

## API Endpoints
- `GET /health` - API + model status
- `POST /train` - train and reload model
- `POST /predict` - predict fake/legit posting

### Sample Prediction Request
```json
{
  "title": "Remote Data Entry Specialist",
  "salary_range": "200000-300000",
  "company_profile": "",
  "description": "Urgent hiring. Share bank details for direct payout.",
  "requirements": "No experience required",
  "telecommuting": 1,
  "has_company_logo": 0,
  "has_questions": 0
}
```

## Deployment

### 1) Deploy Backend (Render)
- Push this project to GitHub
- In Render, create a **Blueprint** service and point to your repo
- Render will auto-read `render.yaml`
- After deploy, copy backend URL (example: `https://jobshield-api.onrender.com`)

### 2) Deploy Frontend (Vercel)
- Import the same repo in Vercel
- Set **Root Directory** to `frontend`
- Add environment variable:
  - `VITE_API_BASE_URL=https://your-render-backend-url`
- Deploy

Frontend will call your live API using `VITE_API_BASE_URL`.
