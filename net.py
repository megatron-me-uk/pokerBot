from math import exp,tanh
import random

class neuron:
    def __init__(self,children,weights):
        self.weights=weights
        self.output=None
        self.output_derivative=None
        for i in children:
            self.weights[self,i]=random.random()*2-1
        self.in_neurons=children
        self.out_neurons=None
    def activation(self):
        #self.output_derivative=self.output*(1-self.output)
        self.output=tanh(self.inputs())
        self.output_derivative=1.0-(self.output**2)
        return self.output
    def inputs(self):
        inp=0
        for i in self.in_neurons:
            inp+=self.weights[self,i]*i.output
        return inp
    def calc_delta(self,train_val):
        if train_val==None:
            self.delta=self.outputs()*self.output_derivative
        else:
            self.delta=(self.output-train_val)*self.output_derivative
    def outputs(self):
        out=0
        for o in self.out_neurons:
            out+=o.delta*self.weights[o,self]
        return out

class input_neuron:
    def __init__(self):
        self.output=None
    def activation(self,input):
        self.output=input

class bias_neuron:
    def __init__(self):
        self.output=1
    def activation(self,input):
        return self.output

class output_neuron(neuron):
    def activation(self):
        self.output=self.inputs()
        self.output_derivative=1
        return self.output

class network:
    def __init__(self,n_neurons=[2,80,20,20,20,2],alpha=0.005):
        self.alpha=alpha
        self.momentum=0.45
        self.shape=n_neurons+[]
        self.input_layer=[input_neuron() for i in range(n_neurons[0])]
        input_layer=self.input_layer
        self.layers=[]
        self.weights=dict()
        self.lastchange=dict()
        self.EPS=1e-4
        bias=bias_neuron()
        for n in n_neurons[1:-1]:
            layer=[]
            for j in range(n):
                layer.append(neuron(input_layer+[bias],self.weights))
            self.layers.append(layer)
            input_layer=layer
        layer=[]
        for j in range(n_neurons[-1]):
            layer.append(output_neuron(input_layer+[bias],self.weights))
        self.layers.append(layer)
        for l,k in zip(self.layers[:-1],self.layers[1:]):
            for n in l:
                n.out_neurons=k
        for k in self.weights.keys():
            self.lastchange[k]=0
    def evaluate(self,inputs):
        for i,input in zip(self.input_layer,inputs):
            i.activation(input)
        for l in self.layers:
            for n in l:
                n.activation()
        return [x.output for x in self.layers[-1]]
    def reevaluate(self):
        for l in self.layers:
            for n in l:
                n.activation()
        return [x.output for x in self.layers[-1]]
    def backprop(self,train_vals):
        out_layer=1
        for l in self.layers[::-1]:
            if out_layer:
                for n,tv in zip(l,train_vals):
                    if tv is not None:
                        n.calc_delta(tv)
                    else:
                        n.delta=0
            else:
                for n in l:
                    n.calc_delta(None)
            out_layer=0
        for k,v in self.weights.items():
            change=self.alpha*k[0].delta*k[1].output+self.momentum*self.lastchange[k]
            self.weights[k]-=change
            self.lastchange[k]=change
    def backprop_numerical(self,train_vals):
        o0=self.reevaluate()
        err=[x0-t for x0,t in zip(o0,train_vals)]
        for k,v in self.weights.items():
            self.weights[k]=v-self.EPS
            o1=self.reevaluate()
            self.weights[k]=v+self.EPS
            o2=self.reevaluate()
            delta=[]
            delta=[(x2-x1)/(2*self.EPS) for x1,x2 in zip(o1,o2)]
            delta_total=0
            for e,d in zip(err,delta):
                delta_total+=e*d
            change=self.alpha*delta_total+self.momentum*self.lastchange[k]
            self.weights[k]=v-change
            self.lastchange[k]=change
    def eq(self,other):
        if len(self.input_layer)!=len(other.input_layer):
            return False
        if len(self.layers[-1])!=len(other.layers[-1]):
            return False
        err=0
        for i in range(1000):
            inp=[random.random() for j in self.input_layer]
            err+=sum([(s-o)**2 for s,o in zip(self.evaluate(inp),other.evaluate(inp))])
        return exp(-err)

def eChoice(values,actions,epsilon=0.4):
    p=[]
    for v in values:
        p+=[epsilon/len(values)]
        if v==max(values):
            p[-1]+=1-epsilon
    rr=random.random()
    cu=0
    for pp,a in zip(p,actions):
        cu+=pp
        if cu>rr:
            return a

a=None
def main():
    global a
    a=network()
    orig_err=0
    test=[]
    for i in range(1000):
        x=random.random()
        y=random.random()
        test.append([x,y])
        o=a.evaluate([x,y])
        orig_err+=((1-x)*x*y*20-o[0])**2+((1-x)*x*(1-y)*20-o[1])**2
    print(orig_err)
    for j in range(200):
        for i in range(1000):
            x=random.random()
            y=random.random()
            o=a.evaluate([x,y])
            a.backprop([(1-x)*x*y*20,(1-x)*x*(1-y)*20])
        err=0
        for i in test:
            x=i[0]
            y=i[1]
            o=a.evaluate([x,y])
            err+=((1-x)*x*y*20-o[0])**2+((1-x)*x*(1-y)*20-o[1])**2
        print(err)
    return a

def main2():
    global a
    a=network(n_neurons=[1,80,20,20,20,2])
    import ladderWorld
    w=ladderWorld.ladder()
    max_state=max(w.states)
    mu_reward=0
    alpha=0.01
    gamma=0.95
    for ep in range(100000):
        ep_reward=0
        state=5#random.choice(w.states)
        i=0
        while state is not None and i<100:
            action=a.evaluate([state/max_state])
            left=action[0]
            right=action[1]
            rr=random.random()
            if rr<0.8:
                if left>right:
                    Q=action[0]
                    action='l'
                elif right>left:
                    Q=action[1]
                    action='r'
                else:
                    print(action)
                    return a
            else:
                if left>right:
                    Q=action[1]
                    action='r'
                else:
                    Q=action[0]
                    action='l'
            (new_state,reward)=w.transition(state,action)
            ep_reward+=reward
            if new_state is None:
                if action=='l':
                    a.backprop([reward/10,None])
                else:
                    a.backprop([None,reward/10])
            else:
                vals=a.evaluate([new_state/max_state])
                a.evaluate([state/max_state])
                if action=='l':
                    a.backprop([reward/10+gamma*max(vals),None])
                else:
                    a.backprop([None,reward/10+gamma*max(vals)])
            state=new_state
            i+=1
        mu_reward*=0.99
        mu_reward+=alpha*ep_reward
        print(mu_reward)
    return a

def mainGrid():
    global a
    a=network(n_neurons=[2,20,20,4])
    import gridWorld
    w=gridWorld.grid()
    a.w=w
    max_state=max(w.states)
    mu_reward=0
    alpha=0.01
    gamma=0.95
    for ep in range(100000):
        ep_reward=0
        state=(0,0)#random.choice(w.states)
        i=0
        while state is not None and i<1000:
            action=a.evaluate([s/m for s,m in zip(state,max_state)])
            action=eChoice(action,['l','r','u','d'])
            (new_state,reward)=w.transition(state,action)
            if ep%1000==0:
                print(state,action,reward,new_state)
            ep_reward+=reward
            if new_state is None:
                R=[reward/100 if action==aa else None for aa in ['l','r','u','d']]
                a.backprop(R)
            else:
                vals=a.evaluate([n/m for n,m in zip(new_state,max_state)])
                a.evaluate([s/m for s,m in zip(state,max_state)])
                R=[reward/100+gamma*max(vals) if action==aa else None for aa in ['l','r','u','d']]
                a.backprop(R)
            state=new_state
            i+=1
        mu_reward*=0.99
        mu_reward+=alpha*ep_reward
        print(mu_reward,i)
    return a

def main3(nn=[1,1,1]):
    global a
    a=network(n_neurons=nn)
    b=network(n_neurons=nn)
    from copy import deepcopy
    c=deepcopy(a)
    #def fn(input):
    #    return 1.0/(1.0+exp((0.5-input)/3.0))
    a.fn=b
    c.fn=b
    error=0.0
    error2=0.0
    for i in range(10000):
        input=[random.random() for n in a.input_layer]
        val=a.fn.evaluate(input)
        output=a.evaluate(input)
        a.backprop(val)
        output2=c.evaluate(input)
        c.backprop_numerical(val)
        error*=0.99
        error+=0.01*sum([(o-v)**2 for o,v in zip(output,val)])
        error2*=0.99
        error2+=0.01*sum([(o-v)**2 for o,v in zip(output2,val)])
        if i%50==0:
            print(error,error2,output[0],val[0],a.eq(a.fn),a.eq(c))
    return a

if __name__=="__main__":
    a=main3()
