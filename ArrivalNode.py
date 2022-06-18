class ArrivalNode:
    def __init__(self, arrival_time, util,id = None):
        self.arrival_time = arrival_time
        self.util = util
        self.id = id
        self.nextNodes = []

    def insert(self,node):
        if self.nextNodes == None:
            self.nextNodes.append(node)

    def insert_path(self,path,cell_in_path = 0):
        if cell_in_path >= len(path):
            return

        if cell_in_path == 0:
            if self.id == None:
                self.id = path[0][0]
                self.arrival_time = path[0][1]
                return self.insert_path(path, cell_in_path + 1)
            elif self.id == path[cell_in_path][0]:
                self.util = 0
                return self.insert_path(path, cell_in_path + 1)

        for node in self.nextNodes:
            if node.id == path[cell_in_path][0]:
                node.util = 0
                return node.insert_path(path,cell_in_path+1)

        self.nextNodes.append(ArrivalNode(path[cell_in_path][1],0,path[cell_in_path][0]))
        return self.nextNodes[-1].insert_path(path, cell_in_path + 1)


    def find_max_path(self,result):
        max_util = 0
        max_util_indx = 0
        j = 0
        if  self.nextNodes == []:
            return result
        for i in self.nextNodes:
            if i.util > max_util:
                max_util =  i.util
                max_util_indx = j
            j+=1

        result.append((self.nextNodes[max_util_indx].id,self.nextNodes[max_util_indx].arrival_time,self.nextNodes[max_util_indx].util))
        return self.nextNodes[max_util_indx].find_max_path(result)

    def update_nodes_util(self,func_params):
        if self.id == None:
            return
        value_z = func_params[self.id][0]
        value_o = func_params[self.id][1]
        res = (value_z + value_o*self.arrival_time) * 0.9
        if res < 0:
            res = 0
        self.util += res
        if self.nextNodes == []:
            return
        for node in self.nextNodes:
            node.update_nodes_util(func_params)


    def damping(self):
        self.util *= 0.1
        if self.nextNodes == []:
            return
        for node in self.nextNodes:
            node.damping()

    def get_id_total_util(self,id):
        res = 0
        if self.id == id:
            res += self.util
        if self.nextNodes == []:
            return res
        for node in self.nextNodes:
            res +=node.get_id_total_util(id)
        return res