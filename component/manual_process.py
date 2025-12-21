"""
マニュアル処理用のモジュール
"""
import threading
from . import settings
from . import mainfunction as mf
from tkinter import messagebox
from .sorter_lot_start import sorter_lot_start
from .sorter_lot_end import sorter_lot_end
from .taping_lot_start import taping_lot_start
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

#マニュアル処理用の関数
#処理用のスレッドを立てて処理を開始する
def manual_process(app,data_dict):
    #manual_flagをTrueで渡す
    process_thread = threading.Thread(target=mf.start_main, args=(app, data_dict,True))
    process_thread.start()
    process_thread.join()

    if app.mergeResult[1]=="0":
        messagebox.showinfo("確認","処理に成功しました")
    else:
        messagebox.showerror("エラー","処理に失敗しました")

    return
