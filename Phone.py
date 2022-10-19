from Product import Product


class Phone(Product):
    def __init__(self, name, color, price, brand):
        super().__init__(name, color, price)
        self.brand = brand
