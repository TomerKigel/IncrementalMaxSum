import copy
import math
from random import random

from sympy import symbols, Eq, solve

from Agent import Agent
from Message import Message, MsgUtilityOffer, MsgInitFromRequster, MsgInitFromProvider
from graphics import color_rgb, Point, Text

from utils import Calculate_Distance


class Requester(Agent):
    def __init__(self, id_, problem_id, skills_needed,max_skill_types, max_required={}, time_per_skill_unit={}, max_util=1000, max_time=10, rate_util_fall = 5):
        Agent.__init__(self, id_, problem_id)

        # Requester variables
        self.max_required = max_required
        self.skill_set = skills_needed
        self.skill_set_for_calcs = copy.deepcopy(skills_needed)
        self.max_util_for_calcs = copy.deepcopy(max_util)

        self.original_util = {}
        self.simulation_times_for_utility = {}
        self.max_skill_types = max_skill_types

        skills_sum = 0
        for skill in self.skill_set:
            skills_sum += skill

        self.offer_already_compiled = False

        self.max_util = max_util

        self.skill_unit_value = {}
        for key in self.skill_set.keys():
            self.skill_unit_value[key] = self.max_util[key] / self.skill_set[key]


        self.time_per_skill_unit = time_per_skill_unit
        self.max_time = max_time
        self.rate_util_fall = rate_util_fall

        self.required_utility = self.calculate_required_utility()

        # Algorithm results
        self.allocated_providers = []

        self.bo = False
        id_text = 0

    def __str__(self):
        return "Requester " + Agent.__str__(self)

    def reset(self):
        self.reset_termination()
        self.reset_util_j()


    def final_utility_orig(self):
        self.simulation_times_for_utility = self.construct_skill_times(self.allocated_providers,False)
        return self.final_utility()


    def send_init_msg(self, agent_id):
        msg_init = MsgInitFromRequster(sender_id=self.id_, context=self.time_per_skill_unit,
                                           receiver_id=agent_id)
        self.outmessagebox.append(msg_init)

    def init_relationships(self):
        for message in self.message_data.values():
                self.neighbor_data[message[0].sender_id] = message[0].context
                util = 0
                for i in self.neighbor_data[message[0].sender_id][1].keys():
                    if i in self.max_util.keys():
                        util += self.neighbor_data[message[0].sender_id][1][i] * self.skill_unit_value[i]
                self.neighbor_util[message[0].sender_id] = util
                self.original_util[message[0].sender_id] = self.neighbor_util[message[0].sender_id]

    def construct_skill_times(self, providers, final ):
        res = {}
        for key in self.skill_set.keys():
            res[key] = {}

        timeLine = {}
        start_finish = {}
        for key in self.skill_set.keys():
            timeLine[key] = []
            start_finish[key] = []

        if providers:
            for provider in providers:
                if final == True:
                    if provider[-1] == False:
                        continue
                start = provider[1][1]
                work_time = 0
                if provider[1][-1] in self.time_per_skill_unit.keys():
                    work_time = self.time_per_skill_unit[provider[1][-1]]
                finish = provider[1][1]+work_time
                if start == finish:
                    continue
                timeLine[provider[1][-1]].append(provider[1][1])
                timeLine[provider[1][-1]].append(provider[1][1]+work_time)
                start_finish[provider[1][-1]].append((start, finish))

        for key in timeLine.keys():
            timeLine[key].sort()
            for j in range(0, len(timeLine[key])):
                res[key][timeLine[key][j]] = 0

        for timel in timeLine.keys():
            for i in start_finish[timel]:
                keep = False
                for j in range(0, len(timeLine[timel])):
                    if timeLine[timel][j] == i[0]:
                        keep = True
                        res[timel][timeLine[timel][j + 1]] += 1
                    elif timeLine[timel][j] == i[1]:
                        keep = False
                    elif keep:
                        res[timel][timeLine[timel][j + 1]] += 1



        return res


    def final_utility(self):
        all_util = 0
        for skill, amount_needed in self.skill_set.items():
            if amount_needed == 0:
                continue
            if skill in self.simulation_times_for_utility.keys():
                rate_of_util_fall = ((- self.max_util[skill] / self.rate_util_fall) / self.max_time)
                util_available = self.max_util[skill]
                util_received = 0
                last_time = 0
                total_amount_complete = 0
                for time, amount_working in self.simulation_times_for_utility[skill].items():
                    time_elapsed = time - last_time
                    skills_complete = min(amount_needed - total_amount_complete,
                                          time_elapsed / self.time_per_skill_unit[skill])

                    if amount_working == 0:  # no service given in this time frame - util is lost
                        util_available += rate_of_util_fall * time_elapsed
                    else:  # service is given in this time frame - util is not lost
                        total_amount_complete += skills_complete
                        cap_multiplier = self.cap(amount_working, self.max_required[skill])
                        util = util_available * (skills_complete / amount_needed) * cap_multiplier
                        util_received += util
                        if total_amount_complete >= amount_needed:
                            break
                    last_time = time

                    if time > self.max_time:
                        break

                all_util += util_received

        if all_util < 0:
            return 0

        x = int((all_util/self.required_utility) * 254)
        if x > 255:
            x = 255
        if x < 0:
            x = 0
        cl = color_rgb(255-x,255,255-x)
        self.graphic.setFill(cl)

        return round(all_util, 2)


    def cap(self,team, max_required):
        # linear
        if team == 0:
            return 0

        if team >= max_required:
            return 1

        rate = 0.5 / (max_required - 1)
        cap_outcome = 0.5 + rate * (team - 1)

        return cap_outcome
