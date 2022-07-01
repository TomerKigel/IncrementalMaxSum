from __future__ import annotations
import math, copy

class Agent():
    def __init__(self, id_, problem_id):
        # Agent variables
        self.problem_id = problem_id
        self.id_ = id_
        self.current_location = []
        self.skill_set = []

        # neighbor variables
        self.neighbor_data = {}
        self.neighbor_util = {}

        #data for graphics
        self.graphic = None
        self.connections = {}
        self.total_connections = {}

        #mailing
        self.outmessagebox = []
        self.inmessagebox = []
        #sorted incoming mail
        self.message_data = {}

    def full_reset(self):
        # mailing
        self.outmessagebox = []
        self.inmessagebox = []
        # sorted incoming mail
        self.message_data = {}

    def __str__(self):
        return "ID: " + str(self.id_)

    def open_mail(self):
        raise NotImplementedError()

    # 1 - reset fields of algorithm
    def reset(self):
        raise NotImplementedError()

    # 2 - after context was updated in method agent_receive_a_single_msg
    def compute(self):
        raise NotImplementedError()

    # 3 - has the agent terminated its run
    def check_termination(self):
        raise NotImplementedError()

    # 4- first init iteration of algorithm
    def send_init_msg(self):
        raise NotImplementedError()

    def init_relationships(self):
        raise NotImplementedError()

    def add_neighbour(self,agent : Agent) -> None:
        if agent.id_ not in self.neighbor_data.keys():
            self.neighbor_data[agent.id_] = 0
            self.neighbor_util[agent.id_] = 0
            self.connections[agent.id_] = agent.current_location
            self.total_connections[agent.id_] = agent.current_location
        else:
            self.connections[agent.id_] = agent.current_location
            self.total_connections[agent.id_] = agent.current_location

    def remove_neighbour(self,agent) -> None:
        if type(agent) == int:
            if agent in self.connections.keys():
                del self.connections[agent]
        else:
            if agent.id_ in self.connections.keys():
                del self.connections[agent.id_]