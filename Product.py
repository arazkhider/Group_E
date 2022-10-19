class Product:
    def __init__(self, name, color, price):
        self.price = price
        self.name = name
        self.color = color

         

    def calculateDiscount(self, discount):
        return self.price - (self.price * (discount / 100))


# class Phone(Product):
p1 = Product('Guitar', 'Brown', 300)
print(p1.calculateDiscount(10))
