'''
Author: Tomer kigel
Contact info: e-mail: tomer.kigel@gmail.com
              phone number: +972507650153
              github: https://github.com/TomerKigel
'''
import copy
import random
import string

import utils
from Message import MsgBeliefVector, MsgUtilityOffer, MsgInitFromProvider, MsgProviderChoice
from Requester import Requester
from utils import to_binary_list, prep_permutate


class MS_Requester(Requester):
    def __init__(self, id_, problem_id, skills_needed,max_skill_types, max_required={}, time_per_skill_unit={}, max_util=1000, max_time=10):
        super().__init__( id_, problem_id, skills_needed,max_skill_types, max_required, time_per_skill_unit, max_util, max_time)

        self.offer = {}
        self.util_message_data = {}
        self.relationship_health = {}
        self.internal_fmr = {}
        self.nclo = 0


    def full_reset(self) -> None:
        super().full_reset()
        self.offer = {}
        self.util_message_data = {}

    def reset_offers(self) -> None:
        for id in self.neighbor_data.keys():
            self.offer[id] = (0,0)
            self.relationship_health[id] = 1
            for elem in self.neighbor_data[id][3]:
                self.offer[id] = (0,0)

    def assemble_neighbour_assignments(self,skill,provider) -> dict:
        output = {}
        for neighbour in self.connections.keys():
            if neighbour in self.internal_fmr[skill] and provider != neighbour:
                output[neighbour] = []
                for key in self.neighbor_data[neighbour][3]:
                    output[neighbour].append(key)
        return output


    def create_value_table(self,provider : int,skill : int) -> list:
        assignments = self.assemble_neighbour_assignments(skill,provider)
        table = []
        keylist = list(assignments.keys())
        table.append(keylist)
        amount_of_lines = 1
        for neighbour in keylist:
            amount_of_lines *= 2
        permutation = utils.truth_table(keylist, amount_of_lines)
        for line in range (0,amount_of_lines):
            table.append(permutation[line])
            table[line+1].append(self.case_utility(table,line+1,skill))

        return table

    def case_utility(self,table : list[int],line : int,skill : int) -> int:
        index = 0
        providers_list = []
        for key in table[line]:
            if key == 1:
                providers_list.append(table[0][index])
            index += 1

        self.simulation_times_for_utility = self.construct_time_line(providers_list,skill)
        t_a_p = self.construct_skill_times(self.allocated_providers,True)
        self.simulation_times_for_utility = self.conjoin_simulation_times(t_a_p,self.simulation_times_for_utility)
        util = self.final_utility()
        return util

    def construct_time_line(self, providers_list : list ,skill : int) -> dict:
        list_of_arrivals = []
        index = 0
        for provider in providers_list:
            prov_location = self.neighbor_data[provider][0]
            prov_speed = self.neighbor_data[provider][2]
            arrival_time = (utils.Calculate_Distance(prov_location,self.current_location)/prov_speed) + self.neighbor_data[provider][-2]
            if skill == -1 or not skill in self.neighbor_data[provider][1]:
                list_of_arrivals.append((provider, (self.id_, arrival_time,self.neighbor_data[provider][-1])))
            elif self.neighbor_data[provider][1][skill] == 0:
                list_of_arrivals.append((provider, (self.id_, arrival_time,self.neighbor_data[provider][-1])))
            else:
                 list_of_arrivals.append((provider,(self.id_,arrival_time,skill)))
            index +=1
        return self.construct_skill_times(list_of_arrivals,False)

    def add_beliefs(self,table : list,provider : int,skill : int) -> list:
        agents_beliefs = {}
        for key in self.connections.keys():
            if key != provider:
                agents_beliefs[key] = self.message_data[key][1].context

        max_belief = {}
        for key in agents_beliefs.keys():
            max_belief[key] = 0
            for nkey in agents_beliefs.keys():
                if nkey != key:
                    for v in agents_beliefs[nkey].keys():
                        for j in agents_beliefs[nkey][v].keys():
                            if agents_beliefs[nkey][v][j] > max_belief[key]:
                                max_belief[key] = agents_beliefs[nkey][v][j]

        for i in range(1,len(table)):
            for elem in range(0,len(table[i])-1):
                if table[i][elem] == 1 and agents_beliefs[table[0][elem]]:
                    if skill in agents_beliefs[table[0][elem]][self.id_]:
                        table[i][-1] += agents_beliefs[table[0][elem]][self.id_][skill]
                else:
                    table[i][-1] += max_belief[table[0][elem]]
        return table

    def select_best_values(self,table : list) -> list:
        max_util = 0
        best_index = 0
        index = 0
        for line in table:
            if index == 0:
                index += 1
                continue
            else:
                if line[-1] >= max_util:
                    best_index = index
                    max_util = line[-1]
            index += 1

        return [table[best_index],table[0]]

    def open_mail(self) -> None:
        index = 0
        idnex_to_del = []
        for i in self.allocated_providers:
            if i[-1] == False:
                idnex_to_del.append(i)
            index+=1
        for i in idnex_to_del:
            self.allocated_providers.remove(i)

        for message in self.inmessagebox:
            if isinstance(message, MsgProviderChoice):
                if (message.sender_id,message.context,message.final) not in self.allocated_providers:
                    self.allocated_providers.append((message.sender_id,message.context,message.final))
            elif message.sender_id not in self.message_data.keys():
                self.message_data[message.sender_id] = [0,0]
            if isinstance(message, MsgInitFromProvider):
                self.message_data[message.sender_id][0] = message
            if isinstance(message, MsgBeliefVector):
                self.message_data[message.sender_id][1] = message

        self.inmessagebox.clear()
        if self.internal_fmr == {}:
            for skill in self.skill_set:
                self.internal_fmr[skill] = [i for i in self.connections]

    def update_nclo(self,table : list) -> None:
        if len(table) == 0:
            self.nclo += 0
        else:
            self.nclo += len(table) - 1

    def set_nclo(self,set_val) -> None:
        self.nclo = set_val

    def compute(self) -> None:
        self.open_mail()
        for provider in self.connections.keys():
            best_cases = {}
            for skill in self.skill_set:
                produced_table = self.create_value_table(provider,skill)
                if len(produced_table) > 1:
                    self.update_nclo(produced_table)
                    produced_table = self.add_beliefs(produced_table,provider,skill)
                    selected_case = self.select_best_values(produced_table)
                    best_cases[skill] = selected_case
            max_u = 0
            max_skill = 0
            for i in best_cases:
                if best_cases[i][0][-1] >= max_u:
                    max_u = best_cases[i][0][-1]
                    max_skill = i
            self.compile_offers(best_cases[max_skill],provider,max_skill)
        self.generate_result_messages()


    def send_offer_msg(self, neighbour: int) -> None:
        new_message = MsgUtilityOffer(self.id_, neighbour, self.offer[neighbour])
        self.outmessagebox.append(new_message)

    def generate_result_messages(self) -> None:
        for neighbour in self.neighbor_data.keys():
            self.send_offer_msg(neighbour)

    def compile_offers(self,selected_case : list,provider : int,skill) -> None:
        providers_list = []
        for i in range(0,len(selected_case[0])-1):
            if selected_case[0][i] == 1:
                providers_list.append(selected_case[1][i])
        self.simulation_times_for_utility = self.construct_time_line(providers_list, skill)
        before_assignment = self.final_utility()

        providers_list.append(provider)
        self.simulation_times_for_utility = self.construct_time_line(providers_list, skill)
        after_assignment  = self.final_utility()

        if after_assignment - before_assignment <= 0:
            calculated_offers = (0,skill)
        else:
            calculated_offers = (round(after_assignment - before_assignment,2),skill)

        self.offer[provider] = calculated_offers


    def calculate_required_utility(self) -> float:
        '''
        calculate overall maximal required utility
        :return: utility
        '''
        utility = 0
        for key in self.max_util.keys():
            utility += self.max_util[key]
        return utility


    def remove_neighbour(self, agent) -> None:
        '''
        remove neighbor and cleanup his data
        :param agent: agent id or reference
        '''
        super().remove_neighbour(agent)
        if type(agent) == int:
            if agent in self.offer.keys():
                del self.offer[agent]
        else:
            if agent.id_ in self.offer.keys():
                del self.offer[agent.id_]
        messages_to_remove = []
        for message in self.outmessagebox:
            if message.receiver_id not in self.connections.keys():
                messages_to_remove.append(message)
        for i in messages_to_remove:
            self.outmessagebox.remove(i)
        messages_to_remove.clear()
        for id in self.message_data:
            if id not in self.connections:
                messages_to_remove.append(id)
        for i in messages_to_remove:
            del self.message_data[i]


    def conjoin_simulation_times(self, t_a_p, simulation_times_for_utility) -> dict:
        '''
        Conjoins two times lines into one
        :param t_a_p: Source to append to destination
        :param simulation_times_for_utility: Destination
        :return: dict of dicts {skill : time : amount of agents }
        '''
        for key in simulation_times_for_utility.keys():
            index_times = 0
            sorted_times = list(simulation_times_for_utility[key].keys())
            sorted_times.sort()
            if sorted_times:
                for nkey in t_a_p[key].keys():
                    if nkey < sorted_times[index_times]:
                        t_a_p[key][nkey] += simulation_times_for_utility[key][sorted_times[index_times]]
                    else:
                        index_times+=1
                        if index_times >= len(sorted_times):
                            break

        dict_to_append = {}
        for key in simulation_times_for_utility.keys():
            for nkey in t_a_p[key].keys():
                if nkey not in simulation_times_for_utility[key]:
                    dict_to_append[nkey] = t_a_p[key][nkey]
        simulation_times_for_utility.update(dict_to_append)


        return simulation_times_for_utility

