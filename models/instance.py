import boto3

from .util import tag, tagged_resource


class Instance(object):
    """
    """

    def __init__(
            self,
            name,
            ami,
            keyname,
            subnet,
            security_group,
            instance_type='t2.micro',
            min_count=1,
            max_count=1
    ):
        """

        Arguments:
        - `name`:
        - `ami`:
        - `keyname`:
        - `subnet_name`:
        - `security_group instance_type`:
        - `min_count`:
        - `max_count`:
        """
        self._name = name
        self._ami = ami
        self._keyname = keyname
        self._subnet = subnet
        self._security_group = security_group
        self._instance_type = instance_type
        self._min_count = min_count
        self._max_count = max_count
        self.resource = boto3.resource('ec2')
        self.instance = None

        self._initialize()

    def _get_resource_reference(self):
        return tagged_resource(self.resource.instances.all(), ('Name', self._name))

    def _exists(self):
        """
        """
        return self._get_resource_reference() is not None

    def _initialize(self):
        """
        """
        if self._exists():
            return

        instances = self.resource.create_instances(
            ImageId=self._ami,
            MinCount=self._min_count,
            MaxCount=self._max_count,
            KeyName=self._keyname,
            InstanceType=self._instance_type,
            NetworkInterfaces=[{
                'SubnetId': self._subnet.resource_id,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': True,
                'Groups': [self._security_group.resource_id]}
            ],
        )
        self._instance = instances[0]

        self._instance.wait_until_running()
        tag(self._instance, ('Name', self._name))
