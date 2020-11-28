import pandas as pd
import seaborn as sns
from sklearn.ensemble import ExtraTreesClassifier
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import warnings
warnings.filterwarnings("ignore")
from clean_data import clean_requirements


# load data set
job_salary = pd.read_csv("data/job_salary.csv")

# get a data frame of features
job_salary_cleaned = clean_requirements(job_salary)

# plot the important words using all requirements
requirements_docs = job_salary_cleaned['requirements_cleaned']
docs = ' '.join([w for w in requirements_docs.values])
word_cloud = WordCloud().generate(docs)
plt.imshow(word_cloud)
plt.axis("off")
plt.show()

# plot the important words using selected features
feature_names = list(job_salary_cleaned.columns[9:])
text = ' '.join([w for w in feature_names])
word_cloud = WordCloud().generate(text)
plt.imshow(word_cloud)
plt.axis("off")
plt.show()

# Training the model
feature_df = job_salary_cleaned.iloc[:, 9:]
extra_tree_forest = ExtraTreesClassifier().fit(feature_df, job_salary_cleaned['job_category'])
# Computing the importance of each feature
feature_importance = extra_tree_forest.feature_importances_
df = pd.DataFrame(feature_importance, columns=['importance'], index=feature_names)
df = df.sort_values('importance', ascending=False)
sns.barplot(x=df['importance'][0:50], y=df.index[0:50])
plt.show()