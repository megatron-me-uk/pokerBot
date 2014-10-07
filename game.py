

class simpleState:
    def __init__(self):
        self.actions=[0]

class randActor:
    def __init__(self):
        self.state=simpleState
    def chooseAction(self,state):
        return sample(state.actions)

cards=[str(x+2) for x in xrange(9)]
cards+=['Jack','Queen','King','Ace']
suits=['Hearts','Diamonds','Clubs','Spades']

class card:
    def __init__(self,num):
        self.num=num
        self.suit=num/13
        self.card=num-self.suit*13
    def __str__(self):
        return "%s of %s" %(cards[self.card],suits[self.suit])

class simpleGame:
    def __init__(self,seed=None):
        if seed is None:
            pass
        else:
            pass
        self.players=[randActor() for _i in xrange(4)]
        self.state=simpleState()
    def play(self):
        pass
    def preflop(self):
        pass
    def flop(self):
        
    def preflop(self):
        
