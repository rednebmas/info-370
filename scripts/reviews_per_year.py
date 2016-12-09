import os
import math
import pandas as pd
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt

data_file_path = '../data/reviews.csv'


df = pd.read_csv(data_file_path)
print df.head(1)


# gender_count = {}
# for name in df['author']:
# 	if isinstance(name, str) == False: continue # we had some nan values, this solves that issue
# 	first_name = name.split(' ')[0]
# 	gender = detector.get_gender(first_name)
# 	gender_count[gender] = gender_count.get(gender, 0) + 1

# idx = np.arange(len(gender_count))
# plt.bar(idx, gender_count.values(), align='center')
# plt.xticks(idx, gender_count.keys())
# plt.show()



