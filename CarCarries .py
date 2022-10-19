from Car import Car


class CarCarries(Car):
    def __init__(self, model, brand, max_speed, carrying_capacity):
        super().__init__(model, brand, max_speed)
        self.carrying_capacity = carrying_capacity
        assert carrying_capacity > 500


car2 = CarCarries(2002, 'TOYUTA', 160, 1000)
car2.printAllAttributes()
print(f"Carrying Capacity is {car2.carrying_capacity}")
