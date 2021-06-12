#!/usr/bin/env python3
import socket
import sys
import re
import ssl

adresa=sys.argv[1]

while True:
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    obj1 = re.findall('(\w+)://',adresa)
    obj2 = re.findall('://([\w\-\.]+)', adresa)
    obj3 = re.findall('[a-z](\/.*|$)',adresa)

    type = obj1[0].strip()
    hostname = obj2[0].strip()
    path = obj3[0].strip()
    if type=='https':
        s.connect((hostname,443))
        s=ssl.wrap_socket(s)
    elif type=='http':
        s.connect((hostname,80))

    f=s.makefile('rwb')
    f.write(('GET ' + path + ' HTTP/1.1\r\n').encode('ASCII'))
    f.write(('Host: ' + hostname + '\r\n').encode('ASCII'))
    f.write(('Accept-charset: UTF-8\r\n\r\n').encode('ASCII'))
    f.flush()


    first = f.readline().decode('ASCII')
    fs=first.split(' ')
    status = fs[1]
    word = fs[2]

    d = {}
    while True:
        head = f.readline().decode('ASCII')
        if head == '\r\n':
            break
        dict = head.split(': ')
        d[dict[0].lower()] = dict[1].lower()
    if status == '200':
        break
    elif status == '301' or status == '302' or status == '303' or status =='307' or status == '308':
        adresa = d['location']
        f.close()
    else:
        sys.stderr.write(status +' '+ word)
        f.close()
        sys.exit(1)
        break
for i in d.keys():
    if i  == 'content-length':
        len = int(d['content-length'])
        data = f.read(len)
        sys.stdout.buffer.write(data)
        break
    elif i == 'transfer-encoding':
        while True:
            number = f.readline().decode('ASCII')
            if not number:
                break
            len = int(number,16)
            chunk = f.read(len)
            if not chunk:
                break
            sys.stdout.buffer.write(chunk)
            f.readline()
        break
f.flush()
f.close()
sys.exit(0)
