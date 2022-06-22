import copy
import math
import random
import time

import Agent
import utils
from Message import Message, MsgUtilityOffer, MsgBeliefVector, MsgInitFromRequster, MsgProviderChoice
from Provider import Provider





class MS_Provider(Provider):
    def __init__(self, id_, problem_id, skill_set, travel_speed=5):
        super().__init__(id_, problem_id, skill_set, travel_speed)
        self.Belief = {}
        self.incoming_utility_messages = []
        self.mistake_probability = 0

        self.After_fmr = 0
        self.cur_iter_fmr = False


    def advance_time_via_choice(self):
        if self.chosen_requester != 0 and self.chosen_requester != None:
            self.graphic.move(self.total_connections[self.chosen_requester[0]][0] - self.current_location[0] , self.total_connections[self.chosen_requester[0]][1] - self.current_location[1])
            self.id_text.move(self.total_connections[self.chosen_requester[0]][0] - self.current_location[0] , self.total_connections[self.chosen_requester[0]][1] - self.current_location[1])
            self.time_invested += utils.Calculate_Distance(self.total_connections[self.chosen_requester[0]],self.current_location) / self.travel_speed
            orig_investment = copy.copy(self.time_invested)
            self.current_location = copy.deepcopy(self.total_connections[self.chosen_requester[0]])
            if self.skill_num in self.requester_service_times[self.chosen_requester[0]]:
                self.time_invested += self.requester_service_times[self.chosen_requester[0]][self.skill_num]

            if self.skill_num in self.skill_set and self.time_invested - orig_investment != 0:
                self.skill_set[self.skill_num] -=1
                if self.skill_set[self.skill_num] == 0:
                    del self.skill_set[self.skill_num]

            self.chosen_requesters.append(self.chosen_requester)

    def up_mistake(self):
        self.mistake_probability = 0.3

    def reconstruct_choice(self,choice):
        self.chosen_requester = choice

    def up_fmr(self):
        if not self.cur_iter_fmr:
            self.After_fmr += 1
            self.cur_iter_fmr = True

    def full_reset(self):
        super().full_reset()
        self.Belief = {}
        self.incoming_utility_messages = []
        self.mistake_probability = 0
        self.cur_iter_fmr = False
        for key in self.neighbor_util.keys():
            self.Belief[key] = {}
            for skill in self.skill_set:
                self.Belief[key][skill] = 0
        keys_to_del = []
        for key in self.Belief.keys():
            if key not in self.connections.keys():
                keys_to_del.append(key)
        for key in keys_to_del:
            del self.Belief[key]

    def open_mail(self):
        for massage in self.inmessagebox:
            if isinstance(massage,MsgUtilityOffer):
                self.incoming_utility_messages.append(massage)
            if isinstance(massage, MsgInitFromRequster):
                self.incoming_setupmessages.append(massage)
            # add other messages handling here
        self.inmessagebox.clear()

    def compute(self):
        self.open_mail()
        self.update_belief()
        self.normalize_belief_vector()
        self.make_a_choice()
        self.generate_result_messages()

    def send_belief_msg(self, requester_id: int) -> None:
        msg = MsgBeliefVector(self.id_,requester_id,self.Belief)
        self.outmessagebox.append(msg)

    def generate_result_messages(self):
        for neighbour in self.neighbor_data.keys():
            self.send_belief_msg(neighbour)

    def reset_belief(self):
        for key in self.neighbor_util.keys():
            self.Belief[key] = {}
            for skill in self.skill_set:
                self.Belief[key][skill] = 0


    def update_belief(self):
        # damping
        for key in self.Belief.keys():
            for nkey in self.Belief[key]:
                self.Belief[key][nkey] *= 0.2
        #update
        res = {}
        for offer_dict in self.incoming_utility_messages:
                if offer_dict.sender_id in self.Belief.keys():
                    if random.random() > 1 - self.mistake_probability:
                        offer_dict.sender_id = random.sample(list(self.Belief.keys()),1)[0]
                    if offer_dict.context[1] in self.Belief[offer_dict.sender_id]:
                        self.Belief[offer_dict.sender_id][offer_dict.context[1]] += offer_dict.context[0] * 0.8

        self.incoming_utility_messages.clear()


    def normalize_belief_vector(self):
        if not self.Belief:
            return
        min_value = 100000
        for value in self.Belief.values():
            for val in value:
                if val < min_value:
                    min_value = val
        for key in self.Belief.keys():
            for nkey in self.Belief[key]:
                if self.Belief[key][nkey] >= min_value:
                    self.Belief[key][nkey] -= min_value

    def make_a_choice(self):
        self.chosen_requester = 0
        if self.Belief and self.connections and self.skill_set:
            best_choice = None
            max_util = 0
            for key in self.connections.keys():
                for nkey in self.Belief[key]:
                    if self.Belief[key][nkey] >= max_util:
                        max_util = self.Belief[key][nkey]
                        best_choice = [key,nkey]

            if best_choice != None:
                expected_time = utils.Calculate_Distance(self.connections[best_choice[0]],self.current_location) / self.travel_speed
                chosen_requester = (best_choice[0],expected_time+self.time_invested,best_choice[1])
                self.chosen_requester = chosen_requester
                self.skill_num = best_choice[1]
                if self.skill_num not in self.skill_set:
                    self.skill_num = -1


            if self.skill_num != -1:
                    if self.chosen_requester != 0:
                        Choice = MsgProviderChoice(self.id_,chosen_requester[0],chosen_requester,False)
                        self.outmessagebox.append(Choice)
            else:
                self.chosen_requester = None

        for element in self.chosen_requesters:
            Choice = MsgProviderChoice(self.id_, element[0], element,True)
            self.outmessagebox.append(Choice)





    def remove_neighbour(self, agent) -> None:
        super().remove_neighbour(agent)
        if type(agent) == int:
            if agent in self.Belief.keys():
                del self.Belief[agent]
        else:
            if agent.id_ in self.Belief.keys():
                del self.Belief[agent.id_]
        messages_to_remove = []
        for message in self.outmessagebox:
            if message.receiver_id not in self.neighbor_data.keys():
                messages_to_remove.append(message)
        for i in messages_to_remove:
            self.outmessagebox.remove(i)
        messages_to_remove.clear()
        for id in self.message_data:
            if id not in self.neighbor_data:
                messages_to_remove.append(id)
        for i in messages_to_remove:
            del self.message_data[i]


