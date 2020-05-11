'''
structures.py
=============

Data structures for MNDP packets.

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

from adapters import *
from construct import *


# MNDP request is 4 null bytes sent to a broadcast
# address to and from UDP port 5678.
MNDP_REQUEST = Struct(
    Const(0, Int32ub),
)

# Known data types in MNDP response
MNDP_TYPES = Enum(Int16ub,
    mac_address = 1,
    identity = 5,
    version = 7,
    platform = 8,
    uptime = 10,
    software_id = 11,
    board = 12,
    unpack = 14,
    ipv6_address = 15,
    interface_name = 16,
    ipv4_address = 17,
)

# MNDP replies include a series of type-length-value (TLV)
# structures. This TLV structure will convert to/from a
# human-readable representation for known types, otherwise
# pass through as raw bytes.
MNDP_TLV = Struct(
    'type' / MNDP_TYPES,
    'value' / Prefixed(Int16ub,
        Switch(this.type, {
            'identity': GreedyString('ascii'),
            'version': GreedyString('ascii'),
            'platform': GreedyString('ascii'),
            'software_id': GreedyString('ascii'),
            'board': GreedyString('ascii'),
            'interface_name': GreedyString('ascii'),
            'ipv6_address': IPv6AddressAdapter(Bytes(16)),
            'ipv4_address': IPv4AddressAdapter(Bytes(4)),
            'uptime': UptimeAdapter(Int32ul), # little endian for some reason
            'mac_address': MACAddressAdapter(Bytes(6)),
            },
            default = GreedyBytes
        )
    ),
)

# Main structure for an MNDP reply
MNDP_REPLY = Struct(
    'header' / Default(Bytes(2), 0),
    'seq' / Int16ub,
    'data' / GreedyRange(MNDP_TLV),
)
