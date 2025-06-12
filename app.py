from flask import Flask, render_template, send_from_directory, request, redirect, url_for, flash, send_file
import os
import json
import sys
import cv2
from werkzeug.utils import secure_filename
from PIL import Image
import threading
import time
from urllib.parse import quote

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # 用于flash消息

CONFIG_PATH = 'config.json'

def get_base_path():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config.get('base', '')

def get_thumb_dir():
    base_path = get_base_path()
    if not base_path:
        return os.path.abspath('video_thumbs')
    return os.path.join(base_path, 'video_thumbs')

def get_image_ratio(image_path):
    """
    获取图片的长宽比，返回最接近的比例类型
    """
    try:
        with Image.open(image_path) as img:
            # 使用 PIL 的内置方法处理 EXIF 旋转
            from PIL import ImageOps
            img = ImageOps.exif_transpose(img)
            
            width, height = img.size
            ratio = width / height
            
            # 定义标准比例和容差
            ratios = {
                '1-1': 1.0,      # 正方形 1:1
                '4-3': 4/3,      # 1.333 横版
                '3-4': 3/4,      # 0.75 竖版
                '16-9': 16/9,    # 1.778 横版
                '9-16': 9/16,    # 0.5625 竖版
                '3-2': 3/2,      # 1.5 横版
                '2-3': 2/3       # 0.667 竖版
            }
            
            # 找到最接近的比例
            closest_ratio = min(ratios.items(), key=lambda x: abs(x[1] - ratio))
            
            # 调试信息
            print(f"图片 {image_path}: {width}x{height}, 比例: {ratio:.3f}, 分类为: {closest_ratio[0]}")
            
            return closest_ratio[0]
    except Exception as e:
        print(f"无法读取图片尺寸: {image_path} {e}")
        return '4-3'  # 默认返回4:3

def get_media_files(base_path, current_path=""):
    """
    获取媒体文件，支持多层目录结构
    current_path: 当前相对于base_path的路径
    """
    categories = {}
    full_path = os.path.join(base_path, current_path) if current_path else base_path
    
    if not os.path.exists(full_path):
        return categories
        
    for item in os.listdir(full_path):
        if item == 'video_thumbs':
            continue  # 排除video_thumbs文件夹
        item_path = os.path.join(full_path, item)
        relative_path = os.path.join(current_path, item) if current_path else item
        
        if os.path.isdir(item_path):
            images = []
            videos = []
            subdirs = []
            
            # 检查当前目录下的文件
            for file in os.listdir(item_path):
                file_path = os.path.join(item_path, file)
                if os.path.isfile(file_path):
                    ext = os.path.splitext(file)[1].lower()
                    if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                        # 获取图片比例信息
                        image_path = os.path.join(item_path, file)
                        ratio = get_image_ratio(image_path)
                        images.append({
                            'filename': file,
                            'ratio': ratio
                        })
                    elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                        videos.append(file)
                elif os.path.isdir(file_path):
                    subdirs.append(file)
            
            # 按比例分组排序图片
            images.sort(key=lambda x: x['ratio'])
            
            categories[relative_path] = {
                'images': images,
                'videos': videos,
                'subdirs': subdirs,
                'display_name': item
            }
    
    return categories

def ensure_thumb_dir():
    thumb_dir = get_thumb_dir()
    if not os.path.exists(thumb_dir):
        os.makedirs(thumb_dir)

def get_video_thumb(base_path, category, video_filename):
    """
    截取视频第一帧作为封面，返回封面图片的相对路径
    """
    ensure_thumb_dir()
    thumb_dir = get_thumb_dir()
    # 对category和文件名做URL安全编码，避免中文或特殊字符导致文件名异常
    safe_category = quote(category, safe='')
    safe_filename = quote(os.path.splitext(video_filename)[0], safe='')
    video_path = os.path.join(base_path, category, video_filename)
    thumb_name = f"{safe_category}__{safe_filename}.jpg"
    thumb_path = os.path.join(thumb_dir, thumb_name)
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

@app.route('/media/<filename>')
def media_root(filename):
    """处理根目录的媒体文件"""
    base_path = get_base_path()
    safe_filename = secure_filename(filename)
    
    file_path = os.path.join(base_path, safe_filename)
    
    # 确保请求的文件在 base_path 内，防止路径遍历攻击
    if not file_path.startswith(base_path):
        return "Access denied", 403
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return "File not found", 404
    
    return send_from_directory(base_path, safe_filename)

@app.route('/media/<path:category>/<filename>')
def media(category, filename):
    base_path = get_base_path()
    # 构建安全的文件路径 - 支持多层路径
    safe_filename = secure_filename(filename)
    
    # 处理多层分类路径
    category_parts = category.split('/')
    safe_category_parts = [secure_filename(part) for part in category_parts]
    safe_category_path = os.path.join(*safe_category_parts) if safe_category_parts else ''
    
    file_path = os.path.join(base_path, safe_category_path, safe_filename)
    
    # 确保请求的文件在 base_path 内，防止路径遍历攻击
    if not file_path.startswith(base_path):
        return "Access denied", 403
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        return "File not found", 404
    
    # 获取目录和文件名
    dir_path = os.path.dirname(file_path)
    filename = os.path.basename(file_path)
    
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
    
    # 检查根目录是否有媒体文件
    root_files = get_media_files_single_level(base_path, "")
    has_root_media = len(root_files['images']) > 0 or len(root_files['videos']) > 0
    
    # 如果根目录有媒体文件，添加根目录卡片
    if has_root_media:
        covers['__root__'] = root_files['images'][0]['filename'] if root_files['images'] else None
    
    return render_template('nav.html', covers=covers, has_root_media=has_root_media)

def get_media_files_single_level(base_path, current_path=""):
    """
    获取单层目录的媒体文件和子目录
    current_path: 当前相对于base_path的路径
    """
    full_path = os.path.join(base_path, current_path) if current_path else base_path
    
    if not os.path.exists(full_path):
        return {'images': [], 'videos': [], 'subdirs': []}
    
    images = []
    videos = []
    subdirs = []
    
    # 检查当前目录下的文件和子目录
    for item in os.listdir(full_path):
        if item == 'video_thumbs':
            continue  # 排除video_thumbs文件夹
        item_path = os.path.join(full_path, item)
        
        if os.path.isfile(item_path):
            ext = os.path.splitext(item)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
                # 获取图片比例信息
                ratio = get_image_ratio(item_path)
                images.append({
                    'filename': item,
                    'ratio': ratio
                })
            elif ext in ['.mp4', '.avi', '.mov', '.mkv', '.webm']:
                videos.append(item)
        elif os.path.isdir(item_path):
            subdirs.append(item)
    
    # 按比例分组排序图片
    ratio_groups = {}
    for image in images:
        ratio = image['ratio']
        if ratio not in ratio_groups:
            ratio_groups[ratio] = []
        ratio_groups[ratio].append(image)
    
    # 将分组后的图片按比例类型排序
    sorted_ratios = sorted(ratio_groups.keys())
    grouped_images = []
    for ratio in sorted_ratios:
        grouped_images.extend(ratio_groups[ratio])
    
    return {
        'images': grouped_images,
        'images_by_ratio': ratio_groups,
        'videos': videos,
        'subdirs': subdirs
    }

@app.route('/album')
@app.route('/album/<path:category_path>')
def album(category_path=None):
    base_path = get_base_path()
    if not base_path or not os.path.exists(base_path):
        flash('请先配置媒体根目录路径')
        return redirect(url_for('config'))
    
    # 获取请求的分类路径
    cat = request.args.get('cat') or category_path
    
    # 特殊处理根目录
    if cat == '__root__':
        cat = ""
    
    # 获取当前目录的媒体文件和子目录
    current_files = get_media_files_single_level(base_path, cat or "")
    
    # 构建显示用的categories字典
    if cat is not None:  # 包括空字符串的情况（根目录）
        if cat == "":
            display_name = "根目录"
        else:
            display_name = os.path.basename(cat)
        categories = {
            cat or "__root__": {
                'images': current_files['images'],
                'videos': current_files['videos'],
                'subdirs': current_files['subdirs'],
                'display_name': display_name
            }
        }
    else:
        # 根目录情况，检查是否有子目录
        if current_files['subdirs']:
            # 有子目录，显示子目录
            categories = {}
            for subdir in current_files['subdirs']:
                subdir_files = get_media_files_single_level(base_path, subdir)
                categories[subdir] = {
                    'images': subdir_files['images'],
                    'videos': subdir_files['videos'],
                    'subdirs': subdir_files['subdirs'],
                    'display_name': subdir
                }
        else:
            # 没有子目录，直接显示根目录内容
            categories = {
                "__root__": {
                    'images': current_files['images'],
                    'videos': current_files['videos'],
                    'subdirs': current_files['subdirs'],
                    'display_name': "根目录"
                }
            }
    
    # 生成视频封面路径
    video_thumbs = {}
    for category, files in categories.items():
        actual_category = "" if category == "__root__" else category
        for video in files['videos']:
            thumb = get_video_thumb(base_path, actual_category, video)
            if thumb:
                video_thumbs[f"{category}/{video}"] = thumb
    
    # 生成面包屑导航数据
    breadcrumbs = []
    if cat and cat != "":
        path_parts = cat.split('/')
        current_path = ""
        for part in path_parts:
            current_path = current_path + '/' + part if current_path else part
            breadcrumbs.append({
                'name': part,
                'path': current_path
            })
    
    # 获取当前目录的子目录信息（用于显示导航卡片）
    current_subdirs = current_files['subdirs'] if cat is not None else []
    
    return render_template('album.html', 
                         categories=categories, 
                         video_thumbs=video_thumbs,
                         current_path=cat,
                         breadcrumbs=breadcrumbs,
                         subdirs=current_subdirs)

@app.route('/video/<filename>')
def video_player_root(filename):
    """处理根目录的视频文件"""
    return render_template('video_player.html', category='', filename=filename)

@app.route('/video/<path:category>/<filename>')
def video_player(category, filename):
    return render_template('video_player.html', category=category, filename=filename)

@app.route('/video_thumb/<thumb_name>')
def video_thumb(thumb_name):
    # 直接返回封面图片
    thumb_dir = get_thumb_dir()
    return send_from_directory(thumb_dir, thumb_name)

@app.route('/reload_library', methods=['POST'])
def reload_library():
    """重载媒体库，清除缓存"""
    try:
        # 清除视频缩略图缓存
        thumb_dir = get_thumb_dir()
        if os.path.exists(thumb_dir):
            for file in os.listdir(thumb_dir):
                file_path = os.path.join(thumb_dir, file)
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
