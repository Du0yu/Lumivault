from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash, send_file
import os
import json
import sys
import cv2
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于flash消息

CONFIG_PATH = 'config.json'
THUMB_DIR = 'video_thumbs'

def get_base_path():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config.get('base', '')

def get_media_files(base_path):
    categories = {}
    for folder in os.listdir(base_path):
        folder_path = os.path.join(base_path, folder)
        if os.path.isdir(folder_path):
            images = []
            videos = []
            for file in os.listdir(folder_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                    images.append(file)
                elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                    videos.append(file)
            categories[folder] = {
                'images': images,
                'videos': videos
            }
    return categories

def ensure_thumb_dir():
    if not os.path.exists(THUMB_DIR):
        os.makedirs(THUMB_DIR)

def get_video_thumb(base_path, category, video_filename):
    """
    截取视频第一帧作为封面，返回封面图片的相对路径
    """
    ensure_thumb_dir()
    video_path = os.path.join(base_path, category, video_filename)
    thumb_name = f"{category}__{os.path.splitext(video_filename)[0]}.jpg"
    thumb_path = os.path.join(THUMB_DIR, thumb_name)
    if not os.path.exists(thumb_path):
        try:
            cap = cv2.VideoCapture(video_path)
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(thumb_path, frame)
            cap.release()
        except Exception as e:
            print(f"生成视频封面失败: {video_path} {e}")
            return None
    return thumb_name if os.path.exists(thumb_path) else None

@app.route('/')
def index():
    base_path = get_base_path()
    if not base_path or not os.path.exists(base_path):
        flash('请先配置媒体根目录路径')
        return redirect(url_for('config'))
    return redirect(url_for('nav'))

@app.route('/media/<category>/<filename>')
def media(category, filename):
    base_path = get_base_path()
    dir_path = os.path.join(base_path, category)
    return send_from_directory(dir_path, filename)

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        base_path = request.form.get('base_path', '').strip()
        if not base_path or not os.path.exists(base_path):
            flash('路径无效，请重新输入')
            return render_template('config.html', base_path=base_path)
        # 适配不同OS，保存绝对路径
        base_path = os.path.abspath(base_path)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump({'base': base_path}, f, ensure_ascii=False, indent=2)
        flash('配置已保存')
        return redirect(url_for('index'))
    # 默认值尝试读取当前目录
    default_path = os.path.abspath(os.path.expanduser('~'))
    return render_template('config.html', base_path=default_path)

@app.route('/nav')
def nav():
    base_path = get_base_path()
    if not base_path or not os.path.exists(base_path):
        flash('请先配置媒体根目录路径')
        return redirect(url_for('config'))
    all_categories = get_media_files(base_path)
    # 获取每个类别的封面图（第一张图片，没有则None）
    covers = {}
    for cat, files in all_categories.items():
        covers[cat] = files['images'][0] if files['images'] else None
    return render_template('nav.html', covers=covers)

@app.route('/album')
def album():
    base_path = get_base_path()
    if not base_path or not os.path.exists(base_path):
        flash('请先配置媒体根目录路径')
        return redirect(url_for('config'))
    cat = request.args.get('cat')
    all_categories = get_media_files(base_path)
    # 生成视频封面路径
    video_thumbs = {}
    for category, files in all_categories.items():
        for video in files['videos']:
            thumb = get_video_thumb(base_path, category, video)
            if thumb:
                video_thumbs[f"{category}/{video}"] = thumb
    if cat:
        categories = {cat: all_categories[cat]} if cat in all_categories else {}
    else:
        categories = all_categories
    return render_template('album.html', categories=categories, video_thumbs=video_thumbs)

@app.route('/video/<category>/<filename>')
def video_player(category, filename):
    return render_template('video_player.html', category=category, filename=filename)

@app.route('/video_thumb/<thumb_name>')
def video_thumb(thumb_name):
    # 直接返回封面图片
    return send_from_directory(THUMB_DIR, thumb_name)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
