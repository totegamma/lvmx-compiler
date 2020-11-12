

def lvm(stringregion, bytecode, codesize, env):
    pc = 0 # program counter
    sp = codesize # stack pointer
    fp = 0 # function pointer

    stack = []

    # init
    for elem in bytecode:
        stack.append(elem)
        codesize -= 1

    for i in range(codesize):
        stack.append(['DUMMY', 0])


    while true:
        opc = stack[sp][0]
        arg = stack[sp][1]

        if opc == 'POP':
            pass
        elif opc == 'PUSH':
            pass
        elif opc == 'ADD':
            pass
        elif opc == 'SUB':
            pass
        elif opc == 'MUL':
            pass
        elif opc == 'GT':
            pass
        elif opc == 'GTE':
            pass
        elif opc == 'LT':
            pass
        elif opc == 'LTE':
            pass
        elif opc == 'EQ':
            pass
        elif opc == 'BEQ0':
            pass
        elif opc == 'LOADA':
            pass
        elif opc == 'LOADL':
            pass
        elif opc == 'LOADG':
            pass
        elif opc == 'STOREA':
            pass
        elif opc == 'STOREL':
            pass
        elif opc == 'STOREG':
            pass
        elif opc == 'JUMP':
            pass
        elif opc == 'CALL':
            pass
        elif opc == 'RET':
            pass
        elif opc == 'POPR':
            pass
        elif opc == 'FRAME':
            pass
        elif opc == 'INPUT':
            pass
        elif opc == 'OUTPUT':
            pass


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
            bytecode.append(elem.split('.'))

    env = lvm(stringregion, bytecode, codesize, {'input': 10, 'output': 0})

    print(env)


