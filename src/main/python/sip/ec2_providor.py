import boto3


HORIZONTAL_LINE = '\u2503'

class Instance():
    def __init__(self, ec2_instance):
        tags = {tag['Key']: tag['Value'] for tag in ec2_instance.tags}
        self.private_ip_address = ec2_instance.private_ip_address
        self.instance_id = ec2_instance.instance_id
        self.name = tags.get('Name') or ec2_instance.private_ip_address
        self.instance_type = ec2_instance.instance_type
        self.state = ec2_instance.state
        self.tags = tags

    def __repr__(self):
        return "{5} {0:<25} {5} {1:<50} {5} {2:<15} {5} {3:<15} {5} {4:<15}".format(
            self.instance_id,
            self.name,
            self.instance_type,
            self.private_ip_address,
            self.state['Name'],
            HORIZONTAL_LINE
        )


class EC2Providor():
    def __init__(self):
        self.ec2 = boto3.resource('ec2')

    def get_all(self):
        return [Instance(i) for i in self.ec2.instances.all()]
