from fastapi import FastAPI, UploadFile, Form, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import shutil
import os
import time
from datetime import datetime
from typing import Optional, List
import boto3
from botocore.exceptions import NoCredentialsError
import database
import models

# --- Configuration ---
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION", "ap-northeast-2") # Default to Seoul if not set

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists (Legacy support or temp storage if needed)
UPLOAD_DIR = "uploads/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mount static files (Still needed for legacy local files if any remain)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
def startup_event():
    database.init_db()

# --- Auth API ---
@app.post("/api/login")
def login(user: models.UserLogin):
    # Mock Auth
    if user.email == "admin@test.com" and (user.password == "admin" or user.password == "password"):
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
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    category: str = Form(...),
    duration: str = Form("00:00"),
    file: Optional[UploadFile] = File(None),
    thumbnail: str = Form("")
):
    video_id = f"v{int(time.time())}"
    video_url = ""

    # Process File Upload with S3
    if file:
        file_extension = os.path.splitext(file.filename)[1]
        new_filename = f"{video_id}{file_extension}"
        
        print(f"[S3 UPLOAD] Starting upload to S3...")
        print(f"[S3 UPLOAD] Bucket: {AWS_S3_BUCKET_NAME}")
        print(f"[S3 UPLOAD] Object Key: {new_filename}")
        print(f"[S3 UPLOAD] Region: {AWS_REGION}")
        
        try:
            # Upload to S3
            s3_client.upload_fileobj(
                file.file,
                AWS_S3_BUCKET_NAME,
                new_filename,
                ExtraArgs={'ContentType': file.content_type} # Ensure correct mime type
            )
            
            # Generate S3 URL
            video_url = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{new_filename}"
            
            print(f"[S3 UPLOAD] ✅ SUCCESS - File uploaded to S3")
            print(f"[S3 UPLOAD] S3 URL: {video_url}")
            
        except NoCredentialsError as e:
            print(f"[S3 UPLOAD] ❌ ERROR - AWS Credentials not found")
            print(f"[S3 UPLOAD] Details: {str(e)}")
            raise HTTPException(status_code=500, detail="AWS Credentials not found")
        except Exception as e:
            print(f"[S3 UPLOAD] ❌ ERROR - S3 Upload failed")
            print(f"[S3 UPLOAD] Error type: {type(e).__name__}")
            print(f"[S3 UPLOAD] Error message: {str(e)}")
            raise HTTPException(status_code=500, detail=f"S3 Upload failed: {str(e)}")

    else:
        print(f"[S3 UPLOAD] ⚠️  No file provided, using fallback URL")
        # Fallback if no file uploaded
        pass

    if not video_url:
         video_url = "https://storage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" # Fallback
         print(f"[S3 UPLOAD] Using fallback URL: {video_url}")

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
    print(f"[S3 UPLOAD] Video record created in database with ID: {video_id}")
    return new_video

@app.delete("/api/videos/{video_id}")
def delete_video(video_id: str):
    video = database.get_video(video_id)
    if video:
        # Delete from S3 if it's an S3 URL
        if AWS_S3_BUCKET_NAME in video["url"] and "amazonaws.com" in video["url"]:
            try:
                # Extract filename from URL
                filename = video["url"].split("/")[-1]
                s3_client.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=filename)
            except Exception as e:
                print(f"Failed to delete from S3: {e}")

        # Legacy: Delete local file if exists
        elif "uploads/videos" in video["url"]:
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
