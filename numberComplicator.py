import math
import random
import regex as re
import pyperclip as p

ops = ["+","-","*","/","^","%","|","&","⊻","<<",">>"]

precedence = {None:69420,"":42069,"^":1,"u":2,"*":3,"/":3,"%":3,"+":4,"-":4,"<<":5,">>":5,"&":6,"⊻":7,"|":8}

associative = {0:{"^":{"^":1},
                  "*":{"*":1,"/":1,"%":0},
                  "/":{"*":0,"/":0,"%":0},
                  "%":{"*":0,"/":0,"%":0},
                  "+":{"+":1,"-":1},
                  "-":{"+":0,"-":0},
                  "<<":{"<<":0,">>":0},
                  ">>":{"<<":0,">>":0},
                  "&":{"&":1},
                  "⊻":{"⊻":1},
                  "|":{"|":1}},

               1:{"^":{"^":0},
                  "*":{"*":1,"/":1,"%":1},
                  "/":{"*":1,"/":1,"%":1},
                  "%":{"*":1,"/":1,"%":1},
                  "+":{"+":1,"-":1},
                  "-":{"+":1,"-":1},
                  "<<":{"<<":1,">>":1},
                  ">>":{"<<":1,">>":1},
                  "&":{"&":1},
                  "⊻":{"⊻":1},
                  "|":{"|":1}}
               }

def format_operator(op1,a,op,b,op2,rounding=False,d=0):        
    if b < 0:
        if op == "+":
            op = "-"
            b = -b
        elif op == "-":
            op = "+"
            b = -b
    
    if type(a) == float: a = f"{a:.12f}".rstrip("0").rstrip(".")
    if type(b) == float: b = f"{b:.12f}".rstrip("0").rstrip(".")

    if d:
        return format_operator(op1,f"([{a}]{op}[{b}])","+",d,op2)
    
    if (precedence[op1] > precedence[op] or (precedence[op1] == precedence[op] and associative[0][op1][op])) and (precedence[op] < precedence[op2] or (precedence[op] == precedence[op2] and associative[1][op][op2])):
        return ("-" if op1 == "u" else "")+(f"[{a}]{op}[{b}]" if rounding else f"{a}{op}{b}")  
    
    return ("-" if op1 == "u" else "")+(f"([{a}]{op}[{b}])" if rounding else f"({a}{op}{b})")

def sign(num):
    return "-" if num < 0 else ""

def zero_round(flt):
    return round(math.copysign(math.floor(abs(flt)),flt))

def length(exp):
    return len(exp) - len(re.findall("[\[\]]",exp))

def rand(d=3,l=-10,r=10):
    return round(random.random()*(r-l)+l,d)

def expand_match(Match):
    op1, num, op2 = Match.groups()
    num = float(num)

    x = random.randint(0,10)
    op = ops[x]

    if num < 0 and precedence[op2] < precedence["u"] < precedence[op]:
        op1 = "u"
        num = -num

    #split into random sum
    if x == 0:
        tot = rand()

        a = tot
        b = num - tot

        return format_operator(op1,a,op,b,op2)

    #split into random difference
    if x == 1:
        dif = rand()

        a = num + dif
        b = dif

        return format_operator(op1,a,op,b,op2)

    #split into random product
    if x == 2:
        prod = rand()
        if prod == 0: prod = 6.9420

        a = num / prod
        b = prod

        return format_operator(op1,a,op,b,op2)

    #split into random quotient
    if x == 3:
        div = rand()
        if div == 0: div = 6.9420

        a = num * div
        b = div

        return format_operator(op1,a,op,b,op2)

    #split into random power
    if x == 4:
        if num == 0:
            a = .0
            b = rand(l=0.05)
            return format_operator(op1,a,op,b,op2)
        
        a = abs(rand())
        if a == 0: a = 6.9420
        if a == 1: a = 4.2069
        b = math.log(abs(num),a)

        return sign(num) + format_operator(op1,a,op,b,op2)

    #split into random modulus
    if x == 5:
        if num == 0:
            a = .0
            b = rand()
            if b == 0: b = 6.9420
            return format_operator(op1,a,op,b,op2)
        
        b = rand(l = math.copysign(math.ceil(abs(num)),num), r = math.copysign(math.ceil(abs(num))+20,num))
        a = rand(d = None)*b + num

        return format_operator(op1,a,op,b,op2)

    #split into random bitwise or
    if x == 6:
        inum = round(num)
        dnum = num-inum

        MAX = 1 if inum == 0 else math.floor(math.log2(abs(inum))) + 1

        bits = (bin(inum) if inum >= 0 else bin(inum & ((1 << MAX) - 1)))[2:].zfill(MAX)

        a = b = 0
        for i in range(len(bits)):
            a <<= 1
            b <<= 1
            if bits[i] == "0": continue

            e = random.randint(1,3)
            if e & 1: a |= 1
            if e & 2: b |= 1

        if inum < 0:
            if random.randint(0,1): a |= (-1 << MAX)
            else: b |= (-1 << MAX)
            
        a += math.copysign(rand(l=0,r=0.95),a)
        b += math.copysign(rand(l=0,r=0.95),b)

        return format_operator(op1,a,op,b,op2,rounding=True,d=dnum)
    
    #split into random bitwise and
    if x == 7:
        inum = round(num)
        dnum = num-inum

        MAX = 1 if inum == 0 else math.floor(math.log2(abs(inum))) + 1

        bits = (bin(inum) if inum >= 0 else bin(inum & ((1 << MAX) - 1)))[2:].zfill(MAX)

        a = b = 0
        for i in range(len(bits)):
            a <<= 1
            b <<= 1
            if bits[i] == "1":
                a |= 1
                b |= 1
                continue

            e = random.randint(0,2)
            if e & 1: a |= 1
            if e & 2: b |= 1

        if inum < 0:
            m = (-1 << MAX)
            a |= m
            b |= m
            
        a += math.copysign(rand(l=0,r=0.95),a)
        b += math.copysign(rand(l=0,r=0.95),b)

        return format_operator(op1,a,op,b,op2,rounding=True,d=dnum)
    
    #split into random bitwise xor
    if x == 8:
        inum = round(num)
        dnum = num-inum

        MAX = 1 if inum == 0 else math.floor(math.log2(abs(inum))) + 1

        bits = (bin(inum) if inum >= 0 else bin(inum & ((1 << MAX) - 1)))[2:].zfill(MAX)

        a = b = 0
        for i in range(len(bits)):
            a <<= 1
            b <<= 1
            if bits[i] == "1":
                if random.randint(0,1): a |= 1
                else: b |= 1
            else:
                if random.randint(0,1):
                    a |= 1
                    b |= 1
            
        if inum < 0:
            if random.randint(0,1): a |= (-1 << MAX)
            else: b |= (-1 << MAX)
            
        a += math.copysign(rand(l=0,r=0.95),a)
        b += math.copysign(rand(l=0,r=0.95),b)

        return format_operator(op1,a,op,b,op2,rounding=True,d=dnum)
    
    #split into random bitwise left shift
    if x == 9:
        inum = round(num)
        dnum = num-inum

        b = 1 if inum <= 3 else random.randint(1,math.floor(math.log2(abs(inum))))
        a = inum >> b

        dnum += (inum - (a << b))

        a += math.copysign(rand(l=0,r=0.95),a)
        b += rand(l=0,r=0.95)

        return format_operator(op1,a,op,b,op2,rounding=True,d=dnum)

    #split into random bitwise right shift
    if x == 10:
        inum = round(num)
        dnum = num-inum

        b = 1 if inum <= 3 else random.randint(1,math.floor(math.log2(abs(inum))))
        a = inum << b

        a += math.copysign(rand(l=0,r=(1<<(b-1))-.05),a)
        b += rand(l=0,r=0.95)

        return format_operator(op1,a,op,b,op2,rounding=True,d=dnum)

magic = "(?<=(?:(\+|\-|\*|\/|\^|\%|\||\&|⊻|>>|<<)\[?)|.|^|$)((?:(?<=^|\+|\-|\*|\/|\^|\%|\||\&|⊻|>>|<<|\(|\[)\-)?[0-9.]+)(?=(?:\]?(\+|\-|\*|\/|\^|\%|\||\&|⊻|>>|<<))|.|^|$)"

def normalize_signs(exp):
    return exp.replace("+-","-").replace("--","+")

def expand_expression(exp):
    return re.sub(magic,expand_match,exp)

def expand_random(exp):
    s = random.choice(list(re.finditer(magic,exp)))
    return exp[:s.start(0)] + expand_match(s) + exp[s.end(0):]

def to_python(exp):
    return exp.replace("^","**").replace("⊻","^").replace("[","zero_round(").replace("]",")")

def to_discord(exp):
    return re.sub("[\[\]]","",exp)

MAXL = 2000

while 1:
    exp0 = input("type ur number: ")

    try: num = int(exp0)
    except: continue

    rejects = 0
    errors = []
 
    while 1:
        exp = exp0
        
        while 1:
            nex = expand_expression(exp)
            if length(nex) > MAXL: break
            exp = nex

        chances = 10
        while 1:
            nex = expand_random(exp)
            if length(nex) > MAXL:
                if chances == 0: break
                chances -= 1
                continue
            exp = nex

        try:
            res = round(eval(to_python(exp)))
        except Exception as error:
            rejects += 1
            errors.append(error)
            continue

        if res == num:
            break

        rejects += 1
        errors.append(Exception(f"Incorrect: requested {num}, got {res}"))

    exp = to_discord(exp)
    print(exp)
    p.copy(exp)
    print(f"Copied to clipboard...\n({len(exp)} chars, {rejects} " + ("reject" if rejects == 1 else "rejects") + (f": {errors})\n" if errors else "!)\n"))
