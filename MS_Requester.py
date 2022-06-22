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
        self.mistake_probability = 0.1
        self.internal_fmr = {}
        for skill in self.skill_set:
            self.internal_fmr[skill] = []


    def full_reset(self):
        super().full_reset()
        self.offer = {}
        self.util_message_data = {}
        self.mistake_probability = 0.1


    def reset_offers(self):
        for id in self.neighbor_data.keys():
            self.offer[id] = (0,0)
            self.relationship_health[id] = 1
            for elem in self.neighbor_data[id][3]:
                self.offer[id] = (0,0)

    def assemble_neighbour_assignments(self):
        output = {}
        for neighbour in self.connections.keys():
            output[neighbour] = []
            for key in self.neighbor_data[neighbour][3]:
                output[neighbour].append(key)
        return output


    def create_value_table(self,provider) -> list:
        assignments = self.assemble_neighbour_assignments()
        table = []
        keylist = list(assignments.keys())
        keylist.remove(provider)
        table.append(keylist)
        amount_of_lines = 1
        for neighbour in keylist:
            amount_of_lines *= 2
        permutation = utils.truth_table(keylist, amount_of_lines)
        for line in range (0,amount_of_lines):
            table.append(permutation[line])
            table[line+1].append(self.case_utility(table,line+1,"marginal utility"))

        return table

    def case_utility(self,table : list[int],line : int,policy : string) -> int:
        util = 0
        if policy == "marginal utility":
            pass
        else:
            pass
        index = 0
        providers_list = []
        for key in table[line]:
            if key == 1:
                providers_list.append(table[0][index])
            index += 1
        res = {}
        for skill in self.skill_set:
            self.simulation_times_for_utility = self.construct_time_line(providers_list,skill)
            t_a_p = self.construct_skill_times(self.allocated_providers,True)
            self.simulation_times_for_utility = self.conjoin_simulation_times(t_a_p,self.simulation_times_for_utility)
            util = self.final_utility()
            res[skill] = [util,skill]
        return res

    def ovp(self):
        curerent_util = 0
        for key in self.neighbor_util.keys():
            curerent_util += self.neighbor_util[key]

        diff = 0
        if curerent_util > self.required_utility:
            diff = curerent_util - self.required_utility
        for key in self.neighbor_util.keys():
            self.neighbor_util[key] -= diff / len(self.neighbor_util)

    def construct_time_line(self, providers_list,skill):
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

    def add_beliefs(self,table : list,provider):
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
                    for skill_num in self.skill_set:
                        if skill_num in agents_beliefs[table[0][elem]][self.id_]:
                            table[i][-1][skill_num][0] += agents_beliefs[table[0][elem]][self.id_][skill_num]
                else:
                    for skill_num in self.skill_set:
                            table[i][-1][skill_num][0] += max_belief[table[0][elem]]
        return table

    def remove_belief(self,table : list,provider):

        gtable = copy.deepcopy(table)
        agents_beliefs = {}
        for key in self.connections.keys():
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
                if gtable[0][elem] == provider:
                    if gtable[i][elem] == 1 and agents_beliefs[gtable[0][elem]]:
                        for skill_num in self.skill_set:
                            if skill_num in agents_beliefs[gtable[0][elem]][self.id_]:
                                gtable[i][-1][skill_num][0] -= agents_beliefs[gtable[0][elem]][self.id_][skill_num]
                    else:
                        for skill_num in self.skill_set:
                            if skill_num in agents_beliefs[gtable[0][elem]][self.id_]:
                                gtable[i][-1][skill_num][0] -= max_belief[gtable[0][elem]]
        return gtable

    def select_best_values(self,table : list,provider : int) -> list:
        # provider_index = 0
        # idx = 0
        # for i in table[0]:
        #     if i == provider:
        #         provider_index = idx
        #     idx +=1

        max_util = 0
        best_index = 0
        index = 0
        best_skill = -1
        for line in table:
            if index == 0:
                index += 1
                continue
            else:
                for item in line[-1].values():
                    if item[0] >= max_util:
                        best_index = index
                        best_skill = item[1]
                        max_util = item[0]
            index += 1

        # multip = 1
        # for i in range(len(table[0])-provider_index-1):
        #     multip *= 2
        # if table[best_index][provider_index] == 0:
        #     multip *= -1
        # best_alternative_index = best_index - multip
        #return [table[best_alternative_index],table[best_index],table[0],best_skill]
        return [table[best_index],table[0],best_skill]

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

    def compute(self):
        self.open_mail()
        self.nclo = len(self.connections) * len(self.connections)
        for provider in self.connections.keys():
            produced_table = self.create_value_table(provider)
            produced_table = self.add_beliefs(produced_table,provider)
            #produced_table = self.remove_belief(produced_table,provider)
            selected_case = self.select_best_values(produced_table,provider)
            self.compile_offers(selected_case,provider)
            self.send_offer_msg(provider)

    def send_offer_msg(self, neighbour: int) -> None:
        new_message = MsgUtilityOffer(self.id_, neighbour, self.offer[neighbour])
        self.outmessagebox.append(new_message)

    def generate_result_messages(self):
        for neighbour in self.neighbor_data.keys():
            self.send_offer_msg(neighbour)

    def compile_offers(self,selected_case : list,provider : int):
        # case_index = 0
        # for i in selected_case[2]:
        #     if i == provider:
        #         break
        #     case_index+=1
        if selected_case[-1] == -1:
            return
        providers_list = []
        for i in range(0,len(selected_case[0])-1):
            if selected_case[0][i] == 1:
                providers_list.append(selected_case[1][i])
        self.simulation_times_for_utility = self.construct_time_line(providers_list, selected_case[-1])
        before_assignment = self.final_utility()

        providers_list.append(provider)
        self.simulation_times_for_utility = self.construct_time_line(providers_list, selected_case[-1])
        after_assignment  = self.final_utility()

        if after_assignment - before_assignment <= 0:
            calculated_offers = (0,selected_case[-1])
        else:
            # agents_belief = self.message_data[provider][1].context
            # if selected_case[-1] in agents_belief:
            calculated_offers = (1*(after_assignment - before_assignment),selected_case[-1] )
            # else:
            #     calculated_offers = (0.1*(selected_case[0][-1][selected_case[-1]][0]) ,selected_case[-1])

        # diff = selected_case[1][-1][selected_case[-1]][0] - selected_case[0][-1][selected_case[-1]][0]
        # if diff > 0 and selected_case[1][case_index] == 1:
        #     calculated_offers = (0.1*selected_case[1][-1][selected_case[-1]][0] ,selected_case[1][-1][selected_case[-1]][1])
        # else:
        #     calculated_offers = (0,selected_case[1][-1][selected_case[-1]][1])
        self.offer[provider] = calculated_offers

    def calculate_required_utility(self):
        utility = 0
        for key in self.max_util.keys():
            utility += self.max_util[key]
        return utility

    def remove_neighbour(self, agent) -> None:
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

    def conjoin_simulation_times(self, t_a_p, simulation_times_for_utility):
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

