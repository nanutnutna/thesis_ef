import numpy as np
import pandas as pd
import time

INPUT_PATH = "source/"
FILE_NAME = "emission_factor"



def read_table():
    t1 = pd.read_csv("source/emission_factor_1.csv")
    t2 = pd.read_csv("source/emission_factor_1_test.csv")
    return t1,t2


def compare_table():
    t1,t2 = read_table()
    if t1.equals(t2):
        return True
    return t1.compare(t2)


if __name__ == "__main__":
    print(compare_table())