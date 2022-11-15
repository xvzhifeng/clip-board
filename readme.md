## 一、python

[TOC]

### 1、python 粘贴板操作

#### 1.1、win32clipboard

##### 1.1.1、安装 win32clipboard

win32clipboard 集成于 win32api 中，不需要单独安装，直接安装 pywin32 就可以了

```
pip install pywin32
```

##### 1.1.2、复制图片

```python
import win32clipboard
from PIL import Image
from io import BytesIO


def copy_image_to_clipboard(img_path: str):
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
```



#### 1.2、pyperclip (支持文本)

使用方法：

```python
import pyperclip

# 复制
pyperclip.copy(123)
pyperclip.copy('添加到剪切板')
# 粘贴
pyperclip.paste()
```



### 2、图片操作

图像处理是常用的技术，python 拥有丰富的第三方扩展库，Pillow 是 Python3 最常用的图像处理库。

使用 pip 安装 Pillow：

```cmd
pip install pillow
```

本项目使用到的基本操作：

```python
def copy_image_to_clipboard(img_path: str):
    import win32clipboard
    from PIL import Image
    from io import BytesIO
    '''输入文件名，执行后，将图片复制到剪切板'''
    # 给定一个图片的路径，读取图片
    image = Image.open(img_path)
    # 将图片转为二进制流
    output = BytesIO()
    image.save(output, 'BMP')
    data = output.getvalue()[14:]
    output.close()
    # 将图片存储粘帖板
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()
    
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
```



### 3、Flask

使用pip 安装Flask

```cmd
pip install Flask
```

一个最小的 Flask 应用看起来会是这样:

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
```

#### 3.1 配置信息

在app.run()中可以加入配置项目

- host：`0.0.0.0`
- port：`1026`
- debug：`True`

#### 3.2 路由配置

函数加上以下注解，前面的代表匹配的路径，可以指定method。

```python
@app.route('/upfile', methods=['POST'])
def copy_remote_clip_multi():
	pass
```

#### 3.3 获取前端传参

##### 3.3.1 Form表单形式

使用flask的request，获取相关参数：

`request.form['type']`其中type是传参的name，可以根据前端的参数改变。

`request.files.get('file')`可以获取form表单上传的文件，包括文件名和文件的二进制流等信息。

以下是项目中使用到的实例：

```python
from flask import Flask, request

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
```

##### 3.3.2 获取json中的数据

`request.json['key']` 就可以获取到json中的数据了。

#### 3.4  response返回json

##### 3.4.1 可以直接返回字典

在返回字典时，会自动转化为json字符串。

##### 3.4.2 使用json包进行格式化

json模块主要有四个比较重要的函数，分别是：

- `dump` - 将Python对象按照JSON格式序列化到文件中
- `dumps` - 将Python对象处理成JSON格式的字符串
- `load` - 将文件中的JSON数据反序列化成对象
- `loads` - 将字符串的内容反序列化成Python对象



以下是项目中的示例代码

```python
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
```

### 5. 静态文件

在当前flask目录下面，新建static文件，下面的内容就可以直接通过url进行访问，下载等。

### 4、文件操作

#### 4.1 文件复制

shutil模块中有大量的函数可以用来复制文件，这一节将详细介绍这些函数的用法和差异。

##### **1. copyfile函数**

该函数的原型如下：

```javascript
copyfile(src, dst)
```

copyfile函数用于复制文件内容（不包含元数据，如文件的权限）。src参数表示源文件，dst表示目标文件。dst必须是完整的目标文件名。如果src和dst是同一文件，会抛出shutil.Error异常。dst必须是可写的，否则会抛出IOError。如果dst已经存在，该文件会被替换。对于特殊文件，例如字符或块设备和管道不能使用此功能，因为copyfile会打开并阅读文件。

**例子：**

```javascript
from shutil import copyfile
# 相对路径
copyfile("test.txt", "xxxx.txt")   
# 绝对路径
copyfile("/file/test.txt", "/product/product.txt")
```

##### **2. copy函数**

该函数的原型如下：

```javascript
copy(src, dst)
```

copy函数与copyfile函数类似，都是用于复制文件的，但与copyfile函数有如下两点区别：

（1）dst可以是文件，也可以是目录，如果是目录，则目标文件名与原文件名相同；

（2）copy函数不仅会复制文件内容，也会复制文件的权限。但并不会复制其他的状态信息，如最后访问时间，最后修改时间等；

**例子：**

```javascript
from shutil import copy
# dst是目录，会生成/product/test.txt文件
copy("test.txt", "/product")
# det是文件
copy("test.txt", "/product/abcd.txt")
```

##### **3. copy2函数**

与copy函数的功能类似，但除了copy函数的功能外，还会复制文件的状态信息，如最后访问时间，最后修改时间等。类似Linux的cp -p命令。

例子：

```javascript
from shutil import copy2
# dst是目录，会生成/product/test.txt文件
copy2("test.txt", "/product")
# det是文件
copy2("test.txt", "/product/abcd.txt")
```

##### **4. copymode函数**

该函数并不复制文件本身，而是复制文件的访问权限，所以dst必须存在。

**例子：**

```javascript
from shutil import copymode
# /product/xyz.txt必须存在，复制后，会发现test.txt与xyz.txt文件的访问权限相同了
copy2("test.txt", "/product/xyz.txt")
```

**5. copyfileobj函数**

copyfileobj函数的两个参数src和dst并不是字符串形式的文件或目录的路径，而是打开文件的句柄，需要先使用open函数打开文件。

**例子：**

```javascript
file_src = 'test.txt'
# 打开源文件
f_src = open(file_src, 'rb')
file_dest = 'okokok.txt'
# 打开目标文件
f_dest = open(file_dest, 'wb')
from shutil import copyfileobj
# 开始复制文件
copyfileobj(f_src, f_dest)
```

### 5、打包

使用Pyinstaller：

```cmd
# install
pip3 install pyinstaller
```

**总结命令**

Pyinstaller -F setup.py 打包exe

Pyinstaller -F -w setup.py 不带控制台的打包

Pyinstaller -F -i xx.ico setup.py 打包指定exe图标打包

平常我们只需要这三个就好了，足够满足所有需求了。

## 二、iPhone 快捷指令

简介：

快捷指令，可以指定基本流程，包括循环，分支等。还可以发起http请求，对于图片有base64编码，解码等操作。

1、获取剪贴板内容

https://www.icloud.com/shortcuts/bd143fa4bc7545bab98056d50dbce8ab

2、多重上传

https://www.icloud.com/shortcuts/bc511fce95ae434b87af632da4305702

### 【注】：

#### 1、如何执行时不进入快捷指令app。

​		可以在主屏幕上使用组件，在组件中调用快捷指令。

