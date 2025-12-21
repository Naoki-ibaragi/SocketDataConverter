import os
import shutil
from . import settings
import glob
import re
from .header import chikugo_picker_header,chikugo_clt_header
import time

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

#宮崎のCLTのデータを筑後形式に変換
def miyazaki_to_chikugo_clt(line,lot_no):
    data_dict={}
    for item in chikugo_clt_header:
        data_dict[item]=""

    miyazaki_data_list=line.replace("\n","").split(",")
    #宮崎仕様のデータにある項目はそれを入れていく
    data_dict["SerialNo"]=miyazaki_data_list[0]
    data_dict["TrayNo"]=miyazaki_data_list[1]
    data_dict["TrayRank"]=miyazaki_data_list[2]
    data_dict["TrayX"]=miyazaki_data_list[3]
    data_dict["TrayY"]=miyazaki_data_list[4]
    data_dict["RingID"]=miyazaki_data_list[5]
    data_dict["WaferNo"]=miyazaki_data_list[6]
    data_dict["WaferX"]=miyazaki_data_list[7]
    data_dict["WaferY"]=miyazaki_data_list[8]

    data_dict["TEST1"]=miyazaki_data_list[13]
    data_dict["TEST1_℃"]=miyazaki_data_list[14]
    data_dict["TEST2"]=miyazaki_data_list[15]
    data_dict["TEST2_℃"]=miyazaki_data_list[16]
    data_dict["TEST3"]=miyazaki_data_list[17]
    data_dict["TEST3_℃"]=miyazaki_data_list[18]
    data_dict["TEST4"]=miyazaki_data_list[19]
    data_dict["TEST4_℃"]=miyazaki_data_list[20]
    data_dict["CHIPT_IP1"]=miyazaki_data_list[26]
    data_dict["CHIPT_IP2"]=miyazaki_data_list[26]


    #ダミーで入れておくところ
    data_dict["TrayMagazine"]="TM00000000"
    data_dict["DCGMagazine"]="DM00000000"
    data_dict["LotNo"]=lot_no
    data_dict["IN_Magazine"]="TM00000000"
    data_dict["IN_TrayNo"]="INTRAY00000000"
    data_dict["IN_TrayX"]="1"
    data_dict["IN_TrayY"]="1"

    return data_dict

def miyazaki_to_chikugo_picker(line,lot_no):

    data_dict={}
    for item in chikugo_clt_header:
        data_dict[item]=""

    miyazaki_data_list=line.replace("\n","").split(",")
    #宮崎仕様のデータにある項目はそれを入れていく
    data_dict["SerialNo"]=miyazaki_data_list[0]
    data_dict["TrayNo"]=miyazaki_data_list[1]
    data_dict["TrayRank"]=miyazaki_data_list[2]
    data_dict["TrayX"]=miyazaki_data_list[3]
    data_dict["TrayY"]=miyazaki_data_list[4]
    data_dict["RingID"]=miyazaki_data_list[5]
    data_dict["WaferNo"]=miyazaki_data_list[6]
    data_dict["WaferX"]=miyazaki_data_list[7]
    data_dict["WaferY"]=miyazaki_data_list[8]

    #ダミーで入れておくところ
    data_dict["TrayMagazine"]="TM00000000"
    data_dict["DCGMagazine"]="DM00000000"
    data_dict["LotNo"]=lot_no

    return data_dict

#LotNo,LotNo-nというフォルダ名のパスリストを取得する
#def get_input_folder_list(base_path,lot_name):
#    start_time=time.time()
#    #パターン: "ABCDE" または "ABCDE-数字"
#    pattern = re.compile(rf"^{lot_name}(-\d+)?$")
#
#    all_folders = [
#        name for name in os.listdir(base_path)
#        if os.path.isdir(os.path.join(base_path, name))
#    ]

#    target_folders = [os.path.join(base_path,f) for f in all_folders if pattern.match(f)]
#    end_time=time.time()
#    print(f"ver1 time:{end_time-start_time}")
#    return target_folders

#高速版
def get_input_folder_list(base_path, lot_name):
    pattern = re.compile(rf"^{lot_name}(?:-\d+)?$")

    target_folders = []
    with os.scandir(base_path) as entries:
        for entry in entries:
            if entry.is_dir() and pattern.match(entry.name):
                target_folders.append(entry.path)

    return target_folders

#メイン関数
def sorter_lot_start(app,data_dict,manual_flag=False):
    lot_name=data_dict["lotno"] #ATP工注
    product_name=data_dict["product_name"] #機種名
    machine_id=data_dict["id"] #装置番号
    wp_lot_name=data_dict["wp_lotno"] #装置番号
    work_quantity=data_dict["quantity"] #仕掛け数
    operator_id=data_dict["operator_id"] #オペレーターID

    if not manual_flag:
        input_folder_path=os.path.join(app.address_dict["DATAPATH"]["LOTSTART_IN"])
        output_folder_path=app.address_dict["DATAPATH"]["LOTSTART_OUT"]
        tmp_folder_path=app.address_dict["DATAPATH"]["LOTSTART_TMP"]
    else: 
        input_folder_path=os.path.join(app.address_dict["MANUAL_DATAPATH"]["LOTSTART_IN"])
        output_folder_path=app.address_dict["MANUAL_DATAPATH"]["LOTSTART_OUT"]
        tmp_folder_path=app.address_dict["MANUAL_DATAPATH"]["LOTSTART_TMP"]

    normal_message_handling(app,f"{lot_name}の清武⇒筑後仕様への分類前データの変換を実施")

    #IN側パスのフォルダ有無確認
    #フォルダ名がLotNoのもの及びLotNo-nのものを確認する
    try:
        input_folders=get_input_folder_list(input_folder_path,lot_name)
        if len(input_folders)==0:
            error_handling(app,f"LotStart時の参照データ先が存在しません")
            return
    except Exception as e:
        error_handling(app,f"LotStart時の参照データ先の検証でエラーが発生しました]:{e}")
        return

    normal_message_handling(app,f"参照データ先のフォルダ一覧を取得しました")

    #OUT側パスのフォルダ有無確認
    if not os.path.exists(output_folder_path):
        error_handling(app,f"LotStart時の出力データ先が存在しません:{output_folder_path}")
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

    normal_message_handling(app,f"tmpフォルダの中身の削除が完了しました")

    #IN側パスのトレイデータをtmpフォルダにコピー
    normal_message_handling(app,f"IN側のパスのトレイデータをtmpフォルダにコピーします")
    try:
        for input_folder in input_folders:
            csv_file_list=glob.glob(os.path.join(input_folder,"*.csv"))
            csv_file_list=[ csv_file for csv_file in csv_file_list if len(os.path.basename(csv_file).split(".")[0])==20 ]
            for csv_file in csv_file_list:
                shutil.copy(csv_file,os.path.join(tmp_folder_path,os.path.basename(csv_file)))
                normal_message_handling(app,f"{csv_file}をコピーしました")
    except Exception as e:
        error_handling(app,f"INファイルのコピーで異常が発生しました:{e})")
        return

    #データ変換を実施
    csv_file_list=glob.glob(os.path.join(tmp_folder_path,"*.csv"))
    if len(csv_file_list)==0: #tmpフォルダ内のファイル数が0であれば終了
        error_handling(app,f"変換対象のトレイデータが1つも存在しません")
        return

    normal_message_handling(app,f"清武データから筑後データへの変換を実施")
    file_type=None
    for csv_file in csv_file_list:
        output_lines=[]
        file_name=os.path.basename(csv_file)
        normal_message_handling(app,f"{file_name}の変換を開始")
        try:
            with open(csv_file,"r") as f:
                line=f.readline() #header行を取得して、CLTまで実施済のデータかトレイ移載までのデータかを確認
                n=1
                if file_type==None:
                    if "TEST1" in line: #CLT実施済
                        file_type="CLT"
                    else: 
                        file_type="PICKER"
                while line:
                    if n>1:
                        if file_type=="CLT":
                            converted_line=miyazaki_to_chikugo_clt(line,lot_name)
                            output_lines.append(converted_line)
                        if file_type=="PICKER":
                            converted_line=miyazaki_to_chikugo_picker(line,lot_name)
                            output_lines.append(converted_line)
                    line=f.readline() #header行を取得して、CLTまで実施済のデータかトレイ移載までのデータかを確認
                    n=n+1
            
            #変換した内容を出力
            output_csv_file=os.path.join(tmp_folder_path,"converted",file_name)
            with open(output_csv_file,"w") as of:
                #header出力
                if file_type=="CLT":
                    header_line=",".join(chikugo_clt_header)+"\n"
                    of.write(header_line)
                elif file_type=="PICKER":
                    header_line=",".join(chikugo_picker_header)+"\n"
                    of.write(header_line)

                for chip_data in output_lines:
                    output_line=""
                    for item in chikugo_clt_header:
                        output_line+=chip_data[item]+","
                    
                    of.write(output_line[0:-1]+"\n") #最後のカンマを省く

            normal_message_handling(app,f"{file_name}の変換が完了")
        
        except Exception as e:
            error_handling(app,f"データの変換に失敗しました:{e}")
            return

    #OUT側パスにアップロード
    #tmp/convetedの中身をアップロード
    normal_message_handling(app,f"変換後データのアップロードを開始します")
    output_folder_path_lot=os.path.join(output_folder_path,lot_name)
    try:
        if not os.path.exists(output_folder_path_lot):
            os.makedirs(output_folder_path_lot)
    except Exception as e:
            error_handling(app,f"アップロード先フォルダの作成に失敗しました:{e}")

    #本番運用時はコメント外す
    #if os.path.exists(output_folder_path_lot):
    #    app.mergeResult=False
    #    app.log_message(f"出力先のロットフォルダがすでに存在しています")
    #    log_file_message(f"出力先のロットフォルダがすでに存在しています","error")
    #    return

    try:
        csv_file_list=glob.glob(os.path.join(tmp_folder_path,"converted","*.csv"))
        for csv_file in csv_file_list:
            shutil.copy(csv_file,os.path.join(output_folder_path_lot,os.path.basename(csv_file)))
            normal_message_handling(app,f"{file_name}のアップロードが完了")
    except Exception as e:
        error_handling(app,f"OUTPUTフォルダへのアップロードで異常が発生しました:{e})")
        return

    normal_message_handling(app,f"{lot_name}の処理に成功しました")

    app.mergeResult=(True,"0") #処理に成功したことを示す

    return
