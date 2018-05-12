import json
import pprint

from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String,
                        create_engine)
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship, sessionmaker

engine = create_engine('postgresql://postgres:d4t4base@localhost/cc-db')
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class JsonifierMixin:
    def to_json(self):
        print(self.__dict__)
        return json.dumps(self.__dict__)


class ResourceGroup(Base):
    __tablename__ = 'ResourceGroup'

    id = Column(Integer, primary_key=True)
    name = Column(String)

    resources = relationship('AwsResource')


class VpcResourceMixin(object):
    @declared_attr
    def VpcId(cls):
        return cls.__table__.c.get('VpcId', Column(String))


class CidrBlockMixin(object):
    @declared_attr
    def CidrBlock(cls):
        return cls.__table__.c.get('CidrBlock', Column(String))


class AwsResource(Base):
    __tablename__ = 'AwsResource'

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    type = Column(String(20))
    resource_group_id = Column(Integer, ForeignKey('ResourceGroup.id'))
    resource_type = Column(String(50))

    __mapper_args__ = {
        'polymorphic_on': type,
        'polymorphic_identity': 'aws_resource'
    }


class Vpc(AwsResource, CidrBlockMixin):
    InstanceTenancy = Column(String(50), default="default")
    EnableDnsSupport = Column(Boolean, default=True)
    EnableDnsHostnames = Column(Boolean, default=True)

    __mapper_args__ = {
        'polymorphic_identity': 'vpc'
    }

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


class Tag(Base):
    __tablename__ = 'Tag'

    id = Column(Integer, primary_key=True)
    key = Column(String(50))
    value = Column(String(50))


class Ipv6Address(Base):
    __tablename__ = 'Ipv6Address'

    id = Column(Integer, primary_key=True)
    Ipv6Address = Column(String(50))

    EmbeddedNetworkInterface = Column(
        Integer,
        ForeignKey('EmbeddedNetworkInterface.id')
    )


class EmbeddedPrivateIpAddressSpecification(Base):
    __tablename__ = 'EmbeddedPrivateIpAddressSpecification'

    # Fields
    id = Column(Integer, primary_key=True)
    PrivateAddress = Column(String(50))
    Primary = Column(Boolean)

    # Relationships
    EmbeddedNetworkInterface = Column(
        Integer,
        ForeignKey('EmbeddedNetworkInterface.id')
    )


class EmbeddedNetworkInterface(Base):
    __tablename__ = 'EmbeddedNetworkInterface'

    # Fields
    AssociatePublicIpAddress = Column(Boolean)
    DeleteOnTermination = Column(Boolean)
    Description = Column(String(50))
    DeviceIndex = Column(String(50))
    GroupSet = Column(postgresql.ARRAY(String, dimensions=1))
    NetworkInterfaceId = Column(String(50))
    Ipv6AddressCount = Column(Integer)
    Ipv6Addresses = Column(postgresql.ARRAY(String, dimensions=1))
    PrivateIpAddress = Column(String(50))
    SecondaryPrivateIpAddressCount = Column(Integer)
    SubnetId = Column(String(50))

    # Relationships
    PrivateIpAddresses = relationship("EmbeddedPrivateIpAddressSpecification")
    Ipv6Addresses = relationship("Ipv6Address")
    Ec2 = Column(Integer, ForeignKey('Ec2'))


class Ec2(AwsResource):
    DisableApiTermination = Column(String(50))
    InstanceInitiatedShutdownBehavior = Column(String(50))
    ImageId = Column(String(50))
    InstanceType = Column(String(50))
    KeyName = Column(String(50))
    Monitoring = Column(String(50))
    SecurityGroupIds = relationship("SecurityGroup")

    # Relationships

    __mapper_args__ = {
        'polymorphic_identity': 'ec2'
    }


class Subnet(AwsResource, VpcResourceMixin, CidrBlockMixin):
    AvailabilityZone = Column(String(50))

    __mapper_args__ = {
        'polymorphic_identity': 'subnet'
    }

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
    __mapper_args__ = {
        'polymorphic_identity': 'internet_gateway'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {}
        }


class DHCPOptions(AwsResource):
    DomainName = Column(String)
    DomainNameServers = Column(postgresql.ARRAY(String, dimensions=1))

    __mapper_args__ = {
        'polymorphic_identity': 'dhcp_options'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "DomainName": self.DomainName,
                "DomainNameServers": self.DomainNameServers
            }
        }


class NetworkAcl(AwsResource, VpcResourceMixin):
    __mapper_args__ = {
        'polymorphic_identity': 'network_acl'
    }

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
    __mapper_args__ = {
        'polymorphic_identity': 'route_table'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }


# Added by Tim  \m/ \m/

class Route(AwsResource):
    DestinationCidrBlock = Column(String(50))
    InstanceId = Column(String(50), ForeignKey="EC2")
    RouteTableId = Column(String, ForeignKey="RouteTable")

    __mapper_args__ = {
        'polymorphic_identity': 'route'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "DestinationCidrBlock": self.DestinationCidrBlock,
                "InstanceId": self.InstanceId,
                "RouteTableId": self.RouteTableId
            }
        }


class SecurityGroupEgress(AwsResource):
    CidrIp = Column(String)
    FromPort = Column(Integer)
    GroupId = Column(String)
    IpProtocol = Column(String)  
    ToPort = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'security_group_egress'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "CidrIp": self.CidrIp,
                "FromPort": self.FromPort,
                "GroupId": {
                    "Ref": self.GroupId
                },
                "IpProtocol": self.IpProtocol,
                "ToPort": self.ToPort
            }
        }


class SecurityGroupInress(AwsResource):
    CidrIp = Column(String(50))
    FromPort = Column(Integer)
    GroupId = Column(String(50))
    IpProtocol = Column(String(50))  
    ToPort = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'security_group_inress'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "CidrIp": self.CidrIp,
                "FromPort": self.FromPort,
                "GroupId": {
                    "Ref": self.GroupId
                },
                "IpProtocol": self.IpProtocol,
                "ToPort": self.ToPort
            }
        }


class SecurityGroup(AwsResource, VpcResourceMixin):
    GroupName = Column(String(50))
    GroupDescription = Column(String(255))
    SecurityGroupEgress = relationship("SecurityGroupEgress")
    SecurityGroupIngress = relationship("SecurityGroupIngress")

    __mapper_args__ = {
        'polymorphic_identity': 'security_group'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "GroupName": self.GroupName,
                "GroupDescription": self.GroupDescription,
                "SecurityGroupEgress": [
                    self.SecurityGroupEgress
                ],
                "SecurityGroupIngress": [
                    self.SecurityGroupIngress
                ],
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }


class Icmp(Base):
    __tablename__ = "Icmp"

    id = Column(Integer, primary_key=True)
    Code = Column(Integer)
    Type = Column(Integer)


class PortRange(Base):
    __tablename__ = "PortRange"

    id = Column(Integer, primary_key=True)
    From = Column(Integer)
    To = Column(Integer)


class NetworkAclEntry(AwsResource, CidrBlockMixin):
    Icmp = Column(Integer, ForeignKey="Icmp")
    NetworkAclId = Column(String, ForeignKey="NetworkAcl")
    PortRange = Column(Integer, ForeignKey="PortRange")
    Protocol = Column(Integer)
    RuleAction  = Column(String(50))
    RuleNumber = Column(Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'network_acl_entry'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "CidrBlock": self.CidrBlock,
                "Icmp": self.Icmp.__dict__, # No idea how to do this
                "NetworkAclId": self.NetworkAclId,
                "PortRange": self.PortRange.__dict__, # No idea how to do this
                "Protocol": self.Protocol,
                "RuleAction": self.RuleAction,
                "RuleNumber": self.RuleNumber
            }
        }


class SubnetNetworkAclAssociation(AwsResource):
    SubnetId = Column(String, ForeignKey="Subnet")
    NetworkAclId = Column(String, ForeignKey="NetworkAcl")

    __mapper_args__ = {
        'polymorphic_identity': 'subnet_network_acl_association'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "SubnetId": self.SubnetId,
                "NetworkAclId": self.NetworkAclId
            }
        }


class VpcGatewayAttachment(AwsResource, VpcResourceMixin):
    InternetGatewayId = Column(String, ForeignKey="InternetGateway")

    __mapper_args__ = {
        'polymorphic_identity': 'vpc_gateway_attachment'
    }

    def to_json(self):
        return {
            "Type": self.resource_type,
            "Properties": {
                "InternetGatewayId": self.InternetGatewayId,
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }


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


Base.metadata.create_all(engine)

rg = basic_ec2_resource_group(session)

pp = pprint.PrettyPrinter()

for resource in rg.resources:
    pp.pprint({resource.name: resource.to_json()})

session.close()
