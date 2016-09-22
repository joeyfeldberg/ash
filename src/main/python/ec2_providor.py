import boto3

class EC2Providor():
    def __init__(self):
        pass

    def get_all(self):
        ec2 = boto3.resource('ec2')
        instances = ec2.instances.filter(Filters=self._filters())

        results = []
        find_name_tag = lambda tag: tag["Key"] == "Name"
        for instance in instances:
            name = next(filter(find_name_tag, instance.tags), None)
            if not name: continue
            results.append((name["Value"], instance.private_ip_address))

        return results

    def _filters(self):
        return [{'Name': 'instance-state-name', 'Values': ['running']}]
