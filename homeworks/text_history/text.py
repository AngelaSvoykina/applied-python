# переименовать text_trivial в приватный
class TextHistory():
    def __init__(self):
        self.text_trivival = ''
        self.version_trivial = 0
        self.history = []

    @property
    def text(self):
        return self.text_trivival

    @property
    def version(self):
        return self.version_trivial

    # по дефолту pos конец строки
    def insert(self, text, pos=None):
        if pos is None:
            pos = len(self.text_trivival)

        action = InsertAction(pos=pos, text=text, from_version=self.version_trivial,
                              to_version=self.version_trivial + 1)
        return self.action(action)

    """
    заменить текст с позиции pos (по умолчанию — конец строки).
    Кидает ValueError, если указана недопустимая позиция.
    Замена за пределами строки работает как вставка 
    (т. е. текст дописывается). 
    Возвращает номер новой версии.
    """

    def replace(self, text, pos):
        # здесь мы воспользуемся классами action
        self.version_trivial += 1
        return 1

    def delete(self, pos, length):
        # возвращаем номер новой версии
        self.version_trivial += 1

    # Возвращает номер новой версии.
    # Версия растет не на 1, а устанавливается та, которая указана в action.
    def action(self, action):
        self.text_trivival = action.apply(self.text_trivival)
        self.history.append(action)

        self.version_trivial = action.to_version
        return self.version_trivial

    #  возвращает list всех действий между двумя версиями.
    def get_actions(self, from_version, to_version):
        return self.history


class Action:
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
            raise ValueError('pos is incorrect')

        before_text = input_text[:(self.pos)]
        insert_text = before_text + self.text + input_text[(self.pos):]
        return (insert_text)


class ReplaceAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        super(ReplaceAction, self).__init__(from_version, to_version)
        self.pos = pos
        self.text = text

    def apply(self, input_text):
        # replace_text = trivial_text(trivial_text[pos-1], text)
        # return(replace_text)
        return 1


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        super(DeleteAction, self).__init__(from_version, to_version)
        self.pos = pos
        self.length = length


def apply(self, input_text):
    return 1

# h = TextHistory()
# h.insert('abc')
# h.insert('xyz', pos=1)
# h.insert('END')
# h.insert('BEGIN', pos=0)
# print(h.text, h.version)
