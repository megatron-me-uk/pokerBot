from math import exp
import random

class neuron:
    def __init__(self,children,weights):
        self.weights=weights
        self.center=random.random()
        self.width=(random.random()+0.01)*2
        self.output=None
        self.output_derivative=None
        for i in children:
            self.weights[self,i]=random.random()*2-1
        self.in_neurons=children
        self.out_neurons=None
    def activation(self):
        #self.output=1.0/(1+exp(-self.inputs()))
        #self.output_derivative=self.output*(1-self.output)
        try:
            self.output=1.0/(1+exp(self.center-self.inputs()/self.width))
        except OverflowError:
            self.output=0.0
        self.output_derivative=self.output*(1-self.output)/self.width
        self.output-=0.5
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

class output_neuron(neuron):
    def activation(self):
        self.output=self.inputs()
        self.output_derivative=1
        return self.output

class network:
    def __init__(self,n_neurons=[2,80,20,20,20,2],alpha=0.05):
        self.alpha=alpha
        self.momentum=0.9
        self.input_layer=[input_neuron() for i in range(n_neurons[0])]
        input_layer=self.input_layer
        self.layers=[]
        self.weights=dict()
        self.lastchange=dict()
        for n in n_neurons[1:-1]:
            layer=[]
            for j in range(n):
                layer.append(neuron(input_layer,self.weights))
            self.layers.append(layer)
            input_layer=layer
        layer=[]
        for j in range(n_neurons[-1]):
            layer.append(output_neuron(input_layer,self.weights))
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
        orig_err+=((1-x)*x*y*2-o[0])**2+((1-x)*x*(1-y)*2-o[1])**2
    print(orig_err)
    for j in range(200):
        for i in range(1000):
            x=random.random()
            y=random.random()
            o=a.evaluate([x,y])
            a.backprop([(1-x)*x*y*2,(1-x)*x*(1-y)*2])
        err=0
        for i in test:
            x=i[0]
            y=i[1]
            o=a.evaluate([x,y])
            err+=((1-x)*x*y*2-o[0])**2+((1-x)*x*(1-y)*2-o[1])**2
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

if __name__=="__main__":
    a=main2()
