# import struct
# st = struct.pack('>H', 1023)
# st2 = struct.unpack('>H', st)
# print(st)
# print(st2)

# st = struct.pack('>HIQ', 1023, 1023, 1023)
# st2 = struct.unpack('>HIQ', st)
# print(st)
# print(st2)

# st = struct.pack('>H', [10, 20])
# print(st)

# st = struct.pack('>HH', 1023, 1023)
# print(st)

# st = struct.pack('>H', 1000000),
# print(st)

# import codecs
# cd = codecs.encode('hello', 'utf-8')
# print(cd)
# print(struct.calcsize(cd))
# cd_un = struct.unpack('>Q', cd)

# import struct, codecs
# st = struct.pack('>H', 100)
# print(st)
# decode = codecs.decode(st, 'utf-8')
# decode2 = st.decode()
# print(decode)
# print(decode2)

string = 'hello'
encode = string.encode()
print(encode)