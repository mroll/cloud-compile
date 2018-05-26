from util import (associate_elastic_ip__ec2, create_ec2, create_keypair,
                  create_rds_instance, create_security_group,
                  create_subnet_group, create_vpc, get_vpc_subnet)

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

subnets = [
    {'CidrBlock': '10.0.1.0/24', 'Public': True}
]
vpc = create_vpc('10.0.0.0/16', subnets)
print('Created vpc {}'.format(vpc.id))

# mark_vpc_for_delete(vpc)


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

security_group = create_security_group(
    'webapp-security-group',
    vpc.id,
    IngressRules=[
        {
            'CidrIp': '0.0.0.0/0',
            'IpProtocol': 'tcp',
            'FromPort': 22,
            'ToPort': 22
        }
    ]
)
print('Created security group {}'.format(security_group.id))


KeyName = 'basic-webapp-key'
create_keypair(KeyName)

subnet = get_vpc_subnet(vpc, '10.0.1.0/24')

instance = create_ec2('ami-916f59f4', KeyName, subnet.id, security_group.id)
elastic_ip = associate_elastic_ip__ec2(instance.id)

print('Created EC2 instance {}'.format(instance.id))
print('Created Elastic IP {} and pointed it at {}'.format(
    elastic_ip,
    instance.id
))


"""
RDS & RDS Resources
---

"""

db_security_group = create_security_group(
    'private-db-security-group',
    vpc.id,
    IngressRules=[
        {
            'SourceSecurityGroupName': 'webapp-security-group'
        }
    ]
)

db_subnet1 = vpc.create_subnet(
    AvailabilityZone='us-east-2a',
    CidrBlock='10.0.2.0/24'
)
db_subnet2 = vpc.create_subnet(
    AvailabilityZone='us-east-2b',
    CidrBlock='10.0.3.0/24'
)
db_subnet_group = create_subnet_group(
    'webapp-db-subnet-group',
    SubnetIds=[db_subnet1.id, db_subnet2.id]
)

rds_response = create_rds_instance('webapp-rds')

print(rds_response)




