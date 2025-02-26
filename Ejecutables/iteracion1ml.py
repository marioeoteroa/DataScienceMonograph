# -*- coding: utf-8 -*-
"""iteracion1ML.ipynb

# Dataset retail ventas online minoristas y mayoristas
"""

print("Inicio Ejecución iteración 1")

# Tratamiento de datos
# ==============================================================================
import pandas as pd
import numpy as np


# Matemáticas y estadísticas
# ==============================================================================
import math

# Preparación de datos
# ==============================================================================
from sklearn.impute import KNNImputer
from sklearn.impute import SimpleImputer
from sklearn.neighbors import LocalOutlierFactor
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split, cross_validate
import time
from sklearn.metrics import mean_squared_error, r2_score
from pylab import *
from pandas import DataFrame
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn import linear_model
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import cross_validate
from statistics import mean
from sklearn.linear_model import LinearRegression



# Gráficos
# ==============================================================================
import matplotlib.pyplot as plt
from matplotlib import style
import seaborn as sns

# Configuración matplotlib
# ==============================================================================
plt.rcParams['image.cmap'] = "bwr"
#plt.rcParams['figure.dpi'] = "100"
plt.rcParams['savefig.bbox'] = "tight"
style.use('ggplot') or plt.style.use('ggplot')

# Configuración warnings
# ==============================================================================
import warnings
warnings.filterwarnings('ignore')

"""## 1. Carga de datos"""

url = 'https://raw.githubusercontent.com/lmbd92/DataScienceMonograph/main/Data/data-raw/online_retail_II.csv'
df = pd.read_csv(url)
df.head()

df.info()

df.shape

df.dtypes

df.nunique()

df.describe()

"""## 2. Limpieza de datos"""

#Borrando columnas que no se emplearán

df.drop([ 'Customer ID', 'Description'], axis='columns', inplace=True)

# Definimos una lista de columnas categoricas y otra de columnas numericas

catCols = df.select_dtypes(include = ["object", 'category']).columns.tolist()
numCols=df.select_dtypes(include = ['float64','float64','int32','int64']).columns.tolist()
catCols

numCols

# Eliminar los caracteres no numéricos de la variable "Invoice"

df['Invoice'] = df['Invoice'].str.replace(r'\D', '', regex=True)

# Limpieza de las variables "Quantity" y "Price" ya que presentan valores negativos correspondientes a casos de devoluciones
df = df[df["Quantity"] > 0]
df = df[df["Price"] > 0]

#Reiniciar el indice
df.reset_index(drop=True, inplace=True)

# Calculo de valores atípicos para la variable "Quantity"


#Calculo de Q1 t Q3
Q1 = np.percentile(df['Quantity'], 25, interpolation = 'midpoint')
Q3 = np.percentile(df['Quantity'], 75, interpolation = 'midpoint')

#Cálculo del rango intercuartil
IQR = Q3 - Q1

#Cálculo de valor mínimo y máximo para los valores atípicos
VAInf = Q1 - 10*IQR
VASup = Q3 + 10*IQR

print(f'Valor atípico leve inferior:{VAInf}')
print(f'Valor atípico leve superior:{VASup}')

# Se eliminan los valores atípicos
df = df.drop(df[df['Quantity']>VASup].index)

#Reiniciar el indice
df.reset_index(drop=True, inplace=True)

df.shape

"""## 3. Preparación de datos"""

# Generación de nuevas variables
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

df['Dates'] = pd.to_datetime(df['InvoiceDate']).dt.date
df['Year'] = pd.to_datetime(df['InvoiceDate']).dt.year
df['Months'] = pd.to_datetime(df['InvoiceDate']).dt.month
df['Month_day'] = pd.to_datetime(df['InvoiceDate']).dt.day
df['Time_hour'] = pd.to_datetime(df['InvoiceDate']).dt.hour
df['wk_day'] = df['InvoiceDate'].dt.dayofweek + 1
df['year_month'] = df['InvoiceDate'].dt.strftime('%Y.%m')
df['TotalSpent'] = df['Quantity']*df['Price']
df.shape

# Calculo de total por transacción "Invoice" y cantidad total de items por transacción

df['TotalTransaction'] = df.groupby('Invoice')['TotalSpent'].transform('sum')
df['TotalQuantity'] = df.groupby('Invoice')['Quantity'].transform('sum')
df.head()

# Calculo de productos  únicos por transacción

df['TotalProductosUnicos'] = df.groupby('Invoice')['StockCode'].transform('nunique')
df.head()

!pip install pycountry_convert

# Función para agrupar por continente los paises

import pycountry_convert as pc

def obtener_continente(country):
    try:
        codigo_pais = pc.country_name_to_country_alpha2(country)
        codigo_continente = pc.country_alpha2_to_continent_code(codigo_pais)
        continente = pc.convert_continent_code_to_continent_name(codigo_continente)
        return continente
    except KeyError:
        return "unknown"

df['Continent'] = df['Country'].apply(obtener_continente)

df.head()

# Visualizar los valores unicos de la nueva variable
df["Continent"].unique()

# Visualizar los registros con etiqueta "unknown"

df_resultado = df[df["Continent"] == "unknown"]
df_resultado

# Visualizar los paises que la función no pudo clasificar
df_resultado["Country"].unique()

# Eliminar los registros del DF original con Country = "Unspecified"

df = df[df["Country"] != "Unspecified"]
df.shape

df.head()

# Etiquetar manualmente los demás paises

df.loc[df['Country'] == 'EIRE', 'Continent'] = 'Europe'
df.loc[df['Country'] == 'Channel Islands', 'Continent'] = 'Europe'
df.loc[df['Country'] == 'RSA', 'Continent'] = 'Africa'
df.loc[df['Country'] == 'West Indies', 'Continent'] = 'North_America'
df.loc[df['Country'] == 'Korea', 'Continent'] = 'Asia'
df.loc[df['Country'] == 'European Community', 'Continent'] = 'Europe'

df.head()

print(df["Continent"].value_counts())

# Estandarizando la variable "StockCode" y "Country" ya que es de tipo objeto y se evidencian caracteres en su composición

df['CodigoUnico'] = pd.factorize(df['StockCode'])[0] + 1
df['CountryUnico'] = pd.factorize(df['Country'])[0] + 1
df

# Verificamos que los valores unicos de las variables "StockCode" y "CodigoUnico" coincidan al igual que "Country" y "CountryUnico"
df.nunique()

# Aplicación de la función de get_dummies a la variable "Continent"

df = pd.get_dummies(df, columns=['Continent'], drop_first=1)

df.shape
df

# Eliminamos las columnas previamente codificadas
df = df.drop(columns=['StockCode','Country','InvoiceDate','Dates'])

df

"""Salvando el DF con datos limpios y transformados, previo a la implementación de los algoritmos ML"""

from google.colab import files

df.to_csv('online_retail_II_limpio.csv', index=False)

files.download('online_retail_II_limpio.csv')

"""## 4. Machine Learning

### 4.1 Regresión Lineal Simple
"""

# Monitoreo del tiempo de procesamiento
import time

start_time = time.time()

print('-------------------INICIO PROCESAMIENTO-----------------')

# Definición variables de entrada y variable de salida

df1= df.drop(columns=['TotalTransaction'])

df2 = df[['TotalTransaction']].copy()

df1.info()

df2.info()

# Creación de variables para el test y el train

TiempoEntrenamientoTRAIN=[]
TiempoEvaluacionTRAIN=[]
RMSETrain=[]
R2Train=[]
MSETrain=[]
MAETrain=[]
nameColum=[]

TiempoEntrenamientoTEST=[]
TiempoEvaluacionTEST=[]
RMSETest=[]
R2Test=[]
MSETest=[]
MAETest=[]

Cantidad = 19
print('-------------------INICIO PROCESAMIENTO -----------------')

for i in range(Cantidad):

    #Selecciono predictores
    X = df1.iloc[:,i]

    #Selecciono target
    y = df2.iloc[:,0]

    NameVariable = df1.columns[i]
    nameColum.append(NameVariable)

    #separo datos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.3, random_state=4444)
    X_train = X_train.values.reshape(-1,1)
    X_test = X_test.values.reshape(-1,1)
    ## se escalan los datos
    escalar = MinMaxScaler(feature_range=(-1,1))
    X_train = escalar.fit_transform(X_train)
    X_test = escalar.fit_transform(X_test)
    #MODELO DE REGRESION LINEAL SIMPLE
    LR_simple = linear_model.LinearRegression(n_jobs=-1)
    scoring = ['r2','neg_root_mean_squared_error','neg_mean_squared_error','neg_mean_absolute_error']

    ###Con datos de Train
    scores = cross_validate(LR_simple, X_train, y_train, scoring=scoring, n_jobs=-1, cv=10)
    TiempoPromedioEntrenamientoTRAIN = mean(scores['fit_time'])
    TiempoPromedioEvaluacionTRAIN = mean(scores['score_time'])
    RMSEPromedioTRAIN = mean(scores['test_neg_root_mean_squared_error'])
    R2PromedioTRAIN = mean(scores['test_r2'])
    MSEPromedioTRAIN = mean(scores['test_neg_mean_squared_error'])
    MAEPromedioTRAIN = mean(scores['test_neg_mean_absolute_error'])
    TiempoEntrenamientoTRAIN.append(TiempoPromedioEntrenamientoTRAIN)
    TiempoEvaluacionTRAIN.append(TiempoPromedioEvaluacionTRAIN)
    RMSETrain.append(RMSEPromedioTRAIN)
    R2Train.append(R2PromedioTRAIN)
    MSETrain.append(MSEPromedioTRAIN)
    MAETrain.append(MAEPromedioTRAIN)

    RMSETrainFinal=pd.DataFrame(RMSETrain)
    R2TrainFinal=pd.DataFrame(R2Train)
    MSETrainFinal=pd.DataFrame(MSETrain)
    MAETrainFinal=pd.DataFrame(MAETrain)

    ###Con datos de Test
    scores = cross_validate(LR_simple, X_test, y_test, scoring=scoring, n_jobs=-1, cv=10)
    TiempoPromedioEntrenamientoTEST = mean(scores['fit_time'])
    TiempoPromedioEvaluacionTEST = mean(scores['score_time'])
    RMSEPromedioTEST = mean(scores['test_neg_root_mean_squared_error'])
    R2PromedioTEST = mean(scores['test_r2'])
    MSEPromedioTEST = mean(scores['test_neg_mean_squared_error'])
    MAEPromedioTEST = mean(scores['test_neg_mean_absolute_error'])
    TiempoEntrenamientoTEST.append(TiempoPromedioEntrenamientoTEST)
    TiempoEvaluacionTEST.append(TiempoPromedioEvaluacionTEST)
    RMSETest.append(RMSEPromedioTEST)
    R2Test.append(R2PromedioTEST)
    MSETest.append(MSEPromedioTEST)
    MAETest.append(MAEPromedioTEST)

    RMSETestFinal=pd.DataFrame(RMSETest)
    R2TestFinal=pd.DataFrame(R2Test)
    MSETestFinal=pd.DataFrame(MSETest)
    MAETestFinal=pd.DataFrame(MAETest)
    NameColumFinal=pd.DataFrame(nameColum)

RMSE1 = pd.concat([RMSETrainFinal,RMSETestFinal], axis=1)
R21 = pd.concat([R2TrainFinal,R2TestFinal], axis=1)
MSE1= pd.concat([MSETrainFinal,MSETestFinal], axis=1)
MAE1= pd.concat([MAETrainFinal,MAETestFinal], axis=1)
nameColum1= pd.concat([NameColumFinal], axis=1)

####Creacion Tablas
tabla1 = pd.concat([nameColum1,RMSE1,R21,MSE1,MAE1], axis=1)
tabla1.columns = ['Variable','RMSETrain','RMSETest','R2Train','R2Test','MSETrain','MSETest','MAETrain','MAETest']


print('--------------------------------------------------------------')
print('PROCESAMIENTO FINALIZADO EXITOSAMENTE!!!')
print('--------------------------------------------------------------')

TIEMPO = (time.time() - start_time)/60
print("--- %s Minutos ---" % (TIEMPO))

tabla1

"""### 4.2 Regresión Lineal Multiple"""

# Monitoreo del tiempo de procesamiento
import time

start_time = time.time()

print('-------------------INICIO PROCESAMIENTO-----------------')

#Selecciono predictores
X = df1.to_numpy()


#Selecciono target
y = df2.iloc[:,0].to_numpy()

#separo datos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size = 0.3, random_state=4444)

## se escalan los datos
escalar = MinMaxScaler(feature_range=(-1,1))
X_train = escalar.fit_transform(X_train)
X_test = escalar.fit_transform(X_test)

#MODELO DE REGRESION LINEAL MULTIPLE
LR_multiple = linear_model.LinearRegression(n_jobs=-1)

cv_results = cross_validate(LR_multiple, X_train, y_train, cv=10,n_jobs=-1,
              scoring=('neg_root_mean_squared_error', 'r2',
                       'neg_mean_squared_error', 'neg_mean_absolute_error'),
              return_train_score=True)

#Resultados Metricas
print('--------------------------------------------------------------')
print('Resultados RMSE')
print("RMSE_TRAIN: %0.3f" % (cv_results['train_neg_root_mean_squared_error'].mean()))
print("RMSE_TEST: %0.3f" % (cv_results['test_neg_root_mean_squared_error'].mean()))
print('--------------------------------------------------------------')

print('--------------------------------------------------------------')
print('Resultados R2')
print("R2_TRAIN: %0.3f" % (cv_results['train_r2'].mean()))
print("R2_TEST: %0.3f" % (cv_results['test_r2'].mean()))
print('--------------------------------------------------------------')

print('--------------------------------------------------------------')
print('Resultados MSE')
print("MSE_TRAIN: %0.3f" % (cv_results['train_neg_mean_squared_error'].mean()))
print("MSE_TEST: %0.3f" % (cv_results['test_neg_mean_squared_error'].mean()))
print('--------------------------------------------------------------')

print('--------------------------------------------------------------')
print('Resultados MAE')
print("MAE_TRAIN: %0.3f" % (cv_results['train_neg_mean_absolute_error'].mean()))
print("MAE_TEST: %0.3f" % (cv_results['test_neg_mean_absolute_error'].mean()))
print('--------------------------------------------------------------')

print('--------------------------------------------------------------')
print('PROCESAMIENTO FINALIZADO EXITOSAMENTE!!!')
print('--------------------------------------------------------------')

TIEMPO = (time.time() - start_time)/60
print("--- %s Minutos ---" % (TIEMPO))

"""### 4.3 Regresión Lineal Multiple vs Regularización Ridge y Lasso"""

# Monitoreo del tiempo de procesamiento
import time

start_time = time.time()

print('-------------------INICIO PROCESAMIENTO-----------------')

# Seleccionar predictores y target
X = df1.values
y = df2.values

# Escalar los datos
scaler = MinMaxScaler(feature_range=(-1, 1))
X_scaled = scaler.fit_transform(X)

# Dividir los datos en entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=4444)

# Modelo de Regresión Lineal Normal
lm = LinearRegression()
lm.fit(X_train, y_train)
y_pred_lm = lm.predict(X_test)
mse_lm = mean_squared_error(y_test, y_pred_lm)
r2_lm = r2_score(y_test, y_pred_lm)

# Modelo de Regresión Ridge
ridge = Ridge(alpha=0.5)
ridge.fit(X_train, y_train)
y_pred_ridge = ridge.predict(X_test)
mse_ridge = mean_squared_error(y_test, y_pred_ridge)
r2_ridge = r2_score(y_test, y_pred_ridge)

# Modelo de Regresión Lasso
lasso = Lasso(alpha=0.5)
lasso.fit(X_train, y_train)
y_pred_lasso = lasso.predict(X_test)
mse_lasso = mean_squared_error(y_test, y_pred_lasso)
r2_lasso = r2_score(y_test, y_pred_lasso)

# Imprimir resultados
print("Regresión Lineal Normal:")
print("MSE:", mse_lm)
print("R^2:", r2_lm)
print()

print("Regresión Ridge:")
print("MSE:", mse_ridge)
print("R^2:", r2_ridge)
print()

print("Regresión Lasso:")
print("MSE:", mse_lasso)
print("R^2:", r2_lasso)

print('--------------------------------------------------------------')
print('PROCESAMIENTO FINALIZADO EXITOSAMENTE!!!')
print('--------------------------------------------------------------')

TIEMPO = (time.time() - start_time)/60
print("--- %s Minutos ---" % (TIEMPO))

"""## Conclusiones

- La carga de datos es un proceso estandar, esto solo cambia dependiendo de la fuente de los datos, la finalidad es la misma, tener un dataframe con información.

- La limpieza y preparación de los datos tomaron aproximadamente el 80% del tiempo para el desarrollo del trabajo, contrastando con un 20% para realizar la parte de Machine Learning.

- El tiempo de procesamiento no fue impedimento aplicando los diferentes algoritmos de Regresión Lineal.

- Los mejores desempeños en la Regresión Lineal Simple se obtuvieron con las variables de entrada "TotalQuantity" y "TotalProductosUnicos".

- En la Regresión Lineal Multiple se consiguieron buenos desempeños aplicando la regresión lineal y sus variantes con regularización Ridge y Lasso, entre estos 3 algoritmos no se encontraron diferencias notorias en los desempeños obtenidos.
"""
