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
        self.utility_budget = 0
        for i in max_util.keys():
            self.utility_budget+= max_util[i]
        self.current_budget = self.utility_budget
        self.offer_already_compiled = False

        self.max_util = max_util
        self.time_per_skill_unit = time_per_skill_unit
        self.max_time = max_time
        self.rate_util_fall = rate_util_fall

        self.required_utility = self.calculate_required_utility()

        # Algorithm results
        self.allocated_providers = []

        self.bo = False
        id_text = 0


    def full_reset(self):
        super().full_reset()
        # Algorithm results
        self.allocated_providers = []
        self.current_budget = self.utility_budget
        self.offer_already_compiled = False

    def __str__(self):
        return "Requester " + Agent.__str__(self)

    def reset(self):
        self.reset_termination()
        self.reset_util_j()

    def reset_budget(self):
        self.current_budget = self.utility_budget

    def turn_update_on(self):
        self.bo = True

    def final_utility_orig(self):
        if self.bo:
            self.simulation_times_for_utility = self.construct_skill_times(self.allocated_providers,True)
            self.reducing_final_Utility()
            self.bo = False
        self.simulation_times_for_utility = self.construct_skill_times(self.allocated_providers,False)
        return self.final_utility()


    def calculate_utility_of_agent(self,provider_id : int) -> float:
            return self.original_util[provider_id]

    def calculate_final_utility_of_agent(self,pid ,provider_tuple : tuple) -> float:
            return self.update_utility_normal(pid,provider_tuple[1])

    def update_utility_normal(self,id : int, Expected_Arrival_time : int):
            res = 0
            for skill in self.skill_set.keys():
                best_util_received = 0
                if skill in self.neighbor_data[id][1].keys():
                    skill_amount_needed = self.skill_set[skill]
                    amount_neighbor_skill = self.neighbor_data[id][1][skill]
                    if amount_neighbor_skill > skill_amount_needed:
                         amount_neighbor_skill = copy.deepcopy(skill_amount_needed)
                    rate_of_util_fall = ((- self.max_util[skill] / self.rate_util_fall) / self.max_time)
                    util_available = self.max_util[skill] + rate_of_util_fall * Expected_Arrival_time
                    if util_available < 0:
                        util_available = 0
                    if skill_amount_needed != 0:
                        best_util_received = util_available * (amount_neighbor_skill / skill_amount_needed)
                    else:
                        best_util_received = 0
                    res = res + round(best_util_received, 2)
            return res


    def send_init_msg(self, agent_id):
        msg_init = MsgInitFromRequster(sender_id=self.id_, context=self.time_per_skill_unit,
                                           receiver_id=agent_id)
        self.outmessagebox.append(msg_init)

    def init_relationships(self):
        for message in self.message_data.values():
                self.neighbor_data[message[0].sender_id] = message[0].context
                # Distance = Calculate_Distance(message[0].context[0],self.current_location) #position
                # Speed =  message[0].context[2]
                # Expected_time = Distance/Speed
                # skills = 0
                # for key,value in message[0].context[1].items():
                #     if key in self.skill_set:
                #         if Expected_time < self.time_per_skill_unit[key]:
                #             skills += min(value, self.skill_set[key])
                util =0
                for i in self.neighbor_data[message[0].sender_id][1].keys():
                    if i in self.max_util.keys():
                        util += self.neighbor_data[message[0].sender_id][1][i] * self.max_util[i]
                self.neighbor_util[message[0].sender_id] = util# self.update_utility_normal(message[0].sender_id,Expected_time)
                self.original_util[message[0].sender_id] = self.neighbor_util[message[0].sender_id]

    def calculate_required_utility(self):
        raise NotImplementedError()


    #def construct_skill_times(self):
    # def construct_skill_times(self,providers,final):
    #     res = {}
    #     for key in self.skill_set.keys():
    #         res[key] = {}
    #
    #
    #     if providers:
    #         times_per_neighbor = {}
    #         for provider in providers:
    #             if final == True:
    #                 if provider[-1] == False:
    #                     continue
    #             times_per_neighbor[provider[0]] = [0 for i in range(self.max_skill_types+1)]
    #
    #             orig = provider[1][1]
    #             for key in self.skill_set.keys():
    #                 if key == provider[1][-1]:
    #                     times_per_neighbor[provider[0]][key] = orig
    #                     orig += self.time_per_skill_unit[key] # self.neighbor_data[provider[0]][1][key] *
    #                 else:
    #                     times_per_neighbor[provider[0]][key] = '-'
    #             times_per_neighbor[provider[0]][self.max_skill_types] = orig
    #
    #         start_finish = {}
    #         timeline = {}
    #         for key in self.skill_set.keys():
    #             start_finish[key] = []
    #             timeline[key] = []
    #             for i in times_per_neighbor.keys():
    #                 if times_per_neighbor[i][key] != '-':
    #                     timeline[key].append(times_per_neighbor[i][key])
    #                     start = times_per_neighbor[i][key]
    #                     minval = 10000
    #                     index = times_per_neighbor[i][-1]
    #                     for j in range(0, len(times_per_neighbor[i])):
    #                         if times_per_neighbor[i][j] == '-':
    #                             continue
    #                         if times_per_neighbor[i][j] > start and times_per_neighbor[i][j] < minval:
    #                             minval = times_per_neighbor[i][j]
    #                             index = j
    #
    #                     finish = times_per_neighbor[i][index]
    #                     timeline[key].append(times_per_neighbor[i][index])
    #                     start_finish[key].append((start, finish))
    #
    #         for timel in timeline.keys():
    #             # timeline[timel].append(0)
    #             timeline[timel] = sorted(timeline[timel])
    #             start_finish[timel] = sorted(start_finish[timel])
    #
    #         for timel in timeline.keys():
    #             for j in range(0, len(timeline[timel])):
    #                 res[timel][timeline[timel][j]] = 0
    #
    #             for i in start_finish[timel]:
    #                 keep = False
    #                 for j in range(0, len(timeline[timel])):
    #                     if timeline[timel][j] == i[0]:
    #                         keep = True
    #                         res[timel][timeline[timel][j + 1]] += 1
    #                     elif timeline[timel][j] == i[1]:
    #                         keep = False
    #                     elif keep:
    #                         res[timel][timeline[timel][j + 1]] += 1
    #
    #     return res


    def construct_skill_times(self, providers, final):
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
                    work_time = provider[1][-1]
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

        #         times_per_neighbor[skill] = (self.neighbor_data[neighbour][1])
        # for provider in self.allocated_providers:
        #     pass

    def reducing_final_Utility(self):
        all_util = 0
        util_per_point = {}
        for skill in self.skill_set.keys():
            if self.skill_set_for_calcs[skill] != 0:
                util_per_point[skill] = self.max_util_for_calcs[skill] / self.skill_set_for_calcs[skill]
            else:
                util_per_point[skill] = 0

        for skill, amount_needed in self.skill_set_for_calcs.items():
            skills_complete = 0
            if skill in self.simulation_times_for_utility.keys():
                rate_of_util_fall = ((- self.max_util_for_calcs[skill] / self.rate_util_fall) / self.max_time)
                util_available = self.max_util_for_calcs[skill]
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
                        if amount_needed != 0:
                            util = util_available * (skills_complete / amount_needed) * cap_multiplier
                        else:
                            util = 0
                        util_received += util
                        if total_amount_complete >= amount_needed:
                            break
                    last_time = time

                    if time > self.max_time:
                        break

                all_util += util_received


                self.skill_set_for_calcs[skill] -= skills_complete
                self.max_util_for_calcs[skill] -= util_per_point[skill]*skills_complete
            # print("req", self.id_, "skill ", skill, "utility ", util_received)

        if all_util < 0:
            return 0

        return round(all_util, 2)

    def final_utility_for_calcs(self):
        all_util = 0
        for skill, amount_needed in self.skill_set_for_calcs.items():
            if amount_needed == 0:
                continue
            if skill in self.simulation_times_for_utility.keys():
                rate_of_util_fall = ((- self.max_util_for_calcs[skill] / self.rate_util_fall) / self.max_time)
                util_available = self.max_util_for_calcs[skill]
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
            #print("req", self.id_, "skill ", skill, "utility ", util_received)

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
            #print("req", self.id_, "skill ", skill, "utility ", util_received)

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
