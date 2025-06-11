# Lumivault - 个人媒体图书馆

一个基于 Flask 的个人媒体文件管理系统，提供优雅的图片和视频浏览体验。

## 功能特性

### 🖼️ 智能图片管理
- **智能比例识别**：自动识别图片比例（3:4、4:3、16:9、9:16）并优化显示
- **比例分组展示**：相同比例的图片自动分组，提供更整齐的浏览体验
- **图片放大预览**：支持键盘导航和触摸滑动的全屏图片查看
- **懒加载优化**：按需加载图片，提升页面加载速度

### 🎬 视频管理
- **自动缩略图生成**：自动提取视频第一帧作为封面
- **多格式支持**：支持 MP4、AVI、MOV、MKV、WebM 等常见视频格式
- **视频播放器**：内置视频播放页面，支持直接播放

### 🎨 用户体验
- **响应式设计**：完美适配桌面端和移动端
- **深色/浅色主题**：支持主题切换，保护眼睛
- **分类浏览**：按文件夹自动分类，支持图片/视频标签页切换
- **移动端优化**：专为移动设备优化的侧边菜单和触摸操作

### ⚙️ 系统管理
- **媒体库重载**：一键刷新媒体文件和清除缓存
- **服务器重启**：远程重启服务器功能
- **路径配置**：灵活的媒体根目录配置

## 安装要求

```bash
pip install flask opencv-python pillow
```

## 快速开始

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd bighouse
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **运行应用**
   ```bash
   python app.py
   ```

4. **配置媒体路径**
   - 访问 `http://localhost:5000`
   - 点击"配置设置"
   - 输入你的媒体文件根目录路径

### 🐳 使用 Docker 部署

1. **构建镜像**
   ```bash
   docker build -t lumivault .
   ```

2. **运行容器**
   ```bash
   docker run -d \
     -p 5000:5000 \
     -v /你的媒体目录:/app/media \
     -v $(pwd)/config.json:/app/config.json \
     --name lumivault \
     lumivault
   ```

   - `/你的媒体目录` 替换为你本地的媒体文件夹路径
   - `config.json` 可选挂载，首次运行后会自动生成

3. **访问应用**
   - 打开浏览器访问 [http://localhost:5000](http://localhost:5000)

## 目录结构

```
bighouse/
├── app.py                 # 主应用文件
├── config.json           # 配置文件（首次运行后生成）
├── static/               # 静态资源
│   ├── css/
│   │   └── style.css     # 主样式文件
│   └── js/
│       ├── app.js        # 通用功能
│       ├── album.js      # 相册功能
│       └── config.js     # 配置页面功能
├── templates/            # HTML 模板
│   ├── home.html         # 首页
│   ├── nav.html          # 分类导航
│   ├── album.html        # 相册页面
│   ├── config.html       # 配置页面
│   └── video_player.html # 视频播放器
```


## 使用说明

### 媒体文件组织
建议按以下结构组织你的媒体文件：

```
媒体根目录/
├── 分类1/
│   ├── 图片1.jpg
│   ├── 图片2.png
│   └