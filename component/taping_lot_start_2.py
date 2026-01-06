import os
import shutil
import time
from . import settings
import glob
from .header import chikugo_sorter_header
import oracledb

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

#数字文字列の0paddingを取る
def de_padding(type,num):
    try:
        return str(int(num))
    except:
        raise ValueError(f"{type}に数値に変換できない文字列が含まれています:{num}")

#宮崎仕様の分類後データを筑後テーピング仕様に変換
#rankが全行で等しいかを確認
def miyazaki_to_chikugo_taping(line,lot_name,lot_rank):
    data_dict={}
    for item in chikugo_sorter_header:
        data_dict[item]=""

    miyazaki_data_list=line.replace("\n","").split(",")

    #ランクのチェックを入れる
    chip_rank=miyazaki_data_list[2]
    if chip_rank != lot_rank: 
        raise ValueError("1つのcsvファイル内に異なるランクが混ざっています")

    #宮崎仕様のデータにある項目はそれを入れていく
    data_dict["SerialNo"]=de_padding("serial",miyazaki_data_list[0])
    data_dict["TrayMagazine"]="TM00000000"
    data_dict["TrayNo"]=miyazaki_data_list[1]
    data_dict["TrayRank"]=miyazaki_data_list[2]
    data_dict["TrayX"]=de_padding("tray_x",miyazaki_data_list[3])
    data_dict["TrayY"]=de_padding("tray_y",miyazaki_data_list[4])
    data_dict["RingID"]=miyazaki_data_list[5]
    data_dict["WaferNo"]=de_padding("waferNo",miyazaki_data_list[6])
    data_dict["WaferX"]=de_padding("wafer_x",miyazaki_data_list[7])
    data_dict["WaferY"]=de_padding("wafer_y",miyazaki_data_list[8])
    data_dict["DCGMagazine"]="DM00000000"
    data_dict["SP1"]=""
    data_dict["SP2"]=""
    data_dict["SP3"]=""
    data_dict["IN_Magazine"]="TM00000000"
    data_dict["IN_TrayNo"]="INTRAY00000000"
    data_dict["IN_TrayX"]="1"
    data_dict["IN_TrayY"]="1"

    data_dict["CHIPT_TOTAL"]=miyazaki_data_list[11]
    data_dict["TEST1"]=miyazaki_data_list[13]
    data_dict["TEST1_℃"]=miyazaki_data_list[14]
    data_dict["TEST2"]=miyazaki_data_list[15]
    data_dict["TEST2_℃"]=miyazaki_data_list[16]
    data_dict["TEST3"]=miyazaki_data_list[17]
    data_dict["TEST3_℃"]=miyazaki_data_list[18]
    data_dict["TEST4"]=miyazaki_data_list[19]
    data_dict["TEST4_℃"]=miyazaki_data_list[20]
    data_dict["CHIPT_IP1"]=miyazaki_data_list[27]
    data_dict["CHIPT_IP2"]=miyazaki_data_list[27]
    data_dict["CHIPT_SP1"]=""   
    data_dict["CHIPT_SP2"]=""
    data_dict["CHIPT_SP3"]=miyazaki_data_list[31] #SORT.NO(ソーターの号機番号)をこっちに避難する

    data_dict["SORT_TOTAL"]=miyazaki_data_list[32]
    data_dict["SORT_IP1"]=miyazaki_data_list[34]
    data_dict["SORT_IP2"]=miyazaki_data_list[34]
    data_dict["SORT_SP1"]=""
    data_dict["SORT_SP2"]=""
    data_dict["SORT_SP3"]=""

    return data_dict

#csvファイルの1行目からデータをランクを取得する
def get_rank_from_line(line):
    rank=line.split(",")[2] #3列目がRank

    if rank not in ["A","B","C","D","E","F","0"]:
        raise ValueError(f"ランクの値が異常です:{rank}")
    
    return rank

#上位のoracle dbから子ロット情報データを取得する
def get_child_lot_data_from_db(app,parent_work_order):
    # Oracle Database 11g以前のバージョンに接続するため、thick接続モードを使用
    # thick接続モードを初期化（Oracle Instant Clientが必要）
    child_lot_list_main=[]
    child_lot_list_hasuu=[]
    normal_message_handling(app,f"上位への接続を開始")
    try:
        # Oracle Instant Clientのパスを指定する場合（必要に応じて変更）
        oracledb.init_oracle_client(lib_dir=r"C:\\oracle\\instantclient_23_0")
    except Exception as e:
        raise RuntimeError("Oracle Instant Clientの初期化に失敗しました") from e

    # Oracle Databaseへの接続設定
    username = "atpusr"
    password = "atpusr"
    host = "10.128.21.81"
    port = 1521
    sid="CIM"

    try:
        # thin接続を作成
        # DSN形式での接続
        dsn = oracledb.makedsn(host, port, sid=sid)
        connection = oracledb.connect(user=username, password=password, dsn=dsn)

        normal_message_handling(app,"Oracle Databaseに正常に接続しました")

        # カーソルを作成してクエリを実行
        cursor = connection.cursor()

        sql_query_1 = """
        SELECT B.NO_ATP_LOT
        FROM ATPCIM.CV_INFO_LOT B
        WHERE B.NO_ATP_WORK_ORDER = :no_atp_lot
        """

        # クエリを実行（バインド変数を使用）
        cursor.execute(sql_query_1, no_atp_lot=parent_work_order)

        # 結果を取得して表示
        results = cursor.fetchall()
        no_atp_lot_value=results[0][0]
        parent_lot_name=no_atp_lot_value
        normal_message_handling(app,f"親ATPロットの取得完了:{parent_lot_name}")

         # SQLクエリ（バインド変数を使用）
        sql_query_atp_lot = """
        --Assy後倉庫のロットと統合分抽出
        SELECT NO_ATP_WORK_ORDER, max(BUNRUI) AS BUNRUI FROM ( 
        --対象ロットのソースロット
        SELECT B.NO_ATP_WORK_ORDER, 'MAIN' AS BUNRUI 
        FROM ATPCIM.CV_INFO_RESERVE A, ATPCIM.CV_INFO_LOT B 
        WHERE A.CD_LINE_INV = 'L1' AND A.NO_ATP_LOT_INV = :no_atp_lot
        AND   A.CD_LINE_INV = B.CD_LINE AND A.NO_ATP_LOT_STK = B.NO_ATP_LOT 
        UNION 
        --対象ロットのソースロットの親
        SELECT C.NO_ATP_WORK_ORDER, 'MAIN' AS BUNRUI 
        FROM ATPCIM.CV_INFO_LOT C WHERE C.NO_ATP_LOT IN (
        SELECT B.NO_SYS_LOT_DVPRT 
        FROM ATPCIM.CV_INFO_RESERVE A, ATPCIM.CV_INFO_LOT B 
        WHERE A.CD_LINE_INV = 'L1' AND A.NO_ATP_LOT_INV = :no_atp_lot
        AND   A.CD_LINE_INV = B.CD_LINE AND A.NO_ATP_LOT_STK = B.NO_ATP_LOT) 
        UNION 
        --対象ロットのソースロットの統合ロット
        SELECT C.NO_ATP_WORK_ORDER, 'MAIN' AS BUNRUI 
        FROM ATPCIM.CV_INFO_RESERVE A, ATPCIM.CV_HIST_LOT_MERGE B, ATPCIM.CV_INFO_LOT C 
        WHERE A.CD_LINE_INV = 'L1' AND A.NO_ATP_LOT_INV = :no_atp_lot
        AND   A.CD_LINE_INV = B.CD_LINE AND A.NO_ATP_LOT_STK = B.NO_ATP_LOT 
        AND   B.CD_LINE = C.CD_LINE AND B.NO_LOT_CHILD = C.NO_ATP_LOT 
        UNION 
        --対象ロットのソースロットの統合ロットの親
        SELECT D.NO_ATP_WORK_ORDER, 'MAIN' AS BUNRUI 
        FROM ATPCIM.CV_INFO_LOT D 
        WHERE D.NO_ATP_LOT IN 
        (SELECT C.NO_SYS_LOT_DVPRT 
        FROM ATPCIM.CV_INFO_RESERVE A, ATPCIM.CV_HIST_LOT_MERGE B, ATPCIM.CV_INFO_LOT C 
        WHERE A.CD_LINE_INV = 'L1' AND A.NO_ATP_LOT_INV = :no_atp_lot
        AND   A.CD_LINE_INV = B.CD_LINE AND A.NO_ATP_LOT_STK = B.NO_ATP_LOT 
        AND   B.CD_LINE = C.CD_LINE AND B.NO_LOT_CHILD = C.NO_ATP_LOT 
        AND   SUBSTRB(C.NO_ATP_LOT,10,3) <> '.00') 
        UNION 
        --対象ロットに統合された端数ロットの親
        SELECT C.NO_ATP_WORK_ORDER, 'HASUU' AS BUNRUI 
        FROM ATPCIM.CV_INFO_LOT C 
        WHERE C.CD_LINE = 'L1' AND C.NO_ATP_LOT IN ( 
        SELECT B.NO_SYS_LOT_DVPRT 
        FROM ATPCIM.CV_INFO_LOT B 
        WHERE B.CD_LINE = 'L1' AND B.NO_ATP_LOT IN 
        (SELECT A.NO_LOT_CHILD
        FROM ATPCIM.CV_HIST_LOT_MERGE A
        WHERE A.CD_LINE = 'L1' AND A.NO_ATP_LOT = :no_atp_lot)) 
        UNION 
        --対象ロットに統合された端数ロットの親から検索
        SELECT B.NO_ATP_WORK_ORDER, 'HASUU' AS BUNRUI 
        FROM ATPCIM.CV_INFO_RESERVE A, ATPCIM.CV_INFO_LOT B 
        WHERE A.CD_LINE_INV = 'L1' AND A.NO_ATP_LOT_INV IN (SELECT NO_ATP_LOT 
        FROM ATPCIM.CV_INFO_LOT 
        WHERE CD_LINE = 'L1' AND NO_ATP_LOT IN 
        (SELECT B.NO_SYS_LOT_DVPRT 
        FROM ATPCIM.CV_HIST_LOT_MERGE A, ATPCIM.CV_INFO_LOT B 
        WHERE A.CD_LINE = 'L1' AND A.NO_ATP_LOT = :no_atp_lot
        AND   A.CD_LINE = B.CD_LINE AND A.NO_LOT_CHILD = B.NO_ATP_LOT)) 
        AND   A.CD_LINE_INV = B.CD_LINE AND A.NO_ATP_LOT_STK = B.NO_ATP_LOT 
        UNION 
        SELECT C.NO_ATP_WORK_ORDER, 'HASUU' AS BUNRUI 
        FROM ATPCIM.CV_INFO_LOT C WHERE C.NO_ATP_LOT IN ( 
        SELECT B.NO_SYS_LOT_DVPRT 
        FROM ATPCIM.CV_INFO_RESERVE A, ATPCIM.CV_INFO_LOT B 
        WHERE A.CD_LINE_INV = 'L1' AND A.NO_ATP_LOT_INV IN (SELECT NO_ATP_LOT 
        FROM ATPCIM.CV_INFO_LOT 
        WHERE CD_LINE = 'L1' AND NO_ATP_LOT IN 
        (SELECT B.NO_SYS_LOT_DVPRT 
        FROM ATPCIM.CV_HIST_LOT_MERGE A, ATPCIM.CV_INFO_LOT B 
        WHERE A.CD_LINE = 'L1' AND A.NO_ATP_LOT = :no_atp_lot
        AND   A.CD_LINE = B.CD_LINE AND A.NO_LOT_CHILD = B.NO_ATP_LOT)) 
        AND   A.CD_LINE_INV = B.CD_LINE AND A.NO_ATP_LOT_STK = B.NO_ATP_LOT) 
        UNION 
        SELECT C.NO_ATP_WORK_ORDER, 'HASUU' AS BUNRUI 
        FROM ATPCIM.CV_INFO_RESERVE A, ATPCIM.CV_HIST_LOT_MERGE B, ATPCIM.CV_INFO_LOT C 
        WHERE A.CD_LINE_INV = 'L1' AND A.NO_ATP_LOT_INV IN (SELECT NO_ATP_LOT 
        FROM ATPCIM.CV_INFO_LOT 
        WHERE CD_LINE = 'L1' AND NO_ATP_LOT IN 
        (SELECT B.NO_SYS_LOT_DVPRT 
        FROM ATPCIM.CV_HIST_LOT_MERGE A, ATPCIM.CV_INFO_LOT B 
        WHERE A.CD_LINE = 'L1' AND A.NO_ATP_LOT = :no_atp_lot
        AND   A.CD_LINE = B.CD_LINE AND A.NO_LOT_CHILD = B.NO_ATP_LOT)) 
        AND   A.CD_LINE_INV = B.CD_LINE AND A.NO_ATP_LOT_STK = B.NO_ATP_LOT 
        AND   B.CD_LINE = C.CD_LINE AND B.NO_LOT_CHILD = C.NO_ATP_LOT 
        UNION 
        SELECT D.NO_ATP_WORK_ORDER, 'HASUU' AS BUNRUI 
        FROM ATPCIM.CV_INFO_LOT D 
        WHERE D.NO_ATP_LOT IN 
        (SELECT C.NO_SYS_LOT_DVPRT 
        FROM ATPCIM.CV_INFO_RESERVE A, ATPCIM.CV_HIST_LOT_MERGE B, ATPCIM.CV_INFO_LOT C 
        WHERE A.CD_LINE_INV = 'L1' AND A.NO_ATP_LOT_INV IN (SELECT NO_ATP_LOT 
        FROM ATPCIM.CV_INFO_LOT 
        WHERE CD_LINE = 'L1' AND NO_ATP_LOT IN 
        (SELECT B.NO_SYS_LOT_DVPRT 
        FROM ATPCIM.CV_HIST_LOT_MERGE A, ATPCIM.CV_INFO_LOT B 
        WHERE A.CD_LINE = 'L1' AND A.NO_ATP_LOT = :no_atp_lot
        AND   A.CD_LINE = B.CD_LINE AND A.NO_LOT_CHILD = B.NO_ATP_LOT)) 
        AND   A.CD_LINE_INV = B.CD_LINE AND A.NO_ATP_LOT_STK = B.NO_ATP_LOT 
        AND   B.CD_LINE = C.CD_LINE AND B.NO_LOT_CHILD = C.NO_ATP_LOT 
        AND   SUBSTRB(C.NO_ATP_LOT,10,3) <> '.00')) 
        GROUP BY NO_ATP_WORK_ORDER 
        ORDER BY BUNRUI DESC, NO_ATP_WORK_ORDER ASC
        """

        # クエリを実行（バインド変数を使用）
        cursor.execute(sql_query_atp_lot, no_atp_lot=parent_lot_name)

        # 結果を取得して表示
        results = cursor.fetchall()

        #子ATP工注名のリストを作成
        for row in results:
            normal_message_handling(app,f"NO_ATP_WORK_ORDER: {row[0]}, BUNRUI: {row[1]}")
            if row[1]=="MAIN":
                child_lot_list_main.append(row[0])
            elif row[1]=="HASUU":
                child_lot_list_hasuu.append(row[0])

        # カーソルをクローズ
        cursor.close()

    except oracledb.Error as error:
        print(f"エラーが発生しました: {error}")

    finally:
        # 接続をクローズ
        if 'connection' in locals():
            connection.close()
            print("接続をクローズしました")
        
    return child_lot_list_main,child_lot_list_hasuu

def taping_lot_start_2(app,data_dict,manual_flag=False):
    lot_name=data_dict["lotno"] #対象のロット番号
    target_rank=data_dict["rank"] #対象のランク
    product_name=data_dict["product_name"] #機種名
    machine_id=data_dict["id"] #装置番号
    wp_lot_name=data_dict["wp_lotno"] #装置番号
    work_quantity=data_dict["quantity"] #仕掛け数
    operator_id=data_dict["operator_id"] #オペレーターID

    #子ロット情報を上位のDBから取得する
    start=time.perf_counter()
    try:
        child_lotname_list_main,child_lotname_list_hasuu=get_child_lot_data_from_db(app,lot_name)
    except Exception as e:
        error_handling(app,f"上位からの子ロット情報データ取得に失敗しました:{input_folder_path}")
        return
    end=time.perf_counter()
    normal_message_handling(app,f"上位からのデータ取得時間 : {end-start:.6f}秒")
    
    if len(child_lotname_list_main)+len(child_lotname_list_hasuu)==0:
        error_handling(app,f"親ロット{lot_name}に紐づいた子ロットが存在しません")
        return
    else:
        normal_message_handling(app,f"親ロット{lot_name}の子ロット一覧(MAIN):{child_lotname_list_main}")
        normal_message_handling(app,f"親ロット{lot_name}の子ロット一覧(HASUU):{child_lotname_list_hasuu}")

    if not manual_flag:
        #子ロットNoは複数あるので、input_folder_path,input_folder_path_hasuuはリストにする
        input_folder_path_list=[]
        input_folder_path_hasuu_list=[]
        for child_lot in child_lotname_list_main:
            input_folder_path_list.append(os.path.join(app.address_dict["DATAPATH"]["LOTSTART_IN"],child_lot)) #編集前データ置き場
        for child_lot in child_lotname_list_hasuu:
            input_folder_path_hasuu_list.append(os.path.join(app.address_dict["DATAPATH"]["LOTSTART_IN_HASUU"],child_lot)) #編集前データ置き場(端数)
        output_folder_path=app.address_dict["DATAPATH"]["LOTSTART_OUT"] #編集後データ置き場
        tmp_folder_path=app.address_dict["DATAPATH"]["LOTSTART_TMP"] #一時作業場所
    else:
        input_folder_path_list=[]
        input_folder_path_hasuu_list=[]
        for child_lot in child_lotname_list_main:
            input_folder_path_list.append(os.path.join(app.address_dict["DATAPATH"]["LOTSTART_IN"],child_lot)) #編集前データ置き場
        for child_lot in child_lotname_list_hasuu:
            input_folder_path_hasuu_list.append(os.path.join(app.address_dict["DATAPATH"]["LOTSTART_IN_HASUU"],child_lot)) #編集前データ置き場(端数)
        output_folder_path=app.address_dict["MANUAL_DATAPATH"]["LOTSTART_OUT"] #編集後データ置き場
        tmp_folder_path=app.address_dict["MANUAL_DATAPATH"]["LOTSTART_TMP"] #一時作業場所

    normal_message_handling(app,f"{lot_name}の清武⇒筑後仕様へのテーピング前データの変換を実施")

    #IN側パスのフォルダ有無確認
    #for input_folder_path in input_folder_path_list:
    #    if not os.path.exists(input_folder_path):
    #        error_handling(app,f"LotStart時の参照データ先が存在しません:{input_folder_path}")
    #        return

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
    file_count=0
    folder_count=0
    for item in os.listdir(tmp_folder_path):
        item_path = os.path.join(tmp_folder_path, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                if file_count>300:
                    raise ValueError("削除ファイル数が多すぎます")
                os.remove(item_path)  # ファイル削除
                file_count+=1
                normal_message_handling(app,f"{item_path}を削除しました")
            elif os.path.isdir(item_path):
                if folder_count>5:
                    raise ValueError("削除フォルダ数が多すぎます")
                shutil.rmtree(item_path)  # フォルダ削除
                folder_count+=1
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

    normal_message_handling(app,f"tmpフォルダの中身を削除が完了しました")

    #IN側パスのトレイデータをtmpフォルダにコピー
    normal_message_handling(app,f"IN側のパスのトレイデータをtmpフォルダにコピーします")
    try:
        for input_folder_path in input_folder_path_list:
            if os.path.exists(input_folder_path):
                csv_file_list=glob.glob(os.path.join(input_folder_path,"*.csv"))
                csv_file_list=[ csv_file for csv_file in csv_file_list if len(os.path.basename(csv_file).split(".")[0])==20 ] #良品トレイデータかの判定
                for csv_file in csv_file_list:
                    shutil.copy(csv_file,os.path.join(tmp_folder_path,os.path.basename(csv_file)))
    except Exception as e:
        error_handling(app,f"INファイルのコピーで異常が発生しました:{e})")
        return
    normal_message_handling(app,f"IN側のパスのトレイデータをtmpフォルダへのコピーが完了しました")

    #端数トレイ用のフォルダがあればそれもサーチする
    try:
        for input_folder_path_hasuu in input_folder_path_hasuu_list:
            normal_message_handling(app,f"端数フォルダパス:{input_folder_path_hasuu}")
            if os.path.exists(input_folder_path_hasuu):
                normal_message_handling(app,f"端数フォルダパス:{input_folder_path_hasuu} のトレイデータをtmpフォルダにコピーします")
                try:
                    csv_file_list=glob.glob(os.path.join(input_folder_path_hasuu,"*.csv"))
                    csv_file_list=[ csv_file for csv_file in csv_file_list if len(os.path.basename(csv_file).split(".")[0])==20] #良品トレイデータかの判定
                    for csv_file in csv_file_list:
                        shutil.copy(csv_file,os.path.join(tmp_folder_path,os.path.basename(csv_file)))
                except Exception as e:
                    error_handling(app,f"端数フォルダのファイルのコピーで異常が発生しました:{e})")
                    return
                normal_message_handling(app,f"端数フォルダパスのトレイデータをtmpフォルダへのコピーが完了しました")
    except Exception as e:
        error_handling(app,f"端数ファイルのコピーで異常が発生しました:{e})")
        return

    #データ変換を実施
    csv_file_list=glob.glob(os.path.join(tmp_folder_path,"*.csv"))
    if len(csv_file_list)==0: #tmpフォルダ内のファイル数が0であれば終了
        error_handling(app,f"変換対象のトレイデータが1つも存在しません")
        return

    normal_message_handling(app,f"データの変換を開始します")
    for csv_file in csv_file_list:
        output_lines=[]
        file_name=os.path.basename(csv_file)
        normal_message_handling(app,f"{file_name}の変換を開始")
        try:
            tray_id=os.path.basename(csv_file).replace(".csv","")
            with open(csv_file,"r") as f:
                line=f.readline() #header行
                n=1
                while line:
                    if n==2: #チップデータの1行目でランクを取得する
                        rank=get_rank_from_line(line)
                    if n>1:
                        converted_line=miyazaki_to_chikugo_taping(line,lot_name,rank)
                        output_lines.append(converted_line)
                    line=f.readline() #header行を取得して、CLTまで実施済のデータかトレイ移載までのデータかを確認
                    n=n+1

            #ファイル内のランクがTP入力のランクと異なればファイル出力しない
            if rank!=target_rank:
                continue 
            #変換した内容を出力
            output_file_name=f"{tray_id}_{rank}.csv"
            output_csv_file=os.path.join(tmp_folder_path,"converted",output_file_name)
            with open(output_csv_file,"w") as of:
                #header出力
                header_line=",".join(chikugo_sorter_header)+"\n"
                of.write(header_line)
                for chip_data in output_lines:
                    output_line=""
                    for item in chikugo_sorter_header:
                        output_line+=chip_data[item]+","
                    
                    of.write(output_line[0:-1]+"\n") #最後のカンマを省く

            normal_message_handling(app,f"{file_name}の変換が完了")
        
        except Exception as e:
            error_handling(app,f"データの変換に失敗しました:{e}")
            return

    normal_message_handling(app,f"全データの変換が完了しました")

    #OUT側パスにアップロード
    #tmp/convetedの中身をアップロード
    normal_message_handling(app,f"変換後データのアップロードを開始します")
    output_folder_path_lot=os.path.join(output_folder_path,lot_name)

    #本番運用時はコメント外す
    #if os.path.exists(output_folder_path_lot):
    #    app.mergeResult=False
    #    app.log_message(f"出力先のロットフォルダがすでに存在しています")
    #    log_file_message(f"出力先のロットフォルダがすでに存在しています","error")
    #    return

    #フォルダを作成する
    normal_message_handling(app,f"アップロード先フォルダを作成します")
    try:
        if not os.path.exists(output_folder_path_lot):
            os.makedirs(output_folder_path_lot)
    except Exception as e:
            error_handling(app,f"アップロード先フォルダの作成に失敗しました:{e}")

    try:
        csv_file_list=glob.glob(os.path.join(tmp_folder_path,"converted","*.csv"))
        if len(csv_file_list)==0:
            raise ValueError("変換後のデータが存在しません.ロットNoとTP入力ランクを確認してください")

        for csv_file in csv_file_list:
            shutil.copy(csv_file,os.path.join(output_folder_path_lot,os.path.basename(csv_file)))
            normal_message_handling(app,f"{csv_file}のアップロードが完了")
    except Exception as e:
        error_handling(app,f"OUTPUTフォルダへのアップロードで異常が発生しました:{e}")
        return

    normal_message_handling(app,f"変換後の全てのデータのアップロードが完了しました")

    normal_message_handling(app,f"{lot_name}の処理に成功しました")

    app.mergeResult=(True,"0") #処理に成功したことを示す

    return

