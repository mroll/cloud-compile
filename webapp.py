from models.vpc import Vpc

webapp_vpc = Vpc('webapp-vpc')
print('[+] Established VPC {}'.format('webapp-vpc'))

webapp_vpc.subnets([
    {'CidrBlock': '10.0.1.0/24', 'Public': True}
])
print('[+] Established subnets')

webapp_vpc.security_group(
    'webapp-security-group',
    IngressRules=[
        {
            'CidrIp': '0.0.0.0/0',
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22
        }
    ]
)
print('[+] Established security group')

KeyName = 'basic-webapp-key'
keypair = webapp_vpc.key_pair(KeyName)
print('[+] Established key pair')

webapp_vpc.instance(
    'webapp-instance-1',
    'ami-916f59f4',
    KeyName,
    '10.0.1.0/24',
    'webapp-security-group'
)
print('[+] Established instance')

webapp_vpc.elastic_ip(
    'webapp-elastic-ip-1',
    InstanceName='webapp-instance-1'
)
print('[+] Established elastic ip')

# webapp_vpc.private_rds(
#     'webapp-private-rds-1',
#     SubnetGroupName='webapp-rds-subnet-group',
#     SecurityGroupName='webapp-rds-sec-group',
#     Engine='postgres',
#     EngineVersion='9.6',
# )
