'''
adapters.py
===========

Construct adapters to help with data representation.

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

from construct import Adapter
import datetime
import ipaddress
import re

# IP address adapter for IPv6
# Uses Python's builtin ipaddress module
class IPv6AddressAdapter(Adapter):
    def _decode(self, obj, context, path):
        return ipaddress.IPv6Address(obj)

    def _encode(self, obj, context, path):
        return ipaddress.IPv6Address(obj).packed

# IP address adapter for IPv4
# Uses Python's builtin ipaddress module
class IPv4AddressAdapter(Adapter):
    def _decode(self, obj, context, path):
        return ipaddress.IPv4Address(obj)

    def _encode(self, obj, context, path):
        return ipaddress.IPv4Address(obj).packed

# MAC address adapter - convert between text and raw bytes
class MACAddressAdapter(Adapter):
    def _decode(self, obj, context, path):
        return ':'.join(map(lambda z: f'{z:02x}', obj))

    def _encode(self, obj, context, path):
        # Strip out anything that's not a hex digit
        x = re.sub('[^A-Fa-f0-9]+', '', obj)
        # Pad with leading zeros to get exactly 12 digits
        x = x.zfill(12)
        # Return hex bytes
        return bytes.fromhex(x)

# Uptime adapter - convert between seconds and Python timedelta
class UptimeAdapter(Adapter):
    def _decode(self, obj, context, path):
        '''Take number of seconds and return a timedelta'''
        return datetime.timedelta(seconds=int(obj))

    def _encode(self, obj, context, path):
        '''Take timedelta and return integer seconds'''
        if isinstance(obj, datetime.timedelta):
            return int(obj.total_seconds())
        else:
            raise TypeError(f'expecting timedelta, got {type(obj)}')
