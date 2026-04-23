import os
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import get_valid_filename
import json
import tempfile
import shutil

import config
from transform.animeganv2 import batch_convert
from crawler.img_download import fn as crawler_fn
from transform.animeganv2 import fn as transform_fn

# 从配置文件加载默认路径（绝对路径用于后端处理）
DEFAULT_UPLOAD_DIR = config.DEFAULT_UPLOAD_DIR
DEFAULT_OUTPUT_DIR = config.DEFAULT_OUTPUT_DIR

# 相对路径用于前端显示
RELATIVE_UPLOAD_DIR = config.RELATIVE_UPLOAD_DIR
RELATIVE_OUTPUT_DIR = config.RELATIVE_OUTPUT_DIR


def media_url_for_path(path):
    """Return a served media URL when the file is inside MEDIA_ROOT."""
    try:
        relative_path = Path(path).resolve().relative_to(Path(settings.MEDIA_ROOT).resolve())
    except ValueError:
        return None
    return settings.MEDIA_URL + str(relative_path).replace("\\", "/")


def index(request):
    """首页"""
    return render(request, 'myapp/index.html')


def page1_crawler(request):
    """页面1：图片爬取"""
    context = {
        'default_save_dir': RELATIVE_UPLOAD_DIR
    }

    if request.method == 'POST':
        url = request.POST.get('url', '').strip()
        save_dir_input = request.POST.get('save_dir', RELATIVE_UPLOAD_DIR).strip()
        custom_headers = request.POST.get('custom_headers', '').strip()

        # 将相对路径转换为绝对路径
        save_dir = config.get_absolute_path(save_dir_input)

        if not url:
            context['error'] = '请输入有效的URL'
            context['url'] = url
            context['save_dir'] = save_dir_input
            context['custom_headers'] = custom_headers
            return render(request, 'myapp/page1_crawler.html', context)

        try:
            # 解析自定义 headers
            headers_dict = {}
            if custom_headers:
                for line in custom_headers.split('\n'):
                    line = line.strip()
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers_dict[key.strip()] = value.strip()

            # 确保目录存在
            os.makedirs(save_dir, exist_ok=True)

            # 执行爬取（传入自定义 headers）
            count, urls = crawler_fn(url, save_dir, headers_dict)

            context['success'] = True
            context['message'] = f'成功下载 {count} 张图片到 {save_dir_input}'
            context['found_count'] = len(urls)
            context['download_count'] = count
            context['url'] = url
            context['save_dir'] = save_dir_input
            context['custom_headers'] = custom_headers

        except Exception as e:
            context['error'] = f'爬取失败: {str(e)}'
            context['url'] = url
            context['save_dir'] = save_dir_input
            context['custom_headers'] = custom_headers

    return render(request, 'myapp/page1_crawler.html', context)


def page2_transform(request):
    """页面2：风格转换"""
    context = {
        'default_input_dir': RELATIVE_UPLOAD_DIR,
        'default_output_dir': RELATIVE_OUTPUT_DIR
    }

    if request.method == 'POST':
        action = request.POST.get('action', 'folder')  # 'folder' 或 'single'

        if action == 'folder':
            # 文件夹批量转换
            input_dir_input = request.POST.get('input_dir', RELATIVE_UPLOAD_DIR).strip()
            output_dir_input = request.POST.get('output_dir', RELATIVE_OUTPUT_DIR).strip()

            # 将相对路径转换为绝对路径
            input_dir = config.get_absolute_path(input_dir_input)
            output_dir = config.get_absolute_path(output_dir_input)

            try:
                os.makedirs(output_dir, exist_ok=True)
                success_count, total = transform_fn(input_dir, output_dir)

                context['success'] = True
                context['message'] = f'转换完成！成功 {success_count}/{total} 张'
                context['converted'] = success_count
                context['total'] = total
                context['input_dir'] = input_dir_input
                context['output_dir'] = output_dir_input

            except Exception as e:
                context['error'] = f'转换失败: {str(e)}'

        elif action == 'single':
            # 单张图片上传转换
            if 'image' in request.FILES:
                image = request.FILES['image']
                output_dir_input = request.POST.get('output_dir', RELATIVE_OUTPUT_DIR).strip()

                # 将相对路径转换为绝对路径
                output_dir = config.get_absolute_path(output_dir_input)

                try:
                    os.makedirs(output_dir, exist_ok=True)

                    # 直接传递文件对象，不保存原始图片
                    output_name = f"anime_{get_valid_filename(image.name)}"
                    output_path = os.path.join(output_dir, output_name)
                    result = transform_single_image(image, output_path)

                    if result:
                        context['success'] = True
                        context['message'] = f'单张图片转换成功！'
                        context['output_image'] = output_name
                        context['output_image_url'] = media_url_for_path(output_path)
                        context['output_dir'] = output_dir_input
                    else:
                        context['error'] = '转换失败，请检查图片格式'

                except Exception as e:
                    context['error'] = f'单张转换失败: {str(e)}'
            else:
                context['error'] = '请选择要上传的图片'

    return render(request, 'myapp/page2_transform.html', context)

def transform_single_image(image_file, output_path):
    """
    单张图片转换 - 直接从内存读取，不保存原始图片
    image_file: Django 的 UploadedFile 对象
    """
    # 创建临时目录（只用于转换过程）
    temp_input_dir = tempfile.mkdtemp()
    temp_output_dir = tempfile.mkdtemp()

    try:
        # 将上传的文件保存到临时目录（转换需要）
        filename = image_file.name
        temp_input_path = os.path.join(temp_input_dir, filename)

        # 写入临时文件
        with open(temp_input_path, 'wb') as f:
            for chunk in image_file.chunks():
                f.write(chunk)

        # 调用批量转换
        success, total = batch_convert(temp_input_dir, temp_output_dir)

        # 复制结果到目标路径
        if success > 0:
            result_file = os.path.join(temp_output_dir, filename)
            if os.path.exists(result_file):
                shutil.copy(result_file, output_path)
                return output_path

        return None

    finally:
        # 清理所有临时目录（原始图片和中间文件都不保留）
        shutil.rmtree(temp_input_dir, ignore_errors=True)
        shutil.rmtree(temp_output_dir, ignore_errors=True)


@csrf_exempt
@require_http_methods(["POST"])
def api_crawler(request):
    """API接口：爬取图片"""
    try:
        data = json.loads(request.body)
        url = data.get('url')
        save_dir_input = data.get('save_dir', RELATIVE_UPLOAD_DIR)

        # 将相对路径转换为绝对路径
        save_dir = config.get_absolute_path(save_dir_input)

        if not url:
            return JsonResponse({'success': False, 'error': 'URL不能为空'})

        os.makedirs(save_dir, exist_ok=True)
        count, urls = crawler_fn(url, save_dir)

        return JsonResponse({
            'success': True,
            'downloaded': count,
            'found': len(urls),
            'save_dir': save_dir_input
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_transform(request):
    """API接口：风格转换"""
    try:
        data = json.loads(request.body)
        input_dir_input = data.get('input_dir', RELATIVE_UPLOAD_DIR)
        output_dir_input = data.get('output_dir', RELATIVE_OUTPUT_DIR)

        # 将相对路径转换为绝对路径
        input_dir = config.get_absolute_path(input_dir_input)
        output_dir = config.get_absolute_path(output_dir_input)

        os.makedirs(output_dir, exist_ok=True)
        success_count, total = transform_fn(input_dir, output_dir)

        return JsonResponse({
            'success': True,
            'converted': success_count,
            'total': total,
            'output_dir': output_dir_input
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
