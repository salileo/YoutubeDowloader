import os
import re
import tempfile
import yt_dlp
import subprocess
import tkinter as tk
from tkinter import filedialog

temp_folder = tempfile.gettempdir()
temp_output_template = os.path.join(temp_folder, '%(id)s.%(ext)s')

# download and install ffmpeg from https://ffmpeg.org/download.html
# and set the path to ffmpeg in the command below
ffmpeg_path = 'E:\\bin\\ffmpreg\\bin\\'

def youtube_to_mp3():
    try:
        # 1. Ask for URL input
        youtube_url = input("Enter the YouTube URL: ").strip()
        
        # 2. Open Windows Explorer dialog to select output folder
        output_folder = pick_output_folder()
        if not output_folder:
            print("No folder selected. Exiting.")
            return

        print("Downloading file...")
        downloaded_file, title = download_youtube_video(youtube_url)

        print("Starting conversion to MP3...")
        mp3_file = convert_to_mp3(downloaded_file, output_folder, title)
        print("✅ Conversion to MP3 complete!")

        os.remove(downloaded_file)
        print(f"\n🎉 All done! MP3 saved to: {mp3_file}")
    except Exception as e:
       print("Error occurred:", str(e))

def pick_output_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Folder to Save MP3")
    root.destroy()
    return folder

def download_youtube_video(youtube_url):
        ydl_opts = {
            'format': 'bestaudio/best',
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
        return (downloaded_file, title)

def sanitize_filename(name, max_length=255):
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", name)
    sanitized = sanitized.strip()
    return sanitized[:max_length]

def convert_to_mp3(input_file, output_folder, title):
    command = [
        ffmpeg_path + 'ffprobe.exe',
        '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        input_file
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    total_duration = float(result.stdout.strip())

    mp3_file = os.path.join(output_folder, f"{title}.mp3")

    command = [
        ffmpeg_path + 'ffmpeg.exe',
        '-i', input_file,
        '-vn',
        '-ab', '192k',
        '-ar', '44100',
        '-y',
        mp3_file
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    while True:
        line = process.stderr.readline()
        if line == '' and process.poll() is not None:
            break
        if 'time=' not in line:
            continue
        current_time = parse_time_from_ffmpeg_output(line)
        if current_time:
            percent = (current_time / total_duration) * 100
            print(f"Converting progress: {percent:.2f}", end="\r")
    
    return mp3_file

def parse_time_from_ffmpeg_output(line):
    """Extract time= value from ffmpeg output line."""
    match = re.search(r'time=(\d+):(\d+):(\d+).(\d+)', line)
    if match:
        hours, minutes, seconds, fraction = map(int, match.groups())
        total_seconds = hours * 3600 + minutes * 60 + seconds + fraction / 100
        return total_seconds
    else:
        return None

# Example usage
youtube_to_mp3()
