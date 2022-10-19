class Car:
    def __init__(self, model, brand, max_speed, color):
        self.model = model
        self.brand = brand
        self.max_speed = max_speed
        self.color = color
        # validation
        assert model > 1900, 'Model should be greater than 1900'
        assert 100 < max_speed, 'Max speed should be greater than 100'

    def printAllAttributes(self):
        print(f"model is {self.model}")
        print(f"brand is {self.brand}")
        print(f"Max Speed is {self.max_speed}")

# car1=Car(2018,'Honda',280)
# car1.printAllAttributes()
