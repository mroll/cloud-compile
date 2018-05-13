from models.base import AwsResourceMixin, CidrBlockMixin, VpcResourceMixin

class Route(AwsResourceMixin):
    def __init__(self, **kwargs):
        self.DestinationCidrBlock = kwargs.pop('destination_cidr_block', None)
        # self.InstanceId = kwargs.pop('instance_id', None)
        self.GatewayId = kwargs.pop('gateway_id', None)
        self.RouteTableId = kwargs.pop('route_table_id', None)

        # Resource Type
        self.Type = 'AWS::EC2::Route'

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "DestinationCidrBlock": self.DestinationCidrBlock,
                "GatewayId": {
                    "Ref": self.GatewayId
                },
                "RouteTableId": {
                    "Ref": self.RouteTableId
                }
            }
        }


class SecurityGroupEgress(AwsResourceMixin):
    def __init__(self, **kwargs):
        self.CidrIp = kwargs.pop('cidr_ip', '0.0.0.0/0')
        self.FromPort = kwargs.pop('from_port', 0)
        self.GroupId = kwargs.pop('group', None)
        self.IpProtocol = kwargs.pop('protocol', 'tcp')
        self.ToPort = kwargs.pop('to_port', 65535)

        # Resource Type
        self.Type = 'AWS::EC2::SecurityGroupEgress'

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
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


class SecurityGroupIngress(AwsResourceMixin):
    def __init__(self, **kwargs):
        self.CidrIp = kwargs.pop('cidr_ip', '0.0.0.0/0')
        self.FromPort = kwargs.pop('from_port', 0)
        self.GroupId = kwargs.pop('group_id', None)
        self.IpProtocol = kwargs.pop('protocol', 'tcp')
        self.ToPort = kwargs.pop('to_port', 65535)

        # Resource Type
        self.Type = 'AWS::EC2::SecurityGroupIngress'

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "CidrIp": self.CidrIp,
                "GroupId": {
                    "Ref": self.GroupId
                },
                "IpProtocol": self.IpProtocol
            }
        }


class SecurityGroup(AwsResourceMixin, VpcResourceMixin):
    def __init__(self, **kwargs):
        self.GroupName = kwargs.pop('group_name', None)
        self.GroupDescription = kwargs.pop('description', None)
        self.SecurityGroupEgress = []
        self.SecurityGroupIngress = []

        # Resource Type
        self.Type = 'AWS::EC2::SecurityGroup'

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
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


class Icmp:
    def __init__(self, code, type):
        self.Code = code
        self.Type = type

    def to_json(self):
        return {
            "Code": self.Code,
            "Type": self.Type
        }


class PortRange:
    def __init__(self, from_port, to_port):
        self.From = from_port
        self.To = to_port

    def to_json(self):
        return {
            "From": self.From,
            "To": self.To
        }


class NetworkAclEntry(AwsResourceMixin, CidrBlockMixin):
    def __init__(self, **kwargs):
        # self.Icmp = kwargs.pop('icmp', None)
        self.Egress = kwargs.pop('egress', False)
        self.NetworkAclId = kwargs.pop('network_acl_id', None)
        self.PortRange = kwargs.pop('port_range', None)
        self.Protocol = kwargs.pop('protocol', None)
        self.RuleAction = kwargs.pop('rule_action', None)
        self.RuleNumber = kwargs.pop('rule_number', None)

        # Resource Type
        self.Type = 'AWS::EC2::NetworkAclEntry'

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "CidrBlock": self.CidrBlock,
                "Egress": self.Egress,
                "NetworkAclId": {
                    "Ref": self.NetworkAclId
                },
                "PortRange": self.PortRange.to_json(),
                "Protocol": self.Protocol,
                "RuleAction": self.RuleAction,
                "RuleNumber": self.RuleNumber
            }
        }


class SubnetNetworkAclAssociation(AwsResourceMixin):
    def __init__(self, **kwargs):
        self.SubnetId = kwargs.pop('subnet_id', None)
        self.NetworkAclId = kwargs.pop('network_acl_id', None)

        # Resource Type
        self.Type = 'AWS::EC2::SubnetNetworkAclAssociation'

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "SubnetId": {
                    "Ref": self.SubnetId
                },
                "NetworkAclId": {
                    "Ref": self.NetworkAclId
                }
            }
        }


class VpcGatewayAttachment(AwsResourceMixin, VpcResourceMixin):
    def __init__(self, **kwargs):
        self.InternetGatewayId = kwargs.pop('internet_gateway_id', None)

        # Resource Type
        self.Type = 'AWS::EC2::VpcGatewayAttachment'

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "InternetGatewayId": {
                    "Ref": self.InternetGatewayId
                },
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }


class VPCDHCPOptionsAssociation(AwsResourceMixin, VpcResourceMixin):
    def __init__(self, **kwargs):
        self.DhcpOptionsId = kwargs.pop('dhcp_options_id', None)

        # Resource Type
        self.Type = 'AWS::EC2::VPCDHCPOptionsAssociation'

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "DhcpOptionsId": {
                    "Ref": self.DhcpOptionsId
                },
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }
