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
import selectors
import socket
import struct


def format_mndp_reply(content, print_json=True):

    # Rearrange the list a bit
    values = dict()

    for v in content.data:
        values[str(v['type'])] = str(v['value'])

    if print_json:
        return json.dumps(values, indent=2, default=str)
    else:
        f = f'{values.get("identity")}  {values.get("mac_address")}  {values.get("ipv4_address", "")}  {values.get("ipv6_address", "")}  {values.get("interface_name")}'
        f = f + f'\n  ver {values.get("version")}  up {values.get("uptime")}  {values.get("platform")} {values.get("board")}  {values.get("software_id")}'
        return f

def main():
    
    # Get the bind addresses for UDP port 5678
    # The AI_PASSIVE option gives us wildcard addresses (0.0.0.0 and ::)
    # instead of loopback addresses when host=None
    
    addr_info = socket.getaddrinfo(host=None, port=5678,
        family=socket.AF_UNSPEC, proto=socket.IPPROTO_UDP,
        flags=socket.AI_PASSIVE)

    # There should be one or two addresses returned
    assert len(addr_info) in [1,2]

    # Loop through and open a socket for each address
    socks = list()
    for addr_info_item in addr_info:
        # Break down the 5-tuple from getaddrinfo()
        addr_family, socket_kind, proto, cname, bind_addr = addr_info_item

        # Create a new socket
        sock = socket.socket(addr_family, socket_kind)

        # Set socket options
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setblocking(False)

        if addr_family is socket.AF_INET:
            # If IPv4, set option to allow broadcast
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        if addr_family is socket.AF_INET6:
            # If IPv6, limit to IPv6 only
            sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 1)

        # Bind the socket and add to list
        sock.bind(bind_addr)
        socks.append(sock)

    # Set up the selector
    sel = selectors.DefaultSelector()

    print('MNDP Discover')

    # Join multicast (if IPv6) and send initial MNDP request
    for sock in socks:
        if sock.family is socket.AF_INET:
            dst_addr = '255.255.255.255'
        else:
            dst_addr = 'ff02::1'

        addr_info = socket.getaddrinfo(host=dst_addr, port=5678,
            family=sock.family, proto=socket.IPPROTO_UDP)

        send_addr = addr_info[0][4]

        # Build the request packet
        req_data = MNDP_REQUEST.build(None)

        if sock.family is socket.AF_INET:
            # For IPv4 broadcast goes automatically to all interfaces     
            sock.sendto(req_data, send_addr)
        else:
            # For IPv6 we can only send multicast one interface at a time
            # Not all interfaces will work
            ifs = socket.if_nameindex()
            for iface in ifs:
                try:
                    sock.setsockopt(socket.IPPROTO_IPV6,
                        socket.IPV6_MULTICAST_IF, iface[0])
                    #print(f'sending request to {send_addr} on {iface[1]}')
                    sock.sendto(req_data, send_addr)
                except OSError:
                    #print(f'OSError sending on {iface[1]}')
                    continue

        # Register with the selector
        sel.register(sock, selectors.EVENT_READ)


    # Wait for replies and print when received
    try:
        while True:
            events = sel.select()

            for key, mask in events:
                sock = key.fileobj

                data, address = sock.recvfrom(2048)

                if len(data) > 18:
                    try:
                        result = MNDP_REPLY.parse(data)
                    except construct.ConstructError:
                        #print('construct error')
                        continue

                    #print(f'Received from {address}:')
                    print(format_mndp_reply(result, print_json=False))

    except KeyboardInterrupt:
        for sock in socks:
            sock.close()

if __name__ == '__main__':
    main()
