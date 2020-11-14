from mnemonic import mnemonic

def lvm(stringregion, bytecode, codesize, env):
    pc = 0 # program counter
    fp = 0 # function pointer

    stack = []

    # init
    for elem in bytecode:
        stack.append(elem)
        codesize -= 1


    clock = 0;
    while True:
        opc = stack[pc][0]
        arg = stack[pc][1]

        clock += 1
        print(f"#{clock=}: {opc=}, {arg=}")

        if opc == 'POP':
            stack.pop()
            pc += 1

        elif opc == 'PUSH':
            stack.append(['push', arg])
            pc += 1

        elif opc == 'ADD':
            a = stack.pop()[1]
            b = stack.pop()[1]
            stack.append(['add', a + b])
            pc += 1

        elif opc == 'SUB':
            a = stack.pop()[1]
            b = stack.pop()[1]
            stack.append(['sub', a - b])
            pc += 1

        elif opc == 'MUL':
            a = stack.pop()[1]
            b = stack.pop()[1]
            stack.append(['mul', a * b])
            pc += 1

        elif opc == 'GT':
            a = stack.pop()[1]
            b = stack.pop()[1]
            stack.append(['gt', a > b])
            pc += 1

        elif opc == 'GTE':
            a = stack.pop()[1]
            b = stack.pop()[1]
            stack.append(['gte', a >= b])
            pc += 1

        elif opc == 'LT':
            a = stack.pop()[1]
            b = stack.pop()[1]
            stack.append(['lt', a < b])
            pc += 1

        elif opc == 'LTE':
            a = stack.pop()[1]
            b = stack.pop()[1]
            stack.append(['lte', a <= b])
            pc += 1

        elif opc == 'EQ':
            a = stack.pop()[1]
            b = stack.pop()[1]
            stack.append(['eq', a == b])
            pc += 1

        elif opc == 'JIF0':
            a = stack.pop()[1]
            if (a == 0):
                pc = arg
            else:
                pc += 1

        elif opc == 'LOADA':
            a = stack[fp - arg - 2]
            stack.append(['loada', a[1]])
            pc += 1

        elif opc == 'LOADL':
            a = stack[fp + arg + 1]
            stack.append(['loadl', a[1]])
            pc += 1

        elif opc == 'LOADG':
            a = stack[arg]
            stack.append(['loadg', a[1]])
            pc += 1

        elif opc == 'STOREA':
            a = stack.pop()
            stack[fp - arg - 2][1] = a[1]
            pc += 1

        elif opc == 'STOREL':
            a = stack.pop()
            stack[fp + arg + 1][1] = a[1]
            pc += 1

        elif opc == 'STOREG':
            a = stack.pop()
            stack[arg][1] = a[1]
            pc += 1

        elif opc == 'JUMP':
            pc = arg

        elif opc == 'CALL':
            stack.append(['call', pc+1])
            pc = arg

        elif opc == 'RET':
            a = stack.pop()
            rewind = len(stack) - fp -1
            for i in range(rewind):
                stack.pop()
            fp = stack.pop()[1]
            pc = stack.pop()[1]
            stack.append(['ret', a[1]])

            if (fp == 0):
                break

        elif opc == 'POPR':
            a = stack.pop()
            for i in range(arg):
                stack.pop()
            stack.append(['popr', a[1]])
            pc += 1

        elif opc == 'FRAME':
            stack.append(['frame', fp])
            fp = len(stack) -1
            for i in range(arg):
                stack.append(['frame', 0])
            pc += 1

        elif opc == 'INPUT':
            key = stringregion[arg]
            stack.append(['input', env[key]])
            pc += 1

        elif opc == 'OUTPUT':
            a = stack.pop()
            key = stringregion[arg]
            env[key] = a[1]
            pc += 1

        else:
            print("unknown opc!!!!!")
            print(f"{opc=}")
            break

        print(f"{pc=}")
        print(f"sp={len(stack)-1}")
        print(f"{fp=}")
        print("-----")
        print(f"{stack=}")
        print("-----")
        #input("Press Enter to continue...")


    return env



if __name__ == '__main__':

    lve = ""
    with open('bytecode.lve', mode='r') as f:
        lve = f.read()

    lvearr = lve.split('\n')

    readmode = "undefined"

    codesize = 0
    stringregion = []
    bytecode = []

    revmnemonic = {v: k for k, v in mnemonic.items()}

    for elem in lvearr:
        if elem == '':
            continue
        if readmode == 'undefined':
            if elem.startswith('.string'):
                readmode = 'string'
        elif readmode == 'string':
            if elem.startswith('.bytecode'):
                readmode = 'bytecode'
                tmp = elem.split(' ')
                codesize = int(tmp[1])
            else:
                stringregion.append(elem)
        elif readmode == 'bytecode':
            opc = revmnemonic[int(elem[0:4], 16)]
            arg = int(elem[4:8], 16)
            bytecode.append([opc, arg])

    env = lvm(stringregion, bytecode, codesize, {'input': 10, 'output': 0})

    print(env)


