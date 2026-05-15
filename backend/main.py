from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from routes import router

load_dotenv()

app = FastAPI(
    title="ResQRoute API",
    description="Evacuation route planning with AI-powered risk assessment",
    version="1.0.0"
)

# CORS — allow all origins in production (restrict to your deployed frontend URL once known)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
@app.head("/")
def read_root():
    return {"message": "ResQRoute API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
