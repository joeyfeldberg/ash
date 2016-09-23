import boto3


def create():
    return EC2Providor()


class EC2Providor():
    def __init__(self):
        pass

    def get_all(self):
        ec2 = boto3.resource('ec2')
        instances = ec2.instances.filter(Filters=self._filters())

        results = []
        for instance in instances:
            name = next(filter(self._find_name_tag, instance.tags), None)
            if not name:
                continue

            results.append((name["Value"], instance.private_ip_address))

        return results

    @staticmethod
    def _find_name_tag(tag): tag["Key"] == "Name"

    def _filters(self):
        return [{'Name': 'instance-state-name', 'Values': ['running']}]
