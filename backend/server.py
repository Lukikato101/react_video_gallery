import boto3
import psycopg2

from typing import List
from pydantic import BaseModel

import uvicorn
from fastapi import FastAPI, UploadFile

from fastapi.middleware.cors import CORSMiddleware

S3_BUCKET_NAME = "video-app-123"

class VideoModel(BaseModel):
    id: int
    video_title: str
    video_url: str
    

app = FastAPI(debug=True)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/videos", response_model=List[VideoModel])
async def get_videos():
    conn = psycopg2.connect(
        database="exampledb", user="docker", password="docker", host="0.0.0.0"
    )
    
    cur = conn.cursor()
    cur.execute("SELECT * FROM video ORDER BY id DESC")
    rows = cur.fetchall()
    
    formatted_videos = []
    for row in rows:
        formatted_videos.append(
            VideoModel(id=row[0], video_title=row[1], video_url=row[2])
        )
        
    cur.close()
    conn.close()
    return formatted_videos

@app.post("/videos", status_code=201)
async def add_video(file: UploadFile):
    #upload file ke AWS S3
    s3 = boto3.resource("s3")
    bucket = s3.bucket(S3_BUCKET_NAME)
    bucket.upload_fileobj(file.file, file.filename, ExtraArgs={"ACL": "public-read"})
    
    uploaded_file_url = f"https://{S3.BUCKET_NAME.s3.amazonaws.com/{file.filename}}"

    #Menyimpan URL di Database
    conn = pyscopg2.connect(
        database="exampledb", user="docker", password="docker", host="0.0.0.0"
    )
    cur = conn.cursor()
    cur.execute(
    "INSERT INTO video (video_title, video_url) VALUES (%s, %s)",
    (file.filename, uploaded_file_url)
    )
    conn.commit()
    
    cur.close()
    conn.close()
    
@app.get('/status')
async def check_status():
     return "hello World"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
    
