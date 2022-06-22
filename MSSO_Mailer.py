import copy
import random
from functools import cmp_to_key
from typing import Any

import utils
from MS_Provider import MS_Provider
from Mailer import Mailer
from Problem import Problem
from Provider import Provider
from Requester import Requester
from utils import Calculate_Distance


class MSSO_Mailer(Mailer):
    def __init__(self,problem : Problem, max_iterations : int,dist_thresh : float):
        super().__init__(problem,max_iterations)
        self.assignments_per_iteration = []
        self.dist_tresh = dist_thresh
        self.req = 0
        self.total_nclos = 0


    def initiate(self) -> None:
        #send initial messages from all(providers) to all (requesters) and visa versa
        for requester in self.Requesters.values():
            for neighbour in requester.neighbor_data.keys():
                requester.send_init_msg(neighbour)
        for provider in self.Providers.values():
            for neighbour in provider.neighbor_data.keys():
                provider.send_init_msg(neighbour)

        self.send_providers_messages()
        self.send_requesters_messages()

        #after all mail recieved open mail
        for requester in self.Requesters.values():
            requester.open_mail()
            requester.init_relationships()
            requester.reset_offers()
        for provider in self.Providers.values():
            provider.open_mail()
            provider.init_relationships()
            provider.generate_result_messages()
            provider.reset_belief()


        for requester in self.Requesters.values():
                self.fmr(requester)

        for provider in self.Providers.values():
            provider.reset_belief()
            for neighbour in provider.neighbor_data.keys():
                provider.send_init_msg(neighbour)
        self.send_providers_messages()
        for requester in self.Requesters.values():
            requester.open_mail()
            requester.init_relationships()
            requester.ovp()
            requester.reset_offers()


    def fmr(self ,requester : Requester) -> None:
        '''
           gets a requester and returns a list of neighbours to detach
           :param requester: the agent we want to apply fmr on
           :return list: a list of neighbours to detach
        '''
        self.req = requester
        neighbours_sorted = sorted(requester.neighbor_util.items(), key=cmp_to_key(self.heuristic_function))
        for skill in self.req.skill_set:
            selected_providers = []
            for i in self.req.allocated_providers:
                selected_providers.append(i[0])
            for provider_tuple in neighbours_sorted:
                requester.simulation_times_for_utility = requester.construct_time_line(selected_providers, self.chosen_skill)
                be = requester.final_utility()
                t_p = copy.deepcopy(selected_providers)
                t_p.append(provider_tuple[0])
                requester.simulation_times_for_utility = requester.construct_time_line(t_p, self.chosen_skill)
                af = requester.final_utility()
                if self.chosen_skill in requester.max_util:
                    if af - be != 0:
                        selected_providers.append(provider_tuple[0])

            self.req.internal_fmr[skill] = copy.deepcopy(selected_providers)



    def heuristic_function(self,provider1 : tuple,provider2 : tuple) -> int:
        for i in self.Providers.keys():
            if self.Providers[i].id_ == provider1[0]:
                this_agent = self.Providers[i]
        for i in self.Providers.keys():
            if self.Providers[i].id_ == provider2[0]:
                this_agent2 = self.Providers[i]

        if utils.Calculate_Distance(self.req.current_location,this_agent.current_location) /0.7 > utils.Calculate_Distance(self.req.current_location,this_agent2.current_location):
            return 1
        elif utils.Calculate_Distance(self.req.current_location,this_agent2.current_location) /0.7 > utils.Calculate_Distance(self.req.current_location,this_agent.current_location):
            return -1
        else:
            if this_agent.After_fmr < this_agent2.After_fmr:
                return -1
            else:
                return 1


    def ms_heuristic_function_helper(self,sum : int,target_sum :int,add_val : int) -> Any:
        if target_sum >= sum:
            return add_val
        else:
            return False

    def remember(self):
        '''
        remembers the assignment of a given iteration
        :return:
        '''
        self.assignments_per_iteration.append({})
        for provider in self.Providers.values():
            self.assignments_per_iteration[self.iteration_num][provider.id_] = provider.chosen_requester

    def recall(self,iteration_num : int) -> None:
        '''
        reconstructs assignment of given iteration
        :param iteration_num: the iteration which we want to reconstruct
        '''
        for provider in self.Providers.values():
            provider.chosen_requester = self.assignments_per_iteration[iteration_num][provider.id_]

    def detach_neighbors(self):
        for provider in self.Providers.values():
            for requester in self.Requesters.values():
                provider.remove_neighbour(requester)
                requester.remove_neighbour(provider)

    def assign_neighbors(self):
        for provider in self.Providers.values():
            for requester in self.Requesters.values():
                distance = Calculate_Distance(provider.current_location, requester.current_location)
                skills_in_common = [s for s in provider.skill_set.keys() if s in requester.skill_set.keys()]
                if distance <= self.dist_tresh and len(skills_in_common) > 0:
                    provider.add_neighbour(requester)
                    requester.add_neighbour(provider)

    def iterate(self) -> int:
        if self.iteration_num % 50 == 0 and self.iteration_num != 0:
            self.recall(self.highest_iter)
            for provider in self.Providers.values():
                provider.advance_time_via_choice()
                provider.full_reset()
            for requester in self.Requesters.values():
                requester.full_reset()
            self.detach_neighbors()
            self.assign_neighbors()
            self.initiate()
        self.remember()
        if self.iteration_num % 50 == 5 and self.iteration_num != 0:
            for provider in self.Providers.values():
                provider.up_mistake()
        return super().iterate()