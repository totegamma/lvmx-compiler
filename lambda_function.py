import glob as g
from compile import value2hex, compile 


def lambda_handler(event, context):


    cpp = Preprocessor()
    cpp.add_path(os.getcwd() + "/lvmxlib")
    tmpf = io.StringIO("")

    with open("/tmp/main.c", mode='w') as f:
        f.write(event['body'])

    with open("/tmp/main.c", mode="r") as f:
        cpp.parse(f)

    cpp.write(tmpf)

    g.init("/tmp/main.c", tmpf.getvalue())

    try:
        dumps = compile(g.source)
    except Exception as e:
        return {
            'statusCode': 400,
            'body': g.r.report()
        }

    if dumps is None:
        return {
            'statusCode': 400,
            'body': g.r.report()
        }

    bytecode = f".data {len(dumps['data'])}" + '\n'
    for elem in dumps['data']:
        bytecode += value2hex(elem) + '\n'
    bytecode += f".code {len(dumps['code'])}" + '\n'
    for elem in dumps['code']:
        bytecode += elem.serialize() + '\n'

    if g.r.hasError():
        return {
            'statusCode': 400,
            'body': g.r.report()
        }
    else:
        return {
            'statusCode': 200,
            'body': bytecode
        }
