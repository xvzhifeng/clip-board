
from io import BytesIO
from shutil import copy2
from PIL import ImageGrab, Image
from flask import Flask, request

import win32clipboard
import base64
import json
import os
import time
import pyperclip

# 创建一个Flask对象
app = Flask(__name__)
# 指定端口为 1026
port = 1026


@app.route('/')
def index():
    return 'load clipboard'


@app.route('/upload', methods=['POST'])
def copy_remote_clip():
    if request.method == 'POST':
        pyperclip.copy(request.form['data'])
        print(request.form['data'])
    return "success"


@app.route('/upfile', methods=['POST'])
def copy_remote_clip_multi():
    """phone to computer"""
    print(request.method)
    if request.method == 'POST':
        print(request.form['type'])
        if request.form['type'] == 'image':
            file_name = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime())+".png"
            file_resource = request.files.get('file')
            data = json.load(file_resource)
            byte_data = base64.b64decode(data['base64'])
            png = open(f"./data/img/{file_name}", 'wb')
            png.write(byte_data)
            png.close()
            copy_image_to_clipboard(f"./data/img/{file_name}")
        elif request.form['type'] == 'text':
            data = request.form['data']
            pyperclip.copy(data)
            print(data)
        elif request.form['type'] == 'file':
            file_resource = request.files.get('file')
            data = json.load(file_resource)
            print(request.form['name'])
            byte_data = base64.b64decode(data['base64'])
            png = open(f"./data/file/{data['name']}", 'wb')
            png.write(byte_data)
            png.close()
    return "success"


@app.route('/download')
def get_clip():
    """computer to phone"""
    text = pyperclip.paste()
    im = ImageGrab.grabclipboard()
    if text:
        res = {'data': text, 'type': 'text'}
        print(res)
        return res
    elif isinstance(im, Image.Image):
        img = get_base64_image_from_clipboard()
        res = {'data': img, 'type': 'img'}
        print(res)
        return res
    elif isinstance(im, list):
        url_list = []
        ip = get_local_ip()
        for i in im:
            file_name = os.path.basename(i)
            copy2(i, f"./static/data/{file_name}")
            url_list.append(f"http://{ip}:{port}/static/data/{file_name}")

        res = {'data': url_list, 'type': 'file'}
        print(res)
        return res


def get_base64_image_from_clipboard():
    """ gain image base64 in clipboard """
    # 获取剪贴板上的图片
    im = ImageGrab.grabclipboard()
    if isinstance(im, Image.Image):
        print(f"size{im.size},mode{im.mode},format{im.format}")
        # 将图片转为二进制
        output = BytesIO()
        im.save(output, 'png')
        byte_date = output.getvalue()
        # 将二进制图片转为base64
        base64_str = base64.b64encode(byte_date).decode('utf-8')
        return base64_str


def get_local_ip():
    """gain local ip"""
    import socket
    def extract_ip():
        st = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            st.connect(('10.255.255.255', 1))
            IP = st.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            st.close()
        return IP

    return extract_ip()


def file():
    a = ""
    clip = win32clipboard.RegisterClipboardFormat("Preferred DropEffect")
    # 返回的clip 就是我们将要代入GetClipboardData函数的该数据结构的代码
    if win32clipboard.OpenClipboard() == None:
        try:
            # 尝试以文件的格式读取剪贴板内容
            clip_ = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
            print(clip_)
            if clip_ != None:
                # 获取标志位
                a = win32clipboard.GetClipboardData(clip)
                print(a)
        finally:
            win32clipboard.CloseClipboard()
    if a[0] == 2:
        print("剪切")
    elif a[0] == 5:
        print("复制")
    else:
        print(a[0])


def copy_image_to_clipboard(img_path: str):
    import win32clipboard
    from PIL import Image
    from io import BytesIO
    '''输入文件名，执行后，将图片复制到剪切板'''
    image = Image.open(img_path)
    output = BytesIO()
    image.save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close()
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
