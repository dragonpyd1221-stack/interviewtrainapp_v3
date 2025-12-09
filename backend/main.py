from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import shutil
import os
import time
from datetime import datetime
from typing import Optional, List
import database
import models

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists
UPLOAD_DIR = "uploads/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
def startup_event():
    database.init_db()

# --- Auth API ---
@app.post("/api/login")
def login(user: models.UserLogin):
    # Mock Auth
    if user.email == "admin@test.com" and user.password == "admin":
        return {"email": user.email, "role": "admin", "token": "mock-admin-token", "name": "Admin User"}
    elif user.email and user.password: # Allow any other user
        return {"email": user.email, "role": "user", "token": "mock-user-token", "name": "Demo User"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

# --- Video API ---
@app.get("/api/videos")
def get_videos(category: Optional[str] = None):
    return database.get_all_videos(category)

@app.get("/api/videos/{video_id}")
def get_video_detail(video_id: str):
    video = database.get_video(video_id)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return video

@app.post("/api/videos")
async def upload_video(
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(...),
    duration: str = Form("00:00"),
    file: Optional[UploadFile] = File(None),
    thumbnail: str = Form("")
):
    video_id = f"v{int(time.time())}"
    
    video_url = ""
    # Process File Upload
    if file:
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"{video_id}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, new_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # URL accessible from frontend
        video_url = f"http://localhost:8000/uploads/videos/{new_filename}"
    else:
        # If no file, maybe it's an external URL logic provided by frontend (though our admin form implies file mostly)
        # For this refactor, let's assume if no file is uploaded, we might have a text URL?
        # But our current requirement emphasizes file upload. If purely URL based, we'd need another field.
        # Let's support an optional 'source_url' form field just in case, or default to placeholder
        pass

    # If the user provided an external URL in the 'url' field (handled by frontend logic sending either file or string),
    # but here we are using multipart. Let's keep it simple: if file, use file. If not file, use placeholder.
    if not video_url:
         video_url = "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" # Fallback

    new_video = {
        "id": video_id,
        "title": title,
        "description": description,
        "url": video_url,
        "thumbnail": thumbnail or "https://via.placeholder.com/300x169.png?text=No+Image",
        "duration": duration,
        "category": category,
        "created_at": datetime.now().isoformat()
    }
    
    database.create_video(new_video)
    return new_video

@app.delete("/api/videos/{video_id}")
def delete_video(video_id: str):
    video = database.get_video(video_id)
    if video:
        # Optional: Delete file from disk
        if "uploads/videos" in video["url"]:
            filename = os.path.basename(video["url"])
            path = os.path.join(UPLOAD_DIR, filename)
            if os.path.exists(path):
                os.remove(path)
        
        database.delete_video(video_id)
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Video not found")

# --- Progress API ---
@app.get("/api/progress/{user_email}")
def get_progress(user_email: str):
    return database.get_user_progress(user_email)

@app.post("/api/progress")
def save_progress(data: models.ProgressUpdate):
    database.update_progress(data.email, data.video_id, data.timestamp, data.status)
    return {"status": "saved"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
