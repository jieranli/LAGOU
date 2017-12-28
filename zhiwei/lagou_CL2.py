#!/usr/bin/env python
# _*_ coding:utf-8 _*_
'''问题1：responseJob出现空值或者全英文或者纯数字影响中文分词(204行)
   问题2：salary出现xxk以上薪资不符合xxk-xxk数据格式(110行)
   问题3：如何实现实时分析出去数据不会覆盖前一次数据
   问题4：计算丰富度的时候，唯一词/所有词,每条数据词总数量不定，没有一个参照物，无法做出精准判断。
   问题5：数据很糟糕，理想很丰满，现实很骨感'''
import jieba as jb
import numpy as np
import pandas as pd
import re
from sklearn import preprocessing
from sklearn.cluster import KMeans
import nltk
#import jieba.analyse
import jieba.posseg as pseg
from matplotlib import pyplot as plt
import matplotlib
from pylab import mpl
from matplotlib.font_manager import FontProperties
font_set = FontProperties(fname=r"C:\work\python\simsunttc\simsun.ttc", size=15)


'''对输出的dataframe数据输出结果做些定义'''
pd.set_option('display.max_rows', None)
pd.set_option('display.height', 10000)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 2000)
pd.set_option('max_colwidth', 100)
'''读取json数据'''
#loandata = pd.DataFrame(pd.read_excel('loan_data.xlsx'))
with open('lagou.json', 'rb') as f:
    #    for eachLine in f:
    #        line = eachLine.strip().decode('utf-8')
    #        line = eachLine.replace('[', '').replace(']', '')
    data = f.readlines()
    '''对json数据做处理（去掉行位空格，将整个每行json数据变成整体[{"aa":["bb"]},{"cc":["dd"]}]）.json()拼接字符串'''
    data = map(lambda x: x.rstrip(), data)
    lagou_json = b"[" + b','.join(data) + b"]"
    lagou = pd.DataFrame(pd.read_json(lagou_json))
    '''shape代表多少行，多少个字段'''
# print(lagou.column,lagou.shape)
'''用于存储清洗后的数据'''
industry = []
'''对industryField字段进行清洗及分列'''
for x in lagou['industryField']:
    c = x.replace("、", ",")
    industry.append(c)
'''替换后的行业数据改为dataframe格式'''
industry = pd.DataFrame(industry, columns=["industry"])
# print(industry)
'''对行业数据进行分列'''
industry_s = pd.DataFrame((x.split(',') for x in industry["industry"]), index=industry["industry"].index,
                          columns=['industry_1', 'industry_2'])
# print(industry_s)
'''将分列后的行业信息匹配回原数据表'''
lagou = pd.merge(lagou, industry_s, right_index=True, left_index=True)

# 清除字段两侧空格
# lagou["industry_2"] = lagou["industry_2"].map(str.strip)
# print(lagou[['financeStage']])
'''提取并处理financeStage中的融资信息'''
f_dict = {'未融资': '未融资',
          '天使轮': '天使轮',
          'A轮': 'A轮',
          'B轮': 'B轮',
          'C轮': 'C轮',
          'D轮': 'D轮',
          '不需要': '不需要融资',
          'None': '未融资',
          '上市公司': '上市公司'
          }
financeStage2 = []
for i in range(len(lagou['financeStage'])):
    '''逐一提取字典中的每一条信息'''
    for (key, value) in f_dict.items():
        '''判断financeStage字段中是否包含字典中的任意一个key'''
        if key in lagou['financeStage'][i]:
            financeStage2.append(value)
lagou["financeStage"] = financeStage2
# print(lagou[["financeStage"]])
# print(lagou['positionName'])
'''提取理positionname中的职位信息'''
positionName3 = []
'''对职位名称进行判断分类'''
for i in range(len(lagou['positionName'])):
    if 'PHP' in lagou['positionName'][i]:
        positionName3.append("PHP开发(大数据方向)")
    elif 'java' in lagou['positionName'][i]:
        positionName3.append("java开发(大数据方向)")
    elif 'Android' in lagou['positionName'][i]:
        positionName3.append("Android开发")
    elif 'python' in lagou['positionName'][i]:
        positionName3.append("python开发")
    elif 'C++' in lagou['positionName'][i]:
        positionName3.append('C++开发(大数据方向)')
    elif '.net' in lagou['positionName'][i]:
        positionName3.append(".net开发(大数据方向)")
    elif '算法' in lagou['positionName'][i]:
        positionName3.append("机器学习")
    elif '深度学习' in lagou['positionName'][i]:
        positionName3.append("机器学习")
    elif '机器学习' in lagou['positionName'][i]:
        positionName3.append("机器学习")
    elif '数据挖掘' in lagou['positionName'][i]:
        positionName3.append("机器学习")
    elif '大数据' in lagou['positionName'][i]:
        positionName3.append("大数据")
    else:
        positionName3.append("其他")
lagou["positionName"] = positionName3
# print(lagou["positionName"])
salary1 = []
'''对salary字段进行清洗'''
for i in lagou['salary']:
    # 设置要替换的正则表达式k|K
    p = re.compile("k|K")
    # 按正则表达式对salary字段逐条进行替换（替换为空）
    salary_date = p.sub("", i)
    salary1.append(salary_date)
lagou['salary'] = salary1
#print(lagou['salary'])
'''对薪资范围字段进行分列'''
salary_s = pd.DataFrame((x.split('-') for x in lagou['salary']), index=lagou['salary'].index,
                        columns=['s_salary', 'e_salary'])
# print(salary_s)
'''更改字段格式'''
salary_s['s_salary'] = salary_s['s_salary'].astype(int)
salary_s['e_salary'] = salary_s['e_salary'].astype(int)
'''计算平均薪资'''
salary_avg = []
'''逐一提取薪资范围字段'''
for i in range(len(salary_s)):
    salary_avg.append((salary_s['s_salary'][i] + salary_s['e_salary'][i]) / 2)
salary_s['salary_avg'] = salary_avg
lagou = pd.merge(lagou, salary_s, right_index=True, left_index=True)
# print(lagou[["salary_avg"]])
'''提取职位描述字段，并对英文统一转化为小写'''
lagou['responseJob'] = lagou['responseJob'].map(str.lower)
tools = ['mysql', 'oracle', 'mongdb', 'hbase', 'hive', 'linux', 'java', 'python', 'r', 'shell', 'sql', 'hadoop',
         'spark', 'excel', 'matlab']
#print(lagou['responseJob'])
'''创建list用于存储数据'''
tool = np.array([[0 for i in range(len(tools))] for j in range(len((lagou['responseJob'])))])
'''逐一提取职位描述信息'''
for i in range(len(lagou['responseJob'])):
    '''逐一提取工具名称'''
    for t in tools:
        '''获得工具名称的索引位置(第几个工具)'''
        index = tools.index(t)
        '''判断工具名称是否出现在职位描述中'''
        if t in lagou['responseJob'][i]:
            '''如果出现，在该工具索引位置(列)填1'''
            tool[i][index] = 1
        else:
            tool[i][index] = 0
            pass
'''将获得的数据转换为Dataframe格式'''
analytics_tools = pd.DataFrame(tool, columns=tools)
'''按行(axis=1)(矩阵的每一行相加)对每个职位描述中出现的工具数量进行求和(横向)'''
tool_num = analytics_tools.sum(axis=1)
'''将工具数量求和拼接到原数据表中'''
analytics_tools["tool_num"] = tool_num
# print(analytics_tools)
'''将表与原数据表进行拼接'''
lagou = pd.merge(lagou, analytics_tools, right_index=True, left_index=True)
'''计算职位描述的字数'''
'''创建list用于存储新数据'''
jd_num = []
'''逐一提取职位描述信息'''
for i in range(len(lagou['responseJob'])):
    '''转换数据格式(list转换为str)'''
    word_str = ''.join(lagou['responseJob'][i])
    '''对文本进行分词'''
    word_split = jb.cut(word_str)
    '''使用|分割结果并转换格式'''
    word_split1 = "| ".join(word_split)
    '''设置字符匹配正则表达式'''
    pattern = re.compile('\w')
    '''查找分词后文本中的所有字符并赋值给word_w'''
    word_w = pattern.findall(word_split1)
    '''计算word_w中字符数量并添加到list中'''
    jd_num.append(len(word_w))
'''对字符数量进行归一化,最小-最大规范化——标准化(也叫离差标准化，是对原始数据的线性变换，将数据映射到[0,1]之间，与功效系数法相同)'''
'''（每一个数-最小的数）*[1/（最大的数-最小的数）]'''
min_max_scaler = preprocessing.MinMaxScaler()
min_max_jd_num = min_max_scaler.fit_transform(jd_num)
'''将归一化的数据添加到原数据表中'''
lagou['jd_num'] = min_max_jd_num
# print(lagou['jd_num'])
# print(jd_num[:10])
'''计算职位描述文字丰富度'''
diversity = []
'''逐一提取职位描述信息'''
for i in range(len(lagou['responseJob'])):
    '''转换数据格式(list转换为str)'''
    word_str = ''.join(lagou['responseJob'][i])
    '''将文本中的英文统一转化为小写'''
    word_str = word_str.lower()
    '''查找职位描述中的所有中文字符'''
    word_list = re.findall(r'[\u4e00-\u9fa5]', word_str)
    '''转换数据格式(list转换为str)'''
    word_str1 = ''.join(word_list)
    '''对文本进行分词'''
    word_split = jb.cut(word_str1)
    '''使用空格分割结果并转换格式'''
    word_split1 = " ".join(word_split)
    #    print(word_split1)
    '''使用nltk对句子进行分词'''
    tokens = nltk.word_tokenize(word_split1)
    #print(tokens)
    '''转化为text对象'''
    text = nltk.Text(tokens)
    #    print(text)
    '''计算职位描述的文字丰富度(唯一词/所有词) set()无序不重复元素集可以消除重复元素'''
    word_diversity = len(set(text)) / len(text)
    #    print(len(set(text)))
    #    print(len(text))
    diversity.append(word_diversity)
lagou["diversity"] = diversity
# print(lagou["diversity"])
'''提取平均工作年限，平均薪资'''
salary_type = np.array(lagou[['salary_avg']])
'''进行聚类分析(3个中心)n_clusters(簇的个数)'''
clf = KMeans(n_clusters=5)
'''训练模型'''
clf = clf.fit(salary_type)
'''将距离结果标签合并到原数据表中(输出结果分成三类0,1,2)clf.labels_(每个样本所属的簇)'''
lagou['cluster_label'] = clf.labels_
#print(lagou['cluster_label'])
'''用来评估簇的个数是否合适，距离越小说明簇分的越好，选取临界点的簇个数'''
#print(clf.inertia_)
'''输出聚类结果'''
#print(clf.cluster_centers_)
'''对平均薪资进行聚类预测'''
#print(clf.predict(9), clf.predict(25), clf.predict(30))
#print(lagou.columns)
# print(lagou.shape)
#lagou.to_csv(lagou, index=False, encoding="gb2312")
#lagou.to_csv("lagou.csv",encoding="utf_8_sig")

'''数据分析'''
'''不同行业机器学习职位数量'''
def INDUSTRY():
    industry = lagou["industry_1"].value_counts()
    #print(industry)
    '''图表字体为华文细黑，字号为10'''
    #plt.rc('font', family='STXihei', size=10)
    '''创建一个一维数组赋值给'''
    a = np.array([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19])
    '''创建柱状图，数据源为按机器学习行业占比汇总的，设置颜色，透明度和外边框颜色#99CC01绿色，#FFFF01黄色，#0000FE蓝色，#FE0000红色，#A6A6A6灰色，#D9E021浅绿色'''
    plt.barh([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19],industry,color='#FE0000',alpha=0.8,align='center',edgecolor='white')
    '''设置x轴标签'''
    plt.xlabel(u'职位数量', fontproperties=font_set)
    '''设置y周标签'''
    plt.ylabel(u'所属行业', fontproperties=font_set)
    '''设置图表标题'''
    plt.title(u'不同行业涉及到机器学习职位数量', fontproperties=font_set)
    '''设置图例的文字和在图表中的位置'''
    plt.legend(['Position the number'],loc='upper right')
    '''设置背景网格线的颜色，样式，尺寸和透明度'''
    plt.grid(color='#95a5a6',linestyle='--', linewidth=1, axis='x', alpha=0.4)
    '''设置数据分类名称'''
    plt.yticks(a,(u'移动互联网',u'金融',u'电子商务',u'企业服务',u'数据服务','O2O',u'硬件',u'游戏',u'教育',u'文化娱乐',u'广告营销',u'医疗健康',u'信息安全',u'社交网络',u'旅游',u'其他',u'生活服务',u'招聘','None'), fontproperties=font_set)
    '''显示图表'''
    plt.show()
#INDUSTRY()
'''不同金融阶段机器学习职位数量'''
def STAGE():
    financeStage=lagou["financeStage"].value_counts()
    '''创建一个一维数组赋值给'''
    #a=np.array([1,2,3,4,5,6,7,8])
    LOCALTION = np.arange(len(financeStage))
    '''创建柱状图，数据源为金融不同阶段，设置颜色，透明度和外边框颜色#99CC01'''
    plt.barh(LOCALTION,financeStage,color='#0000FE',alpha=0.8,align='center',edgecolor='white')
    '''设置x轴标签'''
    plt.xlabel('职位数量', fontproperties=font_set)
    '''设置y周标签'''
    plt.ylabel('所处阶段', fontproperties=font_set)
    '''设置图表标题'''
    plt.title('不同金融阶段业机器学习职位数量', fontproperties=font_set)
    '''设置图例的文字和在图表中的位置'''
    plt.legend(['Position the number'], loc='upper right')
    '''设置背景网格线的颜色，样式，尺寸和透明度'''
    plt.grid(color='#95a5a6',linestyle='--', linewidth=1,axis='x',alpha=0.4)
    '''设置数据分类名称'''
    plt.yticks(LOCALTION,('不需要融资','上市公司','A轮','B轮','C轮','天使轮','D轮','未融资'), fontproperties=font_set)
    plt.show()
#STAGE()

'''不同金融阶段职位平均工资金额占比'''
def XSTAGE():
    plt.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签
    plt.rcParams['font.serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False # 用控制中文乱码
    lagou_salary = lagou.groupby('financeStage')['salary_avg'].agg(sum)
    colors = ["#99CC01", "#FFFF01", "#0000FE", "#FE0000", "#A6A6A6", "#D9E021","#9B59B6","#2ECC71"]
    name = ['A轮', 'B轮', 'C轮', 'D轮', '上市公司', '不要融资','天使轮','未融资']
    '''创建饼图，设置分类标签，颜色和图表起始位置等labels(每一块)饼图外侧显示的说明文字explode (每一块)离开中心距离'''
    plt.pie(lagou_salary, labels=name, colors=colors, explode=(0.1, 0, 0, 0, 0.1, 0.05, 0, 0), startangle=60, autopct='%1.1f%%')
    plt.title('不同金融阶段职位平均工资金额占比', fontproperties=font_set)
    plt.legend(name, loc='upper left')
    plt.show()
#XSTAGE()

'''机器学习职位对工作年限的要求'''
def WORKYEAR():
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['font.serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 用控制中文乱码
    lagou_workYear = lagou['workYear'].value_counts()
    '''创建一个一维数组赋值给'''
    a=np.array([1,2,3,4,5,6,7])
    '''创建柱状图，数据源设置颜色，透明度和外边框颜色'''
    plt.barh([1,2,3,4,5,6,7],lagou_workYear,color='#0000FE',alpha=0.8,align='center',edgecolor='white')
    '''设置x轴标签'''
    plt.xlabel('职位')
    '''设置y周标签'''
    plt.ylabel('工作年限')
    '''设置图表标题'''
    plt.title('机器学习职位对工作年限的要求')
    '''设置图例的文字和在图表中的位置'''
    plt.legend(['职位数量'], loc='upper right')
    '''设置背景网格线的颜色，样式，尺寸和透明度'''
    plt.grid(color='#95a5a6',linestyle='--', linewidth=1,axis='x',alpha=0.4)
    '''设置数据分类名称'''
    plt.yticks(a,('3-5年','1-3年','5-10年','不限','10年以上','1年以下','应届毕业生'))
    plt.show()
#WORKYEAR()
'''对学历的要求'''
def EDUC():
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['font.serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 用控制中文乱码
    lagou_education=lagou['education'].value_counts()
    '''设置饼图中每个数据分类的颜色#FE0000'''
    colors = ["#FE0000","#FFFF01","#0000FE","#99CC01","#A6A6A6"]
    '''设置饼图中每个数据分类的名称'''
    name=['本科', '硕士', '大专', '不限', '博士']
    '''创建饼图，设置分类标签，颜色和图表起始位置等'''
    plt.pie(lagou_education,colors=colors,explode=(0.1, 0, 0, 0, 0),startangle=60,autopct='%1.1f%%')
    '''添加图表标题'''
    plt.title('职位对学历要求')
    '''添加图例，并设置显示位置'''
    plt.legend(['本科', '硕士', '大专', '不限', '博士'], loc='upper left')
    plt.show()
#EDUC()
def MONEY():
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.rcParams['font.serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False  # 用控制中文乱码
    # 创建散点图，贷款金额为x，利息金额为y，设置颜色，标记点样式和透明度等
    lagou_sy = lagou['salary_avg']
    lagou_label = lagou['diversity']
    plt.scatter(lagou_sy, lagou_label, 60, color='white', marker='*', edgecolors='#0D8ECF', linewidth=3, alpha=0.8)
    # 添加x轴标题
    plt.xlabel('平均薪资')
    # 添加y轴标题
    plt.ylabel('职位描述丰富度')
    # 添加图表标题
    plt.title('平均薪资分布')
    # 设置背景网格线的颜色，样式，尺寸和透明度
    plt.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='both', alpha=0.4)
    # 显示图表
    plt.show()
#MONEY()
'''
if __name__=="__main__":
    while True:
        choice = input(u"输入你的选择(I,S,X,W,E):")
        if choice in ["i","I"]:
            INDUSTRY()
        elif choice in ["s","S"]:
            STAGE()
        elif choice in ["x","X"]:
            XSTAGE()
        elif choice in ["w","W"]:
            WORKYEAR()
        elif choice in ["e","E"]:
            EDUC()
        elif choice in ["m","M"]:
            MONEY()
        else:
            print("Exit...")
            sys.exit()
'''

'''转换数据格式'''
word_str = ''.join(lagou['responseJob'])
'''对文本进行分词'''
word_split = jb.cut(word_str)
'''使用|分割结果并转换格式'''
word_split1 = "| ".join(word_split)
'''设置要匹配的关键词'''
pattern=re.compile('sql|mysql|posgresql|python|excel|spss|matplotlib|ppt|powerpoint|sas|r|hadoop|spark|hive|ga|java|perl|tableau')
'''匹配所有文本字符'''
word_w=pattern.findall(word_split1)
word_freq=pd.Series(word_w)
'''计算不同关键词出现的频率'''
word_freq.value_counts()

#手动设置字典
jb.load_userdict('dict.txt')
'''对文本按字典进行分词'''
word_split = jb.cut(word_str)
'''使用|分割结果并转换格式'''
word_split1 = "| ".join(word_split)
'''设置要匹配的关键词'''
pattern=re.compile('数据分析|清洗|预处理|深度学习|神经网络|算法|数据挖掘|模型|用户画像|机器学习')
'''匹配所有文本字符'''
word_w=pattern.findall(word_split1)
word_freq=pd.Series(word_w)
'''计算不同关键词出现的频率'''
word_freq.value_counts()
print(word_freq.value_counts())
pass