'''
Author: Tomer kigel
Contact info: e-mail: tomer.kigel@gmail.com
              phone number: 0507650153
              github: https://github.com/TomerKigel
'''
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
        self.iter_multip = 2


    def initiate(self) -> None:
        '''
        share relevant data between requesters and providers
        and establish the relationship between them
        '''
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
            requester.reset_offers()


    def fmr(self ,requester : Requester) -> None:
        '''
           gets a requester and returns a list of neighbours to detach
           :param requester: the agent we want to apply fmr on
           :return list: a list of neighbours to detach
        '''


        self.req = requester
        neighbours_sorted = sorted(requester.neighbor_util.items(), key=cmp_to_key(self.heuristic_function))

        for skill in requester.skill_set:
            selected_providers = []
            for i in requester.allocated_providers:
                selected_providers.append(i[0])
            for provider_tuple in neighbours_sorted:
                requester.simulation_times_for_utility = requester.construct_time_line(selected_providers, skill)
                be = requester.final_utility()
                t_p = copy.deepcopy(selected_providers)
                t_p.append(provider_tuple[0])
                requester.simulation_times_for_utility = requester.construct_time_line(t_p, skill)
                af = requester.final_utility()
                if skill in requester.max_util:
                    if af - be != 0:
                        selected_providers.append(provider_tuple[0])

            requester.internal_fmr[skill] = copy.deepcopy(selected_providers)



    def heuristic_function(self,provider1 : tuple,provider2 : tuple) -> int:
        '''
        Comparator for sorting neighbors when picking subset in FMR
        compares by distance first. if distance is within range use second criterion which is 'After_fmr'
        an indicator if an agent was already assigned a requester or not in the current FMR.
        :param provider1: First provider we compare to
        :param provider2: the second provider in the list
        :return: 1/-1
        '''
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


    def remember(self) -> None:
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

    def detach_neighbors(self) -> None:
        '''
        Detaches all neighbors on the graph in the problem
        '''
        for provider in self.Providers.values():
            for requester in self.Requesters.values():
                provider.remove_neighbour(requester)
                requester.remove_neighbour(provider)

    def assign_neighbors(self) -> None:
        '''
        Assign neighbors based on distance threshold and commonality of skills
        '''
        for provider in self.Providers.values():
            for requester in self.Requesters.values():
                distance = Calculate_Distance(provider.current_location, requester.current_location)
                skills_in_common = [s for s in provider.skill_set.keys() if s in requester.skill_set.keys()]
                if distance <= self.dist_tresh and len(skills_in_common) > 0:
                    provider.add_neighbour(requester)
                    requester.add_neighbour(provider)

    def iterate(self) -> int:
        '''
        iteratre through the algorithm
        '''

        #increment of MaxSum every 20..30...40... etc iterations
        if self.iteration_num % (self.iter_multip * 10) == 0 and self.iteration_num != 0:
            self.iter_multip += 1
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

        #wait 5 iterations and then add stochastic element
        if self.iteration_num % (self.iter_multip * 10) == 5 and self.iteration_num != 0:
            for provider in self.Providers.values():
                provider.up_mistake()
        return super().iterate()