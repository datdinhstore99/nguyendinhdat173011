# -*- coding: utf-8 -*-
"""House Prices Processing.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lJxE5kYIf23vmVAEmezSI3ivpV5O3yZD
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('train.csv')

df.head()

df.isnull().sum().sort_values(ascending = False)

total = df.isnull().sum().sort_values(ascending = False)
percent = (df.isnull().sum() / df.isnull().count()).sort_values(ascending = False)
missingData = pd.concat([total, percent], axis = 1, keys = ['Total', 'Percent'])
missingData[:20]

sns.set_style("whitegrid")
missing = df.isnull().sum()
missing = missing[missing > 0]
missing.sort_values(inplace=True)
missing.plot.bar()

sns.heatmap(df.isnull(),yticklabels=False,cbar=False)

df.shape

# Rõ ràng là SalePrice không tuân theo phân phối chuẩn, vì vậy trước khi thực hiện hội quy, nó phải được chuyển đổi. 
# Trong khi chuyển đổi Log Normal hoạt động khá tốt, phù hợp nhất là phân phối Johnson không bị ràng buộc

import scipy.stats as stats

y = df['SalePrice']

plt.figure(1); plt.title('Johnson SU')
sns.distplot(y, kde=False, fit=stats.johnsonsu)

plt.figure(2); plt.title('Normal')
sns.distplot(y, kde=False, fit=stats.norm)

plt.figure(3); plt.title('Log Normal')
sns.distplot(y, kde=False, fit=stats.lognorm)

df.info()

df['MSZoning'].value_counts()

df['PoolQC'].value_counts()

# LostFrontage type float64
# Fill missing values

df['LotFrontage']=df['LotFrontage'].fillna(df['LotFrontage'].mean())

df.drop(['Alley'],axis=1,inplace=True)

df['BsmtCond']=df['BsmtCond'].fillna(df['BsmtCond'].mode()[0])
df['BsmtQual']=df['BsmtQual'].fillna(df['BsmtQual'].mode()[0])

df['FireplaceQu']=df['FireplaceQu'].fillna(df['FireplaceQu'].mode()[0])
df['GarageType']=df['GarageType'].fillna(df['GarageType'].mode()[0])

df.drop(['GarageYrBlt'],axis=1,inplace=True)

df['GarageFinish']=df['GarageFinish'].fillna(df['GarageFinish'].mode()[0])
df['GarageQual']=df['GarageQual'].fillna(df['GarageQual'].mode()[0])
df['GarageCond']=df['GarageCond'].fillna(df['GarageCond'].mode()[0])

# Drop cac truong bi mat nhieu du lieu
df.drop(['PoolQC','Fence','MiscFeature'],axis=1,inplace=True)
df.shape

df.drop(['Id'],axis=1,inplace=True)
df.isnull().sum().sort_values(ascending = False)

df['MasVnrType']=df['MasVnrType'].fillna(df['MasVnrType'].mode()[0])
df['MasVnrArea']=df['MasVnrArea'].fillna(df['MasVnrArea'].mode()[0])
df['BsmtExposure']=df['BsmtExposure'].fillna(df['BsmtExposure'].mode()[0])
df['BsmtFinType2']=df['BsmtFinType2'].fillna(df['BsmtFinType2'].mode()[0])

sns.heatmap(df.isnull(),yticklabels=False,cbar=False,cmap='coolwarm')

df.dropna(inplace=True)
df.shape

df.head()

categorical_columns = [col for col in df.columns.values if df[col].dtype == 'object']
data_cat = df[categorical_columns]

data_cat.head()

data_num = df.drop(categorical_columns, axis = 1)
data_num.head(1)
data_num.describe()

qualitative = [f for f in df.columns if df.dtypes[f] == 'object']

def encode(frame, feature):
    ordering = pd.DataFrame()
    ordering['val'] = frame[feature].unique()
    ordering.index = ordering.val
    ordering['spmean'] = frame[[feature, 'SalePrice']].groupby(feature).mean()['SalePrice']
    ordering = ordering.sort_values('spmean')
    ordering['ordering'] = range(1, ordering.shape[0]+1)
    ordering = ordering['ordering'].to_dict()
    
    for cat, o in ordering.items():
        frame.loc[frame[feature] == cat, feature+'_D'] = o
        
qual_encoded = []
for q in qualitative:
    encode(df, q)
    qual_encoded.append(q+'_D')
    
print(qual_encoded)

print(df['Street_D'][:10])
print(df['Street'][:10])

def spearman(frame, features):
    spr = pd.DataFrame()
    spr['feature'] = features
    spr['spearman'] = [frame[f].corr(frame['SalePrice'], 'spearman') for f in features]
    spr = spr.sort_values('spearman')
    plt.figure(figsize=(6, 0.25*len(features)))
    sns.barplot(data=spr, y='feature', x='spearman', orient='h')

features = quantitative + qual_encoded

quantitative = [col for col in data_num.columns.values if df[col].dtype != 'object']
quantitative.remove('SalePrice')
quantitative.remove('Id')

plt.figure(1)
corr = df[quantitative+['SalePrice']].corr()
sns.heatmap(corr)
plt.figure(2)
corr = df[qual_encoded+['SalePrice']].corr()
sns.heatmap(corr)
plt.figure(3)
corr = pd.DataFrame(np.zeros([len(quantitative)+1, len(qual_encoded)+1]), index=quantitative+['SalePrice'], columns=qual_encoded+['SalePrice'])
for q1 in quantitative+['SalePrice']:
    for q2 in qual_encoded+['SalePrice']:
        corr.loc[q1, q2] = df[q1].corr(df[q2])
sns.heatmap(corr)

corr = df.corr()
df[qual_encoded+['SalePrice']].corr()
print(features)

# Simple clustering
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

model = TSNE(n_components=2, random_state=0, perplexity=50)
X = df[features].fillna(0.).values
tsne = model.fit_transform(X)

std = StandardScaler()
s = std.fit_transform(X)
pca = PCA(n_components=30)
pca.fit(s)
pc = pca.transform(s)
kmeans = KMeans(n_clusters=9)
kmeans.fit(pc)

fr = pd.DataFrame({'tsne1': tsne[:,0], 'tsne2': tsne[:, 1], 'cluster': kmeans.labels_})
sns.lmplot(data=fr, x='tsne1', y='tsne2', hue='cluster', fit_reg=False)
print(np.sum(pca.explained_variance_ratio_))

def category_onehot_multcols(multcolumns):
    df_final=final_df
    i=0
    for fields in multcolumns:
        
        print(fields)
        df1=pd.get_dummies(final_df[fields],drop_first=True)
        
        final_df.drop([fields],axis=1,inplace=True)
        if i==0:
            df_final=df1.copy()
        else:
            
            df_final=pd.concat([df_final,df1],axis=1)
        i=i+1
       
        
    df_final=pd.concat([final_df,df_final],axis=1)
        
    return df_final

main_df=df.copy()

test_df=pd.read_csv('formattest.csv')
test_df.shape

final_df=pd.concat([df,test_df],axis=0)

final_df['SalePrice']
final_df.shape

final_df=category_onehot_multcols(categorical_columns)

final_df.head()

print(main_df['SaleType'][:10])
print(final_df['WD'][:10])

final_df =final_df.loc[:,~final_df.columns.duplicated()]

final_df.shape

final_df

df_Train=final_df.iloc[:1422,:]
df_Test=final_df.iloc[1422:,:]
df_Train.head()

sns.heatmap(final_df.isnull(),yticklabels=False,cbar=False)

df_Test.head()

print(df_Train.shape)
print(df_Test.shape)

#df_Test.drop(['SalePrice'],axis=1,inplace=True)

#df_Train.to_csv('DataTrain_new.csv',index=False)

df_Train['SalePrice'].head()

X_train=df_Train.drop(['SalePrice'],axis=1)
y_train=df_Train['SalePrice']

y_train.head

df_Test.head()

df_Test['SalePrice'].isnull().sum()

#df_Test.to_csv('DataTest_new.csv',index=False)

# Prediction and selection
# import xgboost
# classifier = xgboost.XGBRegressor()
# import xgboost
# regressor=xgboost.XGBRegressor()

# booster=['gbtree','gblinear']
# base_score=[0.25,0.5,0.75,1]

# ## Hyper Parameter Optimization


# n_estimators = [100, 500, 900, 1100, 1500]
# max_depth = [2, 3, 5, 10, 15]
# booster=['gbtree','gblinear']
# learning_rate=[0.05,0.1,0.15,0.20]
# min_child_weight=[1,2,3,4]

# # Define the grid of hyperparameters to search
# hyperparameter_grid = {
#     'n_estimators': n_estimators,
#     'max_depth':max_depth,
#     'learning_rate':learning_rate,
#     'min_child_weight':min_child_weight,
#     'booster':booster,
#     'base_score':base_score
#     }

# from sklearn.model_selection import RandomizedSearchCV
# # Set up the random search with 4-fold cross validation
# random_cv = RandomizedSearchCV(estimator=regressor,
#             param_distributions=hyperparameter_grid,
#             cv=5, n_iter=50,
#             scoring = 'neg_mean_absolute_error',n_jobs = 4,
#             verbose = 5, 
#             return_train_score = True,
#             random_state=42)

# random_cv.fit(X_train,y_train)

# random_cv.best_estimator_

# regressor=xgboost.XGBRegressor(base_score=0.25, booster='gbtree', colsample_bylevel=1,
#        colsample_bytree=1, gamma=0, learning_rate=0.1, max_delta_step=0,
#        max_depth=2, min_child_weight=1, missing=None, n_estimators=900,
#        n_jobs=1, nthread=None, objective='reg:linear', random_state=0,
#        reg_alpha=0, reg_lambda=1, scale_pos_weight=1, seed=None,
#        silent=True, subsample=1)

# regressor.fit(X_train,y_train)

# import pickle
# filename = 'finalized_model.pkl'
# pickle.dump(classifier, open(filename, 'wb'))

# df_Test.drop(['SalePrice'],axis=1,inplace=True)

# df_Test.shape

# df_Test.head()

# df_Test.drop(['SalePrice'],axis=1).head()

# y_pred=regressor.predict(df_Test.drop(['SalePrice'],axis=1))

y_pred

