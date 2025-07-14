# tame (MVP)
preventing agents from going rogue

- wraps mcp agent tool calls via sdk
- connects to centralized platform
- enables logging, policy enforcement, compliance (EU AI Act)
- next step is probably authentication

i found arcade.dev is alr doing this idea after i started it. so i built it anyway and gonna open source them. #fukit

---

## Getting Started

### Prerequisites
- [Docker](https://www.docker.com/get-started) and [Docker Compose](https://docs.docker.com/compose/install/)
- (Optional for local dev) [Python 3.11+](https://www.python.org/downloads/) and [Node.js 18+](https://nodejs.org/)

### Quick Start (Recommended: Docker Compose)

1. **Clone the repo:**
   ```bash
   git clone https://github.com/donbool/tame-mvp.git
   cd tame-mvp
   ```
2. **Start all services:**
   ```bash
   docker-compose up --build
   ```
   This will build and start:
   - Backend (FastAPI, port 8000)
   - Frontend (Vite/React, port 3000)
   - Postgres (port 5432)
   - Redis (port 6379)

3. **Access the app:**
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

4. **Stopping services:**
   ```bash
   docker-compose down
   ```

### Local Development (Advanced)

#### Backend
1. Create and activate a Python virtual environment:
   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start Postgres and Redis (use Docker or local installs):
   ```bash
   docker-compose up -d postgres redis
   ```
3. Start the backend server:
   ```bash
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

#### Frontend
1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start the dev server:
   ```bash
   npm run dev
   ```
3. Access at [http://localhost:3000](http://localhost:3000)

### Troubleshooting
- If the frontend cannot reach the backend, make sure both are running and the Vite proxy in `frontend/vite.config.ts` points to the correct backend address:
  - Docker Compose: `http://backend:8000`
  - Local: `http://localhost:8000`
- If you see database errors, ensure Postgres and Redis are running.
- For backend errors, check logs with:
  ```bash
  docker-compose logs backend
  ```

---

Enjoy! 
