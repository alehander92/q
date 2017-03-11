import gc, inspect, re
from ast import parse, dump, Name, Tuple

def read_file(a):
    with open(a, 'r') as f:
        text = f.read()
    return QFile(a, text)

WORD_REGEX = re.compile(r'word')
SENTENCE_REGEX = re.compile(r'sentence')
PARAGRAPH_REGEX = re.compile(r'paragraph')

class Q:
    pass

class QFile(Q):

    def __init__(self, a, text):
        self._a = a
        self._text = text
        self._words = None
        self._sentences = None
        self._paragraphs = None
        self._collection = []
        self._index = 0

    def __iter__(self):
        # ok
        # UGH we hack a valid string python code object of the call loop site
        site = '%s    pass' % inspect.stack()[1].code_context[0]
        logic = parse(site)
        # For(
        #   target=Name(id='s', ctx=Store()),
        #   iter=Name(id='f', ctx=Load()), body=[Pass()], orelse=[])
        f = logic.body[0]
        # print(dump(f))
        if isinstance(f.target, Name):
            iter = f.target.id
        elif isinstance(f.target, Tuple) and isinstance(f.target.elts[1], Name):
            iter = f.target.elts[1].id
        else:
            raise NotImplementedError('wtf')

        if WORD_REGEX.findall(iter):
            self._words = self._words or self._parse_words()
            self._collection = self._words
        elif SENTENCE_REGEX.findall(iter):
            self._sentences = self._sentences or self._parse_sentences()
            self._collection = self._sentences
        elif PARAGRAPH_REGEX.findall(iter):
            self._paragraphs = self._paragraphs or self._parse_paragraphs()
            self._collection = self._paragraphs
        else:
            self._collection = self._text

        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self._collection):
            raise StopIteration
        self._index += 1
        return self._collection[self._index - 1]

    # use nltk if you want "real parsing"
    def _parse_words(self):
        return re.findall(r'[a-zA-Z]+', self._text)

    def _parse_sentences(self):
        return [a.strip() for a in re.split(r' *[\.\?!][\'"\)\]]* *', self._text.replace('\n',' ')) if a.strip()]

    def _parse_paragraphs(self):
        return '\n'.join(a.strip() for a in self._text.split('\n')).split('\n\n')

# f = read_file('a')

# for ugh in f:
#     print(ugh)

# for word_x in f:
#     print(word_x)

# for i, long_sentence in enumerate(f):
#     print('%d:%s' % (i, long_sentence))

# for i, paragraph in enumerate(f):
#     print('%d:%s' % (i, paragraph))
