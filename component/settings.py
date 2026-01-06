"""
パラメータファイル
"""
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import sys

"""1.0.1 テーピング機lotendのarray,summaryファイルのLINEOUT仕様を変更"""
"""25/11/4 1.0.2 テーピング機IN FILE変換時にシリアル、トレイ座標、ウェハ番号、ウェハ座標の0パパディンを取るように変更.テーピング機LOTEND出力ファイルのリール番号を0パディングするように変更"""
"""25/11/13 1.0.3 tmpファイル削除時の上限を50->300に変更"""
"""25/12/23 1.1.0 ATPCIMからの子ロット情報取得処理を追加"""
VERSION="1.1.0" #ソフトバージョン
FONT_TYPE="meiryo"
PASSWORD="1234"

#LOGGINGの設定
#ログ出力先を変える場合はここに絶対パスかmain_ui.pyからの相対パスを書いてください
LOG_DIR = 'MERGE_LOG'

# ロガーの設定
def setup_logger():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    logger = logging.getLogger('DailyLogger_MAIN')
    logger.setLevel(logging.INFO)
    
    # ログファイルのパス
    log_filename = os.path.join(LOG_DIR, 'log.txt')
    
    # 日毎にログファイルをローテーション
    handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=30)
    handler.suffix = "%Y-%m-%d"
    handler.setLevel(logging.INFO)
    
    # ログフォーマットの設定
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger

logger = setup_logger()


#ソケット通信用のLOGGINGの設定
#ログ出力先を変える場合はここに絶対パスかmain_ui.pyからの相対パスを書いてください
SOCKET_LOG_DIR = 'SOCKET_LOG'

# ロガーの設定
def setup_socket_logger():
    if not os.path.exists(SOCKET_LOG_DIR):
        os.makedirs(SOCKET_LOG_DIR)

    logger = logging.getLogger('DailyLogger_SOCKET')
    logger.setLevel(logging.INFO)
    
    # ログファイルのパス
    log_filename = os.path.join(SOCKET_LOG_DIR, 'log.txt')
    
    # 日毎にログファイルをローテーション
    handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=30)
    handler.suffix = "%Y-%m-%d"
    handler.setLevel(logging.INFO)
    
    # ログフォーマットの設定
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger

socket_logger = setup_socket_logger()

APP_LOG_DIR = 'APP_LOG'

# ロガーの設定
def setup_app_logger():
    if not os.path.exists(APP_LOG_DIR):
        os.makedirs(APP_LOG_DIR)

    logger = logging.getLogger('DailyLogger_APP')
    logger.setLevel(logging.INFO)
    
    # ログファイルのパス
    log_filename = os.path.join(APP_LOG_DIR, 'log.txt')
    
    # 日毎にログファイルをローテーション
    handler = TimedRotatingFileHandler(log_filename, when='midnight', interval=1, backupCount=30)
    handler.suffix = "%Y-%m-%d"
    handler.setLevel(logging.INFO)
    
    # ログフォーマットの設定
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger

# ----------------------------
# Loggerをstdoutに接続
# ----------------------------
class LoggerWriter:
    """print()出力をlogging.Loggerに流すためのラッパー"""
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        message = message.strip()
        if message:
            self.level(message)

    def flush(self):
        pass  # 何もしなくてOK

# ロガー初期化
app_logger = setup_app_logger()

# stdout / stderr をログにリダイレクト
sys.stdout = LoggerWriter(app_logger, app_logger.info)
sys.stderr = LoggerWriter(app_logger, app_logger.error)
