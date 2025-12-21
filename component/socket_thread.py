from . import mainfunction as mf
import threading
import socket
import xml.etree.ElementTree as ET
import select
import time
from . import settings

#ログ出力用の関数
socket_logger=settings.socket_logger
def socket_log_file_message(message, level='info'):
    if level == 'info':
        socket_logger.info(message)
    elif level == 'warning':
        socket_logger.warning(message)
    elif level == 'error':
        socket_logger.error(message)
    else:
        socket_logger.debug(message)

#ソケット通信サーバー用のスレッドを立ち上げる.
def create_socket_thread(app):
    """非ブロッキングでソケットスレッドを再起動"""
    
    def restart_socket():
        print("ソケットを作成")
        """バックグラウンドでソケットを再起動する関数"""
        try:
            #既存のスレッドがあれば停止
            if app.socket_thread is not None and app.socket_thread.is_alive():
                app.socket_log_message(">>既存のソケット接続を停止中...")
                app.stop_socket_thread_event.set()

                # サーバーソケットを強制的に閉じる
                if hasattr(app, "server_socket") and app.server_socket:
                    try:
                        app.server_socket.shutdown(socket.SHUT_RDWR)
                        app.server_socket.close()  # 必ずclose()を実行
                    except Exception as e:
                        app.socket_log_message(f">>ソケット終了時エラー: {e}")
                    app.server_socket = None

                # スレッドの終了を待機（タイムアウト付き）
                app.socket_thread.join(timeout=5.0)
                if app.socket_thread.is_alive():
                    app.socket_log_message(">>警告: ソケットスレッドが正常に終了しませんでした")
                
                app.stop_socket_thread_event.clear()

            # 少し待機してから新しいスレッドを開始
            time.sleep(0.1)
            
            socket_log_file_message("新規ソケットを作成")
            app.socket_thread = threading.Thread(target=socket_connect, args=(app,))
            app.socket_thread.daemon = True
            app.socket_thread.start()
            
        except Exception as e:
            app.socket_log_message(f">>ソケット再起動エラー: {e}")
            socket_log_file_message(f"ソケット再起動エラー: {e}")

    # バックグラウンドスレッドで再起動処理を実行
    restart_thread = threading.Thread(target=restart_socket)
    restart_thread.daemon = True
    restart_thread.start()

#サーバーから送付されたコマンドを解析
def get_data_from_xml(xml_data):
    # XMLを解析
    root = ET.fromstring(xml_data)
    dict={}

    # 必要なデータを抽出
    dict["machine"] = root.find("Machine").text #設備種類
    if dict["machine"]=="Taping":
        dict["command_type"] = root.find("CommandType").text #リクエストの内容
        dict["lotno"] = root.find("LotNo").text #ロット名
        dict["rank"] = root.find("Rank").text #ランク
        dict["id"] = root.find("MachineId").text #装置名
        dict["product_name"] = root.find("ProductName").text #機種名
        dict["wp_lotno"] = root.find("WPLotNo").text #装置名
        dict["quantity"]=root.find("WorkQuantity").text #仕掛け数
        dict["operator_id"]=root.find("OperatorId").text #オペID
    elif dict["machine"]=="Sorter":
        dict["command_type"] = root.find("CommandType").text #リクエストの内容
        dict["lotno"] = root.find("LotNo").text #ロット名
        dict["id"] = root.find("MachineId").text #装置名
        dict["product_name"] = root.find("ProductName").text #機種名
        dict["wp_lotno"] = root.find("WPLotNo").text #装置名
        dict["quantity"]=root.find("WorkQuantity").text #仕掛け数
        dict["operator_id"]=root.find("OperatorId").text #オペID
    else:
        raise ValueError("装置名が不適切です")
    
    if dict["command_type"] not in ["LotStart","LotEnd"]:
        raise ValueError("CommandTypeが不適切です")

    return dict

#サーバーへの返信メッセージを作成
def create_response_message(result):
    response_message=f"""<SocketData><Result>{result}</Result></SocketData>"""
    return response_message

#ソケット通信サーバーを立上
def socket_connect(app):
    client_socket = None
    print("受信待ち状態")
    try:
            
        #ソケットを作成
        app.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # ソケットオプションを設定（再利用を許可）
        app.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        #ソケットにIPとポートを紐づけ
        app.server_socket.bind((app.address_dict["SOCKET"]["IP"], int(app.address_dict["SOCKET"]["PORT"])))
        app.server_socket.listen(1)
        
        app.socket_log_message(f'>>IP:{app.address_dict["SOCKET"]["IP"]}:{app.address_dict["SOCKET"]["PORT"]}でサーバー起動中...')
        app.after(0, lambda: app.setSocketInfo({
            "status":"disconnect",
            "server_ip":app.address_dict["SOCKET"]["IP"],
            "server_port":app.address_dict["SOCKET"]["PORT"],
            "client_ip":"",
            "client_port":""
        }))

        while not app.stop_socket_thread_event.is_set():
            try:

                readable, _, _ = select.select([app.server_socket], [], [], 1)  # タイムアウト1秒

                if app.server_socket in readable:
                    # クライアントからの接続を受け入れる
                    client_socket, addr = app.server_socket.accept()
                    app.socket_log_message(f">>クライアント{addr}が接続しました")
                    
                    #SocketStatusFrameを更新
                    app.after(0, lambda: app.setSocketInfo({
                        "status":"connect",
                        "server_ip":app.address_dict["SOCKET"]["IP"],
                        "server_port":app.address_dict["SOCKET"]["PORT"],
                        "client_ip":addr[0],
                        "client_port":addr[1]
                    }))


                    # クライアントとの通信処理
                    handle_client_communication(app, client_socket)
                    
            except socket.error as e:
                if not app.stop_socket_thread_event.is_set():
                    app.socket_log_message(f">>ソケット接続エラー: {e}")
                break
            except Exception as e:
                if not app.stop_socket_thread_event.is_set():
                    app.socket_log_message(f">>予期しないエラー: {e}")
                break

    except Exception as e:
        app.socket_log_message(f">>サーバー立上接続失敗 : {e}")
        socket_log_file_message(f"サーバー立上失敗:{e}")
        app.after(0, lambda: app.setSocketInfo({
            "status":"error",
            "server_ip":app.address_dict["SOCKET"]["IP"],
            "server_port":app.address_dict["SOCKET"]["PORT"],
            "client_ip":"",
            "client_port":""
        }))
    finally:
        # クリーンアップ処理
        if client_socket:
            try:
                client_socket.close()
            except Exception:
                pass
            
        if hasattr(app, "server_socket") and app.server_socket:
            try:
                app.server_socket.close()
            except Exception:
                pass
            app.server_socket = None

def handle_client_communication(app, client_socket):
    """クライアントとの通信を処理する関数"""
    print("クライアント接続状態")
    while not app.stop_socket_thread_event.is_set():
        try:
            # select()でタイムアウト付きでデータを待機
            readable, _, _ = select.select([client_socket], [], [], 1)
            
            if not readable:
                continue  # タイムアウト時は継続

            #通信側のログテキストボックスもある文字数超えた場合消すようにする
            #if len(app.bottom_frame.SocketLoggingTextBox.get("1.0","end-1c"))>1000:
            #    app.after(0, lambda: app.bottom_frame.SocketLoggingTextBox.delete("0.0", "end"))
                
            # サーバーからのコマンドを受信
            command = client_socket.recv(1024).decode('utf-8')

            # データがない場合やクライアントが切断した場合
            if not command:
                raise ConnectionError("クライアントとの接続が切断されました")

            # UIの更新（メインスレッドで実行）
            app.after(0, lambda: app.bottom_frame.LoggingTextBox.delete("0.0", "end"))
            app.after(0, lambda: app.bottom_frame.SocketLoggingTextBox.delete("0.0", "end"))

            app.socket_log_message(f">>クライアントからの受信コマンド : {command}")
            socket_log_file_message(f"メッセージを受信:{command}")

            #xmlコマンドを解析
            try:
                datadict = get_data_from_xml(command)
            except Exception as e:
                response_message = create_response_message(result="1")
                client_socket.send(response_message.encode('utf-8'))
                app.socket_log_message(f">>xml解析でエラー発生 : {e}")
                app.socket_log_message(f">>PCからの送信コマンド : {response_message}")
                socket_log_file_message(f"xml解析でエラー発生 : {e}")
                socket_log_file_message(f"メッセージを送信:{response_message}")
                continue

            # UIの更新（メインスレッドで実行）
            app.after(0, lambda: app.setEntryItem(app.top_frame.LotNameEntry, datadict["lotno"]))

            # メイン処理を実行
            process_thread = threading.Thread(target=mf.start_main, args=(app, datadict,))
            process_thread.start()
            process_thread.join()
            
            # 結果に応じてレスポンスを送信
            response_message = create_response_message(result=app.mergeResult[1])
            app.socket_log_message(f">>サーバーからの送信コマンド : {response_message}")
            socket_log_file_message(f"メッセージを送信:{response_message}")
            client_socket.send(response_message.encode('utf-8'))
            
            app.mergeResult = (None, "")

        except ConnectionError as ce:
            app.socket_log_message(f">>通信が切れました:{ce}")
            socket_log_file_message(f"通信が切れました:{ce}")
            break
        except socket.error as se:
            if not app.stop_socket_thread_event.is_set():
                app.socket_log_message(f">>ソケット通信エラー:{se}")
                socket_log_file_message(f"ソケット通信エラー:{se}")
            break
        except Exception as e:
            app.socket_log_message(f">>予期しないエラー:{e}")
            socket_log_file_message(f"予期しないエラー:{e}")
            break

    print("ソケットイベントが終了しました")
    # クライアント接続を閉じる
    try:
        client_socket.close()
        app.after(0, lambda: app.setSocketInfo({
            "status":"disconnect",
            "server_ip":app.address_dict["SOCKET"]["IP"],
            "server_port":app.address_dict["SOCKET"]["PORT"],
            "client_ip":"",
            "client_port":""
        }))
        print("クライアント接続が閉じました")

    except Exception:
        pass
