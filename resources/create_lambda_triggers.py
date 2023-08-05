import yaml
from datetime import datetime
import time
import logging
import json
import boto3
import random
import secrets
logger = logging.getLogger()
logger.setLevel(logging.INFO)
lambda_function_name="aws-dbt-poc-lambda"
def parse_schedule_yml():
    all_payloads=[]
    with open("scheduler.yml") as file:
        scheduler_yml_file=yaml.safe_load(file)
        scheduler=scheduler_yml_file["schedules"]
        for schedule  in scheduler:
            payload={schedule["cron_schedule"]:schedule["name"]}
            logger.info(f"Successfully parsed the yaml file and extracted {payload}")
            all_payloads.append(payload)
    return all_payloads

def get_names():
    names=[]
    for schedule_payload in parse_schedule_yml():
        for payload_cron,payload_model in schedule_payload.items():
            names.append(payload_model)
    return names

def get_current_triggers():
    arn_list = ["_"]
    try:
        client=boto3.client("lambda")
        response = json.loads(client.get_policy(
            FunctionName='aws-dbt-poc-lambda'
        )["Policy"])
        triggers=response["Statement"]
        for trigger in triggers:
            sid=trigger.get("Sid", {})
            condition = trigger.get("Condition", {})
            source_arn_values = condition.get("ArnLike", {}).get("AWS:SourceArn", None)
            if source_arn_values:
                arn = source_arn_values.split("/")[-1]
                arn_list.append((sid,arn))
    except Exception:
        pass
    #print(arn_list)
    return arn_list

def remove_triggers(event_sid):
    client=boto3.client("lambda")
    get_targets=get_current_triggers()
    get_targets.pop(0)
    response = client.remove_permission(
        FunctionName=lambda_function_name,
        StatementId=event_sid
        )
    return 200
def create_all_triggers():
    lambda_client=boto3.client("lambda")
    events=boto3.client("events")
    for schedule_payload in parse_schedule_yml():
        for payload_cron,payload_model in schedule_payload.items():
            put_rule=events.put_rule(
                Name=f"{payload_model}-event",
                ScheduleExpression=f"cron({payload_cron})",
                Description=f"Payload for the model {payload_model} with cron job {payload_cron} ",
                State='ENABLED'
            )

            put_targets=events.put_targets(
                Rule=f"{payload_model}-event",
                Targets=[
                    {
                        'Id': 'StartFunction',
                        'Arn': 'arn:aws:lambda:us-east-1:698677652952:function:aws-dbt-poc-lambda'
                    }
                ]
            )
            create_triggers = lambda_client.add_permission(
                        FunctionName=lambda_function_name,
                        StatementId=hex(random.getrandbits(16))    + "aws_lambda",
                        Action='lambda:InvokeFunction',
                        Principal='events.amazonaws.com',
                        SourceArn=put_rule['RuleArn']
                    )
    print("DONE")
    return "DONE"

def create_eventbridge_rules():
    events=boto3.client("events")
    rules=[]
    
    for schedule_payload in parse_schedule_yml():
        for payload_cron,payload_model in schedule_payload.items():
            put_rule=events.put_rule(
                Name=f"{payload_model}-event",
                ScheduleExpression=f"cron({payload_cron})",
                Description=f"Payload for the model {payload_model} with cron job {payload_cron} ",
                State='ENABLED'
            )

            put_targets=events.put_targets(
                Rule=f"{payload_model}-event",
                Targets=[
                    {
                        'Id': 'StartFunction',
                        'Arn': 'arn:aws:lambda:us-east-1:698677652952:function:aws-dbt-poc-lambda'
                    }
                ]
            )
            rules.append(put_rule)
    return rules
 #Fixing the permission issue when policy size reaches a certain number by cleaning up sids   
def filter_policies(fn_name):
  client = boto3.client('lambda') 
  policy = client.get_policy(FunctionName=fn_name)['Policy']
  statements = json.loads(policy)['Statement'] 
  unique_policies = []
  duplicate_sids = []
  for item in statements:
    arn = item['Condition']['ArnLike']['AWS:SourceArn']
    if (arn not in unique_policies):
      unique_policies.append(arn)
    else:
      duplicate_sids.append(item['Sid'])
  
  return unique_policies, duplicate_sids

def clean_up_policies(sids, fn_name):
  client = boto3.client('lambda')

  for sid in sids:       
    # print('remove SID {}'.format(sid))
    client.remove_permission(
      FunctionName=fn_name, 
      StatementId=sid
    )

def clean_up():
    fn_names = ['aws-dbt-poc-lambda']
    for fn_name in fn_names:
        uniq_policies, sids = filter_policies(fn_name)
        clean_up_policies(sids, fn_name)
        print("Successfully cleaned up")


def main():
    lambda_client=boto3.client("lambda")
    get_targets = get_current_triggers()
    cleaned_target=get_targets[1:]
    put_rule=create_eventbridge_rules()
    if len(get_targets)==1:
        print("No triggers found... creating all")
        create_all_triggers()
        print("Finished creating all triggers")
    else:
        for sid,arn in cleaned_target:
            arn=arn.split("/")[-1].split("-")[0]   
            if arn not in get_names():
                print(f"Removing {arn} from upstream")
                remove_triggers(sid)         
                print("Finished removing")
            
            for rule in put_rule:
                for model in get_names():
                    if model not in arn:
                        create_triggers = lambda_client.add_permission(
                                FunctionName=lambda_function_name,
                                StatementId=str(random.randint(0,100000))+ "lambda" + str(random.randint(0,100000)),
                                Action='lambda:InvokeFunction',
                                Principal='events.amazonaws.com',
                                SourceArn=rule['RuleArn']
                            )
main()
clean_up()    

