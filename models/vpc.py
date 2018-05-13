from models.base import AwsResourceMixin, CidrBlockMixin, VpcResourceMixin


class Vpc(AwsResourceMixin, CidrBlockMixin):
    def __init__(self, **kwargs):
        self.Type = "AWS::EC2::VPC"
        self.InstanceTenancy = kwargs.pop('instance_tenancy', None)
        self.EnableDnsSupport = kwargs.pop('enable_dns_support', True)
        self.EnableDnsHostnames = kwargs.pop('enable_dns_hostnames', True)

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "CidrBlock": self.CidrBlock,
                "InstanceTenancy": self.InstanceTenancy,
                "EnableDnsSupport": self.EnableDnsSupport,
                "EnableDnsHostnames": self.EnableDnsHostnames
            }
        }


class Subnet(AwsResourceMixin, VpcResourceMixin, CidrBlockMixin):
    def __init__(self, **kwargs):
        self.Type = "AWS::EC2::Subnet"
        self.AvailabilityZone = kwargs.pop('availability_zone', 'us-east-1a')

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "CidrBlock": self.CidrBlock,
                "AvailabilityZone": self.AvailabilityZone,
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }


class InternetGateway(AwsResourceMixin):
    def __init__(self, **kwargs):
        self.Type = "AWS::EC2::InternetGateway"
        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {}
        }


class DHCPOptions(AwsResourceMixin):
    def __init__(self, **kwargs):
        self.Type = "AWS::EC2::DHCPOptions"
        self.DomainName = kwargs.pop('domain_name', 'us-east-2.compute.internal')
        self.DomainNameServers = kwargs.pop(
            'domain_name_servers',
            ["AmazonProvidedDNS"])

        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "DomainName": self.DomainName,
                "DomainNameServers": self.DomainNameServers
            }
        }


class NetworkAcl(AwsResourceMixin, VpcResourceMixin):
    def __init__(self, **kwargs):
        self.Type = "AWS::EC2::NetworkAcl"
        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }


class RouteTable(AwsResourceMixin, VpcResourceMixin):
    def __init__(self, **kwargs):
        self.Type = "AWS::EC2::RouteTable"
        super().__init__(**kwargs)

    def to_json(self):
        return {
            "Type": self.Type,
            "Properties": {
                "VpcId": {
                    "Ref": self.VpcId
                }
            }
        }
