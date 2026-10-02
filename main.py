import struct

ENDIAN = '>'
UNSIGNED_CHAR = 'B'
START_SEPARATOR = 2  # STX
DATA_SEPARATOR = 3  # ETX
END_SEPARATOR = 4  # EOT
ACTIVE_SEPARATOR = 7  # BEL
TYPE_STR = 11  # DC1


def _encode_one_char(text: str) -> bytes:
    return struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', text)


def _encode_length_and_data(text: str) -> bytes:
    numbers = []
    for ch in text:
        numbers.append(ord(ch))
    length = len(numbers)
    if length > 255:
        raise ValueError('Data out of range')
    str_format = UNSIGNED_CHAR * length
    return struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}{str_format}', length, *numbers)


def encode_string(collection: str, key: str, value: str) -> bytes:
    packed_string = _encode_one_char(START_SEPARATOR) + _encode_length_and_data(collection) + _encode_one_char(
        DATA_SEPARATOR) + _encode_length_and_data(key) + _encode_one_char(TYPE_STR) + _encode_length_and_data(
        value) + _encode_one_char(ACTIVE_SEPARATOR) + _encode_one_char(1) + _encode_one_char(END_SEPARATOR)

    if len(packed_string) > 255:
        raise ValueError('Row length out of range')
    packed_string = struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', len(packed_string)) + packed_string
    return packed_string


def decode_row(row: bytes) -> [str, str, str, int]:
    pos = 2
    length = row[pos]
    pos, collection = _decode_data_helper(row, length, pos)

    pos += length + 1
    length = row[pos]
    pos, key = _decode_data_helper(row, length, pos)

    pos += length
    if row[pos] == TYPE_STR:
        pos += 1
        length = row[pos]
    pos, value = _decode_data_helper(row, length, pos)

    pos += length + 1
    status = row[pos]

    return collection, key, value, status

def _decode_data_helper(row: bytes, length: int, pos: int) -> [int, str]:
    pos += 1
    text_bin = _unpack_string(data=row[pos:pos + length], length=length)
    text = ''
    for c in text_bin:
        text = text + str(chr(c))

    return pos, text


def _unpack_string(data: bytes, length: int):
    length_ = UNSIGNED_CHAR * length
    unpacked_string = struct.unpack(f'{ENDIAN}{length_}', data)
    return unpacked_string


def delete_encode_string(collection: str, key: str, value: str) -> bytes:
    packed_string = _encode_one_char(START_SEPARATOR) + _encode_length_and_data(collection) + _encode_one_char(
        DATA_SEPARATOR) + _encode_length_and_data(key) + _encode_one_char(TYPE_STR) + _encode_length_and_data(
        value) + _encode_one_char(ACTIVE_SEPARATOR) + _encode_one_char(0) + _encode_one_char(END_SEPARATOR)

    if len(packed_string) > 255:
        raise ValueError('Row length out of range')
    packed_string = struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', len(packed_string)) + packed_string
    return packed_string


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
        line = encode_string(self.name, key, value)
        with open(self.database.path, 'ab') as data_base:
            data_base.write(line)

    def get(self, key):
        with open(self.database.path, 'rb') as data_base:
            lines = data_base.read()
        entries = []
        start_of_line = 0
        for count, line in enumerate(lines):
            # Better validation needed
            if line == END_SEPARATOR:
                entries.append(lines[start_of_line:count])
                start_of_line = count + 1
        correct_entries = []
        for entry in entries:
            collection_, key_, value_, status_, = decode_row(entry)
            if collection_ == self.name and key_ == key:
                correct_entries.append([collection_, key_, value_, status_])

        if correct_entries[-1][-1]:
            return correct_entries[-1][2]
        return 'not found'

    def delete(self, key):
        value = links.get(key)
        line = delete_encode_string(self.name, key, value)
        with open(self.database.path, 'ab') as data_base:
            data_base.write(line)

    def query(self, callback):
        pass

    def contains(self, key):
        pass


if __name__ == '__main__':
    db = Database('data.db')

    links = db.collection('links')
    links.put('polarion', 'https://polarion.gpdm.fmcglobal.net/polarion/')
    links.put('azure', 'https://dev.azure.com/FreseniusMedicalCare/VSM/')
    value__ = links.get('polarion')
    print(value__)
    links.delete('polarion')
    value__ = links.get('polarion')
    print(value__)

    # links.get_all()
    # value__ = links.get('polarion')
    # value2 = links.get('azure')
    # print(value2)
    #
    # users = db.collection('users')
    # users.put('alice', 'Alice')
    # users.put('bob', 'Bob')
    # user = users.get('alice')
    # user2 = users.get('bobby')
    # print(user)
    # print(user2)

    # users = db.collection('users')
    # users.put('alice', 'Alice')
    # users.put('bob', 'Bob')
    # user = users.get('alice')
    # users.delete('bob')
