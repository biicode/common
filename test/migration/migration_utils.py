from biicode.common.migrations.migration import Migration
from mock import Mock


class TMigration(Migration):

    def __init__(self):
        super(TMigration, self).__init__()
        self.migrate = Mock()


class TMigration1(TMigration):

    def __init__(self):
        super(TMigration1, self).__init__()


class TMigration2(TMigration):
    def __init__(self):
        super(TMigration2, self).__init__()


class TMigration3(TMigration):
    def __init__(self):
        super(TMigration3, self).__init__()
