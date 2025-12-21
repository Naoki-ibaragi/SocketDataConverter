"""
メイン処理以外の関数モジュール
"""
import os
import tkinter as tk

#フォルダを探してtargetEntryに書き込む
def search_folder(targetentry):
    here=targetentry.get()
    if not os.path.exists(here):
        here=os.path.abspath(os.path.dirname(__file__))

    window = tk.Tk() #filedialogをトップに持ってくるための設定
    window.wm_attributes('-topmost', 1)
    window.wm_iconbitmap("icon.ico")
    window.withdraw()   # this supress the tk window

    dir=tk.filedialog.askdirectory(parent=window,initialdir=here)
    if dir != "":
        targetentry.delete(0,tk.END)
        targetentry.insert(0,dir)

#ファイルを探してtargetEntryに書き込む
def search_file(targetentry):
    here=os.path.abspath(os.path.dirname(__file__))

    window = tk.Tk() #filedialogをトップに持ってくるための設定
    window.wm_attributes('-topmost', 1)
    window.withdraw()   # this supress the tk window

    dir=tk.filedialog.askopenfilename(parent=window,initialdir=here)
    if dir != "":
        targetentry.delete(0,tk.END)
        targetentry.insert(0,dir)

