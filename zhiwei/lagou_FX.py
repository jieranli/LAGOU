#!/usr/bin/env python
# _*_ coding:utf-8 _*_
import re
import numpy as np
import pandas as pd
import jieba as jb
import jieba.analyse
import jieba.posseg as pseg
from matplotlib import pyplot as plt

#导入清洗后的数据
lagou = pd.read_csv(open('lagou1.csv','rb'))
print(lagou)
