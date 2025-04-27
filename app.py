from flask import Flask, request, send_from_directory, render_template, jsonify, Response
import os
import re
import tempfile
import threading
import yt_dlp
import subprocess

app = Flask(__name__)
temp_folder = tempfile.gettempdir()
temp_output_template = os.path.join(temp_folder, '%(id)s.%(ext)s')

# download and install ffmpeg from https://ffmpeg.org/download.html
# and set the path to ffmpeg in the command below
ffmpeg_path = 'E:\\bin\\ffmpreg\\bin\\'

# Global dictionary to store job statuses
job_status = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    data = request.json
    youtube_url = data.get('url')

    if not youtube_url:
        return jsonify({'error': 'No URL provided'}), 400

    job_id = str(len(job_status) + 1)

    # Start download/convert in a background thread
    thread = threading.Thread(target=download_and_convert, args=(job_id, youtube_url))
    thread.start()

    return jsonify({'job_id': job_id})

def download_and_convert(job_id, youtube_url):
    try:
        job_status[job_id] = {"status": "downloading", "progress": 0}
        downloaded_file, title = download_youtube_video(job_id, youtube_url)

        job_status[job_id] = {"status": "converting", "progress": 0}
        mp3_file = convert_to_mp3(job_id, downloaded_file, title)

        job_status[job_id] = {"status": "finished", "progress": 0, "data": title + ".mp3"}
        os.remove(downloaded_file)
    except Exception as e:
       job_status[job_id] = {"status": "error", "progress": 0, "data": str(e)}

def download_youtube_video(job_id, youtube_url):
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': temp_output_template,
            'quiet': True,
            'progress_hooks': [lambda d: download_hook({**d, "job_id": job_id})]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=True)
            title = sanitize_filename(info.get('title', 'audio'))
            id = info.get('id', 'id')
            ext = info.get('ext', 'webm')

        downloaded_file = os.path.join(temp_folder, f"{id}.{ext}")
        return (downloaded_file, title)

def download_hook(d):
    job_id = d.get('job_id')
    if d['status'] == 'downloading':
        percent = d.get('_percent')
        job_status[job_id] = {"status": "downloading", "progress": float(percent)}
    elif d['status'] == 'finished':
        job_status[job_id] = {"status": "converting", "progress": 0}

def sanitize_filename(name, max_length=255):
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", name)
    sanitized = sanitized.strip()
    return sanitized[:max_length]

def convert_to_mp3(job_id, input_file, title):
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

    mp3_file = os.path.join(temp_folder, f"{title}.mp3")

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
            job_status[job_id] = {"status": "converting", "progress": percent}
    
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

@app.route('/stream/<job_id>')
def stream(job_id):
    return Response(event_stream(job_id), mimetype='text/event-stream')

def event_stream(job_id):
    last_progress = -1
    while True:
        status = job_status.get(job_id)
        if status:
            state = status.get('status')
            progress = status.get('progress', 0)
            data = status.get('data', None)
            if progress != last_progress:
                yield f"data: {state}:{progress}:{data}\n\n"
                last_progress = progress
            if state == "finished" or state == "error":
                break
        import time
        time.sleep(0.5)

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(temp_folder, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
