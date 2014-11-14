import random

class qActor:
    def __init__(self,states,actions):
        self.Q=dict()
        self.actions=dict()
        self.inv_actions=dict()
        for s in states:
            self.Q[s]=[]
            for i,a in enumerate(actions):
                self.actions[a]=i
                self.inv_actions[i]=a
                self.Q[s].append(random.random())
        self.alpha=0.01
        self.gamma=0.95
        self.epsilon=0.4
    def select_action(self,state):
        pp=[]
        for a in self.Q[state]:
            if a==max(self.Q[state]):
                pp.append(1-self.epsilon+self.epsilon/len(self.Q[state]))
            else:
                pp.append(self.epsilon/len(self.Q[state]))
        rr=random.random()
        if pp[0]>rr:
            return self.inv_actions[0]
        cu=pp[0]
        for i,(p,q) in enumerate(zip(pp[1:],pp[:-1])):
            cu+=p
            if cu>rr:
                return self.inv_actions[i+1]
        print(rr,pp)
        return None
    def update(self,state,action,reward,new_state):
        if new_state is None:
            self.Q[state][self.actions[action]]+=self.alpha*(reward-self.Q[state][self.actions[action]])
        else:
            self.Q[state][self.actions[action]]+=self.alpha*(reward+self.gamma*max(self.Q[new_state])-self.Q[state][self.actions[action]])

class grid:
    def __init__(self):
        self.states=[]
        for i in range(9):
            self.states+=[(i,j) for j in range(9)]
        self.actions=['l','r','u','d']
        self.goal=dict()
        self.goal[(5,5)]=10
        self.goal[(4,5)]=-10
        self.goal[(5,4)]=-10
        self.stepcost=-1
    def transition(self,state,action):
        if state in self.goal:
            return (None,self.goal[state])
        elif action=='l':
            newstate=(state[0]-1,state[1])
        elif action=='r':
            newstate=(state[0]+1,state[1])
        elif action=='u':
            newstate=(state[0],state[1]+1)
        elif action=='d':
            newstate=(state[0],state[1]-1)
        else:
            print('oh dear',action)
        if newstate in self.states:
            return (newstate,self.stepcost)
        else:
            return (state,self.stepcost)

def main():
    w=grid()
    a=qActor(w.states,w.actions)
    mu_reward=0
    alpha=0.01
    for ep in range(100000):
        ep_reward=0
        state=(0,0)#random.choice(w.states)
        i=0
        while state is not None:
            action=a.select_action(state)
            (new_state,reward)=w.transition(state,action)
            ep_reward+=reward
            a.update(state,action,reward,new_state)
            state=new_state
            i+=1
        mu_reward*=0.99
        mu_reward+=alpha*ep_reward
        print(mu_reward,i)
    return a

if __name__=="__main__":
    a=main()
