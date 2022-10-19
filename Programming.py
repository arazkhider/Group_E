from abc import ABCMeta,abstractmethod

class Programming(metaclass=ABCMeta):
    @abstractmethod
    def hasOOP(self):
        pass
    def test(self):
        print('working')
class Python(Programming):
    def hasOOP(self):
        return True
# one=Programming()
two=Python()

print(two.hasOOP())