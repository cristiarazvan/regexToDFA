import json


class NFA:
    def __init__(self):
        self.Q = set()
        self.SIGMA = set()
        self.q0 = None
        self.F = set()
        self.D = {}


class DFA:
    def __init__(self):
        self.Q = set()
        self.SIGMA = set()
        self.q0 = frozenset()
        self.F = set()
        self.D = {}


def priority(x):
    if x == "*" or x == "+" or x == "?":
        return 3
    if x == ".":
        return 2
    if x == "|":
        return 1
    return -1


def isOp(x):
    return x in ["*", "+", "?", "|", "."]


def addOp(x):
    ans = []
    for i in range(len(x)):
        lft = x[i]
        ans.append(x[i])
        if i + 1 < len(x):
            rght = x[i + 1]
            if (lft.isalnum() or lft == ")" or lft in "*+?") and (
                rght.isalnum() or rght == "("
            ):
                ans.append(".")
    return "".join(ans)


def Postfix(x):
    ans = []
    st = []
    for c in x:
        if c == "(":
            st.append(c)
        elif c == ")":
            while st and st[-1] != "(":
                ans.append(st.pop())
            st.pop()
        elif isOp(c):
            if c in "*+?":
                while st and priority(st[-1]) > priority(c):
                    ans.append(st.pop())

            else:
                while st and priority(st[-1]) >= priority(c):
                    ans.append(st.pop())
            st.append(c)
        else:
            ans.append(c)
    while st:
        ans.append(st.pop())

    return "".join(ans)


def new_state():
    global id_ct
    state = {
        "id": id_ct,
        "delta": {},
        "lambda": [],
    }
    id_ct += 1
    return state


def makeNFA(regex):
    postfix = Postfix(addOp(regex))
    st = []
    for c in postfix:
        if not isOp(c):
            s0 = new_state()
            s1 = new_state()
            s0["delta"][c] = [s1]
            st.append((s0, [s1]))
        elif c == ".":
            p2s, p2e = st.pop()
            p1s, p1e = st.pop()
            for ac in p1e:
                ac["lambda"].append(p2s)
            st.append((p1s, p2e))
        elif c == "*":
            s0 = new_state()
            s1 = new_state()
            ps, pe = st.pop()
            s0["lambda"].append(ps)
            s0["lambda"].append(s1)
            for ac in pe:
                ac["lambda"].append(ps)
                ac["lambda"].append(s1)
            st.append((s0, [s1]))
        elif c == "+":
            s1 = new_state()
            ps, pe = st.pop()
            for ac in pe:
                ac["lambda"].append(ps)
                ac["lambda"].append(s1)
            st.append((ps, [s1]))
        elif c == "?":
            s0 = new_state()
            s1 = new_state()
            ps, pe = st.pop()
            s0["lambda"].append(ps)
            s0["lambda"].append(s1)
            for ac in pe:
                ac["lambda"].append(s1)
            st.append((s0, [s1]))
        elif c == "|":
            s0 = new_state()
            s1 = new_state()
            p2s, p2e = st.pop()
            p1s, p1e = st.pop()
            s0["lambda"].append(p1s)
            s0["lambda"].append(p2s)
            for ac in p1e:
                ac["lambda"].append(s1)
            for ac in p2e:
                ac["lambda"].append(s1)
            st.append((s0, [s1]))

    if len(st) != 1:
        print("invalid regex")
        return None

    start, accepts = st[0]
    nfa = NFA()
    nfa.q0 = start["id"]
    nfa.F = {_["id"] for _ in accepts}
    vis = set()
    stk = [start]
    while stk:
        x = stk.pop()
        acId = x["id"]
        if acId in vis:
            continue
        vis.add(acId)
        nfa.Q.add(acId)

        for c, nodes in x["delta"].items():
            nfa.SIGMA.add(c)
            for nou in nodes:
                nfa.D[acId] = nfa.D.get(acId, {})
                nfa.D[acId][c] = nfa.D[acId].get(c, []) + [nou["id"]]

                if nou["id"] not in vis:
                    stk.append(nou)
        for node in x["lambda"]:
            nfa.D[acId] = nfa.D.get(acId, {})
            nfa.D[acId]["lambda"] = nfa.D[acId].get("lambda", []) + [node["id"]]
            if node["id"] not in vis:
                stk.append(node)
    return nfa


def all_lambda(nfa, start):
    st = list(start)
    vis = set(start)

    while st:
        x = st.pop()
        for i in nfa.D.get(x, {}).get("lambda", []):
            if i not in vis:
                vis.add(i)
                st.append(i)
    return vis


def checkStringNFA(nfa, s):
    if nfa is None or nfa.q0 is None:
        return False
    ac = all_lambda(nfa, {nfa.q0})
    for c in s:
        next = set()
        for i in ac:
            next.update(nfa.D.get(i, {}).get(c, []))

        ac = all_lambda(nfa, next)

        if not ac:
            return False
    return any(i in nfa.F for i in ac)


def makeDFA(nfa):
    if nfa is None:
        return None
    dfa = DFA()
    dfa.SIGMA = nfa.SIGMA

    viz = set()
    dfa_trans = {}
    q = []

    start = all_lambda(nfa, [nfa.q0])
    startfs = frozenset(start)
    dfa.q0 = startfs
    viz.add(startfs)
    q.append(startfs)

    while q:
        ac = q.pop()
        dfa_trans[ac] = {}
        for c in nfa.SIGMA:
            nxt = set()
            for x in ac:
                nxt.update(nfa.D.get(x, {}).get(c, []))
            if not nxt:
                continue

            nxtfs = frozenset(all_lambda(nfa, list(nxt)))
            dfa_trans[ac][c] = nxtfs

            if nxtfs not in viz:
                viz.add(nxtfs)
                q.append(nxtfs)

    dfa.Q = viz
    dfa.D = dfa_trans
    dfa.F = set()
    for x in viz:
        if not x.isdisjoint(nfa.F):
            dfa.F.add(x)

    return dfa


def checkStringDFA(dfa, s):
    if dfa is None or dfa.q0 is None:
        return False
    ac = dfa.q0
    for c in s:
        if c not in dfa.SIGMA:
            return False
        ac = dfa.D.get(ac, {}).get(c, None)
        if ac is None:
            return False

    return ac in dfa.F


if __name__ == "__main__":
    with open("tests.json", "r") as f:
        tests = json.load(f)

    nrCorrect = 0
    nrWrong = 0
    for test in tests:
        print("=================")
        regex = test["regex"]
        test_strings = test["test_strings"]
        id_ct = 0
        acNFA = makeNFA(regex)
        acDFA = makeDFA(acNFA)
        for ac in test_strings:
            inp = ac["input"]
            correct = ac["expected"]
            myAnsNFA = checkStringNFA(acNFA, inp)
            myAnsDFA = checkStringDFA(acDFA, inp)
            if myAnsNFA != myAnsDFA:
                print("NFA Answer and DFA Answer are not same")

            if correct != myAnsDFA:
                print(
                    f"Wrong answer on regex {test['name']} {regex} and string {inp}. Your : {myAnsDFA} Expected : {correct}"
                )
                nrWrong += 1
            else:
                nrCorrect += 1
                print("Correct answer!")
    if nrWrong == 0:
        print(f"All ({nrCorrect}) test cases passed")
    else:
        print(f"{nrCorrect} Correct and {nrWrong} Wrong answers")
