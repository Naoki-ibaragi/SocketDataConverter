"""
一番トップのメインUIを作るモジュール
"""
import sys
import socket
import logging
import time
import json
import customtkinter
import tkinter as tk
import component.toplevel as toplevel
import threading
import queue
import component.settings as settings
from component.socket_thread import create_socket_thread
from tkinter import messagebox

FONT_TYPE = "meiryo"
BORDER_WIDTH=0.5

#メインクラス
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        print("起動しました")

        # メンバー変数の設定
        self.fonts = (FONT_TYPE, 15)
        # フォームサイズ設定
        self.title(f"SocketDataConverter_{settings.VERSION}")
        self.geometry("1280x650+50+50")
        self.bg_color = self.cget("fg_color") #customtkinterの背景色

        #アドレス設定ファイルの読込
        json_file=open("address_setting.json","r")
        self.address_dict=json.load(json_file)
        json_file.close()

        #別スレッド用のキューの設定
        self.log_queue=queue.Queue() #マージ処理用スレッドからのメッセージ受渡用のキュー
        self.socket_log_queue=queue.Queue() #ソケット通信処理用スレッドからのメッセージ受渡用のキュー

        #クライアントとの接続状態
        self.server_socket=None
        self.connection_status="disconnect"

        # 画面のセットアップをする
        self.setup_form()

        #ログ部分の初期化
        self.after(10,self.update_log)
        self.after(10,self.socket_update_log)

        #socket_threadの初期化
        self.socket_thread=None
        #socket通信用スレッドの停止用Flag
        self.stop_socket_thread_event=threading.Event()

        #マージの成功・失敗結果
        self.mergeResult=(None,"")

        # アプリ終了時のクリーンアップを設定
        # ver0.0.8で追加
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        #ソフト起動時にサーバーを立ち上げる
        create_socket_thread(self)

    # ウィンドウを閉じる際のクリーンアップ処理
    # ver0.0.8で追加
    def on_closing(self):
        """アプリ終了時のリソースクリーンアップ"""
        print("正常終了しました")
        try:
            self.socket_log_message("アプリ終了処理を開始します...")

            # スレッド停止フラグをセット
            self.stop_socket_thread_event.set()

            # ソケットを安全にクローズ
            if hasattr(self, "server_socket") and self.server_socket:
                try:
                    self.server_socket.shutdown(socket.SHUT_RDWR)
                    self.server_socket.close()
                    self.socket_log_message("サーバーソケットを閉じました。")
                except Exception as e:
                    self.socket_log_message(f"ソケットクローズ時エラー: {e}")
                finally:
                    self.server_socket = None

            # スレッドの終了を待機
            if self.socket_thread and self.socket_thread.is_alive():
                self.socket_log_message("ソケットスレッド終了を待機中...")
                self.socket_thread.join(timeout=3)

            # ログハンドラを安全にクローズ
            self.socket_log_message("ログハンドラをクローズします。")
            logging.shutdown()

            self.socket_log_message("アプリケーションを終了します。")
        except Exception as e:
            print(f"終了処理中に例外が発生しました: {e}")
        finally:
            self.destroy()
            sys.exit(0)


    # 画面作成
    def setup_form(self):
        customtkinter.set_appearance_mode("light")  # Modes: system (default), light, dark
        customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        #topのメニューバーの設定
        self.menubar=MenuBar(self)
        self.config(menu=self.menubar)

        #コンポーネント拡大用       
        self.grid_rowconfigure(0,weight=0)
        self.grid_rowconfigure(1,weight=0)
        self.grid_rowconfigure(2,weight=1)
        self.grid_columnconfigure(0,weight=1)

        #ソケット通信情報が入るフレーム
        self.socket_status_frame=StatusFrame(self)
        self.socket_status_frame.grid(row=0,column=0,pady=(0,0),sticky="nsew")

        #機種名・ATP工注・スタートボタン・処理ログが入るフレーム
        self.top_frame=TopFrame(self)
        self.top_frame.grid(row=1,column=0,pady=(0,0),sticky="nsew")

        #各測定結果とULDのFTP関連設定が入るフレーム
        self.bottom_frame=BottomFrame(self)
        self.bottom_frame.grid(row=2,column=0,pady=(0,0),sticky="nsew")

    #socket通信時エントリー入力用
    def setEntryItem(self,entry,item):
        entry.delete(0,tk.END)
        entry.insert(0,item)

    #socket通信確立時StatusFrameの内容変更
    def setSocketInfo(self,dict):
        status=dict["status"] #接続中か未か
        server_ip=dict["server_ip"] 
        server_port=dict["server_port"]
        client_ip=dict["client_ip"] 
        client_port=dict["client_port"]

        if status=="connect":
            self.connection_status="connect"
            #通信状態の表示を緑にする
            self.socket_status_frame.socket_status_label.configure(
                text=f"ソケット通信状態 : 通信確立済",
            )
            self.socket_status_frame.socket_status_canvas.itemconfig(self.socket_status_frame.socket_status_circle,fill="green")
            self.socket_status_frame.SocketInfoLabel.configure(
                text=f"server socket@{server_ip}:{server_port}, client socket@{client_ip}:{client_port}",
            )
        elif status=="disconnect":
            self.connection_status="disconnect"
            #通信状態の表示を赤にする
            self.socket_status_frame.socket_status_label.configure(
                text=f"ソケット通信状態 : 通信未確立",
            )
            self.socket_status_frame.socket_status_canvas.itemconfig(self.socket_status_frame.socket_status_circle,fill="yellow")
            self.socket_status_frame.SocketInfoLabel.configure(
                text=f"server socket@{server_ip}:{server_port}, client socket@{client_ip}:{client_port}",
            )
        elif status=="error":
            self.connection_status="error"
            #通信状態の表示を赤にする
            self.socket_status_frame.socket_status_label.configure(
                text=f"ソケット通信状態 : サーバー立上失敗",
            )
            self.socket_status_frame.socket_status_canvas.itemconfig(self.socket_status_frame.socket_status_circle,fill="red")
            self.socket_status_frame.SocketInfoLabel.configure(
                text=f"サーバー立上異常 server socket@{server_ip}:{server_port}",
            )

    #ソケット通信ログ用処理
    def socket_log_message(self,message):
        """ログメッセージをキューに追加"""
        self.socket_log_queue.put(message)

    def socket_update_log(self):
        """キューからログメッセージを取り出してテキストボックスに表示"""
        try:
            while True:
                message = self.socket_log_queue.get_nowait()
                self.bottom_frame.SocketLoggingTextBox.insert(tk.END, message + "\n")
                self.bottom_frame.SocketLoggingTextBox.see(tk.END)
        except queue.Empty:
            pass
        self.after(10, self.socket_update_log)

    #マージ処理ログ用処理
    def log_message(self,message):
        """ログメッセージをキューに追加"""
        self.log_queue.put(message)
   
    def update_log(self):
        """キューからログメッセージを取り出してテキストボックスに表示"""
        try:
            while True:
                message = self.log_queue.get_nowait()
                self.bottom_frame.LoggingTextBox.insert(tk.END, message + "\n")
                self.bottom_frame.LoggingTextBox.see(tk.END)
        except queue.Empty:
            pass
        self.after(10, self.update_log)

#menubar
class MenuBar(tk.Menu):
    def __init__(self,master):
        super().__init__(master)
        self.master=master
        self.add_command(label="アドレス設定",command=self.open_setting_window)
        self.add_command(label="サーバー再起動",command=self.restart_server) #サーバーを再起動するか一度確認する処理を入れる
        self.add_command(label="マニュアル処理",command=self.start_manual_convert)
        self.add_command(label="バージョン情報",command=self.open_version_info)

        self.version_window=None
        self.setting_window=None
        self.recipe_window=None
        self.manual_convert_window=None

    #バージョン情報を開く
    def open_version_info(self): #masterはapp
        if self.version_window is None or not self.version_window.winfo_exists():
            self.version_window=toplevel.VersionWindow(self)
            self.version_window.attributes("-topmost",True)
            self.version_window.iconbitmap("icon.ico")
        else:
            self.version_window.focus()
    
    def restart_server(self):
        res=messagebox.askyesno("確認",message="サーバーを再起動しますか?")
        if res:
            create_socket_thread(self.master)

    #設定ウインドウを開く
    def open_setting_window(self):
        if self.setting_window is None or not self.setting_window.winfo_exists():
            self.setting_window=toplevel.SettingWindow(self.master)
            self.setting_window.attributes("-topmost",True)
        else:
            self.setting_window.focus()

    #マニュアルでのロット処理を実施する
    def start_manual_convert(self):
        if self.manual_convert_window is None or not self.manual_convert_window.winfo_exists():
            self.manual_convert_window=toplevel.ManualConvertWindow(self.master)
            self.manual_convert_window.attributes("-topmost",True)
        else:
            self.manual_convert_window.focus()


#サーバーの状態、クライアントの接続状態を表示
class StatusFrame(customtkinter.CTkFrame):
    def __init__(self,master):
        super().__init__(master)
        self.master=master
        self._border_width=BORDER_WIDTH

        #ソケット状態表示
        self.socket_status_label=customtkinter.CTkLabel(self,text="ソケット通信状態",font=(FONT_TYPE,14),width=100)
        self.socket_status_label.grid(row=0,column=0,padx=10,pady=(5,0),sticky="w")
        self.socket_status_canvas = customtkinter.CTkCanvas(self, width=40, height=40,highlightthickness=0,bg="white")
        self.socket_status_canvas.grid(row=1,column=0,rowspan=2,padx=(15,10),pady=(0,10),sticky="w")
        self.socket_status_circle = self.socket_status_canvas.create_oval(5, 5, 35, 35, fill="yellow")

        #ソケット情報表示
        self.SocketInfoLabel=customtkinter.CTkLabel(
            self,
            text=f"",
            font=(FONT_TYPE,14),
            width=100
            )
        self.SocketInfoLabel.grid(row=1,column=0,padx=(60,0),pady=(0,5),sticky="w")

#生産品名、ロットNo,スタートボタン表示用Frame
class TopFrame(customtkinter.CTkFrame):
    def __init__(self,master):
        super().__init__(master)
        self._border_width=BORDER_WIDTH

        #ロット名ラベル
        self.LotNameLabel=customtkinter.CTkLabel(self,text="処理ロットNo",font=(FONT_TYPE,14),width=100)
        self.LotNameLabel.grid(row=0,column=0,padx=10,pady=(10,10),sticky="w")

        #ロット名入力ボックス
        self.LotNameEntry=customtkinter.CTkEntry(self,placeholder_text="Input LotName",width=500)
        self.LotNameEntry.grid(row=0,column=1,padx=10,pady=(10,10),sticky="nsew")

#ログ表示用フレーム
class BottomFrame(customtkinter.CTkFrame):
    def __init__(self,master):
        super().__init__(master)

        #マージログラベル
        label=customtkinter.CTkLabel(self,text="データ変換ログ",font=(FONT_TYPE,14))
        label.grid(row=0,column=0,padx=10,pady=(10,0),sticky="w")

        #マージ処理ログ表示用テキストボックス
        self.LoggingTextBox=customtkinter.CTkTextbox(self)
        self.LoggingTextBox.grid(row=1,column=0,padx=10,pady=(0,5),sticky="nsew")

        #マージログラベル
        label=customtkinter.CTkLabel(self,text="ソケット通信ログ",font=(FONT_TYPE,14))
        label.grid(row=0,column=1,padx=10,pady=(10,0),sticky="w")

        #ソケット通信ログ表示用テキストボックス
        self.SocketLoggingTextBox=customtkinter.CTkTextbox(self)
        self.SocketLoggingTextBox.grid(row=1,column=1,padx=10,pady=(0,5),sticky="nsew")

        # 横方向に広がるように設定
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 横方向に広がるように設定
        self.grid_rowconfigure(1, weight=1)

if __name__ == "__main__":
    # アプリケーション実行
    app = App()
    app.iconbitmap("icon.ico")
    app.mainloop()
