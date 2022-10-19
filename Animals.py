from abc import ABCMeta, abstractmethod


class Animal(metaclass=ABCMeta):
    @abstractmethod
    def move(self):
        print('This Animal Walks')

#This is birds
class Bird(Animal):
    def move(self):
        print('This Animal Fly')

#Bear
class Bear(Animal):
    def move(self):
        print('This Animal Walks')


# this is edited by me
a = Animal()
a.move()


