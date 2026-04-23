# AnimeStyleTransform

AnimeStyleTransform 是一个基于 Django 和 AnimeGANv2 的本地图片处理工作台。项目包含网页图片爬取、批量动漫风格转换、单张上传转换和 REST API，适合在本机快速整理素材并生成动漫风格图片。

## 主要功能

- 网页图片爬取：输入目标 URL，可配置 User-Agent、Referer、Cookie 等请求头。
- 动漫风格转换：内置 AnimeGANv2 权重，支持 Paprika、Face Paint v1/v2、Celeba 等风格。
- 批量处理：读取文件夹中的图片并批量输出转换结果。
- 单张转换：上传一张图片，转换后在页面中预览结果。
- 本地媒体目录：默认使用 `media\uploads` 保存原始图片，使用 `media\outputs` 保存转换结果。
- API 支持：提供 `/api/crawler/` 和 `/api/transform/` 两个 JSON 接口。
- 优化后的前端界面：统一工作台布局、样张展示、分段控件、表单聚焦状态、结果统计和提示浮层。

## 环境要求

- Python 3.10 或更高版本
- Windows、Linux 或 macOS
- 可选：NVIDIA GPU + CUDA，用于提升转换速度

> 说明：当前环境已用 Django 4.2.30 验证通过；`requirements.txt` 允许 Django 4.2 到 5.2 版本范围。

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

如果需要安装 CUDA 版本的 PyTorch，请按本机 CUDA 版本选择对应安装命令，例如：

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

国内网络环境可临时使用镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 检查项目

```bash
python manage.py check
```

### 3. 启动服务

```bash
python manage.py runserver
```

浏览器打开：

```text
http://127.0.0.1:8000/
```

## 页面说明

### 工作台

首页展示项目流程、默认目录和 AnimeGANv2 转换样张。样张来自 `transform\samples\compare`，已复制到 Django app 静态目录 `myapp\static\myapp\images` 供页面使用。

### 图片爬取

1. 打开 `http://127.0.0.1:8000/crawler/`
2. 输入目标网页 URL。
3. 保存目录默认使用 `media\uploads`，也可以手动输入其他路径。
4. 如目标站点需要，可填写自定义请求头。
5. 点击开始爬取，页面会显示发现数量和成功下载数量。

### 风格转换

1. 打开 `http://127.0.0.1:8000/transform/`
2. 选择“文件夹批量”或“单张上传”模式。
3. 批量模式默认从 `media\uploads` 读取，输出到 `media\outputs`。
4. 单张模式上传图片后会保存为 `anime_原文件名`。
5. 如果结果文件位于 Django `MEDIA_ROOT` 内，页面会直接显示预览。

## 配置

主要配置集中在 `config.py`。

```python
RELATIVE_UPLOAD_DIR = r"media\uploads"
RELATIVE_OUTPUT_DIR = r"media\outputs"
DEFAULT_MODEL = "paprika"
USE_GPU = True
IMAGE_SIZE = 512
MAX_WORKERS = 5
REQUEST_TIMEOUT = 10
```

常用调整：

- 无 CUDA 环境时设置 `USE_GPU = False`。
- 切换模型时修改 `DEFAULT_MODEL`，例如 `"face_paint_512_v1"`。
- 爬取速度或稳定性不理想时调整 `MAX_WORKERS`、`DOWNLOAD_DELAY_MIN`、`DOWNLOAD_DELAY_MAX`。

## 模型权重

权重文件存放在 `transform\weights`。

| 文件 | 风格 | 适用场景 |
| --- | --- | --- |
| `paprika.pt` | Paprika | 通用动漫风格 |
| `face_paint_512_v1.pt` | Face Paint v1 | 人像照片 |
| `face_paint_512_v2.pt` | Face Paint v2 | 人像照片 |
| `celeba_distill.pt` | Celeba | 头像类图片 |

如需添加新权重，请放入 `transform\weights`，并在 `config.py` 的 `MODEL_CONFIG` 中登记。

## API

### 爬取图片

```http
POST /api/crawler/
Content-Type: application/json

{
  "url": "https://example.com",
  "save_dir": "media/uploads"
}
```

响应示例：

```json
{
  "success": true,
  "downloaded": 15,
  "found": 20,
  "save_dir": "media/uploads"
}
```

### 批量转换

```http
POST /api/transform/
Content-Type: application/json

{
  "input_dir": "media/uploads",
  "output_dir": "media/outputs"
}
```

响应示例：

```json
{
  "success": true,
  "converted": 10,
  "total": 12,
  "output_dir": "media/outputs"
}
```

## 项目结构

```text
animeStyleTransform/
├── animeStyleTransform/          # Django 项目配置
├── myapp/
│   ├── static/myapp/images/      # 前端样张静态资源
│   ├── templates/myapp/          # 页面模板
│   ├── urls.py
│   └── views.py
├── crawler/                      # 图片爬取模块
├── transform/                    # AnimeGANv2 模型与转换逻辑
│   ├── weights/                  # 预训练权重
│   └── samples/                  # 示例图片
├── media/
│   ├── uploads/                  # 原始图片
│   └── outputs/                  # 转换结果
├── config.py
├── manage.py
├── requirements.txt
└── README.md
```

## 常见问题

### 目录选择后没有自动填充路径

浏览器出于安全原因通常不会暴露完整本地路径。可以直接手动输入：

```text
media\uploads
media\outputs
```

### 转换速度慢

- 确认安装了匹配 CUDA 的 PyTorch。
- 在 `config.py` 中设置 `USE_GPU = True`。
- 如果没有 GPU，设置 `USE_GPU = False`，避免 CUDA 初始化问题。

### 爬取失败

- 确认目标页面可以正常访问。
- 尝试添加 User-Agent、Referer 或 Cookie。
- 降低并发数或增加下载延迟，避免触发反爬策略。

### 页面样式没有更新

清理浏览器缓存后刷新。Django app 静态资源来自 `myapp\static`，媒体文件来自 `media`，两者已经分开配置。

## 技术栈

- Django 4.2 到 5.2
- PyTorch / Torchvision
- OpenCV
- Pillow
- Requests
- BeautifulSoup4
- 原生 HTML、CSS、JavaScript

## License

本项目仅供学习研究使用，请勿用于商业用途。

## 致谢

- [AnimeGANv2](https://github.com/bryandlee/animegan2-pytorch)
- [Django](https://www.djangoproject.com/)
