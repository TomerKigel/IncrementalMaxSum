'''
Author: Tomer kigel (constructed and adjusted based on the work of Mrs. Maya Lavie)
Contact info: e-mail: tomer.kigel@gmail.com
              phone number: 0507650153
              github: https://github.com/TomerKigel
'''
class Message(object):  # standard message
    def __init__(self, sender_id, receiver_id):
        self.sender_id = sender_id
        self.receiver_id = receiver_id

class MsgInitFromProvider(Message):
    def __init__(self, sender_id, receiver_id,context):
        Message.__init__(self, sender_id=sender_id, receiver_id=receiver_id)
        self.context = context
    def __str__(self):
        return "Init msg from Provider: " + str(self.sender_id) + " to " + str(self.receiver_id) + ": " + str(self.context)

class MsgInitFromRequster(Message):
    def __init__(self, sender_id, receiver_id,context):
        Message.__init__(self, sender_id=sender_id, receiver_id=receiver_id)
        self.context = context
    def __str__(self):
        return "Init msg from requester: " + str(self.sender_id) + " to " + str(self.receiver_id) + ": " + str(self.context)

class MsgBeliefVector(Message):
    def __init__(self, sender_id, receiver_id, context):
        Message.__init__(self, sender_id=sender_id, receiver_id=receiver_id)
        self.context = context
    def __str__(self):
        return "Belief Vector Msg from provider " + str(self.sender_id) + " to " + str(self.receiver_id) + ": " + str(self.context)


class MsgUtilityOffer(Message):
    def __init__(self, sender_id, receiver_id, context):
        Message.__init__(self, sender_id=sender_id, receiver_id=receiver_id)
        self.context = context
    def __str__(self):
        return "Utility offer Msg from requester " + str(self.sender_id) + " to " + str(self.receiver_id) + ": " + str(self.context)


class MsgProviderChoice(Message):
    def __init__(self, sender_id, receiver_id,context,final):
        Message.__init__(self, sender_id=sender_id, receiver_id=receiver_id)
        self.context = context
        self.final = final

    def __str__(self):
        return "Choice Msg from provider " + str(self.sender_id) + " to " + str(self.receiver_id)
