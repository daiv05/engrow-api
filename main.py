import uvicorn
from app.main import app  # noqa: F401 — re-export so `uvicorn main:app` works

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8010, reload=True)
