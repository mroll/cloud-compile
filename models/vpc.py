import boto3
from botocore.exceptions import ClientError

from .elastic_ip import ElasticIP
from .instance import Instance
from .internet_gateway import InternetGateway
from .key_pair import KeyPair
from .security_group import SecurityGroup
from .subnet import Subnet
from .util import first, resource_name, tag, tagged_resource


class Vpc:
    def __init__(self, name, public=True):
        self.name = name
        self.public = public
        self.client = boto3.client('ec2')
        self.resource = boto3.resource('ec2')
        self.vpc = None

        self._internet_gateway = None
        self._elastic_ips = {}
        self._subnets = {}
        self._security_groups = {}
        self._key_pairs = {}
        self._instances = {}

        self._create_vpc(name)

        if public:
            self._attach_internet_gateway('internet-gateway')
            self.route_table.create_route(
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=self._internet_gateway.resource_id,
            )

    def _attach_internet_gateway(self, ig_name):
        self._internet_gateway = InternetGateway(ig_name)
        if not self._internet_gateway.is_attached_to_vpc(self.vpc.id):
            self._internet_gateway.attach_to_vpc(self.vpc.id)

    def _vpc_exists(self, name):
        vpc_response = self.client.describe_vpcs()
        return name in [resource_name(vpcd) for vpcd in vpc_response['Vpcs']]

    def _get_vpc(self, vpc_name):
        def vpc_matches_name(vpc_dict):
            return resource_name(vpc_dict) == vpc_name

        response = self.client.describe_vpcs(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [vpc_name]
                }
            ]
        )
        vpc_id = first(vpc_matches_name, response['Vpcs'])['VpcId']

        return self.resource.Vpc(vpc_id)

    def _create_vpc(self, vpc_name, cidr_block='10.0.0.0/16'):
        if self._vpc_exists(vpc_name):
            self.vpc = self._get_vpc(vpc_name)
            return

        self.vpc = self.resource.create_vpc(CidrBlock=cidr_block)
        self.vpc.wait_until_available()
        tag(self.vpc, ('Name', vpc_name))

    @property
    def route_table(self):
        return list(self.vpc.route_tables.all())[0]

    def _get_instance(self, instance_name):
        return tagged_resource(self.vpc.instances.all(), ('Name', instance_name))

    def subnets(self, proposed_subnet_specs):
        """Establish subnets in the vpc according to the given specs.

        - Create subnets if they do not exist
        - Change the privacy of existing subnets if they differ from the spec
        - Delete subnets if they exist but are not given in the spec

        """
        for spec in proposed_subnet_specs:
            subnet_name = spec['CidrBlock']
            self._subnets[subnet_name] = Subnet(subnet_name, self.vpc.id)
            subnet = self._subnets[subnet_name]

            if self.public and spec['Public']:
                self.route_table.associate_with_subnet(SubnetId=subnet.resource_id)

        for subnet in self.vpc.subnets.all():
            if subnet.cidr_block not in self._subnets:
                subnet.delete()

    def security_group(
            self,
            GroupName,
            IngressRules=[],
            EgressRules=[],
            Description='default description'
    ):
        self._security_groups[GroupName] = SecurityGroup(
            GroupName,
            self.vpc.id,
            IngressRules,
            EgressRules,
            Description
        )

    def instance(
            self,
            InstanceName,
            Ami,
            KeyName,
            SubnetName,
            SecurityGroupName,
            InstanceType='t2.micro',
            MinCount=1,
            MaxCount=1
    ):
        subnet = self._subnets[SubnetName]
        security_group = self._security_groups[SecurityGroupName]
        self._instances[InstanceName] = Instance(
            InstanceName,
            Ami,
            KeyName,
            subnet,
            security_group,
            instance_type=InstanceType,
            min_count=MinCount,
            max_count=MaxCount
        )

    def key_pair(self, KeyName, outfile=None):
        self._key_pairs[KeyName] = KeyPair(KeyName, outfile)

    def elastic_ip(self, eip_name, InstanceName=None):
        self._elastic_ips[eip_name] = ElasticIP(eip_name)
        eip = self._elastic_ips[eip_name]

        if InstanceName:
            instance = self._get_instance(InstanceName)
            if not eip.is_pointing_to(instance):
                eip.point_to(instance.id)

        return eip.public_ip
