import boto3


class KeyPair(object):
    """Wrapper class for handling AWS KeyPairs
    """

    def __init__(self, name, outfile=None):
        """

        Arguments:
        - `name`:
        - `outfile`:
        """
        self._name = name
        self._outfile = outfile
        self.resource = boto3.resource('ec2')

        self._initialize()

    def _exists(self):
        """
        """
        return self._name in [kp.name for kp in self.resource.key_pairs.all()]

    def _initialize(self):
        """
        """
        if self._exists():
            return

        key_pair = self.resource.create_key_pair(KeyName=self._name)
        if self._outfile:
            with open(self._outfile, 'w') as fp:
                fp.write(key_pair.key_material)
        else:
            print(key_pair.key_material)
