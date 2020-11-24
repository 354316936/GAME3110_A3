import json
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserProfiles')

def lambda_handler(event, context):
    
    if event['httpMethod'] == 'GET':
        response=table.scan()
        return {
        'statusCode': 200,
        'body': json.dumps(response['Items'])
        }
    
    elif event['httpMethod'] == 'POST':
        if 'body' in event:
            body=json.loads(event['body'])
            if 'UserName' in body and 'Win' in body and 'Lose' in body and 'MMR' in body and 'Kill' in body and 'Death' in body and 'Level' in body:
                UserName=body['UserName']
                Win=body['Win']
                Lose=body['Lose']
                MMR=body['MMR']
                Kill=body['Kill']
                Death=body['Death']
                Level=body['Level']
                table.put_item(
                    Item = {
                        'UserName':UserName,
                        'Win':Win,
                        'Lose':Lose,
                        'MMR':MMR,
                        'Kill':Kill,
                        'Death':Death,
                        'Level':Level
                    }
                )
                response=table.get_item(
                    Key={
                        'UserName':UserName
                    }
                )
                return {
                'statusCode': 200,
                'body': "Player Updated!\n"+json.dumps(response['Item'])
                }
            else:
                return {
                'statusCode': 200,
                'body': json.dumps("Missing UserData!")
                }
        else:
            return {
            'statusCode': 200,
            'body': json.dumps("Need body!")
            }
    else:
        return {
        'statusCode': 200,
        'body': json.dumps("Not Supported Type")
        }
