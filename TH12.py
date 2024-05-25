#!/usr/bin/env python

import os
import datetime

attributes = {
    # Unknown header info preceeds the date
    # Year is 0x2 bytes at 0x35
    "year": [0x35, 0x2],
    # Month is 0x1 byte at 0x37
    "month": [0x37, 0x1],
    # Day of month is 0x1 byte at 0x38
    "day": [0x38, 0x1],
    # Hour is 0x1 byte at 0x39
    "hour": [0x39, 0x1],
    # Minute is 0x1 byte at 0x3A
    "min": [0x3A, 0x1],
    # Second is 0x1 byte at 0x3B
    "sec": [0x3B, 0x1],
    # Zero padding fills the space between the timestamp and the Unknown ID
    # Unknown ID is 0x22 bytes at 0x355
    "uid": [0x355, 0x22],
    # Lot Number is 0xE bytes at 0x377
    "lot": [0x377, 0xE],
    # Serial Number is 0xD bytes at 0x385
    "sn": [0x385, 0xD],
    # Session ID is 0xA bytes at 0x395
    "sid": [0x395, 0xA],
}

data = {
    # Data block starts at 0xB55
    "offset": 0xB55,
    # Segment headers are 8 bytes long
    "header_length": 8,
    # Data packets are 18 bytes long
    "packet_length": 18,
    # Each segment has 500 packets
    "packet_count": 500
}

class Session:
    def __init__(self, filepath):
        self.filepath = filepath
        self._bytelength = None
        with open(filepath, 'rb') as self.file:
            for attribute in attributes:
                self.file.seek(attributes[attribute][0])
                if attribute in ('year','month','day','hour','min','sec'):
                    setattr(self, attribute, int(self.file.read(attributes[attribute][1]).hex()))
                else:
                    setattr(self, attribute, self.file.read(attributes[attribute][1]).decode())

    @property
    def bytelength(self):
        if self._bytelength is None:
            self._bytelength = os.path.getsize(self.filepath)
        return self._bytelength

    @property
    def timestamp(self):
        return datetime.datetime(self.year, self.month, self.day, self.hour, self.min, self.sec)

    def load(self):
            offset = data['offset']
            self.segments = []
            pSegment = None
            count = 0
            while offset < self.bytelength:
                segment = Segment(self, offset)
                self.segments.append(segment)
                offset += data['header_length'] + data['packet_length'] * data['packet_count']
                if pSegment:
                    # print(count, 'Diff:', segment.time - pSegment.time)
                    if segment.time - pSegment.time < 10000:
                        print(segment.time - pSegment.time)
                    count += 1
                pSegment = segment


class Segment:
    def __init__(self, session, offset):
        with open(session.filepath, 'rb') as file:
            file.seek(offset)
            self.header = file.read(data['header_length'])
            flag = self.header[0:2]
            bookmark = self.header[2:3]
            unsure = self.header[3:4]
            self.time = int(self.header[4:].hex(),16)
            # print(self.header.hex(), self.time)

class Reading:
    def __init__(self, packet):
        self.packet = packet
        self.LA = int.from_bytes(packet[0:2], signed=True, byteorder='little')
        self.RA = int.from_bytes(packet[2:4], signed=True, byteorder='little')
        self.V1 = int.from_bytes(packet[4:6], signed=True, byteorder='little')
        self.V2 = int.from_bytes(packet[6:8], signed=True, byteorder='little')
        self.V3 = int.from_bytes(packet[8:10], signed=True, byteorder='little')
        self.V4 = int.from_bytes(packet[10:12], signed=True, byteorder='little')
        self.V5 = int.from_bytes(packet[12:14], signed=True, byteorder='little')
        self.V6 = int.from_bytes(packet[14:16], signed=True, byteorder='little')

    @property
    def LL(self):
        # Left leg is just a ground
        return 0

    @property
    def RL(self):
        # Right leg is just a ground
        return 0

    @property
    def I(self):
        return self.RA - self.LA

    @property
    def II(self):
        return self.RA - self.LL

    @property
    def III(self):
        return self.LA - self.LL

    @property
    def aVL(self):
        return (self.I - self.III)/2

    @property
    def aVR(self):
        return (self.I + self.III)/-2

    @property
    def aVF(self):
        return (self.II + self.III)/2
