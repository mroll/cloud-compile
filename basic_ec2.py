import pprint

from models.base import ResourceGroup
from models.ec2 import *
from models.vpc import (DHCPOptions, InternetGateway, NetworkAcl, RouteTable,
                        Subnet, Vpc)

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
    rule_action='allow',
    rule_number='100',
    network_acl_id=nacl1.name,
    port_range=PortRange(0, 1024)
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

pips = [PrivateIpAddress('172.31.35.56', True)]

nifaces = [
    NetworkInterface(
        False,
        0,
        subnet1.name,
        pips,
        [
            {
                "Ref": sg1.name
            }
        ],
        True
    )
]

ec2 = Ec2(
    name='ada',
    disable_api_termination=False,
    shutdown_behavior='stop',
    image_id='ami-618fab04',
    key_name='ada',
    network_interfaces=nifaces
)

rg.resources.append(sg1)
rg.resources.append(naclent1)
rg.resources.append(subaclass1)
rg.resources.append(vpcgateatt1)
rg.resources.append(r1)
rg.resources.append(vdoa1)
rg.resources.append(ingress1)
rg.resources.append(egress1)


pp = pprint.PrettyPrinter()

pp.pprint(rg.to_json())
