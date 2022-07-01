'''
Author: Tomer kigel
Contact info: e-mail: tomer.kigel@gmail.com
              phone number: 0507650153
              github: https://github.com/TomerKigel
'''
import copy

from Agent import Agent
from Problem import Problem


class Mailer():

    def __init__(self,problem : Problem, max_iterations : int): # Providers : list, Requesters : list,
        '''
        Default constructor with basic mailer fields
        '''
        self.Providers = {}
        for provider in problem.providers:
            self.Providers[provider.id_] = provider

        self.Requesters = {}
        for requster in problem.requesters:
            self.Requesters[requster.id_] = requster

        self.iteration_num = 0
        self.max_iteration = max_iterations

        self.highest_iter = 0
        self.highest_util = 0


    def run(self) -> list:
        '''
        Unused function for running all mailer iterations at once
        '''
        utilities = []
        while self.iteration_num < self.max_iteration:
            utilities.append(self.iterate())
        return utilities


    def iterate(self) -> int:
        '''
        primary function for running mailer iterations
        Flow of control starts and ends here
        Most functionality in self.activate_internal_calculations()
        '''
        self.send_providers_messages()
        self.send_requesters_messages()
        self.activate_internal_calculations()
        utility = self.calculate_utility()
        if utility > self.highest_util:
            self.highest_iter = self.iteration_num
            self.highest_util = utility
        self.iteration_num += 1
        return (utility,self.iteration_nclo())


    def iteration_nclo(self) -> int:
        '''
        extraction of highest nclo
        '''
        max_requester_nclo = 0
        for requester in self.Requesters.values():
            if requester.nclo >= max_requester_nclo:
                max_requester_nclo = requester.nclo
        for requester in self.Requesters.values():
            requester.set_nclo(max_requester_nclo)

        return max_requester_nclo

    #before iteration begins
    def initiate(self) -> None:
        raise NotImplementedError()


    def send_providers_messages(self) -> None:
        '''
        Main mailer functionality lies here
        two functions for passing messages from function nodes to variable nodes and vica-versa
        '''
        for provider in self.Providers.values():
            for message in provider.outmessagebox:
                self.Requesters[message.receiver_id].inmessagebox.append(message)
            provider.outmessagebox.clear()

    def send_requesters_messages(self) -> None:
        '''
        Main mailer functionality lies here
        two functions for passing messages from function nodes to variable nodes and vica-versa
        '''
        for requester in self.Requesters.values():
            for message in requester.outmessagebox:
                self.Providers[message.receiver_id].inmessagebox.append(message)
            requester.outmessagebox.clear()



    def activate_internal_calculations(self) -> None:
        '''
        Activates calculcations for each individual nodes in the network.
        for further details see :py:class: 'MS_Provider<~IncrementalMaxSum.MS_Provider>'
        '''
        for provider in self.Providers.values():
            provider.compute()
        for requester in self.Requesters.values():
            requester.compute()



    def calculate_utility(self) -> int:
        '''
        iterate requesters and extract utility of assignments for iteration
        '''
        utility_sum = 0
        for requester in self.Requesters.values():
            utility_sum += requester.final_utility_orig()
        return utility_sum



    def remove_connection_by_reference(self,provider : Agent,requster : Agent) -> None:
        '''
        adjust graph disconnections
        '''
        provider.remove_neighbour(requster)
        requster.remove_neighbour(provider)

    def add_connection(self,provider : Agent,requster : Agent) -> None:
        '''
        adjust graph connections
        '''
        provider.add_neighbour(requster)
        requster.add_neighbour(provider)