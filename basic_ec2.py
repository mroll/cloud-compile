from models.base import ResourceGroup
from models.vpc import (DHCPOptions, InternetGateway, NetworkAcl, RouteTable,
                        Subnet, Vpc)
from models.ec2 import *

rg = ResourceGroup(name='rg1')

vpc = Vpc(name='vpc1')

subnet1 = Subnet(name='subnet1', vpcid=vpc.name, cidrblock='10.0.0.0/24')
subnet2 = Subnet(name='subnet2', vpcid=vpc.name, cidrblock='10.0.0.1/24')
subnet3 = Subnet(name='subnet3', vpcid=vpc.name, cidrblock='10.0.0.2/24')

ig1 = InternetGateway(name='ig1')

dopt1 = DHCPOptions(name='dopt1')

nacl1 = NetworkAcl(name='nacl1', vpcid=vpc.name)

rt1 = RouteTable(name='rt1', vpcid=vpc.name)

rg.resources.append(vpc)
rg.resources.append(subnet1)
rg.resources.append(subnet2)
rg.resources.append(subnet3)
rg.resources.append(ig1)
rg.resources.append(dopt1)
rg.resources.append(nacl1)
rg.resources.append(rt1)

sg1 = SecurityGroup(name='sg1', vpcid=vpc.name,
                    group_name='sg1', description='sg1 blah blah')

naclent1 = NetworkAclEntry(
    name='naclent1',
    cidrblock='0.0.0.0/0',
    egress=True,
    protocol=-1,
    rule_ation='allow',
    rule_number='100',
    network_acl_id=nacl1.name
)

subaclass1 = SubnetNetworkAclAssociation(
    name='subaclass1',
    network_acl_id=nacl1.name,
    subnet_id=subnet1.name
)

vpcgateatt1 = VpcGatewayAttachment(
    name='vpcgateatt1',
    vpcid=vpc.name,
    internet_gateway_id=ig1.name
)

r1 = Route(
    name='r1',
    destination_cidr_block='0.0.0.0/0',
    route_table_id=rt1.name,
    gateway_id=ig1.name
)

vdoa1 = VPCDHCPOptionsAssociation(
    name='vdoa1',
    vpcid=vpc.name,
    dhcp_options_id=dopt1.name
)

ingress1 = SecurityGroupIngress(
    name='ingress1',
    cidr_ip='0.0.0.0/0',
    from_port='443',
    to_port='443',
    protocol='tcp',
    group_id=sg1.name
)

egress1 = SecurityGroupEgress(
    name='egress1',
    cidr_ip='0.0.0.0/0',
    protocol='-1'
)

ec2 = Ec

print(rg.__dict__)

for resource in rg.resources:
    print(resource.to_json())
