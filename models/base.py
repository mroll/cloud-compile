class ResourceGroup:
    def __init__(self, name, resources=[]):
        self.name = name
        self.resources = resources

    def to_json(self):
        return {resource.name: resource.to_json() for resource in self.resources}


class CidrBlockMixin(object):
    def __init__(self, **kwargs):
        self.CidrBlock = kwargs.pop('cidrblock', '10.0.0.0/16')

        super().__init__(**kwargs)


class VpcResourceMixin:
    def __init__(self, **kwargs):
        self.VpcId = kwargs.pop('vpcid', None)

        super().__init__(**kwargs)


class AwsResourceMixin:
    def __init__(self, **kwargs):
        self.name = kwargs.pop('name', None)

        super().__init__(**kwargs)


