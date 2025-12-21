import os
import shutil
from . import settings
import glob
from .header import miyazaki_sorter_header

#ログ出力用の関数
# ログメッセージの記録関数
logger=settings.logger
def log_file_message(message, level='info'):
    if level == 'info':
        logger.info(message)
    elif level == 'warning':
        logger.warning(message)
    elif level == 'error':
        logger.error(message)
    else:
        logger.debug(message)

#ログとテキストボックスへの出力をまとめる
def normal_message_handling(app,message):
    app.log_message(message)
    log_file_message(message)


#エラー発生時の処理をまとめる
def error_handling(app,message):
    app.mergeResult=(False,"1")
    app.log_message(message)
    log_file_message(message,"error")

#数値の文字列を任意の桁数に変換して文字列に返す(0先埋め)
def adjust_int(s, n):
    try:
        num = int(s)
        return f"{num:0{n}d}"  # n桁ゼロ埋め
    except ValueError:
        return s
    
#数値の文字列を任意の桁数に変換して文字列に返す(0先埋め)
def adjust_float(s):
    try:
        num=float(s)
        num="%.1f"%num
        return str(num)
    except:
        return s

#筑後のテーピング後データを宮崎形式に変換
def chikugo_to_miyazaki_sorter(line,lot_name,machine_id):
    data_list=["" for i in range(len(miyazaki_sorter_header))]
    chikugo_data_list=line.replace("\n","").split(",")
    #宮崎仕様のデータにある項目はそれを入れていく
    #宮崎データのヘッダーは固有になっていないのでdictが使用できない
    #------------------総合-----------------------
    data_list[0]=chikugo_data_list[0] #SerialNo
    data_list[1]=chikugo_data_list[2] #TrayNo
    data_list[2]=chikugo_data_list[3] #TrayRank
    data_list[3]=chikugo_data_list[4] #TrayX
    data_list[4]=chikugo_data_list[5] #TrayY
    data_list[5]=chikugo_data_list[7] #Header名はLotNoだが、RingIDを入れる
    #------------------ピッカー-----------------------
    data_list[6]=chikugo_data_list[8] #WaferNo
    data_list[7]=chikugo_data_list[9] #WaferX
    data_list[8]=chikugo_data_list[10] #WaferY
    data_list[9]="" #SP1
    data_list[10]="" #SP2 
    #------------------CLT-----------------------
    data_list[11]=chikugo_data_list[19] #TOTAL
    data_list[12]="FF" #LD LDというカラムが筑後データにない.一旦FFを入れておく
    data_list[13]=chikugo_data_list[20] #TEST1
    data_list[14]=adjust_float(chikugo_data_list[21]) #℃
    data_list[15]=chikugo_data_list[22] #TEST2
    data_list[16]=adjust_float(chikugo_data_list[23]) #℃
    data_list[17]=chikugo_data_list[24] #TEST3
    data_list[18]=adjust_float(chikugo_data_list[25]) #℃
    data_list[19]=chikugo_data_list[26] #TEST4
    data_list[20]=adjust_float(chikugo_data_list[27]) #℃
    data_list[21]="" #TEST5
    data_list[22]="0.0" #℃
    data_list[23]="" #TEST6
    data_list[24]="0.0" #℃
    data_list[25]="" #SP3
    data_list[26]="FF" #SP4(外観結果が入っていそう.ここまで来るのは全て良品なのでFFを入れておく)
    data_list[27]="" #IP
    data_list[28]="" #SP5
    data_list[29]="" #ULD
    data_list[30]="" #SP6
    #------------------SORTER-----------------------
    if chikugo_data_list[2]!="LINEOUT":
        data_list[31]=adjust_int(str(machine_id),2) #SORT.NO
        data_list[32]=chikugo_data_list[33] #TOTAL
        data_list[33]="FF" #LD
        data_list[34]="FF" #IP
        data_list[35]="FF" #ULD
    else:
        data_list[31]="" #SORT.NO
        data_list[32]="" #TOTAL
        data_list[33]="" #LD
        data_list[34]="" #IP
        data_list[35]="" #ULD
    #------------------TAPING(ヘッダーのみ)-----------------------
    data_list[36]=""
    data_list[37]=""
    data_list[38]=""
    data_list[39]=""
    data_list[40]=""
    data_list[41]=""

    return data_list

#ファイルを読み込んで、チップ単位のリストが入ったリストを返す
def read_traydata(traydata_path,d):
    output_lines=[]
    lot_name=d["lot_name"]
    machine_id=d["machine_id"]
    with open(traydata_path,"r") as f:
        line=f.readline()
        line_num=1
        while line:
            if line_num>1:
                converted_line=chikugo_to_miyazaki_sorter(line,lot_name,machine_id)
                output_lines.append(converted_line)
            line=f.readline() 
            line_num+=1
    return output_lines

#output_linesの内容をファイルに書き込む
def write_traydata(output_path,output_lines,add_flag=False):
    if add_flag==False:
        with open(output_path,"w") as of:
            #header出力
            header_line=",".join(miyazaki_sorter_header)+"\n"
            of.write(header_line)
            for chip_data in output_lines: #chip_dataはlist形式
                output_line=""
                for num in range(len(miyazaki_sorter_header)):
                    output_line+=chip_data[num]+","
                
                of.write(output_line[0:-1]+"\n") #最後のカンマを省く
    elif add_flag: #追記モードで開く
        with open(output_path,"a+") as of:
            #追記の時はヘッダーを出力しない
            for chip_data in output_lines: #chip_dataはlist形式
                output_line=""
                for num in range(len(miyazaki_sorter_header)):
                    output_line+=chip_data[num]+","
                
                of.write(output_line[0:-1]+"\n") #最後のカンマを省く

#summaryファイルを作成する
def create_summaryfie(summary_file_path,summary_info_dict,product_name,wp_lot_name,lot_name):
    summary_file_header=[
        "ProductName",
        "WpOrderNo",
        "AtOrderNo",
        "Quantity",
        "Pass",
        "Fail",
        "LineOut",
        "RankA",
        "QuantityA",
        "RankB",
        "QuantityB",
        "RankC",
        "QuantityC",
        "RankD",
        "QuantityD",
        "RankE",
        "QuantityE",
        ]
    with open(summary_file_path,"w") as of:
        #header出力
        header_line=",".join(summary_file_header)+"\n"
        of.write(header_line)
        output_line=""
        output_line+=product_name+","
        output_line+=wp_lot_name+","
        output_line+=lot_name+","
        output_line+=str(summary_info_dict["PASS"]+summary_info_dict["F"]+summary_info_dict["LINEOUT"])+"," #Quantity
        output_line+=str(summary_info_dict["PASS"])+"," #Pass
        output_line+=str(summary_info_dict["F"])+"," #Fail
        output_line+=str(summary_info_dict["LINEOUT"])+"," #LINEOUT
        output_line+="A"+"," #文字のみ
        output_line+=str(summary_info_dict["A"])+"," #RankAの数量
        output_line+="B"+"," #文字のみ
        output_line+=str(summary_info_dict["B"])+"," #RankBの数量
        output_line+="C"+"," #文字のみ
        output_line+=str(summary_info_dict["C"])+"," #RankCの数量
        output_line+="D"+"," #文字のみ
        output_line+=str(summary_info_dict["D"])+"," #RankDの数量
        output_line+="E"+"," #文字のみ
        output_line+=str(summary_info_dict["E"])+"," #RankEの数量

        of.write(output_line)

def sorter_lot_end(app,data_dict,manual_flag=False):
    #ロット番号、ランク、機台IDを受け取る
    lot_name=data_dict["lotno"] #ATP工注(メインロットNo)
    machine_id=data_dict["id"] #機台番号
    wp_lot_name=data_dict["wp_lotno"] #WP工注
    product_name=data_dict["product_name"] #機種名

    if not manual_flag:
        input_folder_path=os.path.join(app.address_dict["DATAPATH"]["LOTEND_IN"],lot_name)
        output_folder_path=app.address_dict["DATAPATH"]["LOTEND_OUT"]
        output_folder_path_lot=os.path.join(output_folder_path,lot_name)
        tmp_folder_path=app.address_dict["DATAPATH"]["LOTEND_TMP"]
        raw_data_output_path=app.address_dict["DATAPATH"]["RAWDATA_OUT"] #生データ出力先
        raw_data_output_path_lot=os.path.join(raw_data_output_path,lot_name) #生データ出力先(ロット名フォルダ)
    else:
        input_folder_path=os.path.join(app.address_dict["MANUAL_DATAPATH"]["LOTEND_IN"],lot_name)
        output_folder_path=app.address_dict["MANUAL_DATAPATH"]["LOTEND_OUT"]
        output_folder_path_lot=os.path.join(output_folder_path,lot_name)
        tmp_folder_path=app.address_dict["MANUAL_DATAPATH"]["LOTEND_TMP"]
        raw_data_output_path=app.address_dict["MANUAL_DATAPATH"]["RAWDATA_OUT"] #生データ出力先
        raw_data_output_path_lot=os.path.join(raw_data_output_path,lot_name) #生データ出力先(ロット名フォルダ)

    normal_message_handling(app,f"{lot_name}の筑後⇒清武仕様へのソート後データの変換を実施")

    #IN側パスのフォルダ有無確認
    if not os.path.exists(input_folder_path):
        error_handling(app,f"LotEnd時の参照データ先が存在しません:{input_folder_path}")
        return

    #OUT側パスのフォルダ有無確認
    if not os.path.exists(input_folder_path):
        error_handling(app,f"LotEnd時の出力データ先が存在しません:{output_folder_path}")
        return

    #一時作業フォルダ有無確認
    if not os.path.exists(tmp_folder_path):
        error_handling(app,f"一時作業フォルダが存在しません:{tmp_folder_path}")
        return
    
    #tmpフォルダの中身を削除
    normal_message_handling(app,f"tmpフォルダの中身を削除します")
    for item in os.listdir(tmp_folder_path):
        item_path = os.path.join(tmp_folder_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)  # ファイル削除
                normal_message_handling(app,f"{item_path}を削除しました")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)  # フォルダ削除
                normal_message_handling(app,f"{item_path}を削除しました")
        except Exception as e:
            error_handling(app,f"一時作業フォルダの削除に失敗しました:{e}")
            return
    
    #tmpフォルダに変換後ファイルを置くためのconvertedフォルダを作成
    try:
        os.makedirs(os.path.join(tmp_folder_path,"converted"))
    except Exception as e:
            error_handling(app,f"一時作業フォルダ内のフォルダ作成に失敗しました:{e}")
            return

    #IN側パスのトレイデータをtmpフォルダにコピー
    normal_message_handling(app,f"トレイデータをtmpフォルダにコピーします")
    try:
        csv_file_list=glob.glob(os.path.join(input_folder_path,"*.csv"))
        for csv_file in csv_file_list:
            shutil.copy(csv_file,os.path.join(tmp_folder_path,os.path.basename(csv_file)))
    except Exception as e:
        error_handling(app,f"ファイルのコピーで異常が発生しました:{e})")
        return

    #データ変換を実施
    csv_file_list=glob.glob(os.path.join(tmp_folder_path,"*.csv"))
    if len(csv_file_list)==0: #tmpフォルダ内のファイル数が0であれば終了
        error_handling(app,f"IN側のファイルが存在しません")
        return
    
    normal_message_handling(app,f"トレイデータのtmpフォルダへのコピーが完了しました")
    #------------------------ここからメインのデータ変換処理-------------------------------------------
    #summaryファイルにのせる情報を入れるためのdict
    summary_info_dict={
        "PASS":0,
        "F":0,
        "LINEOUT":0,
        "A":0,
        "B":0,
        "C":0,
        "D":0,
        "E":0,
    }

    #-------------------------トレイデータの変換を開始----------------------------------------
    normal_message_handling(app,f"全データの変換を開始")
    all_tray_in_chip_data=[] #全ての個別トレイデータの中身を合わせたもの(ARRAYデータ作成用)
    for csv_file in csv_file_list:
        if "_ALL" in os.path.basename(csv_file): #個別ファイルのみ読み込む
            continue
        file_name=os.path.basename(csv_file)
        name,ext=os.path.splitext(file_name)
        tray_id=name.split("_")[0]
        tray_rank=name.split("_")[1] if name.split("_")[1]!="NG" else "F"
        normal_message_handling(app,f"{file_name}の変換を開始")
        try:
            output_lines=read_traydata(
                csv_file,
                {"lot_name":lot_name,"machine_id":machine_id}
            )
                        
            #出力ファイルの設定
            output_csv_file=os.path.join(tmp_folder_path,"converted",f"{tray_id}.csv")
            #ファイルに書き込む
            write_traydata(output_csv_file,output_lines)
            if tray_rank!="F":
                summary_info_dict["PASS"]+=len(output_lines) #summaryファイル掲載用に良品数を記録する
                summary_info_dict[tray_rank]+=len(output_lines) #summaryファイル掲載用に良品数を記録する
            elif tray_rank=="F":
                summary_info_dict["F"]+=len(output_lines) #summaryファイル掲載用に良品数を記録する
            else:
                raise ValueError("Rankの値が異常です")
            all_tray_in_chip_data+=output_lines #_TAPEデータ出力用に良品のデータをまとめる
            normal_message_handling(app,f"{file_name}の変換が完了")
        
        except Exception as e:
            error_handling(app,f"データの変換に失敗しました:{e}")
            return

    #-----------------------------不良ALLデータの読み取り開始(LINEOUTデータ取得用)---------------------------------------
    normal_message_handling(app,f"不良ALLデータの読み取りを開始(LINEOUTデータの取得用)")
    for csv_file in csv_file_list:
        if "ALL_NG" not in csv_file:
            continue
        output_lines=[]
        file_name=os.path.basename(csv_file)
        tray_id=file_name.replace("_NG.csv","")
        output_file_name=tray_id+".csv"
        normal_message_handling(app,f"{file_name}の読み取りを開始")
        try:
            #データを読み込んでチップ毎のデータを取得
            output_lines=read_traydata(
                csv_file,
                {"lot_name":lot_name,"machine_id":machine_id}
            )

            for chip_data in output_lines:
                if chip_data[1]=="LINEOUT":
                    all_tray_in_chip_data+=[chip_data]
                    summary_info_dict["LINEOUT"]+=1

            normal_message_handling(app,f"{file_name}の読み取りが完了")
        
        except Exception as e:
            error_handling(app,f"データの変換に失敗しました:{e}")
            return

    #------------------------------------_ARRAYデータの出力開始-----------------------------------------------
    #アップロード先にすでにファイルがあればそれを読み込んで追記していく
    normal_message_handling(app,f"ARRAYデータの出力を開始")
    try:
        output_array_data_path=os.path.join(tmp_folder_path,"converted",f"{lot_name}_ARRAY.csv")
        write_traydata(output_array_data_path,all_tray_in_chip_data,add_flag=False)
        normal_message_handling(app,f"{file_name}の出力が完了しました")
    except Exception as e:
        error_handling(app,f"ARRAYデータの出力に失敗しました:{e}")
        return

    #----------------------------------------summary.csvの作成-----------------------------------------------------
    normal_message_handling(app,f"summaryファイルの作成を開始します")
    try:
        #変換した内容を出力
        output_summary_file=os.path.join(tmp_folder_path,"converted","summary.csv")
        create_summaryfie(output_summary_file,summary_info_dict,product_name,wp_lot_name,lot_name)
        normal_message_handling(app,f"summaryファイルの作成が完了")
    except Exception as e:
        error_handling(app,f"Summaryファイルの作成に失敗しました:{e}")
        return

    #OUT側パスにアップロード
    #tmp/convetedの中身をアップロード
    normal_message_handling(app,f"変換後データのアップロードを開始します")

    #フォルダを作成する
    #LotNameのフォルダが無い場合->LotName名のフォルダを作成
    #LotNameのフォルダがある場合->LotName-n名のフォルダを作成
    upload_folder_path=""
    try:
        if not os.path.exists(output_folder_path_lot):
            upload_folder_path=output_folder_path_lot
        else:
            n=1
            while os.path.exists(os.path.join(output_folder_path,f"{lot_name}-{n}")):
                n=n+1
            upload_folder_path=os.path.join(output_folder_path,f"{lot_name}-{n}")

        os.makedirs(upload_folder_path)
    except Exception as e:
        error_handling(app,f"OUTPUTフォルダの作成に失敗しました:{e})")
        return

    try:
        csv_file_list=glob.glob(os.path.join(tmp_folder_path,"converted","*.csv"))
        for csv_file in csv_file_list:
            shutil.copy(csv_file,os.path.join(upload_folder_path,os.path.basename(csv_file)))
            normal_message_handling(app,f"{csv_file}のアップロードが完了")
    except Exception as e:
        error_handling(app,f"OUTPUTフォルダへのアップロードで異常が発生しました:{e})")
        return

    #ver0.0.5で追加。設備生データのアップロード 
    #フォルダを作成する
    #LotNameのフォルダが無い場合->LotName名のフォルダを作成
    #LotNameのフォルダがある場合->LotName-n名のフォルダを作成
    normal_message_handling(app,f"設備生データのアップロードを開始します")
    raw_data_upload_folder_path="" #実際の出力先
    try:
        if not os.path.exists(raw_data_output_path_lot):
            raw_data_upload_folder_path=raw_data_output_path_lot
        else:
            n=1
            while os.path.exists(os.path.join(raw_data_output_path,f"{lot_name}-{n}")):
                n=n+1
            raw_data_upload_folder_path=os.path.join(raw_data_output_path,f"{lot_name}-{n}")

        os.makedirs(raw_data_upload_folder_path)
    except Exception as e:
        error_handling(app,f"設備生データのOUTPUTフォルダの作成に失敗しました:{e})")
        return

    try:
        csv_file_list=glob.glob(os.path.join(tmp_folder_path,"*.csv"))
        for csv_file in csv_file_list:
            shutil.copy(csv_file,os.path.join(raw_data_upload_folder_path,os.path.basename(csv_file)))
            normal_message_handling(app,f"{csv_file}のアップロードが完了")
    except Exception as e:
        error_handling(app,f"設備生データのOUTPUTフォルダへのアップロードで異常が発生しました:{e})")
        return
    
    normal_message_handling(app,f"{lot_name}の処理に成功しました")

    app.mergeResult=(True,"0") #処理に成功したことを示す

    return

