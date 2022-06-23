'''
Author: Tomer kigel (constructed and adjusted based on the work of Mrs. Maya Lavie)
Contact info: e-mail: tomer.kigel@gmail.com
              phone number: 0507650153
              github: https://github.com/TomerKigel
'''
import copy
import math

from Message import Message, MsgInitFromProvider

from Agent import Agent
from graphics import Point, Text
from utils import Calculate_Distance


class Provider(Agent):
    def __init__(self, id_, problem_id, skill_set, travel_speed=5):
        Agent.__init__(self, id_, problem_id)
        # Provider Variables
        self.skill_set = skill_set
        self.travel_speed = travel_speed
        self.skill_num = list(self.skill_set.keys())[0]
        self.time_invested = 0

        self.requester_service_times = {}

        self.incoming_setupmessages = []

        # Algorithm Results
        self.chosen_requester = 0
        self.chosen_requesters = []

        id_text = 0

    def full_reset(self):
        super().full_reset()
        # Algorithm results
        self.chosen_requester = 0

    def __str__(self):
        return "Provider " + Agent.__str__(self)

    def send_init_msg(self, agent_id : int):
        msg_init = MsgInitFromProvider(sender_id=self.id_,
                                       context=[copy.deepcopy(self.current_location),copy.deepcopy(self.skill_set),copy.deepcopy(self.travel_speed),copy.deepcopy(list(self.neighbor_data.keys())),self.time_invested,self.skill_num,],
                                       receiver_id=agent_id)
        self.outmessagebox.append(msg_init)

    def init_relationships(self):
        for message in self.incoming_setupmessages:
            self.requester_service_times[message.sender_id] = message.context

    def make_a_choice(self):
        raise NotImplementedError()
