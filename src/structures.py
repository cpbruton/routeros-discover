'''
structures.py
=============

Data structures for MNDP packets.

Copyright © 2020 Christopher Patrick Bruton

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
)

# Helper type for variable length ascii strings
AString = GreedyString('ascii')

# MNDP replies include a series of type-length-value (TLV)
# structures. This TLV structure will convert to/from a
# human-readable representation for known types, otherwise
# pass through as raw bytes.
MNDP_TLV = Struct(
    'type' / MNDP_TYPES,
    'length' / Int16ub,
    'value' / FixedSized(this.length,
        Switch(this.type, {
            'identity': AString,
            'version': AString,
            'platform': AString,
            'software_id': AString,
            'board': AString,
            'interface_name': AString,
            'uptime': UptimeAdapter(Int32ul), # little endian for some reason
            'mac_address': MACAddressAdapter(Byte[6]),
            },
            default = GreedyBytes
        )
    ),
)

# Main structure for an MNDP reply
MNDP_REPLY = Struct(
    'header' / Bytes(2),
    'seq' / Int16ub,
    'data' / GreedyRange(MNDP_TLV),
)
