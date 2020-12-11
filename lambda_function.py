import glob
import json
from compile import dumpbytecode
def lambda_handler(event, context):

    glob.init()
    code = dumpbytecode(event['body'])

    statuscode = 200
    if (glob.lexerrors != '' or glob.yaccerrors != ''):
        statuscode = 400

    return {
        'statusCode': statuscode,
        'body': code
    }
