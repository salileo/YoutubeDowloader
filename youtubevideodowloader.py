import os
import re
import tempfile
import yt_dlp
import shutil
import tkinter as tk
from tkinter import filedialog

temp_folder = tempfile.gettempdir()
temp_output_template = os.path.join(temp_folder, '%(id)s.%(ext)s')

# download and install ffmpeg from https://ffmpeg.org/download.html
# and set the path to ffmpeg in the command below
ffmpeg_path = 'E:\\bin\\ffmpreg\\bin\\'

def download_youtube_video():
    try:
        # 1. Ask for URL input
        youtube_url = input("Enter the YouTube URL: ").strip()
        isLiveStream = input("Is this a live stream? (y/n): ").strip().lower() == 'y'

        # 2. Open Windows Explorer dialog to select output folder
        output_folder = pick_output_folder()
        if not output_folder:
            print("No folder selected. Exiting.")
            return

        print("Downloading file...")
        ydl_opts = None
        if isLiveStream:
            ydl_opts = {
                'format': 'best',
                'outtmpl': temp_output_template,
                'ffmpeg_location': ffmpeg_path,
                'hls_use_mpegts': True,
                'live_from_start': True,
                'quiet': True,
            }
        else:        
            ydl_opts = {
                'format': 'best',
                'outtmpl': temp_output_template,
                'ffmpeg_location': ffmpeg_path,
                'quiet': True,
            }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = sanitize_filename(info.get('title', 'audio'))
            id = info.get('id', 'id')
            ext = info.get('ext', 'webm')

        downloaded_file = os.path.join(temp_folder, f"{id}.{ext}")
        output_file = os.path.join(output_folder, f"{title}.{ext}")
        shutil.move(downloaded_file, output_file)

        print(f"\n🎉 All done! Video saved to: {output_file}")
    except Exception as e:
       print("Error occurred:", str(e))

def pick_output_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Folder to Save MP3")
    root.destroy()
    return folder

def sanitize_filename(name, max_length=255):
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", name)
    sanitized = sanitized.strip()
    return sanitized[:max_length]

# Example usage
download_youtube_video()
