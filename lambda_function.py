from compile import preparecompile, dumpbytecode
import json
def lambda_handler(event, context):

    preparecompile()

    code = dumpbytecode(event['body'])

    return {
        'statusCode': 200,
        'body': code
    }
