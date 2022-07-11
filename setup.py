import tkinter as tk
import tkinter.filedialog as tk_filedialog
import os
import zipfile
import requests
from tqdm import tqdm

DOWNLOAD_URL = 'https://files.catbox.moe/2ig7dp.zip'

def install(path):
    if not os.path.exists(path): os.mkdir(f'{path}')
    if not os.path.exists(f'{path}\\temp'): os.mkdir(f'{path}\\temp')

    # 下载并解压
    stream = requests.get(DOWNLOAD_URL, stream=True)
    with open(f'{path}\\temp\\temp.zip', 'wb') as file, tqdm(
        desc='temp.zip',
        total=int(stream.headers.get('content-length', 0)),
        unit='iB',
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for data in stream.iter_content(chunk_size=1024):
            size = file.write(data)
            bar.update(size)

    zipf = zipfile.ZipFile(f'{path}\\temp\\temp.zip', 'r')
    for name in zipf.namelist():
        zipf.extract(name, f'{path}')
    zipf.close()
    stream.close()

    # 添加环境变量
    os.system(f'set path=%path%;{path}')


class Page2:
    def __init__(self, path):
        self.page = tk.Tk()
        self.page.geometry('500x300')
        self.page.title('Rainbow安装程序')
        tk.Label(self.page, text='安装已经完成！').pack()
        install(path)
        self.page.mainloop()


class Page1:
    def next_page(self):
        path = self.path_text.get('1.0', '1.end')
        self.page.destroy()
        Page2(path)

    def __init__(self):
        self.page = tk.Tk()
        self.page.geometry('800x450')
        self.page.title('Rainbow安装程序')

        guis = {
            0: tk.Label(self.page,
                text='欢迎使用Rainbow安装向导',
                font=('', 20, ''),
                pady=50),
            1: tk.Label(self.page,
                text='选择安装的文件夹, 然后点击下一步',
                font=('', 12, ''),
                pady=40),
        }
        for gui in guis.values():
            gui.pack()

        def on_browse_click():
            path = tk_filedialog.askdirectory().replace('/', '\\')
            path = path + '\\Rainbow' if len(path) != 0 and path[-1] != '\\' else path + 'Rainbow'
            self.path_text.delete('1.0', '1.end')
            self.path_text.insert(tk.END, path)

        self.path_text = tk.Text(self.page,
            width=40,
            height=1)
        self.path_text.insert(tk.END, 'C:\\Program Files\\Rainbow')
        self.path_text.place(x=200, y=300)

        self.browse = tk.Button(self.page,
            text='浏览',
            width=10,
            command=on_browse_click)
        self.browse.place(x=500, y=290)

        self.next = tk.Button(self.page,
            text='下一步',
            width=20,
            command=self.next_page)
        self.next.place(x=600, y=400)

        tk.Label(self.page, text='文件会在后台下载, 您可以通过控制台窗口了解下载进度')\
            .place(x=270, y=400)

        self.page.mainloop()


Page1()
