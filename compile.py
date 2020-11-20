import sys
import time
from mnemonic import mnemonic
from yacc import makeAST


globalvars = {}
stringregion = {}
funcs = {}

arguments = {}
localvars = {}

labelitr = 0;

def preparecompile():
    globalvars.clear();
    stringregion.clear();
    funcs.clear();
    arguments.clear();
    localvars.clear();
    labelitr.clear();

def decideType(a, b):
    if ('void' in [a, b]):
        print('eval void error')
        return 'error'
    #elif (a == 'any' and b == 'any'):
    #    return 'any'
    #elif (a == 'any'):
    #    return b
    #elif (b == 'any'):
    #    return a
    elif (a == 'uint' and b == 'uint'):
        return 'uint'
    elif (a == 'int' and b == 'int'):
        return 'int'
    elif (a == 'float' and b == 'float'):
        return 'float'
    #elif ('uint' in [a, b] and 'float' in [a, b]):
    #    return 'float'
    #elif ('int' in [a, b] and 'float' in [a, b]):
    #    return 'float'

    print(f'eval type error! {a} and {b}')

    return 'error'


def compile(ast):
    global labelitr

    if (ast['op'] == 'program'):
        for elem in ast['body']:
            compile(elem)
        return
    elif (ast['op'] == 'globalvar'): # TODO 初期値の処理
        globalvars[ast['symbol']] = {
                'type': ast['type'],
                'id': len(globalvars)
                }
        return
    elif (ast['op'] == 'func'):
        frame = []
        arguments.clear()
        localvars.clear()
        for elem in ast['arg']:
            arguments[elem[1]] = {
                    'type': elem[0],
                    'id': len(arguments)
                    }
        code = compile(ast['body'])['code'] # ここでlocalvarsが変わる
        frame.append(['ENTRY', ast['symbol']])
        frame.append(['FRAME', len(localvars)]) # ここでlocalvasを使う
        frame.extend(code)
        frame.append(['RET', 0])
        funcs[ast['symbol']] = {
            'type': ast['type'],
            'code': frame
            }
        return

    elif (ast['op'] == 'block'):
        code = []
        for elem in ast['body']:
            code.extend(compile(elem)['code'])
        return {
            'type': 'void',
            'code': code
            }

    elif (ast['op'] == 'localvar'):
        localvars[ast['symbol']] = {
            'type': ast['type'],
            'id': len(localvars)
            }
        code = compile(ast['body'])['code'] #TODO 評価した型とのassert
        code.append(['STOREL', localvars[ast['symbol']]['id']])
        return {
            'type': ast['type'],
            'code': code
            }

    elif (ast['op'] == 'return'):
        if (ast['body'] != None):
            dump = compile(ast['body'])
            mype = dump['type']
            code = dump['code'] # TODO 自関数との型チェック
            code.append(['RET', 0])
            return {
                'type': mype,
                'code': code
                }
        else:
            return {
                'type': 'void',
                'code': [['RET', 0]]
                }

    elif (ast['op'] == 'funccall'):
        mype = funcs[ast['name']]['type']
        code = []
        for elem in reversed(ast['arg']):
            code.extend(compile(elem)['code'])
        code.append(['CALL', ast['name']])
        code.append(['POPR', len(ast['arg'])])
        return {
            'type': mype,
            'code': code
            }

    elif (ast['op'] == 'if'):
        cond = compile(ast['cond'])['code']
        mhen = compile(ast['then'])['code']

        l0 = labelitr
        labelitr += 1

        code = cond
        code.append(['JIF0', l0])
        code.extend(mhen)
        code.append(['LABEL', l0])
        return {
            'type': 'void',
            'code': code
            }


    elif (ast['op'] == 'ifelse'):
        cond = compile(ast['cond'])['code']
        mhen = compile(ast['then'])['code']
        mlse = compile(ast['else'])['code']

        l0 = labelitr
        labelitr += 1
        l1 = labelitr
        labelitr += 1

        code = cond
        code.append(['JIF0', l0])
        code.extend(mhen)
        code.append(['JUMP', l1])
        code.append(['LABEL', l0])
        code.extend(mlse)
        code.append(['LABEL', l1])
        return {
                'type': 'void',
                'code': code
                }

    elif (ast['op'] == 'while'):
        cond = compile(ast['cond'])['code']
        body = compile(ast['body'])['code']

        l0 = labelitr
        labelitr += 1
        l1 = labelitr
        labelitr += 1

        code = [['LABEL', l0]]
        code.extend(cond)
        code.append(['JIF0', l1])
        code.extend(body)
        code.append(['JUMP', l0])
        code.append(['LABEL', l1])
        return {
                'type': 'void',
                'code': code
                }

    elif (ast['op'] == 'for'):
        init = compile(ast['init'])['code']
        cond = compile(ast['cond'])['code']
        loop = compile(ast['loop'])['code']
        body = compile(ast['body'])['code']

        code = init
        l0 = labelitr
        labelitr += 1
        l1 = labelitr
        labelitr += 1
        code.append(['LABEL', l0])
        code.extend(cond)
        code.append(['JIF0', l1])
        code.extend(body)
        code.extend(loop)
        code.append(['JUMP', l0])
        code.append(['LABEL', l1])
        return {
                'type': 'void',
                'code': code
                }

    elif (ast['op'] == 'input'):
        stringslot = compile(ast['key'])['code'][0][1] # TODO error check
        return {
                'type': 'any',
                'code': [['INPUT', stringslot]]
                }

    elif (ast['op'] == 'output'):
        stringslot = compile(ast['key'])['code'][0][1] # TODO error check
        code = (compile(ast['value']))['code']
        code.append(['OUTPUT', stringslot])
        return {
                'type': 'void',
                'code': code
                }

    elif (ast['op'] == 'readreg'):
        addr = compile(ast['key'])['code'][0][1]
        return {
                'type': 'float',
                'code': [['LOADR', addr]]
                }

    elif (ast['op'] == 'writereg'):
        addr = compile(ast['key'])['code'][0][1]
        code = compile(ast['value'])['code']
        code.append(['STORER', addr])
        return {
                'type': 'void',
                'code': code
                }

    elif (ast['op'] == 'assign'): # TODO: 型チェック
        code = compile(ast['right'])['code']
        if (ast['left'] in localvars):
            code.append(['STOREL', localvars[ast['left']]['id']])
        elif (ast['left'] in arguments):
            code.append(['STOREA', arguments[ast['left']]['id']])
        elif (ast['left'] in globalvars):
            code.append(['STOREG', globalvars[ast['left']]['id']])
        else:
            print("variable not found")

        return {
                'type': 'void',
                'code': code
                }

    elif (ast['op'] == 'inc'):
        dump = compile(ast['right'])
        mype = dump['type']
        code = dump['code']
        if (mype == 'uint'):
            code.extend([['PUSH', 1], ['ADDU', 0]])
        elif (mype == 'int'):
            code.extend([['PUSH', 1], ['ADDI', 0]])
        else:
            print('ERROR: [compile] type error in inc')

        symbol = ast['right']['body']

        if (symbol in localvars):
            code.append(['STOREL', localvars[symbol]['id']])
        elif (symbol in arguments):
            code.append(['STOREA', localvars[symbol]['id']])
        elif (symbol in globalvars):
            code.append(['STOREG', globalvars[symbol]['id']])
        else:
            print("variable not found")
        return {
                'type': 'void',
                'code': code
                }


    elif (ast['op'] == 'dec'):
        dump = compile(ast['right'])
        mype = dump['type']
        code = dump['code']
        if (mype == 'uint'):
            code.extend([['PUSH', 1], ['SUBU', 0]])
        elif (mype == 'int'):
            code.extend([['PUSH', 1], ['SUBI', 0]])
        else:
            print('ERROR: [compile] type error in dec')

        symbol = ast['right']['body']

        if (symbol in localvars):
            code.append(['STOREL', localvars[symbol]['id']])
        elif (symbol in arguments):
            code.append(['STOREA', localvars[symbol]['id']])
        elif (symbol in globalvars):
            code.append(['STOREG', globalvars[symbol]['id']])
        else:
            print("variable not found")
        return {
                'type': 'void',
                'code': code
                }

    elif (ast['op'] == 'inv'): #TODO 違うよ
        code = compile(ast['right'])['code']
        code.extend([['PUSH', -1], ['MULU', 0]])
        return {
                'type': 'uint',
                'code': code
                }

    elif (ast['op'] == 'add'):
        left = compile(ast['left'])
        right = compile(ast['right'])
        mype = decideType(left['type'], right['type'])
        code = left['code']
        code.extend(right['code'])
        if (mype == 'uint'):
            code.append(['ADDU', 0])
        elif (mype == 'int'):
            code.append(['ADDI', 0])
        elif (mype == 'float'):
            code.append(['ADDF', 0])
        return {
                'type': mype,
                'code': code
                }

    elif (ast['op'] == 'sub'):
        left = compile(ast['left'])
        right = compile(ast['right'])
        mype = decideType(left['type'], right['type'])
        code = left['code']
        code.extend(right['code'])
        if (mype == 'uint'):
            code.append(['SUBU', 0])
        elif (mype == 'int'):
            code.append(['SUBI', 0])
        elif (mype == 'float'):
            code.append(['SUBF', 0])
        return {
                'type': mype,
                'code': code
                }


    elif (ast['op'] == 'mul'):
        left = compile(ast['left'])
        right = compile(ast['right'])
        mype = decideType(left['type'], right['type'])
        code = left['code']
        code.extend(right['code'])
        if (mype == 'uint'):
            code.append(['MULU', 0])
        elif (mype == 'int'):
            code.append(['MULI', 0])
        elif (mype == 'float'):
            code.append(['MULF', 0])
        return {
                'type': mype,
                'code': code
                }

    elif (ast['op'] == 'div'):
        left = compile(ast['left'])
        right = compile(ast['right'])
        mype = decideType(left['type'], right['type'])
        code = left['code']
        code.extend(right['code'])
        if (mype == 'uint'):
            code.append(['DIVU', 0])
        elif (mype == 'int'):
            code.append(['DIVI', 0])
        elif (mype == 'float'):
            code.append(['DIVF', 0])
        return {
                'type': mype,
                'code': code
                }


    elif (ast['op'] == 'lt'):
        left = compile(ast['left'])
        right = compile(ast['right'])
        mype = decideType(left['type'], right['type'])
        code = left['code']
        code.extend(right['code'])
        if (mype == 'uint'):
            code.append(['LTU', 0])
        elif (mype == 'int'):
            code.append(['LTI', 0])
        elif (mype == 'float'):
            code.append(['LTF', 0])
        return {
                'type': mype,
                'code': code
                }


    elif (ast['op'] == 'lte'):
        left = compile(ast['left'])
        right = compile(ast['right'])
        mype = decideType(left['type'], right['type'])
        code = left['code']
        code.extend(right['code'])
        if (mype == 'uint'):
            code.append(['LTEU', 0])
        elif (mype == 'int'):
            code.append(['LTEI', 0])
        elif (mype == 'float'):
            code.append(['LTEF', 0])
        return {
                'type': mype,
                'code': code
                }


    elif (ast['op'] == 'gt'):
        left = compile(ast['left'])
        right = compile(ast['right'])
        mype = decideType(left['type'], right['type'])
        code = left['code']
        code.extend(right['code'])
        if (mype == 'uint'):
            code.append(['GTU', 0])
        elif (mype == 'int'):
            code.append(['GTI', 0])
        elif (mype == 'float'):
            code.append(['GTF', 0])
        return {
                'type': mype,
                'code': code
                }


    elif (ast['op'] == 'gte'):
        left = compile(ast['left'])
        right = compile(ast['right'])
        mype = decideType(left['type'], right['type'])
        code = left['code']
        code.extend(right['code'])
        if (mype == 'uint'):
            code.append(['GTEU', 0])
        elif (mype == 'int'):
            code.append(['GTEI', 0])
        elif (mype == 'float'):
            code.append(['GTEF', 0])
        return {
                'type': mype,
                'code': code
                }


    elif (ast['op'] == 'eq'):
        left = compile(ast['left'])
        right = compile(ast['right'])
        mype = decideType(left['type'], right['type'])
        code = left['code']
        code.extend(right['code'])
        if (mype == 'uint'):
            code.append(['EQU', 0])
        elif (mype == 'int'):
            code.append(['EQI', 0])
        elif (mype == 'float'):
            code.append(['EQF', 0])
        return {
                'type': mype,
                'code': code
                }


    elif (ast['op'] == 'neq'):
        left = compile(ast['left'])
        right = compile(ast['right'])
        mype = decideType(left['type'], right['type'])
        code = left['code']
        code.extend(right['code'])
        if (mype == 'uint'):
            code.append(['NEQU', 0])
        elif (mype == 'int'):
            code.append(['NEQI', 0])
        elif (mype == 'float'):
            code.append(['NEQF', 0])
        return {
                'type': mype,
                'code': code
                }


    elif (ast['op'] == 'ternary'):
        pass

    elif (ast['op'] == 'symbol'):
        if (ast['body'] in localvars):
            var = localvars[ast['body']]
            return {
                    'type': var['type'],
                    'code': [['LOADL', var['id']]]
                    }
        elif (ast['body'] in arguments):
            var = arguments[ast['body']]
            return {
                    'type': var['type'],
                    'code': [['LOADA', var['id']]]
                    }
        elif (ast['body'] in globalvars):
            var = globalvars[ast['body']]
            return {
                    'type': var['type'],
                    'code': [['LOADG', var['id']]]
                    }
        else:
            print("variable not found")

    elif (ast['op'] == 'numberi'):
        return {
                'type': 'int',
                'code': [['PUSH', ast['body']]]
                }

    elif (ast['op'] == 'numberf'):
        return {
                'type': 'float',
                'code': [['PUSH', ast['body']]]
                }

    elif (ast['op'] == 'string'):
        if (ast['body'] not in stringregion):
            stringregion[ast['body']] = len(stringregion)
        return {
                'type': 'stringRef',
                'code': [['PUSH', stringregion[ast['body']]]]
                }

    print(f"no match... {ast['op']=}")
    return [['ERROR', ast['op']]]


def dumpbytecode(code):
    start = time.time()

    ast = makeAST(code)

    compile(ast)

    funcLocator = {}
    labelLocator = {}

    middlecode = []
    bytecode = []

    print(funcs)

# search for main
    for key, value in funcs.items():
        if (key == 'main'):
            for byte in value['code']:
                middlecode.append(byte)

# add others
    for key, value in funcs.items():
        if (key != 'main'):
            for byte in value['code']:
                middlecode.append(byte)

    return middlecode ## NOTE DEBUGCODE

# locate func & labels
    for elem in middlecode:
        if (elem[0] == 'ENTRY'):
            funcLocator[elem[1]] = len(bytecode)
        elif (elem[0] == 'LABEL'):
            labelLocator[elem[1]] = len(bytecode)
        else:
            bytecode.append(elem)

# update funcall & jump & JIF0
    for elem in bytecode:
        if (elem[0] == 'CALL'):
            elem[1] = funcLocator[elem[1]]
        elif (elem[0] == 'JUMP' or elem[0] == 'JIF0'):
            elem[1] = labelLocator[elem[1]]
        elif (elem[0] == 'LOADG' or elem[0] == 'STOREG'):
            elem[1] = len(bytecode) + elem[1];

    stream = ""

# append global variable space
    for i in globalvars:
        bytecode.append(['DUMMY', 0])

# writeout
    stream += f".string {len(stringregion)}" + '\n'
    for elem in stringregion:
        stream += elem
        stream += '\n'

    stream += f".bytecode {len(bytecode)}" + '\n'
    for elem in bytecode:
        stream += f"{mnemonic[elem[0]]:04x}{int(elem[1]):04x}" + '\n'

    return stream

    elapsed = time.time() - start
    print(f"done! ({elapsed*1000:.3f}ms)")


if __name__ == '__main__':
    filename = ""
    if (len(sys.argv) == 2):
        filename = sys.argv[1]
    else:
        filename = "test.c"

    data = ""
    with open(filename, mode="r") as f:
        data = f.read()

    bytecode = dumpbytecode(data)

    print(bytecode)

