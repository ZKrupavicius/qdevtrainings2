import struct

ENDIAN = '>'
UNSIGNED_CHAR = 'B'
START_SEPARATOR = 3  # STX
DATA_SEPARATOR = 4  # ETX
KEY_SEPARATOR = 7  # BS
END_SEPARATOR = 5  # EOT
TYPE_STR = 10


def encode_row(name, key, value):
    encoder = _pack_string(text=name, start_of_row=True) + _pack_string(text=key) + _pack_string(text=value,
                                                                                                 type_needed=True,
                                                                                                 data_input=True)
    return encoder


def _pack_string(text: str,
                 type_needed: bool = False,
                 start_of_row: bool = False,
                 data_input: bool = False
                 ) -> bytes:
    numbers = []
    # type_ = TYPE_INT
    # if isinstance(text, str):
    type_ = TYPE_STR
    for ch in text:
        numbers.append(ord(ch))
    length = len(numbers)
    print(length)
    length_ = UNSIGNED_CHAR * length
    if start_of_row:
        packer = struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', START_SEPARATOR)
    elif data_input:
        packer = struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', DATA_SEPARATOR)
    else:
        packer = struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', KEY_SEPARATOR)

    if type_needed:
        packer = packer + struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', type_)

    packer = packer + struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}{length_}', length, *numbers)
    if type_needed:
        packer = packer + struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', END_SEPARATOR)

    return packer


def decode_row(row: bytes):
    c = 1
    length = row[c]
    c += 1
    name_bin = _unpack_string(data=row[c:c+length], length=length)
    name = ''
    for n in name_bin:
        name = name + str(chr(n))

    c += length + 1
    length = row[c]
    c += 1
    key_bin = _unpack_string(data=row[c:c+length], length=length)
    key = ''
    for k in key_bin:
        key = key + str(chr(k))

    c += length + 1
    if row[c] == TYPE_STR:
        c += 1
        length = row[c]
    c += 1
    value_bin = _unpack_string(data=row[c:c + length], length=length)
    value = ''
    for v in value_bin:
        value = value + str(chr(v))

    line = f'collection: {name}, key: {key}, value: {value}'
    return line

def _unpack_string(data: bytes, length: int):
    length_ = UNSIGNED_CHAR * length
    unpacker = struct.unpack(f'{ENDIAN}{length_}', data)
    return unpacker

class Database:
    def __init__(self, path):
        self.path = path

    def collection(self, name):
        return Collection(self, name)


class Collection:
    def __init__(self, database, name):
        self.database = database
        self.name = name

    def put(self, key, value) -> None:
        line = encode_row(self.name, key, value)
        print(line)
        decoded_bytes = decode_row(line)
        print(decoded_bytes)
        # with open(self.database.path, 'ab') as data_base:
        #     data_base.write(line)

    def get(self, key) -> str:
        pass

    def delete(self, key):
        pass

    def query(self, callback):
        pass

    def contains(self, key):
        pass


if __name__ == '__main__':
    db = Database('data.db')

    links = db.collection('links')
    links.put('polarion', 'https://polarion.gpdm.fmcglobal.net/polarion/')
    # links.put('azure', 'https://dev.azure.com/FreseniusMedicalCare/VSM')

    # users = db.collection('users')
    # users.put('alice', 'Alice')
    # users.put('bob', 'Bob')
    # user = users.get('alice')
    # users.delete('bob')
