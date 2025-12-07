from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI,Body
import yt_dlp
import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
app = FastAPI()
load_dotenv()
app.add_middleware(CORSMiddleware,allow_headers =["*"],allow_methods = ["*"],allow_origins = ["*"])
class Query(BaseModel):
    query:str
@app.post('/download')
async def download(q:Query):
    queries = q.query.strip()
    print(f"{queries}")
    KEY = os.getenv("KEY")
    cx = os.getenv("cx") 
    api = f"https://www.googleapis.com/customsearch/v1?key={KEY}&cx={cx}&q={queries}+youtube";
    title = ""
    link =""
    try:
        req = requests.get(api)
        req.raise_for_status()
        fields = req.json()
        link = fields["items"][0]["link"]
        title = fields["items"][0]["title"]
    except Exception as e:
        print("Error:",e)
        return {"status":"failure","error":e}
    link = link.strip()
    try:
        ydl_opts= {
            'format': 'bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link,download=True)
            filename = ydl.prepare_filename(info).replace('.webm','.mp3').replace('.m4a',',mp3')

            return {
                "status":"success"
                ,"title":title,"audio_url":info['url']
            }



    except Exception as e:
        print("Download Error:",e)
        return {
            "status":"failure","error":e
        }
    