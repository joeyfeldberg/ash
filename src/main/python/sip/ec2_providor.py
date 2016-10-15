import boto3


class Instance():
    def __init__(self, ec2_instance):
        tags = {tag['Key']: tag['Value'] for tag in ec2_instance.tags}
        self.private_ip_address = ec2_instance.private_ip_address
        self.instance_id = ec2_instance.instance_id
        self.name = tags.get('Name') or ec2_instance.private_ip_address
        self.instance_type = ec2_instance.instance_type
        self.state = ec2_instance.state
        self.tags = tags

class EC2Providor():
    def __init__(self):
        self.ec2 = boto3.resource('ec2')

    def get_all(self):
        filters = [{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}]
        return [Instance(i) for i in self.ec2.instances.filter(Filters=filters)]
