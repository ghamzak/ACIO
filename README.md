# ACIO: Autonomous Contract Intelligence Orchestrator

Autonomous multi-agent system that orchestrates end-to-end contract intelligence using LLMs, RLHF, and enterprise tool integration.

## Setup

### 1. Clone the repository
```
git clone <your-repo-url>
cd ACIO
```

### 2. Python Backend Setup
- Create a virtual environment and activate it:
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```
- Install dependencies:
  ```
  pip install -r requirements.txt
  ```
- Copy `.env.example` to `.env` and set your 32-byte `ACIO_AES_KEY`:
  ```
  cp .env.example .env
  # Edit .env and set ACIO_AES_KEY to a secure 32-byte string
  ```
  **Note:** The `ACIO_AES_KEY` is required for AES-256 encryption of uploaded documents. It must be exactly 32 characters (bytes). Example:
  ```
  ACIO_AES_KEY=9f8d2e1c4b7a63e1e950adf4cb84792d29cfbba8d0e8b676c942a7f3c8141b26
  ```

- Run the backend server:
  ```
  uvicorn app.main:app --reload
  ```

### 3. Frontend Setup
- In a new terminal, go to the `frontend` directory:
  ```
  cd frontend
  npm install
  npm run dev
  ```
- The React app will be available at [http://localhost:5173](http://localhost:5173)
- **Note:** The backend must be running for the frontend to work.

## API Testing
- You can test the API directly using Swagger UI at [http://localhost:8000/docs](http://localhost:8000/docs)
- Use the `/extract-text/` endpoint to upload and extract text from contracts.
- Use the `/classify-contract/` endpoint to upload a contract file and get the contract type.

## CORS
- CORS (Cross-Origin Resource Sharing) is enabled in the backend to allow the React frontend (running on a different port) to communicate with the FastAPI backend during development. This is necessary for browser security and local development.

---
For more details, see the code and comments in each directory.

