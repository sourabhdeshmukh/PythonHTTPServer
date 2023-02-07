import threading
#import socketserver
import os, errno
import sys
from  argparse import *
import socket
#from urllib.error import HTTPError
import time

current_date = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
class HTTPError(Exception):
    pass

# Weserver Class
class WebServer:

    def __init__(self, ip, port, document_root):
        self.ip = ip
        self.port = port
        self.document_root = document_root
    # def getFilePath(self, filename):
    #     image_paths = []
    #     for r, d, fs in os.walk('./scu'):
    #         for f in fs:
    #             _p = os.path.join(r, f)
    #             _f = _p.replace('./scu', '').lstrip('/')
    #             image_paths.append(os.path.join('', _f))
    #     for filepath in image_paths:
    #         if self.filename in filepath:
    #             return filepath
    
    # Medthod to start server. 
    def startServer(self, ip, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.ip, self.port))
            try:
                while True:
                    sock.listen()
                    conn, addr = sock.accept()
                    thread = threading.Thread(target=self.keepConnectionAlive, args=(conn, addr))
                    thread.start()
            except KeyboardInterrupt:
                conn.close()
    
    # Following method keeps connection alive. 
    # If there is not activity for 3 seconds the connection is closed    
    def keepConnectionAlive(self, conn, address):
        size = 1024
        c = 0
        with conn:
            conn.settimeout(3)
            while True:
                try:
                    data = conn.recv(size).decode()
                    headers = data.split('\r\n')
                    request  = headers[0].split()
                    if request[0] == 'GET':
                        self.handle(conn, request)
                except Exception as e:
                    break
        conn.close()

    # The following function handles the web requests.
    def handle(self, conn, request):  
        if(request[1] == '/'):
            request[1] = '/index.html'
        try:
            if(request[1].find('.html') > 0):
                filename = self.document_root + request[1]
                isFile  = os.path.isfile(filename)
                if not isFile:
                    raise FileNotFoundError  
                with open(filename,  'r', encoding='latin-1') as f:
                    content = f.read()
                f.close()
                response = str.encode("HTTP/1.1 200 OK\n")
                response = response + str.encode('Content-Type: text/html\n')
                response = response + str.encode("Content-Length: " + str(len(content)) + "\r\n")
                response = response + str.encode("Date: " + current_date + "\r\n")
                response = response + str.encode('\r\n')
                conn.sendall(response)
                conn.sendall(content.encode())
            if(request[1].find('.txt') > 0):
                filename = self.document_root + request[1]
                try: 
                    with open(filename,  'r') as f:
                        content = f.read()
                        print(content)
                except IOError as x:
                    if x.errno == errno.ENOENT:
                        raise FileNotFoundError
                    elif x.errno == errno.EACCES:
                        raise HTTPError
                    f.close()
                response = str.encode("HTTP/1.1 200 OK\n")
                response = response + str.encode('Content-Type: text/plain\n')
                response = response + str.encode("Content-Length: " + str(len(content)) + "\r\n")
                response = response + str.encode("Date: " + current_date + "\r\n")
                response = response + str.encode('\r\n')
                conn.sendall(response)
                conn.sendall(content.encode())
            elif(request[1].find('.png') > 0 or request[1].find('.jpeg') > 0  or request[1].find('.jpg') > 0 or request[1].find('.gif') > 0):
                image_type = request[1].split('.')[1]
                filename = self.document_root + request[1]
                isFile  = os.path.isfile(filename)
                if not isFile:
                    raise FileNotFoundError
                image_data = open(filename, 'rb')
                response = str.encode("HTTP/1.1 200 OK\n")
                image_type = "Content-Type: image/" + image_type +"\r\n"
                response = response + str.encode(image_type)
                response = response + str.encode("Date: " + current_date + "\r\n")
                response = response + str.encode("Accept-Ranges: bytes\r\n\r\n")
                conn.sendall(response)
                conn.sendall(image_data.read())
            else:
                # err=str.encode("HTTP/1.1 404 NOT FOUND\r\nFile Not Found")
                # conn.sendall(err)
                # print(err)
                # self.send_error(conn, 404, 'Not Found')
                # conn.sendall(str.encode("HTTP/1.1 404 NOT FOUND\r\nFile Not Found"))
                filename="./error/400.html"
                with open(filename,  'r', encoding='latin-1') as f:
                    content = f.read()
                f.close()
                response = str.encode("HTTP/1.1 400 Bad Request\n")
                response = response + str.encode('Content-Type: text/html\n')
                response = response + str.encode("Content-Length: " + str(len(content)) + "\r\n")
                response = response + str.encode("Date: " + current_date + "\r\n")
                response = response + str.encode('\r\n')
                conn.sendall(response)
                #conn.sendall(str.encode("HTTP/1.1 400 Bad Request\r\nBad Request"))
                conn.sendall(content.encode())
        except FileNotFoundError:
            filename="./error/404.html"
            with open(filename,  'r', encoding='latin-1') as f:
                content = f.read()
            f.close()
            response = str.encode("HTTP/1.1 404 Not Found\n")
            response = response + str.encode('Content-Type: text/html\n')
            response = response + str.encode("Content-Length: " + str(len(content)) + "\r\n")
            response = response + str.encode("Date: " + current_date + "\r\n")
            response = response + str.encode('\r\n')
            conn.sendall(response)
            conn.sendall(content.encode())
            # self.send_error(404, 'Not Found')
        except ValueError:
            filename="./error/400.html"
            with open(filename,  'r', encoding='latin-1') as f:
                content = f.read()
            f.close()
            response = str.encode("HTTP/1.1 400 Bad Request\n")
            response = response + str.encode('Content-Type: text/html\n')
            response = response + str.encode("Content-Length: " + str(len(content)) + "\r\n")
            response = response + str.encode("Date: " + current_date + "\r\n")
            response = response + str.encode('\r\n')
            conn.sendall(response)
            #conn.sendall(str.encode("HTTP/1.1 400 Bad Request\r\nBad Request"))
            conn.sendall(content.encode())
            # self.send_error(400, 'Bad Request')
        except HTTPError:
            filename="./error/403.html"
            with open(filename,  'r', encoding='latin-1') as f:
                content = f.read()
            f.close()
            response = str.encode("HTTP/1.1 403 Forbidden\n")
            response = response + str.encode('Content-Type: text/html\n')
            response = response + str.encode("Content-Length: " + str(len(content)) + "\r\n")
            response = response + str.encode("Date: " + current_date + "\r\n")
            response = response + str.encode('\r\n')
            conn.sendall(response)
            conn.sendall(content.encode())
            # self.send_error(400, 'Bad Request')
            # conn.sendall(str.encode("HTTP/1.1 500 Internal Server Error\r\nInternal Server Error"))
            # self.send_error(500, 'Internal Server Error')
            # print(e)
        except Exception as e:
            filename="./error/500.html"
            with open(filename,  'r', encoding='latin-1') as f:
                content = f.read()
            f.close()
            response = str.encode("HTTP/1.1 500 Internal Server Error\n")
            response = response + str.encode('Content-Type: text/html\n')
            response = response + str.encode("Content-Length: " + str(len(content)) + "\r\n")
            response = response + str.encode("Date: " + current_date + "\r\n")
            response = response + str.encode('\r\n')
            conn.sendall(x.response)
            conn.sendall(content.encode())
    # def send_error(self, conn, code, message):
    #     msg = "HTTP/1.1 " + code + message
    #     print(msg)
    #     #self.conn.sendall(f'HTTP/1.1 {code} {message}\r\n'.encode())  
    #     conn.sendall(str.encode(msg))

def checkIfEmpty(port, document_root):
    try:
        if not port:
            raise TypeError   
        print("Using directory", document_root, "and port", port, "for server.")
    except:
        print("\nExiting !!! Run python", sys.argv[0], " -h for more information.\n" )
        sys.exit(1)


def main():
    runtimeArguments = ArgumentParser()
    #ip = socket.gethostbyname(socket.gethostname())
    ip = 'localhost'
    port = ""
    document_root = ""
    runtimeArguments.add_argument('-port', type=int)
    runtimeArguments.add_argument('-document_root', type=str)
    parsed = runtimeArguments.parse_args()
    port = parsed.port
    document_root = parsed.document_root

    checkIfEmpty(port, document_root)

    try:
        server = WebServer(ip, port, document_root)
        print("Staring Server...\n\t Access Server at http://"+ip+":"+str(port)+"/")
        server.startServer(ip, port)
        while True:
            pass
    except KeyboardInterrupt:
        pass
    print("/nServer Stopped.")

if __name__ == "__main__":
    main()
   

    

