import random
from collections import Counter,deque

def second_largest(numbers):
    first, second = -1,-1
    for n in numbers:
        if n > first:
            first, second = n, first
        elif first > n > second:
            second = n
    return second

class simpleState:
    def __init__(self,balance):
        self.actions=[0]
        self.cards=cardlist()
        self.table=None
        self.balance=balance
        self.min_balance=balance
        self.hand=NoHand()
    def add(self,card):
        self.cards.append(card)
    def clear(self):
        self.cards=cardlist()
        self.hand=NoHand()
        if self.min_balance>self.balance:
            self.min_balance=self.balance

class dumbActor:
    def __init__(self,balance=100):
        self.state=simpleState(balance)
    def chooseAction(self,state):
        return self.sample(state.actions)
    def bet(self,maxbet):
        return maxbet-self.state.inround
    def pay(self,amnt):
        self.state.balance+=amnt

class selectActor(dumbActor):
    def bet(self,maxbet):
        for cc in self.state.cards:
            if cc.card>10:
                return maxbet-self.state.inround
        if self.state.cards[0].card==self.state.cards[1].card:
            return maxbet-self.state.inround
        #if self.state.cards[0].suit==self.state.cards[1].suit:
        #    return maxbet-self.state.inround
        return 0

class humanActor(dumbActor):
    def bet(self,maxbet):
        print("table:")
        print(self.state.table)
        print("hand:")
        print(self.state.cards)
        val=-1
        print("Balance:%f Max in round:%f Your in round:%f"%(self.state.balance,maxbet,self.state.inround))
        while val<0:
            try:
                val=float(input("place bet:"))
            except ValueError:
                pass
        print(val)
        return val
    def pay(self,amnt):
        super().pay(amnt)
        print(self.state.hand.hand)
        print("Won:%f"%(amnt,))

class nnActor(dumbActor):
    def __init__(self,balance=100):
        import net
        super().__init__(balance)
        self.nn=net.network(n_neurons=[2,80,20,20,20,2])
        self.gamma=0.95
        self.epsilon=0.2
        self.state.state=[0,0]
    def bet(self,maxbet):
        s=[]
        for cc in self.state.cards:
            s.append((cc.card+1)/14)
        ac=self.nn.evaluate(s)
        qcall=ac[1]
        qfold=ac[0]
        if qcall>qfold:
            greedyact=1
            explore1=0
        else:
            greedyact=0
            explore1=1
        rr=random.random()
        if rr<(1-self.epsilon):
            a=greedyact
        else:
            a=explore1
        self.nn.evaluate(self.state.state)
        if a==0:
            self.nn.backprop([self.gamma*max(ac),None])
        else:
            self.nn.backprop([None,self.gamma*max(ac)])
        self.state.state=s
        if a==0:
            self.state.action=0
            return 0
        elif a==1:
            self.state.action=1
            return maxbet-self.state.inround
    def pay(self,amnt):
        super().pay(amnt)
        r=amnt-self.state.inround
        self.nn.evaluate(self.state.state)
        if self.state.action==0:
            self.nn.backprop([r,None])
        else:
            self.nn.backprop([None,r])
        self.state.action=0
        self.state.state=[0,0]
    def __str__(self):
        return "nnActor"# with tc=%d" %(self.tc,)

class qActor(dumbActor):
    def __init__(self,balance=100,tc=3):
        super().__init__(balance)
        self.tc=tc
        self.Q=[]
        self.state.record=[]
        n=1
        for i in range(tc+2):
            n+=13**(i+1)
        for i in range(2):
            Qs=[]
            rec=[]
            [Qs.append(random.random()) for k in range(n)]
            [rec.append(0) for k in range(n)]
            self.Q.append(Qs)
            self.state.record.append(rec)
        self.epsilon=0.1
        self.alpha=0.1
        self.gamma=0.95
        self.state.r=None
    def bet(self,maxbet):
        s=0
        mult=0
        for cc in self.state.cards+self.state.table[:self.tc]:
            s+=(1+cc.card)*(13**mult)
            mult+=1
        #qraise=self.Q[2][s]
        qcall=self.Q[1][s]
        qfold=self.Q[0][s]
        #if qraise>qcall and qraise>qfold:
        #    greedyact=2
        #    explore1=1
        #    explore2=0
        if qcall>qfold:
            greedyact=1
        #    explore1=2
            explore2=0
        else:
            greedyact=0
        #    explore1=2
            explore2=1
        rr=random.random()
        if rr<(1-self.epsilon):
            a=greedyact
        #elif rr>(1-self.epsilon/2):
        #    a=explore1
        else:
            a=explore2
        if self.state.r is not None:
            #if self.Q[a][s]==1337:
            #    self.Q[a][s]=self.state.r
            #else:
            self.Q[self.state.action][self.state.state]+=self.alpha*(self.gamma*max([self.Q[0][s],self.Q[1][s]])-self.Q[self.state.action][self.state.state])
        self.state.state=s
        if a==0:
            self.state.action=0
            return 0
        elif a==1:
            self.state.action=1
            return maxbet-self.state.inround
        #else:
        #    self.state.action=2
        #    return maxbet-self.state.inround+1
    def pay(self,amnt):
        super().pay(amnt)
        self.state.record[self.state.action][self.state.state]+=amnt-self.state.inround
        r=amnt-self.state.inround
        self.Q[self.state.action][self.state.state]+=self.alpha*(r+self.gamma*self.Q[0][0]-self.Q[self.state.action][self.state.state])
        self.state.action=0
        self.state.state=0
        self.state.r=0
    def __str__(self):
        return "qActor with tc=%d" %(self.tc,)

cards=[str(x+2) for x in range(9)]
cards+=['Jack','Queen','King','Ace']
suits=['Hearts','Diamonds','Clubs','Spades']

class NoHand:
    def __init__(self):
        self.hand=None
        self.rank=None

class hand(NoHand):
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

class cardlist(list):
    def __str__(self):
        return "||".join([str(x) for x in self])

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
        self.origplayers=[dumbActor() for _i in range(6)]+[qActor(),qActor()]#(tc=0)]
        self.players=deque(self.origplayers)
        #self.state=simpleState()
        self.deck=deck()
        self.lb=-2
        self.bb=-1
        self.lbv=0.5
        self.bbv=1
        self.pot=0
        self.roundplayers=[]
    def play(self):
        self.deck=deck()
        self.blinds()
        self.preflop()
        self.betting()
        self.flop()
        #self.betting()
        self.turn()
        #self.betting()
        self.river()
        #self.betting()
        self.payWinner()
    def blinds(self):
        self.players.rotate(1)
        for pp in self.players:
            pp.state.inround=0
        self.players[self.lb].state.balance-=self.lbv
        self.players[self.lb].state.inround+=self.lbv
        self.pot+=self.lbv
        self.players[self.bb].state.balance-=self.bbv
        self.players[self.bb].state.inround+=self.bbv
        self.pot+=self.bbv
        self.maxbet=self.bbv
        self.raiser=None
    def preflop(self):
        self.table=cardlist()
        self.roundplayers=[]
        for pl in self.players:
            for i in range(2):
                pl.state.add(self.deck.draw())
            pl.state.table=self.table
            self.roundplayers.append(pl)
    def flop(self):
        self.table+=[self.deck.draw() for i in range(3)]
    def turn(self):
        self.table.append(self.deck.draw())
    def river(self):
        self.table.append(self.deck.draw())
    def betting(self):
        maxbet=0
        while maxbet!=self.maxbet:
            maxbet=self.maxbet
            roundplayers=list(self.roundplayers)
            for pl in roundplayers:
                if pl==self.raiser:
                    break
                amnt=pl.bet(self.maxbet)
                pl.state.balance-=amnt
                self.pot+=amnt
                pl.state.inround+=amnt
                if pl.state.inround>self.maxbet:
                    self.maxbet=pl.state.inround
                    self.raiser=pl
                elif pl.state.inround<self.maxbet:
                    self.roundplayers.remove(pl)
        self.raiser=None
    def payWinner(self):
        ranks=[]
        for pp in self.roundplayers:
            pp.state.hand=hand(self.table+pp.state.cards)
            ranks.append(pp.state.hand.rank)
        winners=[]
        best=min(ranks)
        for rr,pp in zip(ranks,self.roundplayers):
            if rr==best:
                winners.append(pp)
        val=self.pot
        for idx,pp in enumerate(self.players):
            if pp in winners:
                pp.pay(self.pot/len(winners))
            else:
                pp.pay(0)
        for pl in self.players:
            pl.state.clear()
        self.pot=0

def main():
    g=simpleGame()
    for i in range(100000):
        g.play()
        if i%1000==0:
            print(i)
            for pl in g.players:
                print(pl,pl.state.balance)
    for pl in g.players:
        print(pl,pl.state.balance)
    return g

if __name__=="__main__":
    g=main()
