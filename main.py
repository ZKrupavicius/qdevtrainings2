import struct
from pathlib import Path
from typing import Callable, Union, List

ENDIAN = '>'
UNSIGNED_CHAR = 'B'
UNSIGNED_SHORT = 'H'
START_SEPARATOR = 2  # STX
DATA_SEPARATOR = 3  # ETX
END_SEPARATOR = 4  # EOT
STATUS_SEPARATOR = 7  # BEL
TYPE_STR = 11  # DC1
TYPE_INT = 12  # DC2


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
    packed_row_str = _encode_one_char(START_SEPARATOR) + _encode_length_and_data(collection) + _encode_one_char(
        DATA_SEPARATOR) + _encode_length_and_data(key) + _encode_one_char(TYPE_STR) + _encode_length_and_data(
        value) + _encode_one_char(STATUS_SEPARATOR) + _encode_one_char(1) + _encode_one_char(END_SEPARATOR)

    if len(packed_row_str) > 255:
        raise ValueError('Row length out of range')
    packed_row_str = struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', len(packed_row_str)) + packed_row_str
    return packed_row_str


def _encode_integer_data(value: int) -> bytes:
    return struct.pack(f'{ENDIAN}{UNSIGNED_SHORT}', value)


def encode_int(collection: str, key: str, value: int) -> bytes:
    packed_row_int = _encode_one_char(START_SEPARATOR) + _encode_length_and_data(collection) + _encode_one_char(
        DATA_SEPARATOR) + _encode_length_and_data(key) + _encode_one_char(TYPE_INT) + _encode_integer_data(
        value) + _encode_one_char(STATUS_SEPARATOR) + _encode_one_char(1) + _encode_one_char(END_SEPARATOR)

    if len(packed_row_int) > 255:
        raise ValueError('Row length out of range')
    packed_row_int = struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', len(packed_row_int)) + packed_row_int
    return packed_row_int


def decode_row(row: bytes) -> [str, str, str, int]:
    pos = 2
    length = row[pos]
    pos, collection = _decode_data_helper(row, length, pos)

    pos += length + 1
    length = row[pos]
    pos, key = _decode_data_helper(row, length, pos)

    pos += length
    value = None
    if row[pos] == TYPE_STR:
        pos += 1
        length = row[pos]
        pos, value = _decode_data_helper(row, length, pos)
        pos += length + 1
    elif row[pos] == TYPE_INT:
        pos += 1
        value = struct.unpack(f'{ENDIAN}{UNSIGNED_SHORT}', row[pos:pos + 2])
        pos += 2
        value = value[0]

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
        value) + _encode_one_char(STATUS_SEPARATOR) + _encode_one_char(0) + _encode_one_char(END_SEPARATOR)

    if len(packed_string) > 255:
        raise ValueError('Row length out of range')
    packed_string = struct.pack(f'{ENDIAN}{UNSIGNED_CHAR}', len(packed_string)) + packed_string
    return packed_string

class Database:
    def __init__(self, path):
        self.path = Path(path)
        self.path.touch()

    def collection(self, name):
        return Collection(self, name)


class Collection:
    def __init__(self, database, name):
        self.database = database
        self.name = name

    def put(self, key, value) -> None:
        line = bytes()
        if type(value) == str:
            line = encode_string(self.name, key, value)
        elif type(value) == int:
            line = encode_int(self.name, key, value)

        if line == bytes():
            raise ValueError('empty row')
        with open(self.database.path, 'ab') as data_base:
            data_base.write(line)

    def _read_entries(self):
        with open(self.database.path, 'rb') as data_base:
            data = data_base.read()

        entries = []
        pos = 0

        while pos < len(data):
            record_length = data[pos]
            record_start = pos
            record_end = pos + 1 + record_length

            if record_end > len(data):
                break

            entry = data[record_start:record_end]

            if entry[-1] != END_SEPARATOR:
                pos = record_end
                continue

            entries.append(entry)
            pos = record_end

        return entries

    def get(self, key: str) -> str:
        entries = self._read_entries()
        if not entries:
            raise BufferError('Empty database')

        correct_entries = []
        for entry in entries:
            collection_, key_, value_, status_, = decode_row(entry)
            if collection_ == self.name and key_ == key:
                correct_entries.append([collection_, key_, value_, status_])

        if correct_entries[-1][-1]:
            return correct_entries[-1][2]
        return 'Value not found'

    def delete(self, key: str) -> None:
        value = self.get(key)
        line = delete_encode_string(self.name, key, value)
        with open(self.database.path, 'ab') as data_base:
            data_base.write(line)

    def contains(self, key: str) -> bool:
        value = self.get(key)
        if value != 'Value not found':
            return True
        return False

    def query(self, fn: Callable[[Union[int, str]], bool]) -> List[Union[int, str]]:
        entries = self._read_entries()

        if not entries:
            raise BufferError('Empty database')

        correct_entries = []
        for entry in entries:
            collection_, key_, value_, status_ = decode_row(entry)
            if collection_ == self.name:
                correct_entries.append([collection_, key_, value_, status_])

        latest_entries = {}
        for entry in correct_entries:
            key_ = entry[1]
            latest_entries[key_] = entry

        results = []
        for entry in latest_entries.values():
            value_ = entry[2]
            status_ = entry[3]

            if status_ and fn(value_):
                results.append(value_)

        return results


if __name__ == '__main__':
    db = Database('data.db')

    links = db.collection('links')
    links.put('polarion', 'https://polarion.gpdm.fmcglobal.net/polarion/')
    links.put('azure', 'https://dev.azure.com/FreseniusMedicalCare/VSM/')
    link = links.get('polarion')
    print(link)
    link = links.contains('polarion')
    print(link)
    links.delete('polarion')
    links.put('polarion', 'https://polarion.gpdm.fmcglobal.net/polarion/')
    link = links.get('polarion')
    print(link)
    link = links.contains('polarion')
    print(link)

    users = db.collection('users')
    users.put('alice', 10000)
    user = users.get('alice')
    print(user)

    result = links.query(lambda link: link.startswith('http'))
    print(result)

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
