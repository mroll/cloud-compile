import boto3
from botocore.exceptions import ClientError

from .util import tag, tagged_resource


class ElasticIP:
    def __init__(self, name):
        self.name = name
        self.resource = boto3.resource('ec2')
        self.client = boto3.client('ec2')
        self.eip = None

        self._initialize()

    def _exists(self):
        return tagged_resource(
            self.resource.vpc_addresses.all(),
            ('Name', self.name)
        ) is not None

    def _create(self):
        allocation_response = self.client.allocate_address(Domain='vpc')

        self.allocation_id = allocation_response['AllocationId']
        self.public_ip = allocation_response['PublicIp']

        self.client.create_tags(
            Resources=[self.allocation_id],
            Tags=[
                {
                    'Key': 'Name',
                    'Value': self.name
                }
            ]
        )

    def _get_resource_reference(self):
        eip = tagged_resource(
            self.resource.vpc_addresses.all(),
            ('Name', self.name)
        )
        self.allocation_id = eip.allocation_id
        self.public_ip = eip.public_ip

    def _initialize(self):
        if not self._exists():
            self._create()
        else:
            self._get_resource_reference()

    def is_pointing_to(self, instance):
        return self.public_ip == instance.public_ip_address

    def point_to(self, instance_id):
        try:
            self.client.associate_address(
                AllocationId=self.allocation_id,
                InstanceId=instance_id,
            )
        except ClientError as e:
            print(e)
