from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import yt_dlp
import os
import requests
from dotenv import load_dotenv
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()
load_dotenv()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

@app.post("/download")
async def download(q: Query):

    queries = q.query.strip()
    print(f"Searching: {queries}")

    KEY = os.getenv("KEY")
    cx = os.getenv("cx")

    search_url = f"https://www.googleapis.com/customsearch/v1?key={KEY}&cx={cx}&q={queries}+youtube"

    # ---- SEARCH YOUTUBE ----
    try:
        r = requests.get(search_url)
        r.raise_for_status()
        data = r.json()

        link = data["items"][0]["link"]
        title = data["items"][0]["title"]

    except Exception as e:
        print("Search error", str(e))
        return JSONResponse(
            status_code=400,
            content={"status": "failure", "error": str(e)},
        )

    # ---- DOWNLOAD AUDIO ----
    try:
        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
            audio_url = info.get("url")

        return {
            "status": "success",
            "title": title,
            "audio_url": audio_url,
        }

    except Exception as e:
        print("Download error", str(e))
        return JSONResponse(
            status_code=400,
            content={"status": "failure", "error": str(e)},
        )
