from abc import ABCMeta, abstractmethod


class Animal(metaclass=ABCMeta):
    @abstractmethod
    def move(self):
        print('This Animal Walks')


class Bird(Animal):
    def move(self):
        print('This Animal Fly')


class Bear(Animal):
    def move(self):
        print('This Animal Walks')


a = Animal()
a.move()
