import math
import random

from MS_Provider import MS_Provider
from MS_Requester import MS_Requester
from Provider import Provider
from utils import Calculate_Distance
from graphics import Rectangle, Text
from graphics import Circle
from graphics import Point

class Problem(object):
    def __init__(self, prob_id, algorithm, utility_type, number_of_providers,
                 number_of_requesters, random_params={}, distance_threshold=5, num_skill_types=1,
                 max_skill_ability_needed=4, max_skill_ability_provided=4, max_capacity_per_skill=4,
                 mean_time_per_skill=1, max_time_per_requester=7, utility_threshold_for_acceptance=50):

        # problem vars
        self.prob_id = prob_id
        self.random_num = random.Random(prob_id)
        self.algorithm = algorithm
        self.utility_type = utility_type
        self.utility_threshold_for_acceptance = utility_threshold_for_acceptance
        self.random_params = random_params

        # generate entities
        self.num_skill_types = num_skill_types
        self.max_skill_ability_needed = max_skill_ability_needed
        self.max_skill_ability_provided = max_skill_ability_provided
        self.max_capacity_per_skill = max_capacity_per_skill
        self.mean_time_per_skill = mean_time_per_skill
        self.max_time_per_requester = max_time_per_requester

        self.number_of_requesters = number_of_requesters
        self.number_of_providers = number_of_providers
        self.requesters = []
        self.create_requesters()
        self.providers = []
        self.create_providers()

        # create locations for all agents
        self.create_initial_locations(self.providers)
        self.create_initial_locations(self.requesters)

        # assign neighbors by location and distance threshold
        self.distance_threshold = distance_threshold
        self.assign_neighbors()


    # creates all requesters
    def create_requesters(self):

        for i in range(self.number_of_providers, self.number_of_providers + self.number_of_requesters):
            requester = None
            skills_needed = self.create_skills(self.max_skill_ability_needed,1)
            max_required = self.get_required_per_skill(skills_chosen=skills_needed)
            time_per_skill = self.create_time_per_skill(skills_chosen=skills_needed)
            max_util = self.create_max_util(skills_needed)
            max_time = self.create_max_time(time_per_skill)
            requester = self.create_single_requester(id_=i, skills_needed=skills_needed, max_required=max_required,
                                                     time_per_skill=time_per_skill, max_util=max_util,
                                                     max_time=max_time)

            self.requesters.append(requester)

    def create_single_requester(self, id_, skills_needed, max_required , time_per_skill , max_util , max_time):
        if self.algorithm == 0:
                return MS_Requester(id_=id_, problem_id=self.prob_id, skills_needed=skills_needed,max_required=max_required,
                                time_per_skill_unit=time_per_skill, max_util=max_util, max_time=max_time,max_skill_types = self.num_skill_types)
    # creates all providers
    def create_providers(self):

        for i in range(self.number_of_providers):
            provider = None
            skill_set = self.create_skills(self.max_skill_ability_provided,0.5)

            if self.algorithm == 0:
                    provider = MS_Provider(id_=i, problem_id=self.prob_id, skill_set=skill_set, travel_speed=self.random_params["travel_speed"])

            self.providers.append(provider)

    # creates neighboring agents by threshold distance - symmetrical
    def assign_neighbors(self):
        for provider in self.providers:
            for requester in self.requesters:
                distance = Calculate_Distance(provider.current_location, requester.current_location)
                skills_in_common = [s for s in provider.skill_set.keys() if s in requester.skill_set.keys()]
                if distance <= self.distance_threshold and len(skills_in_common) > 0:
                    provider.add_neighbour(requester)
                    requester.add_neighbour(provider)

    def create_skills(self, max_skill_ability,i):
        # chooses skills without replacement
        skills_avail = list(range(0, self.num_skill_types))
        num_skills_to_choose = self.random_num.randint(1, self.num_skill_types)

        # choose num_skills_to_choose skills out of skills_available with no replacement
        skills_chosen = self.random_num.sample(population=skills_avail, k=num_skills_to_choose)

        # chooses between 1, max_ability with replacement
        abilities_avail = list(range(1, max_skill_ability))
        abilities_chosen = self.random_num.choices(population=abilities_avail, k=num_skills_to_choose)
        # key: skill, value: quality
        final_skill_dict = dict(zip(skills_chosen, abilities_chosen))
        for key in final_skill_dict.keys():
            final_skill_dict[key] = int(math.ceil(final_skill_dict[key] * i));
        return final_skill_dict

    # defines maximum cap for the cap function
    def get_required_per_skill(self, skills_chosen):
        max_required = {}
        for skill in skills_chosen.keys():
            max_optional = min(self.max_capacity_per_skill, skills_chosen[skill])
            max_required_for_skill = self.random_num.randint(1, max_optional)
            max_required[skill] = max_required_for_skill

        return max_required

    def create_time_per_skill(self, skills_chosen):
        time_per_skill_unit = {}
        for skill in skills_chosen.keys():
            time_per_skill_unit[skill] = abs(round(self.random_num.gauss(self.mean_time_per_skill, 1), 2))
        return time_per_skill_unit

    def create_max_util(self, skills_needed):
        min_util = self.random_params["min_util_threshold"]
        max_util = self.random_params["max_util_threshold"]
        util = {}
        for skill in skills_needed.keys():
            util[skill] = self.random_num.randint(min_util, max_util)
        return util

    def create_max_time(self, time_per_skill):
        all_time = 0
        for skill, time in time_per_skill.items():
            all_time += time

        max_time = round(self.random_num.uniform(all_time * 3, all_time * 3 + self.max_time_per_requester), 2)

        return max_time

    # creates locations for agents in a list according to the thresholds given in params
    def create_initial_locations(self, agents):
        min_x = self.random_params["location_min_x"]
        max_x = self.random_params["location_max_x"]
        min_y = self.random_params["location_min_y"]
        max_y = self.random_params["location_max_y"]

        for a in agents:
            rand_x = round(self.random_num.uniform(min_x, max_x), 2)
            rand_y = round(self.random_num.uniform(min_y, max_y), 2)
            a.current_location = [rand_x, rand_y]
            if isinstance(a,Provider):
                a.graphic = Rectangle(Point(rand_x-1, rand_y-1), Point(rand_x+1, rand_y+1))
                a.id_text = Text(Point(a.current_location[0], a.current_location[1]),
                       "P" + str(a.id_))
            else:
                a.graphic = Circle(Point(rand_x, rand_y), 1)
                a.id_text = Text(Point(a.current_location[0], a.current_location[1]), "R" + str(a.id_))

    def get_agent(self, agent_id):
        for agent in self.providers + self.requesters:
            if agent.id_ == agent_id:
                return agent

