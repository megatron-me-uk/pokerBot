import random

class ladder:
    def __init__(self):
        self.states=[i for i in range(9)]
        self.actions=['l','r']
    def transition(self,state,action):
        if state==0 and action=='l':
            return (None,-10)
        elif state==8 and action=='r':
            return (None,10)
        elif action=='l':
            return (state-1,1)
        elif action=='r':
            return (state+1,-1)
        else:
            print('oh dear')

def main():
    w=ladder()
    import qLearner
    a=qLearner.qActor(w.states,w.actions)
    mu_reward=0
    alpha=0.01
    for ep in range(100000):
        ep_reward=0
        state=5#random.choice(w.states)
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
        print(mu_reward)
    return a

if __name__=="__main__":
    a=main()
