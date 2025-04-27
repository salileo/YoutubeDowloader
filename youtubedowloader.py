import yt_dlp
import os
import tempfile
import tkinter as tk
from tkinter import filedialog
import subprocess

def convert_to_mp3(input_file, output_file):
    command = [
        'E:\\bin\\ffmpreg\\bin\\ffmpeg.exe',
        '-i', input_file,
        '-vn',  # no video
        '-ab', '192k',  # audio bitrate
        '-ar', '44100',  # audio sampling rate
        '-y',  # overwrite if exists
        output_file
    ]

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        bufsize=1
    )

    # Read ffmpeg output line by line
    for line in process.stdout:
        if "size=" in line:
            print(f"Converting: {line.strip()}", end='\r')
    
    process.wait()

def pick_output_folder():
    root = tk.Tk()
    root.withdraw()
    folder = filedialog.askdirectory(title="Select Folder to Save MP3")
    root.destroy()
    return folder

def youtube_to_mp3():
    # 1. Ask for URL input
    youtube_url = input("Enter the YouTube URL: ").strip()
    
    # 2. Open Windows Explorer dialog to select output folder
    output_folder = pick_output_folder()
    if not output_folder:
        print("No folder selected. Exiting.")
        return

    print(f"Selected output folder: {output_folder}")

    temp_folder = tempfile.gettempdir()
    temp_output_template = os.path.join(temp_folder, '%(title)s.%(ext)s')
    
    # 3. yt-dlp options
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': temp_output_template,
        'quiet': True
    }

    print("Downloading file...")
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=True)
        title = info.get('title', None)
        ext = info.get('ext', 'webm')

    downloaded_file = os.path.join(temp_folder, f"{title}.{ext}")
    mp3_file = os.path.join(output_folder, f"{title}.mp3")

    # 4. Start conversion
    print("Starting conversion to MP3...")
    convert_to_mp3(downloaded_file, mp3_file)
    print("\n✅ Conversion to MP3 complete!")

    # 5. Remove original downloaded file
    os.remove(downloaded_file)
    print(f"\n🎉 All done! MP3 saved to: {mp3_file}")

# Example usage
youtube_to_mp3()
