import struct
st = struct.pack('>H', 1023)
st2 = struct.unpack('>H', st)
print(st)
print(st2)

st = struct.pack('>HIQ', 1023, 1023, 1023)
st2 = struct.unpack('>HIQ', st)
print(st)
print(st2)

# st = struct.pack('>H', [10, 20])
# print(st)

