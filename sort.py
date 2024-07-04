import os
from datetime import datetime
import tkinter as tk
import shutil
import exiftool
import threading
from concurrent.futures import ThreadPoolExecutor

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
    if not os.path.isfile(filePath):
        raise ValueError(f"File not found: {filePath}")

    try:
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(filePath)
            for d in metadata:
                if 'EXIF:DateTimeOriginal' in d:
                    return datetime.strptime(d['EXIF:DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
        return None
    except Exception as e:
        print(f"Error reading EXIF data from {filePath}: {e}")
        return None


def procFile(filePath, dest, split, updateProg):
    createDate = getDate(filePath)
    if createDate:
        year = createDate.strftime('%Y')
        month = createDate.strftime('%m')
        day = createDate.strftime('%d')
        if split:
            if 'raf' in filePath.lower():
                destDir = os.path.join(dest, year, month, day, 'raw')
            else:
                destDir = os.path.join(dest, year, month, day, 'jpeg')
        else:
            destDir = os.path.join(dest, year, month, day)
    else:
        destDir = os.path.join(dest, "noDate")
    os.makedirs(destDir, exist_ok=True)
    shutil.move(filePath, os.path.join(destDir, os.path.basename(filePath)))
    updateProg()


def moveItems(src, dest, split, statusLabel, progress):
    statusLabel.config(text='Moving...')
    totalFiles = sum([len(files) for _, _, files in os.walk(src)])
    print(f'Total files: {totalFiles}')
    progress['maximum'] = totalFiles
    progress['value'] = 0

    def updateProg():
        progress['value'] += 1
        window.update_idletasks()

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for root, dirs, files in os.walk(src):
            print(f'Processing {root} with {len(files)} files')
            for file in files:
                filePath = os.path.join(root, file)
                futures.append(executor.submit(
                    procFile, filePath, dest, split, updateProg))
        for future in futures:
            future.result()

    print('Done')
    statusLabel.config(text='Done')


def startMoveItems(src, dest, split, statusLabel):
    statusLabel.config(text='Starting')
    threading.Thread(target=moveItems, args=(
        src, dest, split, statusLabel, progress)).start()


window = tk.Tk()
window.title('File Sorter')
srcBut = tk.Button(window, text='Select Source Folder', command=selectFolder)
srcBut.pack()
destBut = tk.Button(window, text='Select Dest Folder', command=selectDest)
destBut.pack()

splitBut = tk.Button(window, text="Separate Raws", command=splitRaw)
splitBut.pack()

goBut = tk.Button(window, text='Sort Files', command=lambda: startMoveItems(
    srcPath, destPath, isSplit, statusLabel))
goBut.pack()

statusLabel = tk.Label(window, text='Waiting...')
statusLabel.pack()

progress = tk.ttk.Progressbar(
    window, orient='horizontal', mode='determinate')
progress.pack(fill=tk.X, padx=10, pady=10)
window.mainloop()
