import ast

import boto3
from botocore.exceptions import ClientError

global DELETEFILE
global DELETERESOURCES

DELETEFILE = 'resources.delete'
DELETERESOURCES = []

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')


def first(f, l):
    for el in l:
        if f(el):
            return el


def get_vpc_subnet(vpc, cidr_block):
    global ec2_resource

    def filt(subnet):
        return subnet.vpc == vpc and subnet.cidr_block == cidr_block

    return first(filt, ec2_resource.subnets.all())


def get_vpc_route_table(vpc):
    return list(vpc.route_tables.all())[0]


def associate_vpc__internet_gateway(vpc):
    global ec2_client

    create_ig_response = ec2_client.create_internet_gateway()
    ig = ec2_resource.InternetGateway(
        create_ig_response["InternetGateway"]["InternetGatewayId"]
    )

    vpc.attach_internet_gateway(InternetGatewayId=ig.id)
    return ig


def create_vpc(
        CidrBlock,
        SubnetSpecs=[],
        AttachInternetGateway=True
):
    global ec2_resource

    vpc = ec2_resource.create_vpc(CidrBlock=CidrBlock)
    vpc.wait_until_available()

    if AttachInternetGateway:
        ig = associate_vpc__internet_gateway(vpc)

    route_table = get_vpc_route_table(vpc)
    for subnet_spec in SubnetSpecs:
        subnet = vpc.create_subnet(CidrBlock=subnet_spec['CidrBlock'])

        if AttachInternetGateway and subnet_spec['Public']:
            route_table.associate_with_subnet(SubnetId=subnet.id)
            route_table.create_route(
                DestinationCidrBlock='0.0.0.0/0',
                GatewayId=ig.id,
            )

    return vpc


def associate_elastic_ip__ec2(ec2id):
    global ec2_client

    public_ip = ''
    allocation = ''
    elastic_ips = ec2_client.describe_addresses()

    for address in elastic_ips['Addresses']:
        print('Found existing Elastic IP: ', address)
        if 'InstanceId' not in address:
            allocation = address['AllocationId']
            public_ip = address['PublicIp']
            break

    if allocation == '':
        try:
            allocation_response = ec2_client.allocate_address(Domain='vpc')
            allocation = allocation_response['AllocationId']
            public_ip = allocation_response['PublicIp']
        except ClientError as e:
            print(e)

    try:
        ec2_client.associate_address(
            AllocationId=allocation,
            InstanceId=ec2id,
        )
    except ClientError as e:
        print(e)

    return public_ip


def create_security_group(
        GroupName,
        VpcId,
        Description='default description',
        IngressRules=[],
        EgressRules=[]
):
    global ec2_client, ec2_resource

    security_group_response = ec2_client.create_security_group(
        GroupName=GroupName,
        Description=Description,
        VpcId=VpcId
    )
    security_group = ec2_resource.SecurityGroup(
        security_group_response['GroupId']
    )

    for ingress_rule in IngressRules:
        security_group.authorize_ingress(**ingress_rule)

    for egress_rule in EgressRules:
        security_group.authorize_egress(**ingress_rule)

    return security_group


def create_keypair(KeyName, outfile=None):
    try:
        key_pair = ec2_client.create_key_pair(
            KeyName=KeyName,
        )
        if outfile:
            with open(outfile, 'w') as fp:
                fp.write(key_pair['KeyMaterial'])
        else:
            print(key_pair['KeyMaterial'])
    except ClientError as e:
        print('Found keypair {}'.format(KeyName))

    return KeyName


def create_ec2(
        Ami, KeyName, SubnetId, SecurityGroupId,
        InstanceType='t2.micro',
        MinCount=1,
        MaxCount=1
):
    global ec2_resource

    instances = ec2_resource.create_instances(
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

    return(instance)


def create_subnet_group(
        GroupName,
        SubnetIds,
        GroupDescription='default group description',
        Tags=[]
):
    global ec2_client

    response = ec2_client.create_db_subnet_group(
        DBSubnetGroupName=GroupName,
        DBSubnetGroupDescription=GroupDescription,
        SubnetIds=SubnetIds,
        Tags=Tags
    )

    return response


def create_rds_instance(
        DBInstanceIdentifier,
        AllocatedStorage=20,
        DBInstanceClass='db.t2.micro',
        EngineVersion='10.1',
        MasterUsername='root',
        MasterUserPassword='pa55word',
        DBSecurityGroups=[db_security_group.name],
        AvailabilityZone='us-east-2b',
        DBSubnetGroupName=db_subnet_group['DBSubnetGroupName'],
        BackupRetentionPeriod=0,
        Port=5432,  # default for postgres
        Engine='postgres',
        AutoMinorVersionUpgrade=True,
        StorageType='gp2',
        PubliclyAccessible=False,
):
    rds_response = ec2_client.create_db_instance(
        DBInstanceIdentifier=DBInstanceIdentifier,
        AllocatedStorage=AllocatedStorage,
        DBInstanceClass=DBInstanceClass,
        Engine=Engine,
        MasterUsername=MasterUsername,
        MasterUserPassword=MasterUserPassword,
        DBSecurityGroups=DBSecurityGroups,
        AvailabilityZone=AvailabilityZone,
        DBSubnetGroupName=DBSubnetGroupName,
        BackupRetentionPeriod=BackupRetentionPeriod,
        Port=Port,
        AutoMinorVersionUpgrade=AutoMinorVersionUpgrade,
        StorageType=StorageType,
        PubliclyAccessible=PubliclyAccessible,
    )

    return rds_response


def mark_vpc_for_delete(id):
    global DELETERESOURCES
    DELETERESOURCES.append({'type': 'vpc', 'id': id})


def write_resources_for_deletion():
    global DELETEFILE, DELETERESOURCES
    with open(DELETEFILE, 'w') as fp:
        fp.write(str(DELETERESOURCES))


def delete_resources():
    global DELETEFILE
    with open(DELETEFILE, 'r') as fp:
        resources = ast.literal_eval(fp.read())

    for resource in
