#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  5 13:50:19 2022

@author: franciscojjimenezh
"""

import socket

host = '10.38.91.155'
port = 12345
BUFFER_SIZE = 1024

while True:
    
    song = str(input('Cancion: '))
    volume = int(input('Volumen: '))
    
    MESSAGE = f'{song}///{volume}'
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as socket_tcp:
        socket_tcp.connect((host, port))
        
        socket_tcp.send(MESSAGE.encode('utf-8'))
        data = socket_tcp.recv(BUFFER_SIZE)
        print(data)
