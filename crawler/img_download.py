import re
import os
import requests
from urllib.parse import urljoin,unquote
from bs4 import BeautifulSoup
import time
import random
from concurrent.futures import ThreadPoolExecutor,as_completed
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 基础请求头，可以选择添加其他参数 cookie,accept-language,referer等
headers = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0",
    }

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def create_re_session():
    session = requests.Session()
    re_strategy=Retry(total=2, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504],allowed_methods=["GET"])
    adapter = HTTPAdapter(max_retries=re_strategy) # 装入适配器
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.headers.update(headers)
    return session

def get_images(url,custom_headers=None):
    # 修复双重编码问题
    url = unquote(url)

    session = create_re_session()
    # 如果有自定义 headers，更新 session
    if custom_headers:
        session.headers.update(custom_headers)
    resp = session.get(url, headers=headers, stream=True, timeout=10)
    resp.raise_for_status()   # stream=True+ 分块写入、timeout超时、raise_for_status错误检测；
    resp.encoding = resp.apparent_encoding or "utf-8"
    soup = BeautifulSoup(resp.text, "lxml")
    base_url = url   # 爬取网站的url
    img_urls = set()   # 图片url集合，集合能去重

    # 1. 爬 img 标签(src / data-src / data-original)
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-original")
        if src:   # 如果不为空，urllib.parse进行补全url路径
            full_url = urljoin(base_url, src.strip())
            if "istockphoto.com" not in full_url:  # 过滤istockphoto外链
                img_urls.add(full_url)

    # 2. 爬 background-image 背景图
    bg_pattern = re.compile(r'background-image:\s*url\(["\']?(.*?)["\']?\)')
    for tag in soup.find_all(style=True):
        style = tag["style"]
        match = bg_pattern.search(style)
        if match:
            bg_url = match.group(1).strip()
            full_url = urljoin(base_url, bg_url.strip())
            if "istockphoto.com" not in full_url:
                img_urls.add(full_url)

    return list(img_urls)

def download_img(img_url, save_dir=os.path.join(BASE_DIR, "media", "uploads")):
    time.sleep(random.uniform(0.01, 0.1)) # 反反爬
    try:
        resp = requests.get(img_url, headers=headers, stream=True, timeout=10)
        resp.raise_for_status()

        # 过滤非图片URL
        content_type = resp.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"非图片URL，跳过：{img_url}")
            return

        # 自动识别图片后缀，设置正确扩展名，避免图片损坏
        content_type = resp.headers.get("Content-Type", "")
        ext = "jpg"
        if "jpeg" in content_type:
            ext = "jpg"
        elif "png" in content_type:
            ext = "png"
        elif "webp" in content_type:
            ext = "webp"
        elif "gif" in content_type:
            ext = "gif"

        # 用哈希当文件名，避免重复/乱码
        filename = f"{hash(img_url)}.{ext}"  # 部分系统不兼容负数可以加入abs()
        path = os.path.join(save_dir, filename)

        with open(path, "wb") as f:
            for chunk in resp.iter_content(1024):  # 防止卡死
                if chunk: # 过滤空字节块
                    f.write(chunk)

        print("已保存:", path)
        return path
    except Exception as e:
        print("下载失败:", img_url, e)
        return None

def batch_download(img_urls, save_dir=os.path.join(BASE_DIR, "media", "uploads")):  #线程池提高效率
    os.makedirs(save_dir, exist_ok=True)
    downloaded = []  # 记录成功下载的图片

    with ThreadPoolExecutor(max_workers=5) as executor:
        # 提交所有任务
        future_to_url = {
            executor.submit(download_img, img_url, save_dir): img_url
            for img_url in img_urls
        }

        # 获取结果
        for future in as_completed(future_to_url):
            img_url = future_to_url[future]
            try:
                result = future.result()  # 获取 download_img 的返回值
                if result:  # 如果返回了路径（成功）
                    downloaded.append(result)
                    print(f"成功下载: {img_url} -> {result}")
                else:
                    print(f"下载失败: {img_url} (返回 None)")
            except Exception as e:
                print(f"下载异常: {img_url}, 错误: {e}")

    print(f"总计: 发现 {len(img_urls)} 张, 成功 {len(downloaded)} 张")

    return downloaded

def fn(target_url, save_dir=os.path.join(BASE_DIR, "media", "uploads"), custom_headers=None):

    # 自定义 headers
    if custom_headers:
        headers.update(custom_headers)  # 更新默认 headers

    image_list = get_images(target_url)
    downloaded_list = batch_download(image_list, save_dir)
    return len(downloaded_list), image_list