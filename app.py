from flask import Flask, render_template, request, send_file, jsonify
import os
import subprocess
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def cleanup_files(file_paths):
    for f in file_paths:
        if os.path.exists(f):
            os.remove(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/merge_audio', methods=['POST'])
def merge_audio():
    files = request.files.getlist('files[]')
    input_paths = []

    # Save all uploaded MP3s
    for file in files:
        if file and file.filename.endswith('.mp3'):
            unique_name = f"{uuid.uuid4()}.mp3"
            path = os.path.join(UPLOAD_FOLDER, unique_name)
            file.save(path)
            input_paths.append(path)
        else:
            cleanup_files(input_paths)
            return jsonify({'error': 'Only .mp3 files allowed'}), 400

    # Create input text file for ffmpeg concat
    input_txt = os.path.join(UPLOAD_FOLDER, 'input_audio.txt')
    with open(input_txt, 'w') as f:
        for path in input_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    output_path = os.path.join(UPLOAD_FOLDER, 'merged_audio.mp3')
    if os.path.exists(output_path):
        os.remove(output_path)

    try:
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', input_txt,
            '-c', 'copy', output_path
        ], check=True)
        return send_file(output_path, as_attachment=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'FFmpeg audio merge failed', 'details': e.stderr.decode()}), 500
    finally:
        cleanup_files(input_paths + [input_txt])

@app.route('/merge_video', methods=['POST'])
def merge_video():
    files = request.files.getlist('files[]')
    input_paths = []

    # Save all uploaded MP4 videos
    for file in files:
        if file and file.filename.endswith('.mp4'):
            unique_name = f"{uuid.uuid4()}.mp4"
            path = os.path.join(UPLOAD_FOLDER, unique_name)
            file.save(path)
            input_paths.append(path)
        else:
            cleanup_files(input_paths)
            return jsonify({'error': 'Only .mp4 files allowed'}), 400

    # Create input text file for ffmpeg concat
    input_txt = os.path.join(UPLOAD_FOLDER, 'input_video.txt')
    with open(input_txt, 'w') as f:
        for path in input_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")

    output_path = os.path.join(UPLOAD_FOLDER, 'merged_video.mp4')
    if os.path.exists(output_path):
        os.remove(output_path)

    try:
        subprocess.run([
            'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', input_txt,
            '-c', 'copy', output_path
        ], check=True)
        return send_file(output_path, as_attachment=True)
    except subprocess.CalledProcessError as e:
        return jsonify({'error': 'FFmpeg video merge failed', 'details': e.stderr.decode()}), 500
    finally:
        cleanup_files(input_paths + [input_txt])

if __name__ == '__main__':
    app.run(debug=True)
