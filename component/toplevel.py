"""
メインウインドウを親としたトップレベルウインドウを作るモジュール
"""
import customtkinter
from . import settings
from . import subfunction as sf
from . import manual_process
import json
import tkinter as tk
from sys import platform

#version情報を書いたtoplevel
class VersionWindow(customtkinter.CTkToplevel):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.geometry("300x100")
        self.title("バージョン情報")
        self.label=customtkinter.CTkLabel(self,text=f"バージョン : {settings.VERSION}\n\n作成者 : 高橋直己",font=(settings.FONT_TYPE,14))
        self.label.pack(padx=20,pady=20)
        if platform.startswith("win"):
            self.after(200, lambda: self.iconbitmap("icon.ico"))

#各測定結果へのパスを設定するtoplevel
class SettingWindow(customtkinter.CTkToplevel):
    def __init__(self,master,*args,**kwargs):
        super().__init__(master,*args,**kwargs)
        self.geometry("1050x550+50+50")
        self.title("アドレス設定")
        self.iconbitmap("icon.ico")
        self.master=master
        if platform.startswith("win"):
            self.after(200, lambda: self.iconbitmap("icon.ico"))

        self.grid_rowconfigure(1, weight=1)  # タブビューの行を拡張可能に
        self.grid_columnconfigure(0, weight=0)  # 全体を埋めるように設定
        self.grid_columnconfigure(1, weight=1)  # 全体を埋めるように設定
        self.grid_columnconfigure(2, weight=0)  # 全体を埋めるように設定
        
        #変更保存ボタン
        SaveButton=customtkinter.CTkButton(self,text="変更保存",command=lambda:self.update_initialpath(),fg_color="red")
        SaveButton.grid(row=0,column=2,padx=10,pady=(10,0),sticky="w")

        #メイン処理の設定とソケット通信の設定をタブで切り替える
        settingtab=customtkinter.CTkTabview(master=self)
        settingtab.grid(row=1,column=0,padx=2,pady=(10,0),sticky="nsew",columnspan=3)
        tab1=settingtab.add("データ変換処理設定")
        tab2=settingtab.add("ソケット通信設定")
        tab3=settingtab.add("マニュアル変換処理設定")

        #まずスクロール可能なフレームを用意して、そこに各レシピのフレームを入れていく
        scrolledframe=BaseFrame(master=tab1)
        scrolledframe.pack(fill="both",expand=True)
        scrolledframe.columnconfigure(0,weight=1)

        scrolledframe_2=BaseFrame(master=tab2)
        scrolledframe_2.pack(fill="both",expand=True)

        scrolledframe_3=BaseFrame(master=tab3)
        scrolledframe_3.pack(fill="both",expand=True)
        scrolledframe_3.columnconfigure(0,weight=1)

        """tab1の設定"""
        bg_color = customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]
        machine_setting_frame=tk.LabelFrame(scrolledframe,text="オート処理パス設定",font=("Arial",18),bg=bg_color[0])
        machine_setting_frame.grid(row=0,column=0,padx=(10,10),pady=(10,10),sticky="nsew")
        machine_setting_frame.columnconfigure(1,weight=1)

        #ロットスタート時データ参照先ラベル
        self.LotStartInDataPathLabel=customtkinter.CTkLabel(machine_setting_frame,text="ロットスタート時データ参照先",font=(settings.FONT_TYPE,18))
        self.LotStartInDataPathLabel.grid(row=1,column=0,padx=10,pady=(10,0),sticky="w")
        #IN側パス入力ボックス
        self.LotStartInDataPathEntry=customtkinter.CTkEntry(machine_setting_frame,placeholder_text="DirPath",width=600)
        self.LotStartInDataPathEntry.grid(row=1,column=1,padx=10,pady=(10,0),sticky="ew",columnspan=7)
        self.LotStartInDataPathEntry.insert(0,self.master.address_dict["DATAPATH"]["LOTSTART_IN"])
        #IN側パス選択ボタン
        self.LotStartInDataPathButton=customtkinter.CTkButton(machine_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.LotStartInDataPathEntry))
        self.LotStartInDataPathButton.grid(row=1,column=8,padx=10,pady=(10,0),sticky="w")

        #ロットスタート時端数データ参照先ラベル(T&Rでのみ使用)
        self.LotStartInHasuuDataPathLabel=customtkinter.CTkLabel(machine_setting_frame,text="ロットスタート時データ参照先_TR端数",font=(settings.FONT_TYPE,14),bg_color="gray")
        self.LotStartInHasuuDataPathLabel.grid(row=2,column=0,padx=10,pady=(10,0),sticky="w")
        #IN側パス入力ボックス
        self.LotStartInHasuuDataPathEntry=customtkinter.CTkEntry(machine_setting_frame,placeholder_text="DirPath",width=600)
        self.LotStartInHasuuDataPathEntry.grid(row=2,column=1,padx=10,pady=(10,0),sticky="ew",columnspan=7)
        self.LotStartInHasuuDataPathEntry.insert(0,self.master.address_dict["DATAPATH"]["LOTSTART_IN_HASUU"])
        #IN側パス選択ボタン
        self.LotStartInHasuuDataPathButton=customtkinter.CTkButton(machine_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.LotStartInHasuuDataPathEntry))
        self.LotStartInHasuuDataPathButton.grid(row=2,column=8,padx=10,pady=(10,0),sticky="w")

        #ロットスタート時出力先ラベル
        self.LotStartOutDataPathLabel=customtkinter.CTkLabel(machine_setting_frame,text="ロットスタート時データ出力先",font=(settings.FONT_TYPE,18))
        self.LotStartOutDataPathLabel.grid(row=3,column=0,padx=10,pady=(15,0),sticky="w")
        #ロットスタート時出力先入力ボックス
        self.LotStartOutDataPathEntry=customtkinter.CTkEntry(machine_setting_frame,placeholder_text="DirPath")
        self.LotStartOutDataPathEntry.grid(row=3,column=1,padx=10,pady=(15,0),sticky="ew",columnspan=7)
        self.LotStartOutDataPathEntry.insert(0,self.master.address_dict["DATAPATH"]["LOTSTART_OUT"])
        #ロットスタート時出力先選択ボタン
        self.LotStartOutDataPathButton=customtkinter.CTkButton(machine_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.LotStartOutDataPathEntry))
        self.LotStartOutDataPathButton.grid(row=3,column=8,padx=10,pady=(15,0),sticky="w")

        #ロットスタート時一時作業ラベル
        self.LotStartTmpPathLabel=customtkinter.CTkLabel(machine_setting_frame,text="ロットスタート時一時作業場所",font=(settings.FONT_TYPE,18))
        self.LotStartTmpPathLabel.grid(row=4,column=0,padx=10,pady=(15,0),sticky="w")
        #ロットスタート時一時作業入力ボックス
        self.LotStartTmpPathEntry=customtkinter.CTkEntry(machine_setting_frame,placeholder_text="DirPath")
        self.LotStartTmpPathEntry.grid(row=4,column=1,padx=10,pady=(15,0),sticky="ew",columnspan=7)
        self.LotStartTmpPathEntry.insert(0,self.master.address_dict["DATAPATH"]["LOTSTART_TMP"])
        #ロットスタート時一時作業選択ボタン
        self.LotStartTmpPathButton=customtkinter.CTkButton(machine_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.LotStartTmpPathEntry))
        self.LotStartTmpPathButton.grid(row=4,column=8,padx=10,pady=(15,0),sticky="w")

        #ロットエンド時データ参照先ラベル
        self.LotEndInDataPathLabel=customtkinter.CTkLabel(machine_setting_frame,text="ロットエンド時データ参照先",font=(settings.FONT_TYPE,18))
        self.LotEndInDataPathLabel.grid(row=5,column=0,padx=10,pady=(30,0),sticky="w")
        #IN側パス入力ボックス
        self.LotEndInDataPathEntry=customtkinter.CTkEntry(machine_setting_frame,placeholder_text="DirPath",width=600)
        self.LotEndInDataPathEntry.grid(row=5,column=1,padx=10,pady=(30,0),sticky="ew",columnspan=7)
        self.LotEndInDataPathEntry.insert(0,self.master.address_dict["DATAPATH"]["LOTEND_IN"])
        #IN側パス選択ボタン
        self.LotEndInDataPathButton=customtkinter.CTkButton(machine_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.LotEndInDataPathEntry))
        self.LotEndInDataPathButton.grid(row=5,column=8,padx=10,pady=(30,0),sticky="w")

        #ロットエンド時出力先ラベル
        self.LotEndOutDataPathLabel=customtkinter.CTkLabel(machine_setting_frame,text="ロットエンド時データ出力先",font=(settings.FONT_TYPE,18))
        self.LotEndOutDataPathLabel.grid(row=6,column=0,padx=10,pady=(15,0),sticky="w")
        #ロットエンド時出力先入力ボックス
        self.LotEndOutDataPathEntry=customtkinter.CTkEntry(machine_setting_frame,placeholder_text="DirPath")
        self.LotEndOutDataPathEntry.grid(row=6,column=1,padx=10,pady=(15,0),sticky="ew",columnspan=7)
        self.LotEndOutDataPathEntry.insert(0,self.master.address_dict["DATAPATH"]["LOTEND_OUT"])
        #ロットエンド時出力先選択ボタン
        self.LotEndOutDataPathButton=customtkinter.CTkButton(machine_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.LotEndOutDataPathEntry))
        self.LotEndOutDataPathButton.grid(row=6,column=8,padx=10,pady=(15,0),sticky="w")

        #ロットエンド時端数出力先ラベル
        self.LotEndOutHasuuDataPathLabel=customtkinter.CTkLabel(machine_setting_frame,text="ロットエンド時データ出力先_TR端数",font=(settings.FONT_TYPE,14),bg_color="gray")
        self.LotEndOutHasuuDataPathLabel.grid(row=7,column=0,padx=10,pady=(15,0),sticky="w")
        #ロットエンド時端数出力先入力ボックス
        self.LotEndOutHasuuDataPathEntry=customtkinter.CTkEntry(machine_setting_frame,placeholder_text="DirPath")
        self.LotEndOutHasuuDataPathEntry.grid(row=7,column=1,padx=10,pady=(15,0),sticky="ew",columnspan=7)
        self.LotEndOutHasuuDataPathEntry.insert(0,self.master.address_dict["DATAPATH"]["LOTEND_OUT_HASUU"])
        #ロットエンド時端数出力先選択ボタン
        self.LotEndOutHasuuDataPathButton=customtkinter.CTkButton(machine_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.LotEndOutHasuuDataPathEntry))
        self.LotEndOutHasuuDataPathButton.grid(row=7,column=8,padx=10,pady=(15,0),sticky="w")

        #ロットエンド時一時作業ラベル
        self.LotEndTmpPathLabel=customtkinter.CTkLabel(machine_setting_frame,text="ロットエンド時一時作業場所",font=(settings.FONT_TYPE,18))
        self.LotEndTmpPathLabel.grid(row=8,column=0,padx=10,pady=(15,10),sticky="w")
        #ロットエンド時一時作業入力ボックス
        self.LotEndTmpPathEntry=customtkinter.CTkEntry(machine_setting_frame,placeholder_text="DirPath")
        self.LotEndTmpPathEntry.grid(row=8,column=1,padx=10,pady=(15,10),sticky="ew",columnspan=7)
        self.LotEndTmpPathEntry.insert(0,self.master.address_dict["DATAPATH"]["LOTEND_TMP"])
        #ロットエンド時一時作業選択ボタン
        self.LotEndTmpPathButton=customtkinter.CTkButton(machine_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.LotEndTmpPathEntry))
        self.LotEndTmpPathButton.grid(row=8,column=8,padx=10,pady=(15,10),sticky="w")

        #ロットエンド後生データ出力先ラベル
        self.LotEndRawDataPathLabel=customtkinter.CTkLabel(machine_setting_frame,text="設備生データ出力先",font=(settings.FONT_TYPE,18))
        self.LotEndRawDataPathLabel.grid(row=9,column=0,padx=10,pady=(15,10),sticky="w")
        #ロットエンド時一時作業入力ボックス
        self.LotEndRawDataPathEntry=customtkinter.CTkEntry(machine_setting_frame,placeholder_text="DirPath")
        self.LotEndRawDataPathEntry.grid(row=9,column=1,padx=10,pady=(15,10),sticky="ew",columnspan=7)
        self.LotEndRawDataPathEntry.insert(0,self.master.address_dict["DATAPATH"]["RAWDATA_OUT"])
        #ロットエンド時一時作業選択ボタン
        self.LotEndRawDataPathButton=customtkinter.CTkButton(machine_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.LotEndRawDataPathEntry))
        self.LotEndRawDataPathButton.grid(row=9,column=8,padx=10,pady=(15,10),sticky="w")

        """tab2の設定"""
        # スクロールフレームの列幅を設定
        scrolledframe_2.grid_columnconfigure(0, weight=1)  # Entry が配置されている列を拡張可能に

        #サーバーIP・ポートの設定関係を入れるフレーム
        bg_color = customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]
        server_setting_frame=tk.LabelFrame(scrolledframe_2,text="サーバー設定",font=("Arial",18),bg=bg_color[0])
        server_setting_frame.grid(row=0,column=0,padx=(10,10),pady=(10,10),sticky="nsew")
        server_setting_frame.columnconfigure(1,weight=1)

        #ソケット通信IPラベル
        label=customtkinter.CTkLabel(server_setting_frame,text="サーバーIP",font=(settings.FONT_TYPE,18))
        label.grid(row=1,column=0,padx=10,pady=(10,0))
        #ソケット通信IP入力ボックス
        self.SocketIPEntry=customtkinter.CTkEntry(server_setting_frame,placeholder_text="SocketServerIP")
        self.SocketIPEntry.grid(row=1,column=1,padx=10,pady=(10,0),sticky="ew")
        self.SocketIPEntry.insert(0,self.master.address_dict["SOCKET"]["IP"])
        #ソケット通信ポートラベル
        label=customtkinter.CTkLabel(server_setting_frame,text="サーバーPORT",font=(settings.FONT_TYPE,18))
        label.grid(row=2,column=0,padx=10,pady=(15,10))
        #ソケット通信ポート入力ボックス
        self.SocketPortEntry=customtkinter.CTkEntry(server_setting_frame,placeholder_text="SocketServerPort")
        self.SocketPortEntry.grid(row=2,column=1,padx=10,pady=(15,10),sticky="ew")
        self.SocketPortEntry.insert(0,self.master.address_dict["SOCKET"]["PORT"])

        """tab3の設定"""
        bg_color = customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]
        manual_setting_frame=tk.LabelFrame(scrolledframe_3,text="マニュアルパス設定",font=("Arial",18),bg=bg_color[0])
        manual_setting_frame.grid(row=0,column=0,padx=(10,10),pady=(10,10),sticky="nsew")
        manual_setting_frame.columnconfigure(1,weight=1)
        #ロットスタート時データ参照先ラベル
        self.ManualLotStartInDataPathLabel=customtkinter.CTkLabel(manual_setting_frame,text="ロットスタート時データ参照先",font=(settings.FONT_TYPE,18))
        self.ManualLotStartInDataPathLabel.grid(row=1,column=0,padx=10,pady=(10,0),sticky="w")
        #IN側パス入力ボックス
        self.ManualLotStartInDataPathEntry=customtkinter.CTkEntry(manual_setting_frame,placeholder_text="DirPath",width=600)
        self.ManualLotStartInDataPathEntry.grid(row=1,column=1,padx=10,pady=(10,0),sticky="ew",columnspan=7)
        self.ManualLotStartInDataPathEntry.insert(0,self.master.address_dict["MANUAL_DATAPATH"]["LOTSTART_IN"])
        #IN側パス選択ボタン
        self.ManualLotStartInDataPathButton=customtkinter.CTkButton(manual_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.ManualLotStartInDataPathEntry))
        self.ManualLotStartInDataPathButton.grid(row=1,column=8,padx=10,pady=(10,0),sticky="w")

        #ロットスタート時端数データ参照先ラベル(T&Rでのみ使用)
        self.ManualLotStartInHasuuDataPathLabel=customtkinter.CTkLabel(manual_setting_frame,text="ロットスタート時データ参照先_TR端数",font=(settings.FONT_TYPE,14),bg_color="gray")
        self.ManualLotStartInHasuuDataPathLabel.grid(row=2,column=0,padx=10,pady=(10,0),sticky="w")
        #IN側パス入力ボックス
        self.ManualLotStartInHasuuDataPathEntry=customtkinter.CTkEntry(manual_setting_frame,placeholder_text="DirPath",width=600)
        self.ManualLotStartInHasuuDataPathEntry.grid(row=2,column=1,padx=10,pady=(10,0),sticky="ew",columnspan=7)
        self.ManualLotStartInHasuuDataPathEntry.insert(0,self.master.address_dict["MANUAL_DATAPATH"]["LOTSTART_IN_HASUU"])
        #IN側パス選択ボタン
        self.ManualLotStartInHasuuDataPathButton=customtkinter.CTkButton(manual_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.ManualLotStartInHasuuDataPathEntry))
        self.ManualLotStartInHasuuDataPathButton.grid(row=2,column=8,padx=10,pady=(10,0),sticky="w")

        #ロットスタート時出力先ラベル
        self.ManualLotStartOutDataPathLabel=customtkinter.CTkLabel(manual_setting_frame,text="ロットスタート時データ出力先",font=(settings.FONT_TYPE,18))
        self.ManualLotStartOutDataPathLabel.grid(row=3,column=0,padx=10,pady=(15,0),sticky="w")
        #ロットスタート時出力先入力ボックス
        self.ManualLotStartOutDataPathEntry=customtkinter.CTkEntry(manual_setting_frame,placeholder_text="DirPath")
        self.ManualLotStartOutDataPathEntry.grid(row=3,column=1,padx=10,pady=(15,0),sticky="ew",columnspan=7)
        self.ManualLotStartOutDataPathEntry.insert(0,self.master.address_dict["MANUAL_DATAPATH"]["LOTSTART_OUT"])
        #ロットスタート時出力先選択ボタン
        self.ManualLotStartOutDataPathButton=customtkinter.CTkButton(manual_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.ManualLotStartOutDataPathEntry))
        self.ManualLotStartOutDataPathButton.grid(row=3,column=8,padx=10,pady=(15,0),sticky="w")

        #ロットスタート時一時作業ラベル
        self.ManualLotStartTmpPathLabel=customtkinter.CTkLabel(manual_setting_frame,text="ロットスタート時一時作業場所",font=(settings.FONT_TYPE,18))
        self.ManualLotStartTmpPathLabel.grid(row=4,column=0,padx=10,pady=(15,0),sticky="w")
        #ロットスタート時一時作業入力ボックス
        self.ManualLotStartTmpPathEntry=customtkinter.CTkEntry(manual_setting_frame,placeholder_text="DirPath")
        self.ManualLotStartTmpPathEntry.grid(row=4,column=1,padx=10,pady=(15,0),sticky="ew",columnspan=7)
        self.ManualLotStartTmpPathEntry.insert(0,self.master.address_dict["MANUAL_DATAPATH"]["LOTSTART_TMP"])
        #ロットスタート時一時作業選択ボタン
        self.ManualLotStartTmpPathButton=customtkinter.CTkButton(manual_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.ManualLotStartTmpPathEntry))
        self.ManualLotStartTmpPathButton.grid(row=4,column=8,padx=10,pady=(15,0),sticky="w")

        #ロットエンド時データ参照先ラベル
        self.ManualLotEndInDataPathLabel=customtkinter.CTkLabel(manual_setting_frame,text="ロットエンド時データ参照先",font=(settings.FONT_TYPE,18))
        self.ManualLotEndInDataPathLabel.grid(row=5,column=0,padx=10,pady=(30,0),sticky="w")
        #IN側パス入力ボックス
        self.ManualLotEndInDataPathEntry=customtkinter.CTkEntry(manual_setting_frame,placeholder_text="DirPath",width=600)
        self.ManualLotEndInDataPathEntry.grid(row=5,column=1,padx=10,pady=(30,0),sticky="ew",columnspan=7)
        self.ManualLotEndInDataPathEntry.insert(0,self.master.address_dict["MANUAL_DATAPATH"]["LOTEND_IN"])
        #IN側パス選択ボタン
        self.ManualLotEndInDataPathButton=customtkinter.CTkButton(manual_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.ManualLotEndInDataPathEntry))
        self.ManualLotEndInDataPathButton.grid(row=5,column=8,padx=10,pady=(30,0),sticky="w")

        #ロットエンド時出力先ラベル
        self.ManualLotEndOutDataPathLabel=customtkinter.CTkLabel(manual_setting_frame,text="ロットエンド時データ出力先",font=(settings.FONT_TYPE,18))
        self.ManualLotEndOutDataPathLabel.grid(row=6,column=0,padx=10,pady=(15,0),sticky="w")
        #ロットエンド時出力先入力ボックス
        self.ManualLotEndOutDataPathEntry=customtkinter.CTkEntry(manual_setting_frame,placeholder_text="DirPath")
        self.ManualLotEndOutDataPathEntry.grid(row=6,column=1,padx=10,pady=(15,0),sticky="ew",columnspan=7)
        self.ManualLotEndOutDataPathEntry.insert(0,self.master.address_dict["MANUAL_DATAPATH"]["LOTEND_OUT"])
        #ロットエンド時出力先選択ボタン
        self.ManualLotEndOutDataPathButton=customtkinter.CTkButton(manual_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.ManualLotEndOutDataPathEntry))
        self.ManualLotEndOutDataPathButton.grid(row=6,column=8,padx=10,pady=(15,0),sticky="w")

        #ロットエンド時端数出力先ラベル
        self.ManualLotEndOutHasuuDataPathLabel=customtkinter.CTkLabel(manual_setting_frame,text="ロットエンド時データ出力先_TR端数",font=(settings.FONT_TYPE,14),bg_color="gray")
        self.ManualLotEndOutHasuuDataPathLabel.grid(row=7,column=0,padx=10,pady=(15,0),sticky="w")
        #ロットエンド時端数出力先入力ボックス
        self.ManualLotEndOutHasuuDataPathEntry=customtkinter.CTkEntry(manual_setting_frame,placeholder_text="DirPath")
        self.ManualLotEndOutHasuuDataPathEntry.grid(row=7,column=1,padx=10,pady=(15,0),sticky="ew",columnspan=7)
        self.ManualLotEndOutHasuuDataPathEntry.insert(0,self.master.address_dict["MANUAL_DATAPATH"]["LOTEND_OUT_HASUU"])
        #ロットエンド時端数出力先選択ボタン
        self.ManualLotEndOutHasuuDataPathButton=customtkinter.CTkButton(manual_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.ManualLotEndOutHasuuDataPathEntry))
        self.ManualLotEndOutHasuuDataPathButton.grid(row=7,column=8,padx=10,pady=(15,0),sticky="w")

        #ロットエンド時一時作業ラベル
        self.ManualLotEndTmpPathLabel=customtkinter.CTkLabel(manual_setting_frame,text="ロットエンド時一時作業場所",font=(settings.FONT_TYPE,18))
        self.ManualLotEndTmpPathLabel.grid(row=8,column=0,padx=10,pady=(15,10),sticky="w")
        #ロットエンド時一時作業入力ボックス
        self.ManualLotEndTmpPathEntry=customtkinter.CTkEntry(manual_setting_frame,placeholder_text="DirPath")
        self.ManualLotEndTmpPathEntry.grid(row=8,column=1,padx=10,pady=(15,10),sticky="ew",columnspan=7)
        self.ManualLotEndTmpPathEntry.insert(0,self.master.address_dict["MANUAL_DATAPATH"]["LOTEND_TMP"])
        #ロットエンド時一時作業選択ボタン
        self.ManualLotEndTmpPathButton=customtkinter.CTkButton(manual_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.ManualLotEndTmpPathEntry))
        self.ManualLotEndTmpPathButton.grid(row=8,column=8,padx=10,pady=(15,10),sticky="w")

        #ロットエンド後生データ出力先ラベル
        self.ManualLotEndRawDataPathLabel=customtkinter.CTkLabel(manual_setting_frame,text="設備生データ出力先",font=(settings.FONT_TYPE,18))
        self.ManualLotEndRawDataPathLabel.grid(row=9,column=0,padx=10,pady=(15,10),sticky="w")
        #ロットエンド時一時作業入力ボックス
        self.ManualLotEndRawDataPathEntry=customtkinter.CTkEntry(manual_setting_frame,placeholder_text="DirPath")
        self.ManualLotEndRawDataPathEntry.grid(row=9,column=1,padx=10,pady=(15,10),sticky="ew",columnspan=7)
        self.ManualLotEndRawDataPathEntry.insert(0,self.master.address_dict["MANUAL_DATAPATH"]["RAWDATA_OUT"])
        #ロットエンド時一時作業選択ボタン
        self.ManualLotEndRawDataPathButton=customtkinter.CTkButton(manual_setting_frame,text="フォルダ選択",command=lambda:sf.search_folder(self.ManualLotEndRawDataPathEntry))
        self.ManualLotEndRawDataPathButton.grid(row=9,column=8,padx=10,pady=(15,10),sticky="w")

    #jsonの内容を更新してウインドウを閉じる    
    def update_initialpath(self):

        #socket通信部分の保存
        self.master.address_dict["DATAPATH"]["LOTSTART_IN"]=self.LotStartInDataPathEntry.get()
        self.master.address_dict["DATAPATH"]["LOTSTART_IN_HASUU"]=self.LotStartInHasuuDataPathEntry.get()
        self.master.address_dict["DATAPATH"]["LOTSTART_OUT"]=self.LotStartOutDataPathEntry.get()
        self.master.address_dict["DATAPATH"]["LOTSTART_TMP"]=self.LotStartTmpPathEntry.get()
        self.master.address_dict["DATAPATH"]["LOTEND_IN"]=self.LotEndInDataPathEntry.get()
        self.master.address_dict["DATAPATH"]["LOTEND_OUT"]=self.LotEndOutDataPathEntry.get()
        self.master.address_dict["DATAPATH"]["LOTEND_OUT_HASUU"]=self.LotEndOutHasuuDataPathEntry.get()
        self.master.address_dict["DATAPATH"]["LOTEND_TMP"]=self.LotEndTmpPathEntry.get()
        self.master.address_dict["DATAPATH"]["RAWDATA_OUT"]=self.LotEndRawDataPathEntry.get()
        self.master.address_dict["SOCKET"]["IP"]=self.SocketIPEntry.get()
        self.master.address_dict["SOCKET"]["PORT"]=self.SocketPortEntry.get()
        self.master.address_dict["MANUAL_DATAPATH"]["LOTSTART_IN"]=self.ManualLotStartInDataPathEntry.get()
        self.master.address_dict["MANUAL_DATAPATH"]["LOTSTART_IN_HASUU"]=self.ManualLotStartInHasuuDataPathEntry.get()
        self.master.address_dict["MANUAL_DATAPATH"]["LOTSTART_OUT"]=self.ManualLotStartOutDataPathEntry.get()
        self.master.address_dict["MANUAL_DATAPATH"]["LOTSTART_TMP"]=self.ManualLotStartTmpPathEntry.get()
        self.master.address_dict["MANUAL_DATAPATH"]["LOTEND_IN"]=self.ManualLotEndInDataPathEntry.get()
        self.master.address_dict["MANUAL_DATAPATH"]["LOTEND_OUT"]=self.ManualLotEndOutDataPathEntry.get()
        self.master.address_dict["MANUAL_DATAPATH"]["LOTEND_OUT_HASUU"]=self.ManualLotEndOutHasuuDataPathEntry.get()
        self.master.address_dict["MANUAL_DATAPATH"]["LOTEND_TMP"]=self.ManualLotEndTmpPathEntry.get()
        self.master.address_dict["MANUAL_DATAPATH"]["RAWDATA_OUT"]=self.ManualLotEndRawDataPathEntry.get()
        json_file=open("address_setting.json","w")
        json.dump(self.master.address_dict,json_file,ensure_ascii=False)
        json_file.close()

        self.destroy()

#マニュアル処理用のウインドウ
class ManualConvertWindow(customtkinter.CTkToplevel):
    def __init__(self,master,*args,**kwargs):
        super().__init__(master,*args,**kwargs)
        self.geometry("600x350")
        self.title("マニュアル処理")
        if platform.startswith("win"):
            self.after(200, lambda: self.iconbitmap("icon.ico"))

        self.grid_rowconfigure(0, weight=1)  # タブビューの行を拡張可能に
        self.grid_columnconfigure(0, weight=1)  # 全体を埋めるように設定
        
        #メイン処理の設定とソケット通信の設定をタブで切り替える
        self.rowconfigure(0,weight=1)
        self.columnconfigure(0,weight=1)
        settingtab=customtkinter.CTkTabview(master=self)
        settingtab.grid(row=0,column=0,padx=2,pady=(10,0),sticky="nsew")
        tab1=settingtab.add("分類機マニュアル処理")
        tab2=settingtab.add("T&Rマニュアル処理")

        #まずスクロール可能なフレームを用意して、そこに各レシピのフレームを入れていく
        scrolledframe=BaseFrame(master=tab1)
        scrolledframe.pack(fill="both",expand=True)
        scrolledframe.columnconfigure(0,weight=1)

        scrolledframe_2=BaseFrame(master=tab2)
        scrolledframe_2.pack(fill="both",expand=True)

        bg_color = customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]
        sorter_setting_frame=tk.LabelFrame(scrolledframe,text="分類機設定",font=("Arial",18),bg=bg_color[0])
        sorter_setting_frame.grid(row=0,column=0,padx=(10,10),pady=(10,10),sticky="nsew")
        sorter_setting_frame.columnconfigure(1,weight=1)

        """分類機処理の設定"""
        #ロットスタート時データ参照先ラベル
        label=customtkinter.CTkLabel(sorter_setting_frame,text="分類機処理内容",font=(settings.FONT_TYPE,16))
        label.grid(row=0,column=0,padx=10,pady=(10,0),sticky="w")

        # ラジオボタンの本体
        self.sorter_process_select = customtkinter.StringVar(value="LotStart")

        # ラジオボタンを作成（同じ variable を指定）
        self.sorter_select_process_radio1 = customtkinter.CTkRadioButton(
            sorter_setting_frame, 
            text="清武⇒筑後(ロット開始前)", 
            variable=self.sorter_process_select, 
            value="LotStart",
            font=(settings.FONT_TYPE,16))
        self.sorter_select_process_radio1.grid(row=0,column=1,padx=10,pady=(10,0),sticky="w")

        self.sorter_select_process_radio2 = customtkinter.CTkRadioButton(
            sorter_setting_frame, 
            text="筑後⇒清武(ロット終了後)", 
            variable=self.sorter_process_select, 
            value="LotEnd",
            font=(settings.FONT_TYPE,16))
        self.sorter_select_process_radio2.grid(row=1,column=1,padx=10,pady=(10,0),sticky="w")

        label=customtkinter.CTkLabel(sorter_setting_frame,text="ロット情報入力",font=(settings.FONT_TYPE,16))
        label.grid(row=2,column=0,padx=10,pady=(10,0),sticky="w")

        label=customtkinter.CTkLabel(sorter_setting_frame,text="ロット番号",font=(settings.FONT_TYPE,16))
        label.grid(row=3,column=0,padx=10,pady=(5,0),sticky="w")
        
        self.SorterLotNameEntry=customtkinter.CTkEntry(sorter_setting_frame,placeholder_text="LotName")
        self.SorterLotNameEntry.grid(row=3,column=1,padx=10,pady=(5,0),sticky="ew")

        #処理開始ボタン
        self.SorterStartButton=customtkinter.CTkButton(sorter_setting_frame,text="処理開始",command=self.sorter_lot_start,fg_color="red")
        self.SorterStartButton.grid(row=4,column=0,padx=10,pady=(10,10),sticky="w")

        """テーピング処理の設定"""
        # スクロールフレームの列幅を設定
        scrolledframe_2.grid_columnconfigure(0, weight=1)  # Entry が配置されている列を拡張可能に

        bg_color = customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"]
        taping_setting_frame=tk.LabelFrame(scrolledframe_2,text="テーピング設定",font=("Arial",18),bg=bg_color[0])
        taping_setting_frame.grid(row=0,column=0,padx=(10,10),pady=(10,10),sticky="nsew")
        taping_setting_frame.columnconfigure(1,weight=1)

        #ロットスタート時データ参照先ラベル
        label=customtkinter.CTkLabel(taping_setting_frame,text="処理内容",font=(settings.FONT_TYPE,16))
        label.grid(row=0,column=0,padx=10,pady=(10,0),sticky="w")

        # ラジオボタンの本体
        self.taping_process_select = customtkinter.StringVar(value="LotStart")

        # ラジオボタンを作成（同じ variable を指定）
        self.taping_select_process_radio1 = customtkinter.CTkRadioButton(
            taping_setting_frame, text="清武⇒筑後(ロット開始前)", variable=self.taping_process_select, value="LotStart",font=(settings.FONT_TYPE,16))
        self.taping_select_process_radio1.grid(row=0,column=1,padx=10,pady=(10,0),sticky="w")

        self.taping_select_process_radio2 = customtkinter.CTkRadioButton(
            taping_setting_frame, text="筑後⇒清武(ロット終了後)", variable=self.taping_process_select, value="LotEnd",font=(settings.FONT_TYPE,16))
        self.taping_select_process_radio2.grid(row=1,column=1,padx=10,pady=(10,0),sticky="w")

        label=customtkinter.CTkLabel(taping_setting_frame,text="ロット情報入力",font=(settings.FONT_TYPE,16))
        label.grid(row=2,column=0,padx=10,pady=(10,0),sticky="w")

        label=customtkinter.CTkLabel(taping_setting_frame,text="ロット番号",font=(settings.FONT_TYPE,16))
        label.grid(row=3,column=0,padx=10,pady=(10,0),sticky="w")
        
        self.TapingLotNameEntry=customtkinter.CTkEntry(taping_setting_frame,placeholder_text="LotName")
        self.TapingLotNameEntry.grid(row=3,column=1,padx=10,pady=(10,0),sticky="ew")

        label=customtkinter.CTkLabel(taping_setting_frame,text="ランク",font=(settings.FONT_TYPE,16))
        label.grid(row=4,column=0,padx=10,pady=(10,0),sticky="w")
        
        self.TapingRankEntry=customtkinter.CTkEntry(taping_setting_frame,placeholder_text="Rank")
        self.TapingRankEntry.grid(row=4,column=1,padx=10,pady=(10,0),sticky="ew")

        #変更保存ボタン
        self.TapingStartButton=customtkinter.CTkButton(taping_setting_frame,text="処理開始",command=self.taping_lot_start,fg_color="red")
        self.TapingStartButton.grid(row=5,column=0,padx=10,pady=(10,10),sticky="w")

    #sorterのマニュアル処理開始ボタン
    def sorter_lot_start(self):
        process=self.sorter_process_select.get()
        lot_name=self.SorterLotNameEntry.get()
        dict={}
        dict["machine"]="Sorter"
        dict["command_type"] = process
        dict["lotno"] = lot_name
        dict["id"] = "3"
        dict["product_name"] = "TMP"
        dict["wp_lotno"] = "TMP"
        dict["quantity"]="TMP"
        dict["operator_id"]="TMP"

        self.destroy()

        manual_process.manual_process(self.master,dict)

        return

    #sorterのマニュアル処理開始ボタン
    def taping_lot_start(self):
        process=self.taping_process_select.get()
        lot_name=self.TapingLotNameEntry.get()
        rank=self.TapingRankEntry.get()
        dict={}
        dict["machine"]="Taping"
        dict["command_type"] = process
        dict["lotno"] = lot_name
        dict["rank"] = rank
        dict["id"] = "3"
        dict["product_name"] = "TMP"
        dict["wp_lotno"] = "TMP"
        dict["quantity"]="TMP"
        dict["operator_id"]="TMP"

        self.destroy()

        manual_process.manual_process(self.master,dict)

        return

#スクロール可能なフレーム
class BaseFrame(customtkinter.CTkScrollableFrame):
    def __init__(self,master,**kwargs):
        super().__init__(master,**kwargs)

