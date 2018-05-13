from models.base import ResourceGroup
from models.vpc import (DHCPOptions, InternetGateway, NetworkAcl, RouteTable,
                        Subnet, Vpc)

rg = ResourceGroup(name='rg1')

vpc = Vpc(name='vpc1')

subnet1 = Subnet(name='subnet1', vpcid=vpc.name, cidrblock='10.0.0.0/24')
subnet2 = Subnet(name='subnet2', vpcid=vpc.name, cidrblock='10.0.0.1/24')
subnet3 = Subnet(name='subnet3', vpcid=vpc.name, cidrblock='10.0.0.2/24')

ig1 = InternetGateway(name='ig1')

dopt1 = DHCPOptions()

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

print(rg.__dict__)

for resource in rg.resources:
    print(resource.to_json())
