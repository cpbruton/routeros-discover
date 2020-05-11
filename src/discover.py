#!/usr/bin/env python3
'''
discover.py
===========

Discover RouterOS neighbors on the network and print the list.

Copyright © 2020 Christopher Patrick Bruton 

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

'''

from structures import *
import construct
import json
import socket


def format_mndp_reply(content):

    # Rearrange the list a bit
    values = dict()

    for v in content.data:
        values[str(v['type'])] = v['value']

    return json.dumps(values, indent=2, default=str)


def main():
    
    bind_addr = socket.getaddrinfo(host='0.0.0.0', port=5678, family=socket.AF_INET, proto=socket.IPPROTO_UDP)
    #print(f'bind_addr: {bind_addr}')

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:

        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        sock.bind(bind_addr[0][4])

        req_data = MNDP_REQUEST.build(None)

        for n in range(0,4):
            sock.sendto(req_data, ('255.255.255.255', 5678))

        while True:
            #print('waiting for data')
            data, address = sock.recvfrom(4096)

            if data:
                #print('received data')
                try:
                    result = MNDP_REPLY.parse(data)
                except construct.ConstructError:
                    #print('construct error')
                    continue

                print(f'Received from {address}:')
                print(format_mndp_reply(result))





if __name__ == '__main__':
    main()
