from core.serializers import *

class Command:
    def __init__(self, issuing_user, **kwargs):
        self.issuing_user = issuing_user
        self.data = kwargs
        self._setup()

    def _setup():
        pass

    def is_valid(self):
        return True

    def execute(self):
        raise Exception("override execute to make your command do something")

# class CommandSuccess:
#     pass
#
# class CommandFailed:
#     pass

class AddAvailabilityChange(Command):
    def _setup(self):
        self.deserialized_model = AvailabilitySerializer(data=self.data)

    def is_valid(self):
        return self.deserialized_model.is_valid()

    # TODO: Change this to use a success object from execute
    def success_data(self):
        return self.deserialized_model.data

    # TODO: Change this to use a failure object from execute
    def errors(self):
        return self.deserialized_model.errors

    def execute(self):
        return self.deserialized_model.save()
        #     return CommandSuccess(self.deserialized_model.data)
        # else
        #     return CommandFailed(reason = "You suck")



# AddAvailabiltyChange(start_date = "2016-10-03", quantity)
