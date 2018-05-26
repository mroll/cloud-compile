import boto3
from botocore.exceptions import ClientError


def first(f, l):
    for el in l:
        if f(el):
            return el


def resource_name(resource_dict):
    if 'Tags' in resource_dict:
        for tag in resource_dict['Tags']:
            if tag['Key'] == 'Name':
                return tag['Value']


def tag(resource, *tags):
    resource.create_tags(Tags=[{'Key': k, 'Value': v} for k, v in tags])


def taglist_keys(taglist):
    return [tag['Key'] for tag in taglist]


def tagged_resource(resources, target_tag):
    target_key = target_tag[0]
    target_val = target_tag[1]

    def has_matching_tag(resource):
        if not resource.tags:
            return

        for resource_tag in resource.tags:
            if target_key == resource_tag['Key'] and \
               target_val == resource_tag['Value']:
                return resource

    for resource in resources:
        if has_matching_tag(resource):
            return resource


class Vpc:
    def __init__(self, name, public=True):
        self.name = name
        self.public = public
        self.client = boto3.client('ec2')
        self.resource = boto3.resource('ec2')
        self.vpc = None
        self._internet_gateway = None

        self._create_vpc(name)

        if public:
            self._attach_internet_gateway('internet-gateway')

    def _get_internet_gateway(self, ig_name):
        return tagged_resource(self.resource.internet_gateways.all(), ('Name', ig_name))

    def _internet_gateway_exists(self, ig_name):
        return self._get_internet_gateway(ig_name) is not None

    def _create_internet_gateway(self, ig_name):
        ig = self.resource.create_internet_gateway()
        tag(ig, ('Name', ig_name))

        return ig

    def _attach_internet_gateway(self, ig_name):
        if not self._internet_gateway_exists(ig_name):
            ig = self._create_internet_gateway(ig_name)
        else:
            ig = self._get_internet_gateway(ig_name)

        attached_vpcs = [a['VpcId'] for a in ig.attachments]
        if self.vpc.id not in attached_vpcs:
            ig.attach_to_vpc(VpcId=self.vpc.id)

        self._internet_gateway = ig

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

    def _elastic_ip_exists(self, eip_name):
        return self._get_elastic_ip(eip_name) is not None

    def _get_elastic_ip(self, eip_name):
        def eip_matches_name(eip_dict):
            return resource_name(eip_dict) == eip_name

        response = self.client.describe_addresses(
            Filters=[
                {
                    'Name': 'tag:Name',
                    'Values': [eip_name]
                }
            ]
        )
        eip_dict = first(eip_matches_name, response['Addresses'])

        if eip_dict:
            return (eip_dict['AllocationId'], eip_dict['PublicIp'])

    def _create_vpc(self, vpc_name, cidr_block='10.0.0.0/16'):
        if self._vpc_exists(vpc_name):
            self.vpc = self._get_vpc(vpc_name)
            return

        self.vpc = self.resource.create_vpc(CidrBlock=cidr_block)
        self.vpc.wait_until_available()
        tag(self.vpc, ('Name', vpc_name))

    def _subnet_exists(self, subnet_name):
        subnet_response = self.client.describe_subnets()
        return subnet_name in [resource_name(subnetd) for subnetd in subnet_response['Subnets']]

    def _existing_subnet_names(self):
        def find_tag_with_key(tags, key):
            for tag in tags:
                if tag['Key'] == key:
                    return tag

        names = []
        for subnet in self.vpc.subnets.all():
            tag = find_tag_with_key(subnet.tags, 'Name')
            if tag:
                names.append(tag['Value'])

        return names

    def _subnet_id(self, subnet_name):
        return first(lambda s: resource_name(s) == subnet_name, )

    @property
    def _route_table(self):
        return list(self.vpc.route_tables.all())[0]

    def _get_subnet(self, subnet_name):
        return tagged_resource(self.vpc.subnets.all(), ('Name', subnet_name))

    def _get_security_group(self, security_group_name):
        return tagged_resource(self.vpc.security_groups.all(),
                               ('Name', security_group_name))

    def _get_instance(self, instance_name):
        return tagged_resource(self.vpc.instances.all(), ('Name', instance_name))

    def _delete_subnet(self, subnet_name):
        subnet = self._get_subnet(subnet_name)
        subnet.delete()

    def _create_subnet(self, subnet_spec):
        cidrblock = subnet_spec['CidrBlock']

        subnet = self.vpc.create_subnet(CidrBlock=cidrblock)
        tag(subnet, ('Name', cidrblock))

        return subnet

    def subnets(self, proposed_subnet_specs):
        """Establish subnets in the vpc according to the given specs.

        - Create subnets if they do not exist
        - Change the privacy of existing subnets if they differ from the spec
        - Delete subnets if they exist but are not given in the spec

        """
        existing_subnet_names = self._existing_subnet_names()
        proposed_subnet_names = [spec['CidrBlock'] for spec in proposed_subnet_specs]

        route_table = self._route_table
        for subnet_spec in proposed_subnet_specs:
            cidrblock = subnet_spec['CidrBlock']
            if cidrblock not in existing_subnet_names:
                subnet = self._create_subnet(subnet_spec)
                if self.public and subnet_spec['Public']:
                    route_table.associate_with_subnet(SubnetId=subnet.id)
                    route_table.create_route(
                        DestinationCidrBlock='0.0.0.0/0',
                        GatewayId=self._internet_gateway.id,
                    )

        for subnet_name in existing_subnet_names:
            if subnet_name not in proposed_subnet_names:
                self._delete_subnet(subnet_name)

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

        SubnetId = self._get_subnet(SubnetName).id
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
        if not self._elastic_ip_exists(eip_name):
            allocation_response = self.client.allocate_address(Domain='vpc')
            allocation_id = allocation_response['AllocationId']
            public_ip = allocation_response['PublicIp']

            self.client.create_tags(
                Resources=[allocation_id],
                Tags=[
                    {
                        'Key': 'Name',
                        'Value': eip_name
                    }
                ]
            )
        else:
            allocation_id, public_ip = self._get_elastic_ip(eip_name)

        if InstanceName:
            instance = self._get_instance(InstanceName)
            if instance.public_ip_address != public_ip:
                try:
                    self.client.associate_address(
                        AllocationId=allocation_id,
                        InstanceId=instance.id,
                    )
                except ClientError as e:
                    print(e)

        return public_ip
