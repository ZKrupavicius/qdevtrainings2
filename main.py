import struct

ENDIAN = '>'
UNSIGNED_CHAR = 'B'
TYPE_STR, TYPE_INT = 2, 3

def _pack_each_text(text):
    numbers = []
    type_ = TYPE_INT
    if isinstance(text, str):
        type_ = TYPE_STR
    for ch in text:
        numbers.append(ord(ch))
    length = len(numbers)
    print(length)
    length_ = UNSIGNED_CHAR * length
    packer = struct.pack(f'{ENDIAN}HH{length_}', length, type_, *numbers)

    # for byte in numbers:
    #     packer2 = struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', byte)
    #     print(byte, packer2)
    #     packer = packer + packer2
    return packer

def encode_str(name, key ,value):
    encoder = _pack_each_text(name) + _pack_each_text(key) + _pack_each_text(value)
    return encoder

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
        line = encode_str(self.name, key, value)
        # with open(self.database.path, 'ab') as data_base:
        #     data_base.write(line)
        print(line)

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
    links.put('azure', 'https://dev.azure.com/FreseniusMedicalCare/VSM')

    # users = db.collection('users')
    # users.put('alice', 'Alice')
    # users.put('bob', 'Bob')
    # user = users.get('alice')
    # users.delete('bob')
