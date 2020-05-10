'''
adapters.py
===========

Construct adapters to help with data representation.

Copyright © 2020 Christopher Patrick Bruton

'''

from construct import Adapter
import datetime
import re

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
