from collections.abc import Mapping
import os


class Dirdict(Mapping):
    def __init__(self, path):
        if not os.path.isdir(path):
            raise TypeError('Path doesn\'t exist!')

        self.path = path

    def __iter__(self):
        file_names = [name for name in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, name))]
        return iter(file_names)

    def __getitem__(self, key):
        with open(os.path.join(self.path, key),
                  encoding='utf-8') as inp_file:
            value = ''.join(inp_file.readlines())

        return value

    def __setitem__(self, key, value):
        if not isinstance(value, str):
            value = str(value)

        with open(os.path.join(self.path, key), 'w',
                  encoding='utf-8') as inp_file:
            inp_file.write(value)

    def __len__(self):
        return len([name for name in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, name))])


d = Dirdict('./test')
d['lang'] = 'Python\n'
d['lang'] += 'C++\n'

d['langs'] = ['c', 'c++']

