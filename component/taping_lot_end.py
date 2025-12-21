import os
import shutil
from . import settings
import glob
from .header import miyazaki_taping_header

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
def chikugo_to_miyazaki_taping(line,lot_name,machine_id,rank,remain_flag=False):
    data_list=["" for i in range(len(miyazaki_taping_header))]
    chikugo_data_list=line.replace("\n","").split(",")
    #宮崎仕様のデータにある項目はそれを入れていく
    #宮崎データのヘッダーは固有になっていないのでdictが使用できない
    #------------------総合-----------------------
    data_list[0]=adjust_int(chikugo_data_list[0],5) #SerialNo
    data_list[1]=chikugo_data_list[2] #TrayNo
    data_list[2]=chikugo_data_list[3] #TrayRank
    data_list[3]=adjust_int(chikugo_data_list[4],5) #TrayX
    data_list[4]=adjust_int(chikugo_data_list[5],5) #TrayY
    data_list[5]=chikugo_data_list[7] #Header名はLotNoだが、RingIDを入れる
    #------------------ピッカー-----------------------
    data_list[6]=adjust_int(chikugo_data_list[8],5) #WaferNo
    data_list[7]=adjust_int(chikugo_data_list[9],5) #WaferX
    data_list[8]=adjust_int(chikugo_data_list[10],5) #WaferY
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
    data_list[31]=chikugo_data_list[32] #SORT.NO CHIPT_SP3にSORT.NOをいれている
    data_list[32]=chikugo_data_list[33] #TOTAL
    data_list[33]="FF" #LD
    data_list[34]="FF" #IP
    data_list[35]="FF" #ULD
    #------------------TAPING-----------------------
    if remain_flag==False: #残留データではないデータ
        #LINEOUTの場合を先に分岐する
        if chikugo_data_list[48] == "LINEOUT": #ReelCount
            data_list[1]="LINEOUT"
            data_list[36]=adjust_int(str(machine_id),2) #TPG.NO
            data_list[37]=""
            data_list[38]=""
            data_list[39]=""
            data_list[40]="" #ReelID
            data_list[41]="" #PocketID
        else: #LINEOUTではない場合
            data_list[36]=adjust_int(str(machine_id),2) #TPG.NO
            #BINについては下記の対応を実施
            #IP1=0 and IP2=0 => TOTAL=0
            #IP1=D => TOTAL=21,IP=21
            #IP2=D => TOTAL=41,IP=41
            data_list[38]="FF" #LD 筑後データにはLDという区分がないのでFFを入れておく
            if chikugo_data_list[40]=="0" and chikugo_data_list[41]=="0": #良品
                data_list[37]="FF" #TOTAL
                data_list[39]="FF" #IP
            elif chikugo_data_list[40]=="D" and chikugo_data_list[41]=="0": #表面外観異常
                data_list[37]="21" #TOTAL
                data_list[39]="21" #IP
            elif chikugo_data_list[40]=="0" and chikugo_data_list[41]=="D": #裏面外観異常
                data_list[37]="41" #TOTAL
                data_list[39]="41" #IP
            else: #不明
                data_list[37]="" #TOTAL
                data_list[39]="" #IP
            data_list[40]=chikugo_data_list[48] #RealID
            data_list[41]=chikugo_data_list[49] #PocketID
    else:
        data_list[36]="" #TPG.NO
        data_list[37]=""
        data_list[38]=""
        data_list[39]=""
        data_list[40]=""
        data_list[41]=""

    return data_list

#ファイルを読み込んで、チップ単位のリストが入ったリストを返す
#ラインアウト数を2個目の返り値として返す
def read_traydata(traydata_path,d):
    output_lines=[]
    lot_name=d["lot_name"]
    machine_id=d["machine_id"]
    rank=d["rank"]
    remain_flag=d["remain_flag"]
    lineout_num=0 #ラインアウトしたチップ数
    with open(traydata_path,"r") as f:
        line=f.readline()
        line_num=1
        while line:
            if line_num>1:
                converted_line=chikugo_to_miyazaki_taping(line,lot_name,machine_id,rank,remain_flag)
                if "LINEOUT" in converted_line:
                    lineout_num+=1
                output_lines.append(converted_line)
            line=f.readline() 
            line_num+=1
    return output_lines,lineout_num

#output_linesの内容をファイルに書き込む
def write_traydata(output_path,output_lines,add_flag=False):
    if add_flag==False:
        with open(output_path,"w") as of:
            #header出力
            header_line=",".join(miyazaki_taping_header)+"\n"
            of.write(header_line)
            for chip_data in output_lines: #chip_dataはlist形式
                output_line=""
                for num in range(len(miyazaki_taping_header)):
                    output_line+=chip_data[num]+","
                
                of.write(output_line[0:-1]+"\n") #最後のカンマを省く
    elif add_flag: #追記モードで開く
        with open(output_path,"a+") as of:
            #追記の時はヘッダーを出力しない
            for chip_data in output_lines: #chip_dataはlist形式
                output_line=""
                for num in range(len(miyazaki_taping_header)):
                    output_line+=chip_data[num]+","
                
                of.write(output_line[0:-1]+"\n") #最後のカンマを省く

#summaryファイルを作成する
def create_summaryfile(summary_file_path,summary_info_dict,product_name,wp_lot_name,lot_name):
    summary_file_header=["ProductName","WpOrderNo","AtOrderNo","Quantity","PickUp","Pass","Fail","LineOut","Remain"]
    with open(summary_file_path,"w") as of:
        #header出力
        header_line=",".join(summary_file_header)+"\n"
        of.write(header_line)
        output_line=""
        output_line+=product_name+","
        output_line+=wp_lot_name+","
        output_line+=lot_name+","
        output_line+=str(summary_info_dict["PASS"]+summary_info_dict["FAIL"]+summary_info_dict["LINEOUT"]+summary_info_dict["REMAIN"])+","
        output_line+=str(summary_info_dict["PASS"]+summary_info_dict["FAIL"]+summary_info_dict["LINEOUT"])+","
        output_line+=str(summary_info_dict["PASS"])+","
        output_line+=str(summary_info_dict["FAIL"])+","
        output_line+=str(summary_info_dict["LINEOUT"])+","
        output_line+=str(summary_info_dict["REMAIN"])+"\n"
        of.write(output_line)

def taping_lot_end(app,data_dict,manual_flag=False):
    #ロット番号、ランク、機台IDを受け取る
    lot_name=data_dict["lotno"] #ATP工注(メインロットNo)
    machine_id=data_dict["id"] #機台番号
    rank=data_dict["rank"] #ランク
    wp_lot_name=data_dict["wp_lotno"] #WP工注
    product_name=data_dict["product_name"] #機種名

    if not manual_flag:
        input_folder_path=os.path.join(app.address_dict["DATAPATH"]["LOTEND_IN"],lot_name)
        output_folder_path=app.address_dict["DATAPATH"]["LOTEND_OUT"]
        output_folder_path_hasuu=app.address_dict["DATAPATH"]["LOTEND_OUT_HASUU"]
        tmp_folder_path=app.address_dict["DATAPATH"]["LOTEND_TMP"]
        raw_data_output_path=app.address_dict["DATAPATH"]["RAWDATA_OUT"] #生データ出力先
        raw_data_output_path_lot=os.path.join(raw_data_output_path,lot_name) #生データ出力先(ロット名フォルダ)
    else:
        input_folder_path=os.path.join(app.address_dict["MANUAL_DATAPATH"]["LOTEND_IN"],lot_name)
        output_folder_path=app.address_dict["MANUAL_DATAPATH"]["LOTEND_OUT"]
        output_folder_path_hasuu=app.address_dict["MANUAL_DATAPATH"]["LOTEND_OUT_HASUU"]
        tmp_folder_path=app.address_dict["MANUAL_DATAPATH"]["LOTEND_TMP"]
        raw_data_output_path=app.address_dict["MANUAL_DATAPATH"]["RAWDATA_OUT"] #生データ出力先
        raw_data_output_path_lot=os.path.join(raw_data_output_path,lot_name) #生データ出力先(ロット名フォルダ)

    normal_message_handling(app,f"{lot_name}の筑後⇒清武仕様へのテーピング後データの変換を実施")

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
    normal_message_handling(app,f"リールデータをtmpフォルダにコピーします")
    try:
        csv_file_list=glob.glob(os.path.join(input_folder_path,"*.csv"))
        #csv_file_list=[ csv_file for csv_file in csv_file_list if len(os.path.basename(csv_file).split(".")[0])==20 ]
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
    
    #------------------------ここからメインのデータ変換処理-------------------------------------------
    #summaryファイルにのせる情報を入れるためのdict
    summary_info_dict={
        "PASS":0,
        "FAIL":0,
        "LINEOUT":0,
        "REMAIN":0,
    }

    #-------------------------良品個別リールデータの変換を開始----------------------------------------
    reel_num=1
    normal_message_handling(app,f"良品個別データの変換を開始")
    all_reel_in_chip_data=[] #全ての個別リールデータの中身を合わせたもの(TAPEデータ作成用)
    while os.path.exists(os.path.join(tmp_folder_path,f"{lot_name}_{reel_num}.csv")):
        file_name=f"{lot_name}_{reel_num}.csv"
        normal_message_handling(app,f"{file_name}の変換を開始")
        try:
            output_lines,_=read_traydata(
                os.path.join(tmp_folder_path,f"{lot_name}_{reel_num}.csv"),
                {"lot_name":lot_name,"rank":rank,"machine_id":machine_id,"remain_flag":False}
                )
                        
            #出力ファイルの設定
            #出力ファイルのreel_numを3桁に0パディングする
            output_file_name=f"{lot_name}-{rank}-{adjust_int(reel_num,3)}.csv"
            output_csv_file=os.path.join(tmp_folder_path,"converted",output_file_name)
            #ファイルに書き込む
            write_traydata(output_csv_file,output_lines)
            summary_info_dict["PASS"]+=len(output_lines) #summaryファイル掲載用に良品数を記録する
            all_reel_in_chip_data+=output_lines #_TAPEデータ出力用に良品のデータをまとめる
            normal_message_handling(app,f"{file_name}の変換が完了")
        
        except Exception as e:
            app.mergeResult=(False,"1")
            normal_message_handling(app,f"データの変換に失敗しました:{e}")
            return
    
        reel_num+=1

    #-----------------------------不良トレイ個別データの変換開始-----------------------------------------
    normal_message_handling(app,f"不良個別データの変換を開始")
    for csv_file in csv_file_list:
        if "_NG" not in csv_file:
            continue
        output_lines=[]
        file_name=os.path.basename(csv_file)
        tray_id=file_name.replace("_NG.csv","")
        output_file_name=tray_id+".csv"
        normal_message_handling(app,f"{file_name}の変換を開始")
        try:
            #データを読み込んでチップ毎のデータを取得
            output_lines,_=read_traydata(
                csv_file,
                {"lot_name":lot_name,"rank":rank,"machine_id":machine_id,"remain_flag":False}
            )

            #出力パス設定
            output_csv_file=os.path.join(tmp_folder_path,"converted",output_file_name)
            #ファイルに書き込む
            write_traydata(output_csv_file,output_lines)
            summary_info_dict["FAIL"]+=len(output_lines) #summaryファイル掲載用
            normal_message_handling(app,f"{file_name}の変換が完了")
        
        except Exception as e:
            error_handling(app,f"データの変換に失敗しました:{e}")
            return

    #-----------------------_REMAINデータの変換開始---------------------------------
    normal_message_handling(app,f"残留チップデータの変換を開始")
    for csv_file in csv_file_list:
        if "_REMAIN" not in csv_file:
            continue
        output_lines=[]
        file_name=os.path.basename(csv_file)
        tray_id=file_name.replace("_REMAIN.csv","")
        output_file_name=tray_id+"_REMAIN.csv"
        normal_message_handling(app,f"{file_name}の変換を開始")
        try:
            #データを読み込んでチップ毎のデータを取得
            output_lines,_=read_traydata(
                csv_file,
                {"lot_name":lot_name,"rank":rank,"machine_id":machine_id,"remain_flag":True}
            )

            #変換した内容を出力
            output_csv_file=os.path.join(tmp_folder_path,"converted",output_file_name)
            #ファイルに出力
            write_traydata(output_csv_file,output_lines)
            summary_info_dict["REMAIN"]+=len(output_lines) #summaryファイル掲載用
            normal_message_handling(app,f"{file_name}の変換が完了")

        except Exception as e:
            error_handling(app,f"データの変換に失敗しました:{e}")
            return
        
    #-----------------------------_TAPEデータの出力を実施----------------------------------------------
    output_folder_path_lot=os.path.join(output_folder_path,lot_name)
    server_tape_data_path=os.path.join(output_folder_path_lot,f"{lot_name}_TAPE.csv")
    tmp_tape_data_path=os.path.join(tmp_folder_path,"converted",f"{lot_name}_TAPE.csv")
    tape_data_already_exists_flag=False
    #_TAPEデータの変換開始
    #アップロード先にすでにファイルがあればそれを読み込んで追記していく
    if os.path.exists(server_tape_data_path):
        shutil.copy(server_tape_data_path,tmp_tape_data_path)
        tape_data_already_exists_flag=True

    normal_message_handling(app,f"TAPEデータの出力を開始")
    try:
        if tape_data_already_exists_flag: #_TAPEデータがすでにサーバー上に存在していた場合
            normal_message_handling(app,f"既存のTAPEデータに追記します")
            write_traydata(tmp_tape_data_path,all_reel_in_chip_data,add_flag=True)
        else:
            normal_message_handling(app,f"TAPEデータを新規作成します")
            write_traydata(tmp_tape_data_path,all_reel_in_chip_data,add_flag=False)

        normal_message_handling(app,f"{file_name}の出力が完了しました")
    except Exception as e:
        error_handling(app,f"TAPEデータの出力に失敗しました:{e}")
        return

    #------------------------------------_ARRAYデータの変換開始-----------------------------------------------
    #アップロード先にすでにファイルがあればそれを読み込んで追記していく
    server_all_data_path=os.path.join(output_folder_path_lot,f"{lot_name}_ARRAY.csv")
    all_data_already_exists_flag=False
    tmp_all_data_path=os.path.join(tmp_folder_path,"converted",f"{lot_name}_ARRAY.csv")
    if os.path.exists(server_all_data_path):
        shutil.copy(server_tape_data_path,tmp_all_data_path)
        all_data_already_exists_flag=True

    normal_message_handling(app,f"ARRAYデータの出力を開始")
    try:
        #データを読み込んでチップ毎のデータを取得
        output_lines,lineout_num=read_traydata(
            os.path.join(tmp_folder_path,f"{lot_name}_ALL.csv"),
            {"lot_name":lot_name,"rank":rank,"machine_id":machine_id,"remain_flag":False}
        )

        summary_info_dict["LINEOUT"]=lineout_num
            
        if all_data_already_exists_flag: #_ALLデータがすでにサーバー上に存在していた場合
            normal_message_handling(app,f"既存のARRAYデータに追記します")
            write_traydata(tmp_all_data_path,output_lines,add_flag=True) #ver0.0.7で変更。元々テープデータと同じものを作成してしまっていた
        else: #新規にALLファイルを作成する場合
            normal_message_handling(app,f"ARRAYデータを新規作成します")
            write_traydata(tmp_all_data_path,output_lines,add_flag=False) #ver0.0.7で変更。元々テープデータと同じものを作成してしまっていた

        normal_message_handling(app,f"{file_name}の出力が完了しました")
    except Exception as e:
        error_handling(app,f"ARRAYデータの出力に失敗しました:{e}")
        return

    #----------------------------------------summary.csvの作成-----------------------------------------------------
    normal_message_handling(app,f"summaryファイルの作成を実施します")
    try:
        #変換した内容を出力
        output_summary_file=os.path.join(tmp_folder_path,"converted","summary.csv")
        create_summaryfile(output_summary_file,summary_info_dict,product_name,wp_lot_name,lot_name)
        normal_message_handling(app,f"summaryファイルの作成が完了")
    except Exception as e:
        error_handling(app,f"Summaryファイルの作成に失敗しました:{e}")
        return

    #OUT側パスにアップロード
    #tmp/convetedの中身をアップロード
    normal_message_handling(app,f"変換後データのアップロード先フォルダを作成します")
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
    
    normal_message_handling(app,f"変換後データのアップロード先フォルダを作成しました:{upload_folder_path}")
    
    #端数データ(Remainデータ)アップロード用のフォルダを作成
    normal_message_handling(app,f"変換後端数データのアップロード先フォルダを作成します")
    try:
        upload_folder_path_hasuu=os.path.join(output_folder_path_hasuu,lot_name)
        if not os.path.exists(upload_folder_path_hasuu):
            os.makedirs(upload_folder_path_hasuu)
    except Exception as e:
        error_handling(app,f"端数データOUTPUTフォルダの作成に失敗しました:{e})")
        return

    normal_message_handling(app,f"変換後データをアップロードします")
    try:
        csv_file_list=glob.glob(os.path.join(tmp_folder_path,"converted","*.csv"))
        for csv_file in csv_file_list:
            if not "_REMAIN" in os.path.basename(csv_file): #通常ファイルのアップロード
                shutil.copy(csv_file,os.path.join(upload_folder_path,os.path.basename(csv_file)))
                normal_message_handling(app,f"{csv_file}のアップロードが完了")
            else: #端数ファイルのアップロード
                shutil.copy(csv_file,os.path.join(upload_folder_path_hasuu,os.path.basename(csv_file)))
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

