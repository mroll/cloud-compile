import boto3

from .util import tag, tagged_resource


class Subnet:
    def __init__(self, name, vpc_id):
        self.name = name
        self.vpc_id = vpc_id
        self.cidrblock = name
        self.resource = boto3.resource('ec2')
        self.subnet = None

        self._initialize()

    @property
    def resource_id(self):
        return self.subnet.id

    def _get_resource_reference(self):
        return tagged_resource(
            self.resource.subnets.all(),
            ('Name', self.name)
        )

    def _exists(self):
        return self._get_resource_reference() is not None

    def _initialize(self):
        if not self._exists():
            self.subnet = self.resource.create_subnet(
                CidrBlock=self.cidrblock,
                VpcId=self.vpc_id
            )
            tag(self.subnet, ('Name', self.name))
        else:
            self.subnet = self._get_resource_reference()
