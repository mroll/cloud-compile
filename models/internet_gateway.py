import boto3

from .util import tag, tagged_resource


class InternetGateway:
    def __init__(self, name):
        self.name = name
        self.resource = boto3.resource('ec2')
        self.ig = None

        self._initialize()

    @property
    def resource_id(self):
        return self.ig.id

    def _exists(self):
        return tagged_resource(
            self.resource.internet_gateways.all(),
            ('Name', self.name)
        ) is not None

    def _get_resource_reference(self):
        return tagged_resource(
            self.resource.internet_gateways.all(),
            ('Name', self.name)
        )

    def _initialize(self):
        if not self._exists():
            self.ig = self.resource.create_internet_gateway()
            tag(self.ig, ('Name', self.name))
        else:
            self.ig = self._get_resource_reference()

    def is_attached_to_vpc(self, vpc_id):
        return vpc_id in [a['VpcId'] for a in self.ig.attachments]

    def attach_to_vpc(self, vpc_id):
        self.ig.attach_to_vpc(VpcId=vpc_id)
