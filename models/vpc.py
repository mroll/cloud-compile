import boto3
from botocore.exceptions import ClientError

from .elastic_ip import ElasticIP
from .internet_gateway import InternetGateway
from .subnet import Subnet
from .util import resource_name, tag, tagged_resource


def first(f, l):
    for el in l:
        if f(el):
            return el


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

    def _get_security_group(self, security_group_name):
        return tagged_resource(self.vpc.security_groups.all(),
                               ('Name', security_group_name))

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

    def _security_group_exists(self, GroupName):
        return GroupName in [sg.group_name for sg in self.vpc.security_groups.all()]

    def security_group(self, GroupName, IngressRules=[], EgressRules=[],
                       Description='default description'):
        if self._security_group_exists(GroupName):
            return

        security_group = self.vpc.create_security_group(
            Description=Description,
            GroupName=GroupName
        )
        tag(security_group, ('Name', GroupName))

        for ingress_rule in IngressRules:
            security_group.authorize_ingress(**ingress_rule)

        for egress_rule in EgressRules:
            security_group.authorize_egress(**ingress_rule)

        return security_group

    def _instance_exists(self, instance_name):
        return self._get_instance(instance_name) is not None

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
        if self._instance_exists(InstanceName):
            return

        SubnetId = self._subnets[SubnetName].resource_id
        SecurityGroupId = self._get_security_group(SecurityGroupName).id
        instances = self.resource.create_instances(
            ImageId=Ami,
            MinCount=MinCount,
            MaxCount=MaxCount,
            KeyName=KeyName,
            InstanceType=InstanceType,
            NetworkInterfaces=[{
                'SubnetId': SubnetId,
                'DeviceIndex': 0,
                'AssociatePublicIpAddress': True,
                'Groups': [SecurityGroupId]}
            ],
        )
        instance = instances[0]

        instance.wait_until_running()
        tag(instance, ('Name', InstanceName))

        return instance

    def _key_pair_exists(self, KeyName):
        return KeyName in [kp.name for kp in self.resource.key_pairs.all()]

    def key_pair(self, KeyName, outfile=None):
        if self._key_pair_exists(KeyName):
            return

        key_pair = self.client.create_key_pair(KeyName=KeyName)
        if outfile:
            with open(outfile, 'w') as fp:
                fp.write(key_pair['KeyMaterial'])
        else:
            print(key_pair['KeyMaterial'])

    def elastic_ip(self, eip_name, InstanceName=None):
        self._elastic_ips[eip_name] = ElasticIP(eip_name)
        eip = self._elastic_ips[eip_name]

        if InstanceName:
            instance = self._get_instance(InstanceName)
            if not eip.is_pointing_to(instance):
                eip.point_to(instance.id)

        return eip.public_ip
