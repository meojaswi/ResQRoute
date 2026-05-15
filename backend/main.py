from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Mount frontend static files
frontend_dist = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))

# Only mount if the dist folder actually exists (i.e. after npm run build)
if os.path.exists(frontend_dist):
    # Mount the assets directory directly
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")
    
    # Catch-all route to serve the React app
    @app.get("/{full_path:path}")
    @app.head("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Don't intercept API calls
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API route not found")
        
        # Serve exact file if it exists (e.g. favicon.ico, images)
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Otherwise serve index.html for SPA routing
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    @app.get("/")
    @app.head("/")
    def read_root():
        return {"message": "ResQRoute API (Frontend not built yet. Run npm run build in frontend folder)"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
