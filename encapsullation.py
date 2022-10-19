class Book:
    __author = ""
    __title = ""
    __pages = 0
    _words = 0

    def __init__(self) -> None:
        pass

    def authorSeter(self, author):
        self.__author = author

    def authorGetter(self):
        return self.__author

    def titleSeter(self, title):
        self.__title = title

    def titleGetter(self):
        return self.__title

    def pageSeter(self, pages):
        self.__pages = pages

    def pageGetter(self):
        return self.__pages


b1 = Book()
b1.__author = 'asdlkf'
# b1.authorSeter('Jhone')
print(b1.__author)
