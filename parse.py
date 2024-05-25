#!/usr/bin/env python

import sys

from TH12 import Session

session = Session(sys.argv[1])
print(f'UID: {session.uid}')
print(f'Lot: {session.lot}')
print(f'SN: {session.sn}')
print(f'SID: {session.sid}')
print('Timestamp:', session.timestamp.strftime('%c'))
session.load()
