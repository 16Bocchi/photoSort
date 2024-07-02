import os
from datetime import datetime
from tkinter import filedialog
import tkinter as tk
import shutil
from PIL import Image

isSplit = True


def splitRaw():
    global isSplit
    isSplit = not isSplit
    if isSplit:
        splitBut.config(text='Separate Raws')
    else:
        splitBut.config(text='Keep Raws Together')
    print(isSplit)


def selectFolder():
    global srcPath
    srcPath = tk.filedialog.askdirectory()
    print(srcPath)


def selectDest():
    global destPath
    destPath = tk.filedialog.askdirectory()
    print(destPath)


def getDate(filePath):
    im = Image.open(filePath)
    exifData = im.getexif()
    createDate = exifData.get(36867)
    if createDate:
        return datetime.strptime(createDate, '%Y:%m:%d')


def moveItems(src, dest, split):
    if split:
        print('Moving Raws')
        for root, dirs, files in os.walk(src):
            for file in files:
                filePath = os.path.join(root, file)
                createDate = getDate(filePath)
                if createDate:
                    year = createDate.strftime('%Y')
                    month = createDate.strftime('%m')
                    day = createDate.strftime('%d')
                    if 'raf' in file.lower():
                        destDir = os.path.join(dest, year, month, day, 'raw')
                    else:
                        destDir = os.path.join(dest, year, month, day, 'jpeg')
                    os.makedirs(destDir, exist_ok=True)
                    shutil.copy(filePath, os.path.join(destDir, file))
                else:
                    destDir = os.path.join(dest, "noDate")
                    os.makedirs(destDir, exist_ok=True)
                    shutil.copy(filePath, os.path.join(destDir, file))
    else:
        print('Moving Both')
        for root, dirs, files in os.walk(src):
            for file in files:
                filePath = os.path.join(root, file)
                createDate = getDate(filePath)
                if createDate:
                    year = createDate.strftime('%Y')
                    month = createDate.strftime('%m')
                    day = createDate.strftime('%d')
                    destDir = os.path.join(dest, year, month, day)
                    os.makedirs(destDir, exist_ok=True)
                    shutil.copy(filePath, os.path.join(destDir, file))
                else:
                    destDir = os.path.join(dest, "noDame")
                    os.makedirs(destDir, exist_ok=True)
                    shutil.copy(filePath, os.path.join(destDir, file))


window = tk.Tk()
window.title('File Sorter')
srcBut = tk.Button(window, text='Select Source Folder', command=selectFolder)
srcBut.pack()
destBut = tk.Button(window, text='Select Dest Folder', command=selectDest)
destBut.pack()

splitBut = tk.Button(window, text="Separate Raws", command=splitRaw)
splitBut.pack()

goBut = tk.Button(window, text='Sort Files',
                  command=lambda: moveItems(srcPath, destPath, isSplit))
goBut.pack()
window.mainloop()
