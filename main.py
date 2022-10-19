from Computer import Computer
from Phone import Phone
from Product import Product

mouse = Product('JeDEL', 'black', 5)
ph1 = Phone('Galaxy A20', "White", 350, "SAMSUNG")
pc = Computer('Lenove-1200', 'Black', 800, 'Lenovo', 'Laptop')
# print(mouse.price)
print(pc.__dict__)
