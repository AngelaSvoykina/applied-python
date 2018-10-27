# -*- encoding: utf-8 -*-
from functools import reduce


def optimize(result, op):
    prev = result[-1] if len(result) else None

    if type(prev) is InsertAction and type(op) is InsertAction:
        if prev.pos + len(prev.text) == op.pos:
            newOp = InsertAction(prev.pos, prev.text + op.text, prev.from_version, op.to_version)
            return result[:-1] + [newOp]

    if type(prev) is DeleteAction and type(op) is InsertAction:
        if prev.pos == op.pos and prev.length == len(op.text):
            newOp = ReplaceAction(prev.pos, op.text, prev.from_version, op.to_version)
            return result[:-1] + [newOp]

    return result + [op]


class TextHistory(object):
    def __init__(self):
        self.__text_trivial = ''
        self.__version_trivial = 0
        self.history = []

    @property
    def text(self):
        return self.__text_trivial

    @property
    def version(self):
        return self.__version_trivial

    def insert(self, text, pos=None):
        if pos is None:
            pos = len(self.__text_trivial)

        action = InsertAction(pos=pos, text=text, from_version=self.__version_trivial,
                              to_version=(self.__version_trivial + 1))
        return self.action(action)

    def replace(self, text, pos=None):
        if pos is None:
            pos = len(self.__text_trivial)

        action = ReplaceAction(pos=pos, text=text, from_version=self.__version_trivial,
                               to_version=self.__version_trivial + 1)
        return self.action(action)

    def delete(self, length, pos=None):
        if pos is None:
            pos = len(self.__text_trivial)

        action = DeleteAction(pos=pos, length=length, from_version=self.__version_trivial,
                              to_version=self.__version_trivial + 1)
        return self.action(action)

    def action(self, action):
        self.__text_trivial = action.apply(self.__text_trivial)
        self.history.append(action)

        self.__version_trivial = action.to_version
        return self.__version_trivial

    def get_actions(self, from_version=None, to_version=None):
        if len(self.history) == 0:
            return []

        if from_version is None:
            from_version = self.history[0].from_version
        if to_version is None:
            to_version = self.history[-1].to_version

        if from_version > to_version:
            raise ValueError('from_version cannot be bigger or equal to_version')
        if from_version < 0 or to_version < 0:
            raise ValueError('from_version and to_version mus be positive numbers')
        if to_version > self.history[-1].to_version:
            raise ValueError('to_version cannot be more than latest version: {}'.format(self.history[-1].to_version))

        return list(
            reduce(
                optimize,
                filter(
                    lambda action: action.from_version >= from_version and action.to_version <= to_version,
                    self.history
                ),
                []
            )
        )


class Action(object):
    def __init__(self, from_version, to_version):
        if to_version <= from_version:
            raise ValueError('versions incorrect')
        self.from_version = from_version
        self.to_version = to_version


class InsertAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super(InsertAction, self).__init__(from_version, to_version)
        self.pos = pos
        self.text = text

    def apply(self, input_text):
        if self.pos > len(input_text) or self.pos < 0:
            raise ValueError('pos index is out of range')

        before_text = input_text[:self.pos]
        insert_text = before_text + self.text + input_text[self.pos:]
        return insert_text


class ReplaceAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super(ReplaceAction, self).__init__(from_version, to_version)
        self.pos = pos
        self.text = text

    def apply(self, input_text):
        if self.pos > len(input_text) or self.pos < 0:
            raise ValueError('pos index is out of range')

        if self.pos == len(input_text):
            replace_text = input_text + self.text
        else:
            replace_text = input_text.replace(input_text[self.pos], self.text)

        return replace_text


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        super(DeleteAction, self).__init__(from_version, to_version)
        self.pos = pos
        self.length = length

    def apply(self, input_text):
        if self.pos > len(input_text) or self.pos < 0 or self.pos + self.length > len(input_text):
            raise ValueError('pos index is out of range')

        before_text = input_text[:self.pos]
        insert_text = before_text + input_text[(self.pos + self.length):]
        return insert_text


h = TextHistory()
h.insert('ENDddd')
h.insert(' again bla')
h.replace(text='ING', pos=3)
h.delete(3, 0)
h.insert('asd', 0)
res = h.get_actions(0, 5)
print(res)
print(h.text, h.version)
