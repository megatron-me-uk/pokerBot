import random

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
    import qLearner
    a=qLearner.qActor(w.states,w.actions)
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
