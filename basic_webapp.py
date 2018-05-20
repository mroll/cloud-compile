import boto3
from botocore.exceptions import ClientError

ec2_client = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')


"""
----------------------------------------------------------------------
VPC & VPC Resources
---

creates:
  - vpc
  - network acl
  - route table
  - subnet
  - internet gateway
  - route table
  - route
uses existing:
  - dhcp options
----------------------------------------------------------------------
"""
vpc = ec2_resource.create_vpc(CidrBlock='10.0.0.0/16')
vpc.wait_until_available()
print(vpc.id)

subnet = vpc.create_subnet(CidrBlock='10.0.0.1/24')

create_ig_response = ec2_client.create_internet_gateway()
ig = ec2_resource.InternetGateway(
    create_ig_response["InternetGateway"]["InternetGatewayId"]
)

vpc.attach_internet_gateway(InternetGatewayId=ig.id)
print(ig.id)


route_table = list(vpc.route_tables.all())[0]
route_table.associate_with_subnet(SubnetId=subnet.id)
route_table.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=ig.id,
)


"""
----------------------------------------------------------------------
EC2 & EC2 Resources
---

creates:
  - security group
  - security group ingress
  - (if dne) keypair
  - instance
  - network interface

"""
# Create sec group
sec_group_response = ec2_client.create_security_group(
    GroupName='webapp',
    Description='basic webapp sec group',
    VpcId=vpc.id
)
sec_group = ec2_resource.SecurityGroup(sec_group_response['GroupId'])

sec_group.authorize_ingress(
    CidrIp='0.0.0.0/0',
    IpProtocol='tcp',
    FromPort=22,
    ToPort=22
)

try:
    key_pair = ec2_client.create_key_pair(
        KeyName='basic-webapp-key',
    )
    print(key_pair['KeyMaterial'])
except ClientError:
    print('Key pair basic-web-app already exists')

instances = ec2_resource.create_instances(
    ImageId='ami-916f59f4',
    MinCount=1,
    MaxCount=1,
    KeyName='basic-webapp-key',
    InstanceType='t2.micro',
    NetworkInterfaces=[{
        'SubnetId': subnet.id,
        'DeviceIndex': 0,
        'AssociatePublicIpAddress': True,
        'Groups': [sec_group.group_id]}
    ],
)
instances[0].wait_until_running()
print(instances[0].id)
