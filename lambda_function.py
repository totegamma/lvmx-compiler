import glob
import json
from compile import dumpbytecode
def lambda_handler(event, context):

    glob.init()

    try:
        code = dumpbytecode(event['body'])
    except Exception as e:
        code = str(e)
        statuscode = 400

    statuscode = 200
    if (glob.lexerrors != '' or glob.yaccerrors != '' or glob.compileerrors != ''):
        statuscode = 400

    return {
        'statusCode': statuscode,
        'body': code
    }
