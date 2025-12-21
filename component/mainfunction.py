"""
メイン処理用のモジュール
"""
import time
from . import settings
from .sorter_lot_start import sorter_lot_start
from .sorter_lot_end import sorter_lot_end
from .taping_lot_start import taping_lot_start
from .taping_lot_start_2 import taping_lot_start_2
from .taping_lot_end import taping_lot_end

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

#エラー発生時の処理をまとめる
def error_handling(app,message):
    app.mergeResult=(False,"1")
    app.log_message(message)
    log_file_message(message,"error")

#マージ処理のメイン関数
#data_dict->lot_no,プロセス名,装置名
def start_main(app,data_dict,manual_flag=False):
    print("メイン処理を開始")
    machine_name=data_dict["machine"] #Taping or Sorter
    command_type=data_dict["command_type"] #LotStart or LotEnd
    type_name=data_dict["product_name"] #機種名

    #PLCスままキャンタ待ち用のタイマを入れる
    time.sleep(1)

    if machine_name=="Taping" and command_type=="LotStart": #LotStart時は清武仕様から筑後仕様に変換
        #taping lotstart時はロット統合実施機種と通常機種で処理を分ける
        #設定csvからロット統合する機種情報を取得する
        type_name_list=[]
        try:
            with open("lot_merge_typename_list.csv","r") as f:
                type_name_list=f.readlines()
                type_name_list=[t.strip() for t in type_name_list ]
            print(type_name_list)
        except Exception as e:
            error_handling(app,f"ロット統合機種名リストの読み込みに失敗しました:{e}")
            return
        if type_name in type_name_list:
            taping_lot_start_2(app,data_dict,manual_flag)
        else:
            taping_lot_start(app,data_dict,manual_flag)

        print("メイン処理が完了")
        return

    elif machine_name=="Taping" and command_type=="LotEnd":
        taping_lot_end(app,data_dict,manual_flag)
        print("メイン処理が完了")
        return

    elif machine_name=="Sorter" and command_type=="LotStart":
        sorter_lot_start(app,data_dict,manual_flag)
        print("メイン処理が完了")
        return

    elif machine_name=="Sorter" and command_type=="LotEnd":
        sorter_lot_end(app,data_dict,manual_flag)
        print("メイン処理が完了")
        return
    else:
        error_handling(app,"設備からのコマンドが適切ではありません")
        print("メイン処理が完了")
        return



