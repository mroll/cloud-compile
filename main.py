import json
import pprint


class ResourceGroup:
    def __init__(self, name, resources=[]):
        self.name = name
        self.resources = resources


class CidrBlockMixin(object):
    def __init__(self, **kwargs):
        self.cidrblock = kwargs['cidrblock']

        super().__init__(**kwargs)


class VpcResourceMixin:
    def __init__(self, **kwargs):
        self.VpcId = kwargs['vpcid']

        super().__init__(**kwargs)


class AwsResourceMixin:
    def __init__(self, **kwargs):
        self.name = kwargs['name']
        self.resource_group = kwargs['resource_group']

        super().__init__(**kwargs)


class Vpc(AwsResourceMixin, CidrBlockMixin):
    def __init__(self, **kwargs):
        self.InstanceTenancy = kwargs['instance_tenancy']
        self.EnableDnsSupport = kwargs['enable_dns_support']
        self.EnableDnsHostnames = kwargs['enable_dns_hostnames']

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "CidrBlock": self.CidrBlock,
                "InstanceTenancy": self.InstanceTenancy,
                "EnableDnsSupport": self.EnableDnsSupport,
                "EnableDnsHostnames": self.EnableDnsHostnames
            }
        }


class Subnet(AwsResource, VpcResourceMixin, CidrBlockMixin):
    def __init__(self, **kwargs):
        self.AvailabilityZone = kwargs['availability_zone']

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "CidrBlock": self.CidrBlock,
                "AvailabilityZone": self.AvailabilityZone,
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }


class InternetGateway(AwsResource):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {}
        }


class DHCPOptions(AwsResource):
    def __init__(self, **kwargs):
        DomainName = kwargs['domain_name']
        DomainNameServers = kwargs['domain_name_servers']

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "DomainName": self.DomainName,
                "DomainNameServers": self.DomainNameServers
            }
        }


class NetworkAcl(AwsResource, VpcResourceMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }


class RouteTable(AwsResource, VpcResourceMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }


class Tag:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class Ipv6Address:
    def __init__(self, ipv6address):
        self.Ipv6Address = ipv6address


class EmbeddedPrivateIpAddressSpecification:
    def __init__(self, private_address=None, primary=None):
        self.PrivateAddress = private_address
        self.Primary = primary


class EmbeddedNetworkInterface():
    def __init__(self):
        self.AssociatePublicIpAddress = Column(Boolean)
        self.DeleteOnTermination = Column(Boolean)
        self.Description = Column(String(50))
        self.DeviceIndex = Column(String(50))
        self.GroupSet = Column(postgresql.ARRAY(String, dimensions=1))
        self.NetworkInterfaceId = Column(String(50))
        self.Ipv6AddressCount = Column(Integer)
        self.Ipv6Addresses = Column(postgresql.ARRAY(String, dimensions=1))
        self.PrivateIpAddress = Column(String(50))
        self.SecondaryPrivateIpAddressCount = Column(Integer)
        self.SubnetId = Column(String(50))

        self.PrivateIpAddresses = []
        self.Ipv6Addresses = []


# Added by Tim  \m/ \m/

# class Route(AwsResource):
#     DestinationCidrBlock = Column(String(50))
#     InstanceId = Column(String(50), ForeignKey="EC2")
#     RouteTableId = Column(String, ForeignKey="RouteTable")

#     __mapper_args__ = {
#         'polymorphic_identity': 'route'
#     }

#     def to_json(self):
#         return {
#             "Type": self.resource_type,
#             "Properties": {
#                 "DestinationCidrBlock": self.DestinationCidrBlock,
#                 "InstanceId": self.InstanceId,
#                 "RouteTableId": self.RouteTableId
#             }
#         }


# class SecurityGroupEgress(AwsResource):
#     # CidrIp = Column(String)
#     FromPort = Column(Integer)
#     GroupId = Column(String)
#     IpProtocol = Column(String)  
#     ToPort = Column(Integer)

#     __mapper_args__ = {
#         'polymorphic_identity': 'security_group_egress'
#     }

#     def to_json(self):
#         return {
#             "Type": self.resource_type,
#             "Properties": {
#                 "FromPort": self.FromPort,
#                 "GroupId": {
#                     "Ref": self.GroupId
#                 },
#                 "IpProtocol": self.IpProtocol,
#                 "ToPort": self.ToPort
#             }
#         }


# class SecurityGroupInress(AwsResource):
#     # CidrIp = Column(String(50))
#     FromPort = Column(Integer)
#     GroupId = Column(String(50))
#     IpProtocol = Column(String(50))  
#     ToPort = Column(Integer)

#     __mapper_args__ = {
#         'polymorphic_identity': 'security_group_inress'
#     }

#     def to_json(self):
#         return {
#             "Type": self.resource_type,
#             "Properties": {
#                 "FromPort": self.FromPort,
#                 "GroupId": {
#                     "Ref": self.GroupId
#                 },
#                 "IpProtocol": self.IpProtocol,
#                 "ToPort": self.ToPort
#             }
#         }


class SecurityGroup(AwsResource, VpcResourceMixin):
    GroupName = Column(String(50))
    GroupDescription = Column(String(255))
    # SecurityGroupEgress = relationship("SecurityGroupEgress")
    # SecurityGroupIngress = relationship("SecurityGroupIngress")

    __mapper_args__ = {
        'polymorphic_identity': 'security_group'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "GroupName": self.GroupName,
                "GroupDescription": self.GroupDescription,
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }


class Icmp():
    __tablename__ = "Icmp"

    id = Column(Integer, primary_key=True)
    Code = Column(Integer)
    Type = Column(Integer)


class PortRange():
    __tablename__ = "PortRange"

    id = Column(Integer, primary_key=True)
    From = Column(Integer)
    To = Column(Integer)


# class NetworkAclEntry(AwsResource, CidrBlockMixin):
#     NetworkAclId = Column(String, ForeignKey="NetworkAcl")
#     PortRange = Column(Integer, ForeignKey="PortRange")
#     Protocol = Column(Integer)
#     RuleAction  = Column(String(50))
#     RuleNumber = Column(Integer)

#     __mapper_args__ = {
#         'polymorphic_identity': 'network_acl_entry'
#     }

#     def to_json(self):
#         return {
#             "Type": self.resource_type,
#             "Properties": {
#                 "CidrBlock": self.CidrBlock,
#                 "NetworkAclId": self.NetworkAclId,
#                 "Protocol": self.Protocol,
#                 "RuleAction": self.RuleAction,
#                 "RuleNumber": self.RuleNumber
#             }
#         }


# class SubnetNetworkAclAssociation(AwsResource):
#     __mapper_args__ = {
#         'polymorphic_identity': 'subnet_network_acl_association'
#     }

#     def to_json(self):
#         return {
#             "Type": self.resource_type,
#             "Properties": {
#                 "SubnetId": self.SubnetId,
#                 "NetworkAclId": self.NetworkAclId
#             }
#         }


# class VpcGatewayAttachment(AwsResource, VpcResourceMixin):
#     InternetGatewayId = Column(String, ForeignKey="InternetGateway")

#     __mapper_args__ = {
#         'polymorphic_identity': 'vpc_gateway_attachment'
#     }

#     def to_json(self):
#         return {
#             "Type": self.resource_type,
#             "Properties": {
#                 "InternetGatewayId": self.InternetGatewayId,
#                 "VpcId": {
#                     "Ref": self.VpcId
#                 }
#             }
#         }


def basic_ec2_resource_group(session):
    rg = ResourceGroup(name='rg1')

    vpc = Vpc(name='vpc72b5da1b', CidrBlock="10.0.0.0/16", resource_type="AWS::EC2::VPC")
    subnet1 = Subnet(name="subnet32403d5b", CidrBlock="172.31.0.0/20",
                     AvailabilityZone="us-east-2a", VpcId=vpc.name,
                     resource_type="AWS::EC2::Subnet")
    subnet2 = Subnet(name="subnetc16cd7ba", CidrBlock="172.31.16.0/20",
                     AvailabilityZone="us-east-2b", VpcId=vpc.name,
                     resource_type="AWS::EC2::Subnet")
    subnet3 = Subnet(name="subnet9325edde", CidrBlock="172.31.32.0/20",
                     AvailabilityZone="us-east-2c", VpcId=vpc.name,
                     resource_type="AWS::EC2::Subnet")
    internet_gateway = InternetGateway(name="igw9fdf5ef6")
    dhcp_options = DHCPOptions(name="dopt9893e6f1",
                               DomainName="us-east-2.compute.internal",
                               DomainNameServers=[
                                   "AmazonProvidedDNS"
                               ])
    network_acl = NetworkAcl(name="acl992252f0", VpcId=vpc.name)
    route_table = RouteTable(name="rtb11c7ee79", VpcId=vpc.name)

    rg.resources = [vpc, subnet1, subnet2, subnet3, internet_gateway,
                    dhcp_options, network_acl, route_table]

    session.add(rg)
    session.add(vpc)
    session.add(subnet1)
    session.add(subnet2)
    session.add(subnet3)

    session.commit()

    return rg


.metadata.create_all(engine)


ec2 = Ec2(name='ec2')

sg1 = SecurityGroup(name='sg1')
sg2 = SecurityGroup(name='sg2')

ec2.security_groups = [sg1, sg2]

session.add(ec2)
session.add(sg1)
session.add(sg2)

# rg = basic_ec2_resource_group(session)

# pp = pprint.PrettyPrinter()

# for resource in rg.resources:
#     pp.pprint({resource.name: resource.to_json()})

session.close()
