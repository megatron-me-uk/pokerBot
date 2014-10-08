import random
from collections import Counter

def second_largest(numbers):
    first, second = None, None
    for n in numbers:
        if n > first:
            first, second = n, first
        elif first > n > second:
            second = n
    return second

class simpleState:
    def __init__(self):
        self.actions=[0]
        self.cards=[]
        self.table=None
        self.balance=100
    def add(self,card):
        self.cards.append(card)

class randActor:
    def __init__(self):
        self.state=simpleState()
    def chooseAction(self,state):
        return sample(state.actions)

cards=[str(x+2) for x in range(9)]
cards+=['Jack','Queen','King','Ace']
suits=['Hearts','Diamonds','Clubs','Spades']

class hand:
    def __init__(self,cards):
        self.cards=cards
        self.N=len(self.cards)
        if self.N<5:
            self.hand='Incomplete'
            self.rank=-1
            return None
        self.nums=[x.card for x in cards]
        self.suits=[x.suit for x in cards]
        self.numsCount=Counter([x.card for x in cards])
        self.suitsCount=Counter([x.suit for x in cards])
        self.highCard=max(self.nums)
        self.rank=-1
        if self.suitsCount.most_common(1)[0][1]>4:
            suitnums=[x.num-x.suit*13 for x in cards if x.suit==self.suitsCount.most_common(1)[0][0]]
            st=self.isStraight(suitnums)
            if st>-1:
                self.hand='Straight Flush'#10 perms
                self.rank=13-st
                return None
            else:
                self.hand='Flush'#lt 46656 perms
                self.rank=322+(13-max(suitnums))*9*9*9*8
        if self.numsCount.most_common(1)[0][1]>3:
            self.hand='4 of a Kind'#156 perms
            self.rank=10+(13-self.numsCount.most_common(1)[0][0])*12
            if max(self.nums)>self.numsCount.most_common(1)[0][0]:
                self.rank-=max(self.nums)-1
            elif max(self.nums)==self.numsCount.most_common(1)[0][0]:
                if second_largest(self.nums)>self.numsCount.most_common(1)[0][0]:
                    self.rank-=second_largest(self.nums)-1
                else:
                    self.rank-=second_largest(self.nums)
            else:
                self.rank-=max(self.nums)
            return None
        if self.numsCount.most_common(1)[0][1]>2 and self.numsCount.most_common(2)[1][1]>1:
            self.hand='Full House'#156 perms
            self.rank=166+(13-self.numsCount.most_common(1)[0][0])*12
            if self.numsCount.most_common(2)[1][0]>self.numsCount.most_common(1)[0][0]:
                self.rank-=self.numsCount.most_common(2)[1][0]-1
            else:
                self.rank-=self.numsCount.most_common(2)[1][0]
            return None
        if self.rank>-1:
            return None#flush
        st=self.isStraight(self.nums)
        if st>-1:
            self.hand='Straight'#10 perms
            self.rank=46978+(13-st)
            return None
        if self.numsCount.most_common(1)[0][1]>2:
            self.hand='3 of a Kind'
            self.rank=46988+(13-self.numsCount.most_common(1)[0][0])*12*11
            return None
        if self.numsCount.most_common(1)[0][1]>1:
            if self.numsCount.most_common(2)[1][1]>1:
                self.hand='2 Pair'
                self.rank=48704+(13-self.numsCount.most_common(1)[0][0])*12*11
                return None
            self.hand='Pair'
            self.rank=50420+(13-self.numsCount.most_common(1)[0][0])*12*11
            return None
        self.hand='High Card'
        self.rank=52136+(13-self.numsCount.most_common(1)[0][0])*12*11
    def isStraight(self,nums):
        return -1

class card:
    def __init__(self,num):
        self.num=num
        self.suit=num//13
        self.card=num-self.suit*13
    def __str__(self):
        return "%s of %s" %(cards[self.card],suits[self.suit])

class deck:
    def __init__(self):
        self.cards=[card(i) for i in range(52)]
        self.burn=[]
        random.shuffle(self.cards)
    def __str__(self):
        return "%s cards left" %(len(self.cards))
    def draw(self):
        cc=self.cards.pop()
        self.burn.append(cc)
        return cc

class simpleGame:
    def __init__(self,seed=None):
        if seed is None:
            pass
        else:
            pass
        self.players=[randActor() for _i in range(4)]
        self.state=simpleState()
        self.deck=deck()
    def play(self):
        self.blinds()
        self.preflop()
        self.betting()
        self.flop()
        self.betting()
        self.turn()
        self.betting()
        self.river()
        self.betting()
        self.payWinner()
    def blinds(self):
        pass
    def preflop(self):
        self.table=[]
        for pl in self.players:
            for i in range(2):
                pl.state.add(self.deck.draw())
            pl.state.table=self.table
    def flop(self):
        self.table+=[self.deck.draw() for i in range(3)]
    def turn(self):
        self.table.append(self.deck.draw())
    def river(self):
        self.table.append(self.deck.draw())
    def betting(self):
        pass
    def payWinner(self):
        #for pp in 
        pass

def main():
    g=simpleGame()
    g.play()
    ranks=[]
    for pp in g.players:
        pp.state.hand=hand(g.table+pp.state.cards)
        ranks.append(pp.state.hand.rank)
    print(ranks)
    winners=[]
    best=min(ranks)
    for idx,rr in enumerate(ranks):
        if rr==best:
            winners.append(idx)
    for cc in g.table:
        print(cc)
    for ww in winners:
        print(g.players[ww].state.hand.hand)
        for cc in g.players[ww].state.cards:
            print(cc)

if __name__=="__main__":
    main()
