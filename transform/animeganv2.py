import os
import sys
import cv2
import torch
import numpy as np
from PIL import Image
from tqdm import tqdm

'''
注：animeganv2 模型源码在 GitHub：https://github.com/bryandlee/animegan2-pytorch

访问：https://github.com/bryandlee/animegan2-pytorch
把下载的 animegan2-pytorch-main.zip 解压到你的项目目录
此py文件要在animegan2-pytorch-main/animegan2-pytorch-main/animeganv2.py

animegan2-pytorch/raw/main/weights/paprika.pt
把 paprika.pt 文件放到你的项目目录下
'''

# 添加源码路径到系统环境
sys.path.append(os.path.join(os.path.dirname(__file__), "animegan2-pytorch-main"))
from transform.model import Generator  # 直接从源码导入模型


# INPUT_DIR = r"D:\pycharm\code\animeStyleTransform\media\uploads"        # 爬虫图片文件夹
# OUTPUT_DIR = r"D:\pycharm\code\animeStyleTransform\media\outputs" # 转换后保存路径
MODEL_PATH = r"D:\pycharm\code\animeStyleTransform\transform\weights\paprika.pt" # 下载的权重文件路径
USE_GPU = True  # 有GPU设为True，无则保持False

# 图片预处理/后处理
def preprocess(img, size=512):
    # 预处理图片为模型输入格式
    img = img.resize((size, size), Image.LANCZOS)
    img = np.array(img).astype(np.float32) / 127.5 - 1.0
    img = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)
    return img

def postprocess(img):
    # 把模型输出转回图片格式
    img = img.squeeze(0).permute(1, 2, 0).cpu().numpy()
    img = (img + 1.0) * 127.5
    img = img.astype(np.uint8)
    return img

# 批量转换主函数
def batch_convert(input_dir, output_dir):
    # 创建输出文件夹
    os.makedirs(output_dir, exist_ok=True)

    # 加载模型
    device = torch.device("cuda" if USE_GPU and torch.cuda.is_available() else "cpu")
    model = Generator()
    # 加载权重时忽略不匹配的参数（解决running_mean/running_var缺失问题）
    state_dict = torch.load(MODEL_PATH, map_location=device)
    model.load_state_dict(state_dict, strict=False)  # strict=False 关键！
    model.to(device)
    model.eval()

    # 获取所有图片
    img_ext = ['.jpg', '.jpeg', '.png', '.webp', '.bmp']
    img_files = [f for f in os.listdir(input_dir) if os.path.splitext(f)[1].lower() in img_ext]

    if not img_files:
        print(f"输入文件夹 {input_dir} 无图片")
        return 0, 0

    success_count = 0  # 记录成功数量
    total_count = len(img_files)

    print(f"找到 {len(img_files)} 张图片，使用 {device} 转换...")
    with torch.no_grad():  # 禁用梯度，节省内存
        for filename in tqdm(img_files):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            # 读取图片
            try:
                img = Image.open(input_path).convert('RGB')

                # 预处理 + 风格转换
                img_tensor = preprocess(img).to(device)
                output_tensor = model(img_tensor)

                # 后处理 + 保存
                output_img = postprocess(output_tensor)
                output_img = cv2.cvtColor(output_img, cv2.COLOR_RGB2BGR)  # 适配OpenCV保存
                cv2.imwrite(output_path, output_img)
                success_count += 1  # 成功计数+1

            except Exception as e:
                print(f"跳过损坏图片：{filename} ({str(e)[:30]})")
                continue
    print(f"\n转换完成！所有图片已保存到：{os.path.abspath(output_dir)}")
    return success_count, total_count  # 返回元组 (成功数, 总数)
def fn(input_dir=r"D:\pycharm\code\animeStyleTransform\media\uploads", output_dir=r"D:\pycharm\code\animeStyleTransform\media\outputs"):
    return batch_convert(input_dir,output_dir)

