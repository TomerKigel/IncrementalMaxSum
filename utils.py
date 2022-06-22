import copy
import math
import string
from collections import Iterable
import random

import matplotlib.pyplot as plt
from importlib import reload
import pandas as pd

def Calculate_Distance(iterable_one : Iterable ,iterable_two : Iterable) -> float:
    return round(math.sqrt(sum((px - qx) ** 2.0 for px, qx in zip(iterable_one, iterable_two))), 2)

def plot_xy_graph( YSeries : list,XSeries : list) -> None:
    reload(plt)
    plt.plot(XSeries,YSeries)
    plt.ylabel('Utilitiy')
    plt.xlabel('nclo')
    plt.show()

def export_to_file(data : list) -> None:
    resulted_zip = zip()
    for d in data:
        resulted_zip = zip(resulted_zip,d)
    df = pd.DataFrame(resulted_zip)
    df.to_excel("results.xlsx")

def to_binary_list(number : int,amount_of_bits : int) -> list[bool]:
    output_list = []
    tstr = format(number,"b")
    tstr = padding(tstr,amount_of_bits)
    for char in tstr:
        if char == '1':
            output_list.append(True)
        else:
            output_list.append(False)
    return output_list

def padding(str :string ,amount_of_bits : int) -> string:
    if len(str) < amount_of_bits:
        str = '0' + str
    return str

def travel_time(start_location, end_location,travel_speed) -> float:
    distance = Calculate_Distance(start_location, end_location)
    distance_in_time = distance / travel_speed
    return distance_in_time

def truth_table(source : list,value : int) -> dict:
    res = {}
    row = [0 for i in range(0,len(source))]
    for i in range(value):
        res[i] = copy.deepcopy(row)
        if i == value -1:
            break
        j = 1
        row[-j] += 1
        while row[-j] == 2:
            row[-j] = 0
            j+=1
            row[-j] += 1
    row = [i for i in source]
    res[value] = row
    return res

def prep_permutate(source : dict,value : int) -> dict:
    res = {}
    max_indexes = []
    indexes = []
    for key in source.keys():
        max_indexes.append(len(source[key]))
        indexes.append(0)
    for row in range(0,value):
        res[row] = copy.deepcopy(indexes)
        if row == value - 1:
            return res
        place = 0
        placed = False
        while not placed:
            if indexes[place] < max_indexes[place]-1:
                indexes[place]+=1
                placed = True
            else:
                indexes[place] = 0
                place+=1
    return res

def rotate_dict(dic : dict) -> dict:
    init_key = (-1,0)
    prev_key = 0
    for key in dic.keys():
        if init_key == (-1,0):
            init_key = (key,dic[key])
        else:
            dic[prev_key] = dic[key]
        prev_key = key
    if dic:
        dic[key] = init_key[1]
    return dic


def heapPermutation(id_list, size , lst ):
    # if size becomes 1 then prints the obtained
    # permutation
    if len(lst) > 100:
        return

    if size == 1:
        lst.append(copy.deepcopy(id_list))
        return

    for i in range(size):
        heapPermutation(id_list, size - 1,lst)
        if len(lst) > 100:
            return
        # if size is odd, swap 0th i.e (first)
        # and (size-1)th i.e (last) element
        # else If size is even, swap ith
        # and (size-1)th i.e (last) element
        if size & 1:
            id_list[0], id_list[size - 1] = id_list[size - 1], id_list[0]
        else:
            id_list[i], id_list[size - 1] = id_list[size - 1], id_list[i]


