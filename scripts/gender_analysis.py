import os
import math
import pandas as pd
import sexmachine.detector as genderdetector
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

data_file_path = '../data/reviews.csv'
detector = genderdetector.Detector()
print 'test gender of Sam: ' + detector.get_gender('Sam')


df = pd.read_csv(data_file_path)
print df.head(1)

gender_count = {}
andy = []
for name in df['author']:
	if isinstance(name, str) == False: continue # we had some nan values, this solves that issue
	first_name = name.split(' ')[0]
	gender = detector.get_gender(first_name)
	gender_count[gender] = gender_count.get(gender, 0) + 1
	if gender == 'andy': andy.append(first_name)

print gender_count
# print list(set(andy))[0:30]

idx = np.arange(len(gender_count.keys()))
plt.bar(idx, gender_count.values(), align='center')
plt.xticks(idx, gender_count.keys())
plt.show()



# with open(data_file_path) as f:
# 	c = 0
# 	for line in f: 
# 		print line.split(',')
# 		if c == 2: break
# 		c += 1

