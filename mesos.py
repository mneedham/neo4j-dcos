import boto3
import time

# create cloud formation client
client = boto3.client('cloudformation')

response = client.create_stack(
    TemplateURL = "https://s3-us-west-2.amazonaws.com/downloads.dcos.io/dcos/stable/commit/602edc1b4da9364297d166d4857fc8ed7b0b65ca/cloudformation/single-master.cloudformation.json",
    StackName = "mark-mesos-again-again4",
    Parameters = [
        {
            'ParameterKey': 'KeyName',
            'ParameterValue': 'mark-mesos',
            'UsePreviousValue': False
        },
        {
            'ParameterKey': 'OAuthEnabled',
            'ParameterValue': 'false',
            'UsePreviousValue': False
        }
    ],
    Capabilities=[ 'CAPABILITY_IAM'])

stack_id = response["StackId"]
print("Stack id: {0}".format(stack_id))
print("Waiting for stack to come up...")

while True:
    status = client.describe_stacks(StackName=stack_id)["Stacks"][0]["StackStatus"]

    if status == "CREATE_COMPLETE":
        break
    else:
        print("Status: {0}".format(status))
        time.sleep(30)

mesos_master = [key for key in client.describe_stacks(StackName=stack_id)["Stacks"][0]["Outputs"] if key["Description"] == 'Mesos Master'][0]["OutputValue"]

print("Mesos Master: {0}".format(mesos_master))

# all the failure states
# 'StackStatus': 'CREATE_IN_PROGRESS'|'CREATE_FAILED'|'CREATE_COMPLETE'|'ROLLBACK_IN_PROGRESS'|'ROLLBACK_FAILED'|'ROLLBACK_COMPLETE'|'DELETE_IN_PROGRESS'|'DELETE_FAILED'|'DELETE_COMPLETE'|'UPDATE_IN_PROGRESS'|'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS'|'UPDATE_COMPLETE'|'UPDATE_ROLLBACK_IN_PROGRESS'|'UPDATE_ROLLBACK_FAILED'|'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS'|'UPDATE_ROLLBACK_COMPLETE'|'REVIEW_IN_PROGRESS',
