from Phone import Phone


class Computer(Phone):
    def __init__(self, name, color, price, brand, type):
        super().__init__(name, color, price, brand)
        self.type = type


print(c.brand)
