from abc import ABC, abstractmethod

class Fourmis(ABC):
    def __init__(self, hp: int, atk: int):
        self.hp = hp
        self.atk = atk

    @abstractmethod
    def attack(self, other):
        pass

class Ouvriere(Fourmis):
    def __init__(self):
        super().__init__(hp=10, atk=2)

    def attack(self, other):
        other.hp -= self.atk



class Soldat(Fourmis):
    def __init__(self):
        super().__init__(hp=25, atk=5)

    def attack(self, other):
        other.hp -= self.atk
