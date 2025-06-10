from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash, send_file
import os
import json
import sys
import cv2
from werkzeug.utils import secure_filename
from PIL import Image
import threading
import time

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

def get_image_ratio(image_path):
    """
    获取图片的长宽比，返回最接近的比例类型
    """
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            ratio = width / height
            
            # 定义标准比例和容差
            ratios = {
                '4-3': 4/3,      # 1.333
                '3-4': 3/4,      # 0.75
                '16-9': 16/9,    # 1.778
                '9-16': 9/16     # 0.5625
            }
            
            # 找到最接近的比例
            closest_ratio = min(ratios.items(), key=lambda x: abs(x[1] - ratio))
            return closest_ratio[0]
    except Exception as e:
        print(f"无法读取图片尺寸: {image_path} {e}")
        return '3-4'  # 默认返回3:4

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
                    # 获取图片比例信息
                    image_path = os.path.join(folder_path, file)
                    ratio = get_image_ratio(image_path)
                    images.append({
                        'filename': file,
                        'ratio': ratio
                    })
                elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                    videos.append(file)
            
            # 按比例分组排序图片
            images.sort(key=lambda x: x['ratio'])
            
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
    return render_template('home.html')

@app.route('/vault')
def vault():
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
        covers[cat] = files['images'][0]['filename'] if files['images'] else None
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

@app.route('/reload_library', methods=['POST'])
def reload_library():
    """重载媒体库，清除缓存"""
    try:
        # 清除视频缩略图缓存
        if os.path.exists(THUMB_DIR):
            for file in os.listdir(THUMB_DIR):
                file_path = os.path.join(THUMB_DIR, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        
        # 重新扫描媒体文件
        base_path = get_base_path()
        if base_path and os.path.exists(base_path):
            get_media_files(base_path)
        
        return {'status': 'success', 'message': '媒体库重载成功'}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

@app.route('/restart_server', methods=['POST'])
def restart_server():
    """重启服务器"""
    def restart():
        time.sleep(1)
        # 根据运行环境选择重启方式
        if hasattr(sys, '_MEIPASS'):
            # 如果是打包的exe文件
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            # 如果是Python脚本
            python = sys.executable
            os.execl(python, python, *sys.argv)
    
    try:
        # 在后台线程中重启
        threading.Thread(target=restart, daemon=True).start()
        return {'status': 'success', 'message': '服务器正在重启'}, 200
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
