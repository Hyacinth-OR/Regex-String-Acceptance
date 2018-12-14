'''
CS454 Final Project
By: Colin Dutra

Problem 9
Problem:
Implement a program that tests membership of a given string w in a regular expression R.
Specifically, your program will take as input a regular expression (such as (a+a.b)*.(a+ε)
and a string w = abaab, and outputs ‘yes’ if w is in L(R), ‘no’ else. Three steps are
involved in solving this problem:
1. convert the regular expression to an ε-NFA
2. remove ε-moves and
3. Test if w is accepted by the ε-free NFA.
'''
import random
import tkinter
import sys
class Automata:

    def __init__(self, language = set(['0', '1'])):
        self.states = set()
        self.startstate = None
        self.finalstates = []
        self.transitions = dict()
        self.language = language

    @staticmethod
    def epsilon():
        return ":e:"

    def setStartState(self, state):
        self.startstate = state
        self.states.add(state)

    def acceptsString(self, string):
        currentstate = self.startstate
        for ch in string:
            if ch==":e:":
                continue
            st = list(self.gettransitions(currentstate, ch))
            if len(st) == 0:
                return False
            currentstate = st[0]
        if currentstate in self.finalstates:
            return True
        return False


    def addFinalStates(self, state):
        if isinstance(state, int):
            state = [state]
        for s in state:
            if s not in self.finalstates:
                self.finalstates.append(s)

    def addTransition(self, fromstate, tostate, inp):
        if isinstance(inp, str):
            inp = set([inp])
        self.states.add(fromstate)
        self.states.add(tostate)
        if fromstate in self.transitions:
            if tostate in self.transitions[fromstate]:
                self.transitions[fromstate][tostate] = self.transitions[fromstate][tostate].union(inp)
            else:
                self.transitions[fromstate][tostate] = inp
        else:
            self.transitions[fromstate] = {tostate : inp}

    def addTransition_dict(self, transitions):
        for fromstate, tostates in transitions.items():
            for state in tostates:
                self.addTransition(fromstate, state, tostates[state])

    def gettransitions(self, state, key):
        if isinstance(state, int):
            state = [state]
        trstates = set()
        for st in state:
            if st in self.transitions:
                for tns in self.transitions[st]:
                    if key in self.transitions[st][tns]:
                        trstates.add(tns)
        return trstates

    def getEClose(self, findstate):
        allstates = set()
        states = set([findstate])
        while len(states)!= 0:
            state = states.pop()
            allstates.add(state)
            if state in self.transitions:
                for tns in self.transitions[state]:
                    if Automata.epsilon() in self.transitions[state][tns] and tns not in allstates:
                        states.add(tns)
        return allstates


    def newBuildFromNumber(self, startnum):
        translations = {}
        for i in list(self.states):
            translations[i] = startnum
            startnum += 1
        rebuild = Automata(self.language)
        rebuild.setStartState(translations[self.startstate])
        rebuild.addFinalStates(translations[self.finalstates[0]])
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.addTransition(translations[fromstate], translations[state], tostates[state])
        return [rebuild, startnum]

    def newBuildFromEquivalentStates(self, equivalent, pos):
        rebuild = Automata(self.language)
        for fromstate, tostates in self.transitions.items():
            for state in tostates:
                rebuild.addTransition(pos[fromstate], pos[state], tostates[state])
        rebuild.setStartState(pos[self.startstate])
        for s in self.finalstates:
            rebuild.addFinalStates(pos[s])
        return rebuild



class BuildAutomata:
    @staticmethod
    def basicstruct(inp):
        state1 = 1
        state2 = 2
        basic = Automata()
        basic.setStartState(state1)
        basic.addFinalStates(state2)
        basic.addTransition(1, 2, inp)
        return basic

    @staticmethod
    def barAutomata(a, b):
        [a, m1] = a.newBuildFromNumber(2)
        [b, m2] = b.newBuildFromNumber(m1)
        state1 = 1
        state2 = m2
        bar = Automata()
        bar.setStartState(state1)
        bar.addFinalStates(state2)
        bar.addTransition(bar.startstate, a.startstate, Automata.epsilon())
        bar.addTransition(bar.startstate, b.startstate, Automata.epsilon())
        bar.addTransition(a.finalstates[0], bar.finalstates[0], Automata.epsilon())
        bar.addTransition(b.finalstates[0], bar.finalstates[0], Automata.epsilon())
        bar.addTransition_dict(a.transitions)
        bar.addTransition_dict(b.transitions)
        return bar

    @staticmethod
    def dotAutomata(a, b):
        [a, m1] = a.newBuildFromNumber(1)
        [b, m2] = b.newBuildFromNumber(m1)
        state1 = 1
        state2 = m2-1
        dot = Automata()
        dot.setStartState(state1)
        dot.addFinalStates(state2)
        dot.addTransition(a.finalstates[0], b.startstate, Automata.epsilon())
        dot.addTransition_dict(a.transitions)
        dot.addTransition_dict(b.transitions)
        return dot

    @staticmethod
    def starAutomata(a):
        [a, m1] = a.newBuildFromNumber(2)
        state1 = 1
        state2 = m1
        star = Automata()
        star.setStartState(state1)
        star.addFinalStates(state2)
        star.addTransition(star.startstate, a.startstate, Automata.epsilon())
        star.addTransition(star.startstate, star.finalstates[0], Automata.epsilon())
        star.addTransition(a.finalstates[0], star.finalstates[0], Automata.epsilon())
        star.addTransition(a.finalstates[0], a.startstate, Automata.epsilon())
        star.addTransition_dict(a.transitions)
        return star


class eFreefromNFA:

    def __init__(self, nfa):
        self.buildeFree(nfa)


    def geteFree(self):
        return self.eFree


    def displayeFree(self):
        self.eFree.display()


    def buildeFree(self, nfa):
        allstates = dict()
        eclose = dict()
        count = 1
        state1 = nfa.getEClose(nfa.startstate)
        eclose[nfa.startstate] = state1
        eFree = Automata(nfa.language)
        eFree.setStartState(count)
        states = [[state1, count]]
        allstates[count] = state1
        count +=  1
        while len(states) != 0:
            [state, fromindex] = states.pop()
            for char in eFree.language:
                trstates = nfa.gettransitions(state, char)
                for s in list(trstates)[:]:
                    if s not in eclose:
                        eclose[s] = nfa.getEClose(s)
                    trstates = trstates.union(eclose[s])
                if len(trstates) != 0:
                    if trstates not in allstates.values():
                        states.append([trstates, count])
                        allstates[count] = trstates
                        toindex = count
                        count +=  1
                    else:
                        toindex = [k for k, v in allstates.items() if v == trstates][0]
                    eFree.addTransition(fromindex, toindex, char)
        for value, state in allstates.items():
            if len(nfa.finalstates) == 0:
                continue
            elif nfa.finalstates[0] in state:
                eFree.addFinalStates(value)
        self.eFree = eFree

    def acceptsString(self, string):
        currentstate = self.eFree.startstate
        for ch in string:
            if ch==":e:":
                continue
            st = list(self.eFree.gettransitions(currentstate, ch))
            if len(st) == 0:
                return False
            currentstate = st[0]
        if currentstate in self.eFree.finalstates:
            return True
        return False



class NFAfromRegex:

    def __init__(self, regex):
        self.star = '*'
        self.plus = '|'
        self.dot = '.'
        self.openParen = '('
        self.closeParen = ')'
        self.Ops = [self.plus, self.dot]
        self.regex = regex
        self.alphabet = [chr(i) for i in range(65,91)]
        self.alphabet.extend([chr(i) for i in range(97,123)])
        self.alphabet.extend([chr(i) for i in range(48,58)])
        self.buildNFA()

    def getNFA(self):
        return self.nfa

    def buildNFA(self):
        language = set()
        self.stack = []
        self.automata = []
        previous = "::e::"
        for char in self.regex:
            if char in self.alphabet:
                language.add(char)
                if previous != self.dot and (previous in self.alphabet or previous in [self.closeParen, self.star]):
                    self.addOpToStack(self.dot)
                self.automata.append(BuildAutomata.basicstruct(char))
            elif char == self.openParen:
                if previous != self.dot and (previous in self.alphabet or previous in [self.closeParen, self.star]):
                    self.addOpToStack(self.dot)
                self.stack.append(char)
            elif char  ==  self.closeParen:
                if previous in self.Ops:
                    print("Character error, please check that your regex is valid and try again.")
                    sys.exit("Error.")
                while(1):
                    if len(self.stack) == 0:
                        print("Stack Empty Error, please check that your regex is valid and try again.")
                        sys.exit("Error.")
                    o = self.stack.pop()
                    if o == self.openParen:
                        break
                    elif o in self.Ops:
                        self.processOp(o)
            elif char == self.star:
                if previous in self.Ops or previous  == self.openParen or previous == self.star:
                    print("Character error, please check that your regex is valid and try again.")
                    sys.exit("Error.")
                self.processOp(char)
            elif char in self.Ops:
                if previous in self.Ops or previous  == self.openParen:
                    print("Character error, please check that your regex is valid and try again.")
                    sys.exit("Error.")
                else:
                    self.addOpToStack(char)
            else:
                print("Invalid Character Error, please check your inputs and try again.")
                sys.exit("Error.")
            previous = char
        while len(self.stack) != 0:
            op = self.stack.pop()
            self.processOp(op)
        if len(self.automata) > 1:
            print(self.automata)
            print("Expression Error, please check that your regex is valid and try again.")
            sys.exit("Error.")
        try:
            self.nfa = self.automata.pop()
        except IndexError:
            print("Index error encountered, this is likely caused by an empty regex.")
            sys.exit("Exiting")
        self.nfa.language = language

    def addOpToStack(self, char):
        while(1):
            if len(self.stack) == 0:
                break
            top = self.stack[len(self.stack)-1]
            if top == self.openParen:
                break
            if top == char or top == self.dot:
                op = self.stack.pop()
                self.processOp(op)
            else:
                break
        self.stack.append(char)

    def processOp(self, Op):
        if Op == self.star:
            a = self.automata.pop()
            self.automata.append(BuildAutomata.starAutomata(a))
        elif Op in self.Ops:
            if len(self.automata) < 2:
                print("Operator Error, please check that your input is valid and try again.")
                sys.exit("Error.")
            a = self.automata.pop()
            b = self.automata.pop()
            if Op == self.plus:
                self.automata.append(BuildAutomata.barAutomata(b,a))
            elif Op == self.dot:
                self.automata.append(BuildAutomata.dotAutomata(b,a))


def Check():

    regex = E1.get()
    string = E2.get()
    epsnfa = NFAfromRegex(regex)
    nfa = epsnfa.getNFA()
    eFree = eFreefromNFA(nfa)
    finalnfa = eFree.geteFree()
    result = finalnfa.acceptsString(string)
    if result:
        result = "Yes."
    else:
        result = "No."

    display.configure(
        text="Is our string: {" + string + "} inside of our regular expression: {" + regex + "}?" + "\n" + result)

window = tkinter.Tk()
myTitle = tkinter.Label(window, text="Project 9", font="Helvetica 16 bold")
myTitle.pack()
demo1 =['((s.u.n)|(m.o.(o*).n))|(t.e.r.(r*).a)', "sun","mooooooooooon","terrrra","terra","moon"]
demo2 =['(1.2).((b.a)*).(3.4)', "12bababa34","12ba34"]
demo3 = ['((2|4|6|8|10)|(1|3|5|7|9))|0','1','2','5','7','9','0']
demo = random.randint(1,3)
if demo == 1:
    regex = demo1[0]
    string = demo1[random.randint(1,len(demo1)-1)]
elif demo == 2:
   regex = demo2[0]
   string = demo2[random.randint(1, len(demo2) - 1)]
else:
    regex = demo3[0]
    string = demo3[random.randint(1, len(demo3) - 1)]
result = ""


L1 = tkinter.Label(window, text="Regular Expression:")
L1.pack()

E1 = tkinter.Entry(window)
E1.pack()
E1.insert(10,regex)

L2 =tkinter.Label(window,text = "String:")
L2.pack()

E2 = tkinter.Entry(window)
E2.pack()
E2.insert(10,string)

display = tkinter.Label(window, font="Helvetica 16 bold")
display.pack()
B = tkinter.Button(window, text="Check", command=Check)
B.pack()

display.configure(
        text="Is our string: {" + string + "} inside of our regular expression: {" + regex + "}?" + "\n" + result)
Check()
window.mainloop()

