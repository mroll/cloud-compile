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

    def _is_running(self):
        """
        """
        # 16 is the code that signals a running instance;
        #     http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.Instance.state
        if self.instance is None:
            self.instance = self._get_resource_reference()

        return self.instance.state['Code'] == 16

    def _initialize(self):
        """
        """
        if self._exists() and self._is_running():
            self.instance = self._get_resource_reference()
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
        self.instance = instances[0]

        self.instance.wait_until_running()
        tag(self.instance, ('Name', self._name))

    @property
    def resource_id(self):
        return self.instance.id

    @property
    def public_ip_address(self):
        return self.instance.public_ip_address
