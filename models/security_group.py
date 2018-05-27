import boto3

from .util import tag, tagged_resource


class IpPermission:
    possible_fields = [
        'FromPort',
        'ToPort',
        'IpProtocol',
        'IpRanges',
        'Ipv6Ranges',
        'PrefixListIds',
        'UserIdGroupPairs',
    ]

    def __init__(self, **kwargs):
        for arg in kwargs:
            if arg in IpPermission.possible_fields:
                setattr(self, arg, kwargs[arg])

    def __eq__(self, other):
        for field in IpPermission.possible_fields:
            if hasattr(self, field) and hasattr(other, field):
                if not getattr(self, field) == getattr(other, field):
                    return False
            elif hasattr(self, field) and not hasattr(other, field):
                return False
            elif not hasattr(self, field) and hasattr(other, field):
                return False

        return True

    def to_dict(self):
        return {
            field: getattr(self, field)
            for field in IpPermission.possible_fields
            if hasattr(self, field)
        }


class SecurityGroup:
    def __init__(self, name, vpc_id, ingress_rules=[], egress_rules=[], desc='default description'):
        self.name = name
        self.vpc_id = vpc_id
        self.ingress_rules = [IpPermission(**rule) for rule in ingress_rules]
        self.egress_rules = [IpPermission(**rule) for rule in egress_rules]
        self.description = desc
        self.resource = boto3.resource('ec2')
        self.sg = None

        self._initialize()

    @property
    def resource_id(self):
        return self.sg.id

    def _get_resource_reference(self):
        return tagged_resource(
            self.resource.security_groups.all(),
            ('Name', self.name)
        )

    def _exists(self):
        return self._get_resource_reference() is not None

    def _revoke_obsolete_ingress_rules(self):
        for ingress_rule in self.sg.ip_permissions:
            ir = IpPermission(**ingress_rule)
            if ir not in self.ingress_rules:
                self.sg.revoke_ingress(IpPermissions=[ir.to_dict()])

    def _revoke_obsolete_egress_rules(self):
        for egress_rule in self.sg.ip_permissions_egress:
            er = IpPermission(**egress_rule)
            if er not in self.egress_rules:
                self.sg.revoke_egress(IpPermissions=[er.to_dict()])

    def _initialize(self):
        if not self._exists():
            self.sg = self.resource.create_security_group(
                GroupName=self.name,
                VpcId=self.vpc_id,
                Description=self.description
            )
            tag(self.sg, ('Name', self.name))
        else:
            self.sg = self._get_resource_reference()

        self._revoke_obsolete_ingress_rules()
        self._revoke_obsolete_egress_rules()

        for ingress_rule in self.ingress_rules:
            self.sg.authorize_ingress(IpPermissions=[ingress_rule.to_dict()])

        for egress_rule in self.egress_rules:
            self.sg.authorize_egress(IpPermissions=[egress_rule.to_dict()])

        return self.sg
