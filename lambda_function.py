from compile import dumpbytecode
import json
def lambda_handler(event, context):

    code = dumpbytecode(event['body'])

    return {
        'statusCode': 200,
        'body': code
    }
