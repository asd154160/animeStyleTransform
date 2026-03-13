一个基于 AnimeGANv2 实现的动漫风格转换项目，集成图片爬虫模块和 Django 网页交互界面，支持将普通图片转换成多种动漫风格（如人脸彩绘、Paprika 风格等）

核心功能
图片爬虫：自动爬取网络图片，为风格转换提供素材
动漫风格转换：基于 AnimeGANv2 模型，支持 Celeba、Face Paint v1/v2、Paprika 等多种动漫风格
网页交互：Django 搭建的可视化界面，支持图片上传、风格选择、转换结果预览
数据管理：本地存储爬取的图片和转换后的结果，方便后续使用

环境要求
Python 3.8+

快速开始


1. 克隆仓库
git clone https://github.com/asd154160/animeStyleTransform.git
cd animeStyleTransform

2. 安装依赖

用清华镜像源加速安装（国内必加，避免超时）

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

(电脑有N卡可以安装GUP版本torch加速  
pip install torch>=1.7.1 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118)

验证

python -c "import requests, torchvision, bs4, cv2, torch, numpy, PIL, tqdm; print('所有依赖安装成功！')"

3. 运行项目
# 项目根目录下直接运行，无需切换目录 或者 Pycharm里运行manage.py
python manage.py runserver
运行成功后，打开浏览器访问：http://127.0.0.1:8000/即可通过可视化网页完成「图片上传 → 风格选择 → 动漫风格转换」全流程。

📂 项目结构
plaintext

animeStyleTransform/

├── animeStyleTransform/  # Django 项目核心配置

├── crawler/              # 图片爬虫模块

├── media/uploads/        # 爬取/上传的图片存储目录

├── myapp/                # Django 业务逻辑模块（网页界面）

├── transform/            # 动漫风格转换核心（AnimeGANv2）

│   ├── weights/          # 预训练模型权重

│   ├── animeganv2.py     # 转换模块

│   └── requirements.txt  # 依赖清单

├── db.sqlite3            # Django 默认数据库

└── manage.py             # Django 项目管理入口
