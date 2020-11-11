from yacc import makeAST


globalvars = {}
stringregion = {}
funcs = []

arguments = {}
localvars = {}

labelitr = 0;

def compile(ast):
    global labelitr
    f = ast[0]

    if (f == 'program'):
        for elem in ast[1]:
            compile(elem)
    elif (f == 'globalvar'):
        globalvars[ast[1]] = len(globalvars)
    elif (f == 'func'):
        frame = []
        code = []
        arguments.clear()
        localvars.clear()
        for elem in ast[2]:
            arguments[elem] = len(arguments)
        for elem in ast[3]: # code
            code.extend(compile(elem))
        frame.append(['ENTRY', ast[1]])
        frame.append(['FRAME', len(localvars)])
        frame.extend(code)
        frame.append(['RET', 0])
        funcs.append([ast[1], frame])
    elif (f == 'localvar'):
        localvars[ast[1]] = len(localvars)
        code = compile(ast[2])
        code.append(['STOREL', localvars[ast[1]]])
        return code
    elif (f == 'return'):
        if (ast[1] != None):
            code = compile(ast[1])
            code.append(['RET', 0])
            return code
        else:
            return [['RET', 0]]
    elif (f == 'funccall'):
        code = []
        for elem in ast[2]:
            code.extend(compile(elem))
        code.append(['CALL', ast[1]])
        code.append(['POPR', len(ast[2])])
        return code

    elif (f == 'if'):
        pass
    elif (f == 'ifelse'):
        pass
    elif (f == 'while'):
        pass
    elif (f == 'for'):
        init = compile(ast[1])
        cond = compile(ast[2])
        cont = compile(ast[3])
        blck = []
        for elem in ast[4]:
            blck.extend(compile(elem))
        code = init
        l0 = labelitr
        labelitr += 1
        l1 = labelitr
        labelitr += 1
        code.append(['LABEL', l0])
        code.extend(cond)
        code.append(['BEQ0', l1])
        code.extend(blck)
        code.extend(cont)
        code.append(['JUMP', l0])
        code.append(['LABEL', l1])
        return code
    elif (f == 'input'):
        code = compile(ast[1])
        code.append(['INPUT', 0])
        return code
    elif (f == 'output'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['OUTPUT', 0])
        return code
    elif (f == 'assign'):
        code = compile(ast[2])
        if (ast[1] in localvars):
            code.append(['STOREL', localvars[ast[1]]])
            return code
        elif (ast[1] in arguments):
            code.append(['STOREA', arguments[ast[1]]])
            return code
        elif (ast[1] in globalvars):
            code.append(['STOREG', globalvars[ast[1]]])
            return code
        else:
            print("variable not found")
    elif (f == 'inc'):
        code = compile(ast[1])
        code.extend([['PUSH', 1], ['ADD', 0]])
        return code

    elif (f == 'dec'):
        code = compile(ast[1])
        code.extend([['PUSH', 1], ['SUB', 0]])
        return code

    elif (f == 'inv'):
        code = compile(ast[1])
        code.extend([['PUSH', -1], ['MUL', 0]])
        return code

    elif (f == 'add'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['ADD', 0])
        return code

    elif (f == 'sub'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['SUB', 0])
        return code

    elif (f == 'mul'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['MUL', 0])
        return code

    elif (f == 'div'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['DIV', 0])
        return code

    elif (f == 'lt'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['LT', 0])
        return code

    elif (f == 'lte'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['LTE', 0])
        return code

    elif (f == 'gt'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['GT', 0])
        return code

    elif (f == 'gte'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['GTE', 0])
        return code

    elif (f == 'eq'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['EQ', 0])
        return code

    elif (f == 'neq'):
        code = compile(ast[1])
        code.extend(compile(ast[2]))
        code.append(['NEQ', 0])
        return code

    elif (f == 'ternary'):
        pass

    elif (f == 'symbol'):
        if (ast[1] in localvars):
            return [['LOADL', localvars[ast[1]]]]
        elif (ast[1] in arguments):
            return [['LOADA', arguments[ast[1]]]]
        elif (ast[1] in globalvars):
            return [['LOADG', globalvars[ast[1]]]]
        else:
            print("variable not found")
    elif (f == 'number'):
        return [['PUSH', ast[1]]]

    elif (f == 'string'):
        if (ast[1] not in stringregion):
            stringregion[ast[1]] = len(stringregion)
        return [['PUSH', stringregion[ast[1]]]]


    return [['ERROR', f]]


ast = makeAST('main.c')
print(ast)

compile(ast)

print(f'{globalvars=}')
print(f'{stringregion=}')
print(f'{funcs=}')

for elem in funcs:
    print(elem[0])
    for byte in elem[1]:
        print(byte)


