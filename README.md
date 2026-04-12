# AnimeStyleTransform - 动漫风格图片转换系统

基于 AnimeGANv2 实现的动漫风格转换工具，集成图片爬虫模块和 Django 网页交互界面，支持将普通图片转换成多种精美的动漫风格。

## ✨ 功能特点

- **🕷️ 智能图片爬虫**：自动从指定网页爬取图片素材，支持自定义 HTTP Headers
- **🎨 多种动漫风格**：内置 AnimeGANv2 模型，支持多种动漫风格转换
  - Paprika（帕帕rika风格）
  - Face Paint v1/v2（人脸彩绘风格）
  - Celeba（名人脸风格）
- **🌐 Web 可视化界面**：简洁易用的 Django 网页界面
- **⚡ GPU 加速支持**：支持 CUDA 加速，大幅提升转换速度
- **📦 批量处理**：支持文件夹批量转换，处理效率高
- **🔧 集中配置管理**：所有参数通过 `config.py` 统一管理

## 📂 项目结构

```
animeStyleTransform/
│
├── animeStyleTransform/         # Django 项目核心配置
│   ├── settings.py              # Django 配置文件
│   ├── urls.py                  # URL 路由配置
│   └── wsgi.py / asgi.py       # WSGI/ASGI 应用入口
│
├── myapp/                      # Django 业务应用模块
│   ├── views.py                # 核心业务逻辑（爬虫 + 风格转换）
│   ├── urls.py                 # 应用路由
│   ├── models.py               # 数据库模型
│   ├── admin.py                # Django 后台管理
│   └── templates/              # HTML 模板
│       └── myapp/
│           ├── index.html       # 首页
│           ├── page1_crawler.html   # 图片爬虫页面
│           └── page2_transform.html # 风格转换页面
│
├── crawler/                    # 图片爬虫核心模块
│   └── img_download.py         # 爬虫实现（多线程并发下载）
│
├── transform/                  # 动漫风格转换核心
│   ├── model.py                # AnimeGANv2 生成器模型
│   ├── animeganv2.py           # 风格转换主逻辑
│   ├── weights/               # 预训练模型权重
│   │   ├── paprika.pt
│   │   ├── face_paint_512_v1.pt
│   │   ├── face_paint_512_v2.pt
│   │   └── celeba_distill.pt
│   └── samples/                # 测试样本图片
│
├── media/                      # 媒体文件存储目录
│   ├── uploads/               # 上传/爬取的原始图片
│   └── outputs/               # 转换后的动漫风格图片
│
├── config.py                   # ⭐ 集中配置文件
├── requirements.txt            # 项目依赖清单
├── manage.py                   # Django 项目管理脚本
└── db.sqlite3                  # SQLite 数据库文件
```

## 🛠️ 环境要求

- **Python**: 3.8 或更高版本
- **系统**: Windows / Linux / macOS
- **GPU** (可选): NVIDIA GPU + CUDA 加速（推荐）

## 🚀 快速开始

### 1. 安装依赖

```bash
# 克隆项目（如果从 GitHub 拉取）
git clone https://github.com/asd154160/animeStyleTransform.git
cd animeStyleTransform

# 安装依赖（使用清华镜像源加速，国内推荐）
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 可选：安装 GPU 版本的 PyTorch（大幅提升转换速度）
pip install torch>=1.7.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 2. 验证安装

```bash
python -c "import requests, torchvision, bs4, cv2, torch, numpy, PIL, tqdm; print('✅ 所有依赖安装成功！')"
```

### 3. 启动服务

```bash
# 在项目根目录下运行
python manage.py runserver
```

### 4. 访问 Web 界面

打开浏览器访问：**<http://127.0.0.1:8000/>**

## 📖 使用指南

### 🕷️ 图片爬虫

1. 访问爬虫页面
2. 输入目标网页 URL
3. 选择保存目录（两种方式）：
   - **点击"📂 选择目录"按钮**：弹出系统目录选择器，智能识别并转换路径
   - **手动输入相对路径**：例如 `media\uploads` 或 `media\outputs`
4. 可选：添加自定义 HTTP Headers（如 Cookie、Referer 等）
5. 点击开始爬取
6. 图片自动保存到所选目录

### 🎨 风格转换

#### 批量转换

1. 选择输入目录（两种方式）：
   - **点击"📂 选择目录"按钮**：弹出系统目录选择器
   - **手动输入相对路径**：例如 `media\uploads`
2. 选择输出目录
3. 点击开始转换
4. 等待转换完成

#### 单张上传转换

1. 直接上传单张图片
2. 选择输出目录
3. 点击转换
4. 查看转换结果

## ⚙️ 配置管理

项目使用 `config.py` 集中管理所有配置项。

### 📁 路径配置

#### 绝对路径（后端处理）

```python
BASE_DIR = Path(__file__).resolve().parent  # 项目根目录
MEDIA_UPLOAD_DIR = BASE_DIR / "media" / "uploads"  # D:\pycharm\code\animeStyleTransform\media\uploads
MEDIA_OUTPUT_DIR = BASE_DIR / "media" / "outputs"  # D:\pycharm\code\animeStyleTransform\media\outputs
```

#### 相对路径（前端显示）

```python
# 前端显示的相对路径格式，便于理解和使用
RELATIVE_UPLOAD_DIR = r"media\uploads"    # 前端显示
RELATIVE_OUTPUT_DIR = r"media\outputs"    # 前端显示
```

#### 路径自动转换

```python
def get_absolute_path(path):
    """
    自动将相对路径转换为绝对路径
    - 相对路径：media\uploads
    - 绝对路径：D:\pycharm\code\animeStyleTransform\media\uploads
    """
    if os.path.isabs(path):
        return path
    return str(BASE_DIR / path)
```

### 📂 目录选择器

#### 智能路径识别

- ✅ 支持从系统目录选择器获取的路径
- ✅ 自动识别 `media/uploads`、`media/outputs` 格式
- ✅ 自动转换为 Windows 路径格式（反斜杠）
- ✅ 支持多种路径变体：
  - `media\uploads` → 自动转换为 `D:\...\animeStyleTransform\media\uploads`
  - `animeStyleTransform\uploads` → 自动识别
  - `D:\完整路径\uploads` → 自动提取相对部分

#### 使用方式

```html
<!-- 前端界面 -->
保存目录：[____________________] [📂 选择目录]

<!-- 点击按钮后 -->
1. 弹出系统目录选择对话框
2. 用户选择任意文件
3. 自动识别并转换为相对路径格式
4. 显示成功提示（绿色）
5. 路径自动填充到文本框
```

#### 路径格式说明

| 前端显示（相对路径）                    | 后端处理（绝对路径）                                          |
| ----------------------------- | --------------------------------------------------- |
| `media\uploads`               | `D:\pycharm\code\animeStyleTransform\media\uploads` |
| `media\outputs`               | `D:\pycharm\code\animeStyleTransform\media\outputs` |
| `animeStyleTransform\uploads` | `D:\pycharm\code\animeStyleTransform\uploads`       |

### 🎨 风格转换模型配置

```python
MODEL_CONFIG = {
    "paprika": {
        "name": "Paprika",
        "path": "transform/weights/paprika.pt",
        "description": "通用动漫风格"
    },
    "face_paint_512_v1": {
        "name": "Face Paint v1",
        "path": "transform/weights/face_paint_512_v1.pt",
        "description": "人像照片"
    },
    # ... 其他模型
}

# 切换默认模型
DEFAULT_MODEL = "paprika"  # 改为 "face_paint_512_v1" 等

# GPU 配置
USE_GPU = True  # True: GPU, False: CPU
```

### 🕷️ 爬虫配置

```python
MAX_WORKERS = 5              # 并发下载线程数
REQUEST_TIMEOUT = 10          # 请求超时（秒）
RETRY_COUNT = 2              # 重试次数
DOWNLOAD_DELAY_MIN = 0.01    # 下载延迟范围
DOWNLOAD_DELAY_MAX = 0.1
FILTER_ISTOCKPHOTO = True    # 是否过滤外链
```

### 常用配置示例

```python
# 启用 CPU 模式（无 GPU 时）
USE_GPU = False

# 增加爬虫并发数
MAX_WORKERS = 10

# 调整下载延迟（反爬策略）
DOWNLOAD_DELAY_MIN = 0.5
DOWNLOAD_DELAY_MAX = 2.0

# 禁用外链过滤
FILTER_ISTOCKPHOTO = False
```

## 🔧 模型配置说明

预训练模型权重存放在 `transform/weights/` 目录：

| 模型文件                   | 风格      | 适用场景   |
| ---------------------- | ------- | ------ |
| `paprika.pt`           | Paprika | 通用动漫风格 |
| `face_paint_512_v1.pt` | 人脸彩绘 v1 | 人像照片   |
| `face_paint_512_v2.pt` | 人脸彩绘 v2 | 人像照片   |
| `celeba_distill.pt`    | Celeba  | 动漫头像   |

如需使用其他风格，请从 [AnimeGANv2 GitHub](https://github.com/bryandlee/animegan2-pytorch) 下载对应权重文件。

## 🌐 API 接口

项目提供 RESTful API 接口：

### 爬虫 API

```http
POST /api/crawler/
Content-Type: application/json

{
    "url": "https://example.com",
    "save_dir": "media/uploads"
}
```

**响应示例：**

```json
{
    "success": true,
    "downloaded": 15,
    "found": 20,
    "save_dir": "media/uploads"
}
```

### 转换 API

```http
POST /api/transform/
Content-Type: application/json

{
    "input_dir": "media/uploads",
    "output_dir": "media/outputs"
}
```

**响应示例：**

```json
{
    "success": true,
    "converted": 10,
    "total": 12,
    "output_dir": "media/outputs"
}
```

## 📦 依赖列表

```
# Django Web Framework
django==3.2

# Deep Learning & Image Processing
torch>=1.7.1
torchvision
opencv-python>=4.5.0
numpy>=1.20.0
Pillow>=9.0.0

# Web Crawling
requests>=2.25.0
beautifulsoup4>=4.9.0
lxml>=4.6.0

# Utilities
tqdm>=4.60.0
```

#### 常见问题

**Q: 为什么选择目录后路径没有自动填充？**

- **原因**：某些浏览器由于安全限制，无法获取完整的本地路径
- **解决**：
  1. 查看右上角的橙色警告提示
  2. 根据提示手动输入相对路径（如 `media\uploads`）
  3. 确保项目目录结构正确

**Q: 浏览器不支持目录选择器？**

- **支持**：Chrome、Edge（推荐使用）
- **部分支持**：Firefox、Safari
- **不支持**：Internet Explorer
- **推荐**：使用 Chrome 或 Edge 浏览器获得最佳体验

## 🐛 常见问题

### Q1: 目录选择器无法获取路径？

- 由于浏览器安全限制，某些情况下无法获取完整路径
- 查看右上角是否有橙色警告提示
- 手动输入相对路径：`media\uploads` 或 `media\outputs`
- 使用 Chrome 或 Edge 浏览器以获得最佳体验

### Q2: 转换速度很慢？

- 确保已安装 GPU 版本的 PyTorch
- 在 `config.py` 中设置 `USE_GPU = True`

### Q3: 图片爬取失败？

- 检查目标网站是否可访问
- 尝试添加自定义 Headers（如 Cookie、User-Agent）
- 部分网站可能有反爬机制，可尝试添加 `Referer` 等字段
- 调整 `DOWNLOAD_DELAY_MIN/MAX` 增加下载间隔

### Q4: 转换效果不理想？

- 建议使用清晰、正面、光照均匀的人像照片
- 不同模型权重适合不同的图片类型
- 可以尝试不同的模型权重找到最佳效果

### Q5: 依赖安装失败？

- 使用国内镜像源：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple`
- 确保 Python 版本 ≥ 3.8
- 某些依赖可能需要编译，确保系统有 C++ 编译器

### Q6: 如何切换不同的动漫风格？

- 编辑 `config.py`
- 修改 `DEFAULT_MODEL` 为其他模型名称（如 `"face_paint_512_v1"`）
- 重启服务

## 📝 项目技术栈

- **后端框架**: Django 3.2
- **深度学习**: PyTorch
- **图像处理**: OpenCV, PIL (Pillow)
- **网络爬虫**: Requests, BeautifulSoup4
- **前端**: HTML5 + CSS3 + 原生 JavaScript

## 🎯 项目亮点

1. **模块化设计**：爬虫、转换、界面分离，代码结构清晰
2. **配置集中管理**：所有参数通过 `config.py` 统一管理，便于维护
3. **易于扩展**：可轻松添加新的模型权重和风格
4. **用户体验**：提供可视化 Web 界面，操作简便
5. **性能优化**：支持 GPU 加速，多线程并发下载，批量处理效率高
6. **API 支持**：提供 RESTful 接口，便于集成和二次开发
7. **智能目录选择**：系统目录选择器 + 相对路径支持 + 自动路径转换

## 📄 License

本项目仅供学习研究使用，请勿用于商业用途。

## 🙏 致谢

- [AnimeGANV2](https://github.com/bryandlee/animegan2-pytorch) - 动漫风格转换模型
- [Django](https://www.djangoproject.com/) - Web 框架
- 所有开源社区的贡献者

