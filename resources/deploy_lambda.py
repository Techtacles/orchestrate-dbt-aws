import yaml
from datetime import datetime
import time
import logging
import boto3
import os
logger = logging.getLogger()
logger.setLevel(logging.INFO)
project_name=os.environ["PROJECT_NAME"]
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


def lambda_handler(event,context):
    codebuild=boto3.client("codebuild")
    for schedule_payload in parse_schedule_yml():
        for payload_cron,payload_model in schedule_payload.items():
            event_resource=event["resources"][0]
            if payload_model == event_resource.split("/")[-1].split("-")[0]:
                build_project=codebuild.start_build(
                        projectName=project_name,
                        environmentVariablesOverride=[
                            {
                                'name': 'DBT_RUN_MODELS',
                                'value': payload_model  
                            }
                        ]
            )
                print(f"Building {payload_model} on {str(datetime.now())}")
    return f"Successful end to end deployment of {payload_model}"
    