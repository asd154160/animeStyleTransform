"""
项目配置文件
集中管理所有可配置参数，便于维护和修改
"""

import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent


def get_absolute_path(path):
    """
    将相对路径转换为绝对路径
    如果已经是绝对路径则直接返回
    """
    if os.path.isabs(path):
        return path
    return str(BASE_DIR / path)

# ==================== 媒体文件配置 ====================

MEDIA_DIR = BASE_DIR / "media"
MEDIA_UPLOAD_DIR = MEDIA_DIR / "uploads"
MEDIA_OUTPUT_DIR = MEDIA_DIR / "outputs"

# 确保目录存在
MEDIA_DIR.mkdir(exist_ok=True)
MEDIA_UPLOAD_DIR.mkdir(exist_ok=True)
MEDIA_OUTPUT_DIR.mkdir(exist_ok=True)

# ==================== 风格转换模型配置 ====================

TRANSFORM_DIR = BASE_DIR / "transform"
MODEL_WEIGHTS_DIR = TRANSFORM_DIR / "weights"

# 模型配置
MODEL_CONFIG = {
    "paprika": {
        "name": "Paprika",
        "path": str(MODEL_WEIGHTS_DIR / "paprika.pt"),
        "description": "通用动漫风格"
    },
    "face_paint_512_v1": {
        "name": "Face Paint v1",
        "path": str(MODEL_WEIGHTS_DIR / "face_paint_512_v1.pt"),
        "description": "人像照片"
    },
    "face_paint_512_v2": {
        "name": "Face Paint v2",
        "path": str(MODEL_WEIGHTS_DIR / "face_paint_512_v2.pt"),
        "description": "人像照片"
    },
    "celeba_distill": {
        "name": "Celeba",
        "path": str(MODEL_WEIGHTS_DIR / "celeba_distill.pt"),
        "description": "动漫头像"
    }
}

# 当前使用的模型（默认为 Paprika）
DEFAULT_MODEL = "paprika"

# GPU 配置
USE_GPU = True  # True: 使用 GPU（需要 CUDA），False: 使用 CPU

# 图片预处理配置
IMAGE_SIZE = 512  # 模型输入图片大小
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']

# ==================== 图片爬虫配置 ====================

CRAWLER_DIR = BASE_DIR / "crawler"

# HTTP 请求头
DEFAULT_HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
}

# 下载配置
MAX_WORKERS = 5  # 并发下载线程数
REQUEST_TIMEOUT = 10  # 请求超时时间（秒）
RETRY_COUNT = 2  # 重试次数
RETRY_BACKOFF_FACTOR = 0.3  # 重试间隔因子
RETRY_STATUS_CODES = [429, 500, 502, 503, 504]  # 需要重试的 HTTP 状态码
DOWNLOAD_DELAY_MIN = 0.01  # 下载间隔最小值（秒）
DOWNLOAD_DELAY_MAX = 0.1  # 下载间隔最大值（秒）

# 过滤配置
FILTER_ISTOCKPHOTO = True  # 是否过滤 istockphoto.com 外链

# ==================== Django 配置 ====================

# 相对路径（用于前端显示，相对于项目根目录）
RELATIVE_UPLOAD_DIR = r"media\uploads"
RELATIVE_OUTPUT_DIR = r"media\outputs"

# 默认上传目录（用于后端处理，兼容旧代码）
DEFAULT_UPLOAD_DIR = str(MEDIA_UPLOAD_DIR)
DEFAULT_OUTPUT_DIR = str(MEDIA_OUTPUT_DIR)
