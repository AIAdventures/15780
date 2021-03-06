################################################################################
# Check if a given partial assignment is consistent with the cnf
# Input: formula is a CNF encoded as described in the problem set.
#        ass is a dictionary of assignments.
# Output: Whether there is a clause that is false in the formula.
################################################################################
def check(formula, ass):
    for clause in formula: #of the form (x0 or ~x1 or x3)
        ret = 0
        for v in clause:
            if(v[1] in ass):
                ret = ret or (ass[v[1]] if v[0] == 0 else not ass[v[1]])
            else:
                ret = 1 #special case, cant determine if clause is false yet
                break
        if(not ret): 
            return False #if a clause in the formula is false, return false
    return True #all clauses evaluate to true

################################################################################
# Simple Sat Problem Solver
# Input: n is the number of variables (numbered 0, ..., n-1).
#        formula is CNF
# Output: An assignment that satisfies the formula
#         A count of how many variable assignments were tried
################################################################################
def simpleSolver(n, formula):
    count = 0
    ass = {}
    i = 0
    while i < n:
        if i not in ass:
            ass[i] = 0
        elif ass[i] == 0:
            ass[i] = 1
        count = count + 1
        if check(formula, ass):
            if len(ass) == n:
                return ass, count
        else:
            if ass[i] == 0:
                continue
            elif ass[i] == 1:
                while i >= 0 and ass[i] == 1:
                    del ass[i]
                    i = i - 1
                if i == -1:
                    return False, count
                continue
        i = i + 1
    return False, count

################################################################################
# Simple Sat Problem Solver with unit propagation
## Input: n is the number of variables (numbered 0, ..., n-1).
#        formula is CNF
# Output: An assignment that satisfies the formula
#         A count of how many variable assignments were tried
################################################################################
def unitSolver(n, formula):
    count = 0
    bval = []
    ass = {}
    i = 0
    if not propSinglesUnit(formula, ass):
        return False, count
    valid = True
    tmp = myCopy(formula)
    while i < n:
        if i not in ass:
            ass[i] = 0
            bval.append(i)
        elif ass[i] == 0 and not valid:
            ass[i] = 1
        else:
            i = i + 1
            continue
        count = count + 1
        valid = True
        if check(formula, ass):
            if len(ass) == n:
                return ass, count
            if propVal(i, ass[i], formula):
                if propSinglesUnit(formula, ass):
                    if check(formula, ass):
                        if len(ass) == n:
                            return ass, count
                        i = i + 1
                        continue #skip backtrack
        #Case: backtracking
        dellist = []
        for v in ass:
            if v not in bval:
                if v != i:
                    dellist.append(v)
        for v in dellist:
            del ass[v]
        valid = False
        formula = myCopy(tmp)
        if ass[i] == 0:
            continue #try the 1 branch of this variable
        elif ass[i] == 1:
            #backtrack to previous branch val
            while ass[i] == 1 and len(bval) > 0:
                i = bval.pop()
            if len(bval) == 0:
                return False, count
    return False, count

def propSinglesUnit(formula, ass):
    recurse = True
    while recurse:
        recurse = False
        for clause in formula:
            if len(clause) == 1:
                var = clause[0][1]
                if var not in ass:
                    ass[var] = 0 if clause[0][0] else 1
                    if not check(formula, ass):
                        return False
                    ret = propVal(var, ass[var], formula)
                    if not ret:
                        return False
                    if ret == -1:
                        recurse = True
                elif bool(ass[var]) == bool(clause[0][0]):
                    #a singleton for which the current assigment
                    #will always produce a false clause
                    return False
    return True

#Returns false if assignment fails
def propSingles(formula, ass, level =-1, ig = None):
    recurse = True
    while recurse:
        recurse = False
        for clause in formula:
            if len(clause) == 1:
                var = clause[0][1]
                if var not in ass:
                    ass[var] = 0 if clause[0][0] else 1
                    if ig != None:
                        recurse = ig[var].assign(ass[var], level, ass)
                        updateAssociations(ass, ig, ig[var])
                    if not check(formula, ass):
                        return False
                    ret = propVal(var, ass[var], formula)
                    if not ret:
                        return False
                    if ret == -1:
                        recurse = True
                elif bool(ass[var]) == bool(clause[0][0]):
                    #a singleton for which the current assigment
                    #will always produce a false clause
                    return False
    return True

#Returns false when a contradiction occurs
def propVal(var, val, f):
    ret = True
    for clause in f:
        for literal in clause:
            if literal[1] == var:
                tval = bool(val) != bool(literal[0])
                if tval:
                    for l2 in clause:
                        if l2 != literal:
                            clause.remove(l2)
                    break
                else:
                    clause.remove(literal)
                    if len(clause) == 1:
                        #special case, need to recurse
                        #another call to propSingles
                        ret = -1
                    if len(clause) == 0:
                        return False
    return ret

def myCopy(f):
    ret = []
    for clause in f:
        tmp = []
        for literal in clause:
            tmp.append((literal[0],literal[1]))
        ret.append(tmp)
    return ret

################################################################################
# Clause Learning SAT Problem Solver                      
# Input: n is the number of variables (numbered 0, ..., n-1).
#        formula is CNF
# Output: An assignment that satisfies the formula
#         A count of how many variable assignments where tried
#         A list of all conflict-induced clauses that were found
################################################################################
def clauseLearningSolver(n, formula):
    count = 0
    bval = []
    ass = {}
    ig = []
    learned = []
    level = 0
    i = 0
    #Initialize nodes
    for j in range(0,n):
        ig.append(Node(j, formula))
    if not propSingles(formula, ass, level=level, ig=ig):
        return False, count
    valid = True
    tmp = myCopy(formula)
    #Begin search algorithm
    while i < n:
        node = ig[i]
        if i not in ass:
            ass[i] = 0
            bval.append(i)
        elif ass[i] == 0 and not valid:
            ass[i] = 1
            level = node.level
            node.impliedBy = []
            node.implies = []
        else:
            i = i + 1
            continue
        imp = node.assign(ass[i], level, ass)
        count = count + 1
        valid = True

        if imp:
            #must be done before assigment made via propagation
            updateAssociations(ass, ig, node)

        if check(formula, ass):
            if len(ass) == n:
                return ass, count, learned
            if propVal(i, ass[i], formula):
                ret = propSingles(formula, ass, level, ig)
                if ret:
                    if check(formula, ass):
                        if len(ass) == n:
                            return ass, count, learned
                        i = i + 1
                        level = level + 1
                        continue #skip backtrack
        #Case: backtracking
        conflictNode =  getLastDecided(ig)
        clause = getUIP(conflictNode, ig, level)
        learned.append(clause)
        dellist = []
        for v in ass:
            if v not in bval:
                if v != i:
                    dellist.append(v)
        for v in dellist:
            del ass[v]
            ig[v].unAssign()
        valid = False
        formula = myCopy(tmp)
        if ass[i] == 0:
            continue #try the 1 branch of this variable
        elif ass[i] == 1:
            #backtrack to previous branch val
            while ass[i] == 1 and len(bval) > 0:
                i = bval.pop()
            if len(bval) == 0:
                return False, count, learned
    return False, count, learned

def getUIP(n, graph, level):
    clause = []
    impl = []
    for v in graph[n].impliedBy:
        clause.append((graph[v].val,v))
        if graph[v].level == level:
            impl.append(v)
    if len(impl) == 1:
        #found UIP
        return clause
    else:
        #need to traverse up implication levels until shared parent
        i = 0
        for t in impl:
            if graph[t].level == level:
                if t not in impl:
                    impl.append(t)
                else:
                    for v in graph[t].impliedBy:
                        clause.append((graph[v].val,v))

    return clause
#TODO: this may need to search more in current level


def printReadable(ig):
    for n in ig:
        print "var:",n.var,"val:",n.val, "level:", n.level
        print "\timplied by:", n.impliedBy
        print "\timplies:", n.implies

def updateAssociations(ass, ig, n):
    for i in n.implies:
        node = ig[i]
        s = set(n.clauses)
        clauseIntersect = [val for val in node.clauses if val in s]
        for c in clauseIntersect:
            count = len(c)
            for l in c:
                if l[1] in ass:
                    if ass[l[1]] == l[0]:
                        count = count - 1
            if count == 1:
                for l in c:
                    if l[1] != node.var:
                        if l[1] not in node.impliedBy:
                            node.impliedBy.append(l[1])
                        if l[1] != n.var:
                            ig[l[1]].implies.append(node.var)

def getLastDecided(ig):
    n = ig[0]
    ret = n.decided.pop()
    n.decided.append(ret)
    return ret

################################################################################
# Conflict-directed backjumping with clause learning SAT Problem Solver                      
# Input: n is the number of variables (numbered 0, ..., n-1).
#        formula is CNF
# Output: An assignment that satisfies the formula
#         A count of how many variable assignments where tried
################################################################################
def backjumpSolver(n, formula):
    count = 0
    bval = []
    ass = {}
    ig = []
    level = -1
    i = 0
    #Initialize nodes
    for j in range(0,n):
        ig.append(Node(j, formula))
    if not propSingles(formula, ass, level=level, ig=ig):
        return False, count
    valid = True
    tmp = myCopy(formula)
    #Begin search algorithm
    level = level + 1
    while i < n:
        node = ig[i]
        if i not in ass:
            ass[i] = 0
            bval.append(i)
        elif ass[i] == 0 and not valid:
            if level == node.level:
                ass[i] = 1
                level = node.level
                node.impliedBy = []
                node.implies = []
            elif level < node.level:
                #continue backjumping
                del ass[i]
                node.unAssign()
                i = bval.pop()
                continue
            else:
                print "wiggity wiggity what?"
                return False, ass
        else:
            i = i + 1
            continue
        imp = node.assign(ass[i], level, ass)
        count = count + 1
        valid = True

        if imp:
            #must be done before assigment made via propagation
            updateAssociations(ass, ig, node)

        if check(formula, ass):
            if len(ass) == n:
                return ass, count
            if propVal(i, ass[i], formula):
                ret = propSingles(formula, ass, level, ig)
                if ret:
                    if check(formula, ass):
                        if len(ass) == n:
                            return ass, count
                        i = i + 1
                        level = level + 1
                        continue #skip backtrack
        #Case: backtracking
        conflictNode =  getLastDecided(ig)
        clause = getUIP(conflictNode, ig, level)
        level = getBackJumpLevel(clause, level, ig)
        dellist = []
        for v in ass:
            if ig[v].level >= level:
                dellist.append(v)
        for v in dellist:
            del ass[v]
            ig[v].unAssign()
        valid = False
        formula = myCopy(tmp)
        formula.append(clause)
        tmp = myCopy(formula)
        if len(ass) == 0:
            propSingles(formula, ass, -1, ig)
            if len(ass) == 0:
                return False, count
            i = 0
            valid = True
            level = 0
            continue
        if ass[i] == 0:
            continue #try the 1 branch of this variable
        elif ass[i] == 1:
            #backtrack to previous branch val
            while ass[i] == 1 and len(bval) > 0:
                i = bval.pop()
            if len(bval) == 0:
                return False, count
    return False, count

def getBackJumpLevel(clause, level, ig):
    new = 0
    for l in clause:
        if ig[l[0]].level != level:
            if ig[l[0]].level > new:
                new = ig[l[0]].level
    return new

def main():
    f = [[(1,0),(0,2),(0,3)],[(0,1),(1,4)],[(0,0), (0,1), (0,2), (0,3), (0,4)]]
    h = [[(1,0)],[(0,1),(0,2)],[(0,1),(1,2)],[(1,1),(0,2)],[(1,1),(1,2)]]
    g = [[(0,0), (1, 1)],[(0,1), (0,2)],[(0,1), (1,2)]]
    m = [[(0,0)],[(1,0)]]
    #checkCheck(f)
    #simple(f, 5)
    #simple(h, 3)
    #simple(g, 3)
    #unit(f,5)
    #unit(h,3)
    #unit(g,3)
    #unit(m,1)
    #claus(g,3)
    #claus([[(0,0)], [(1,0),(0,1)]],2)
    #claus([[(0,0),(0,1),(0,2)],[(1,0),(1,1)],[(1,1),(1,2)],[(1,2),(1,0)]],4)
    #claus([[(0,0),(0,1),(0,2)],[(0,0),(0,1),(1,2)]],3)
    jb(g,3)

def jb(f, n):
    print backjumpSolver(n, f)

def claus(f, n):
    print clauseLearningSolver(n, f)

def unit(f, n):
    print unitSolver(n, f)

def simple(f, n):
    print simpleSolver(n, f)

def checkCheck(f):
    a = {1:1, 3:0, 4:1}
    b = {0:1, 1:0, 2:0, 3:0, 4:0}
    c = {0:0, 1:0, 2:0, 3:0, 4:1}
    print check(f,a)
    print check(f,b)
    print check(f,c)
    print check(f, {4:1});
    print check(f, {4:1, 1:0});

class Node:
    decided = [] #stack keeps track of order in which variables were determined
    def __init__(self, var, formula):
        self.var = var
        self.impliedBy = []
        self.implies = []
        self.clauses = []
        self.val = None
        self.level = None
        for c in formula:
            for l in c:
                if l[1] == var:
                    self.clauses.append(tuple(c))
                    break

    def assign(self, val, level, ass):
        if self.val == None:
            self.decided.append(self.var)
        if self.var not in ass:
            print "oops I'm kind of an idiot"
        self.val = val
        self.level = level
        ret = False
        v = -1
        for c in self.clauses:
            count = len(c)
            for l in c:
                if l[1] in ass:
                    if ass[l[1]] == l[0]:
                        #assignment in this clause is 0 so it may imply
                        count = count - 1
                else:
                    v = l
            if count == 1 and v != -1:
                #implication of v
                self.implies.append(v[1])
                ret = True
        return ret

    def unAssign(self):
        self.decided.pop()
        self.val = None
        self.level = None
        self.impliedBy = []
        self.implies = []

if __name__ == "__main__":
    main()
