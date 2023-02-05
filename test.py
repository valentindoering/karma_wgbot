class Mother():
    preference = None

    def __init__(self):
        self.name = "I am Mother"
    def print(self):
        print(self.name)
    
    def pref(self):
        print(self.preference)

class Daughter(Mother):
    preference = "I like to eat"

    def __init__(self):
        super().__init__()
        self.name = "I am Daughter"

d = Daughter()
d.pref()