#-------------------------------------------------------------------------------------------------------#
import ipynb 
import sys
import os
import collections
from os import listdir
from os.path import isfile, join

# Biblioteca de download de arquivos
import wget

#Biblioteca de manilpulacao de dataframe
import pandas as pd
from pandas import *
import numpy as np

# Visualizacao de dados
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.pyplot import *
import seaborn as sns
from termcolor import colored
from PIL import Image
from IPython.display import display, Image , HTML
from django.core.files.base import ContentFile

# Decode 
import base64
import collections
from django.core.files.base import ContentFile
import datetime as datetime 
from datetime import date, datetime

# Json
import json as js
from pandas.io.json import json_normalize

# panda data frame
df = pd.DataFrame()
pd.set_option('display.max_colwidth', -1)
# Cria um dataframe colection
df = {} 
# Cria indice de cada aba
abas = {} 

# Listas
csv_import_list = {}
xlsx_import_list = {}
IMGS = []


coluna = ""

#*******************************************************************************************************#

# Download files from Gdrive

#*******************************************************************************************************#


def get_file_gdrive( file_id, file_name, type_import = "" ):
  if type_import == "byid":
   file_id = file_id    
  else :
    file_id = file_id.replace('https://drive.google.com/open?id=','')  
  remove_file(file_name)
  return exec('wget.download(url="https://drive.google.com/uc?authuser=0&id=' + file_id + '&export=download",out="' + file_name + '")')


#*******************************************************************************************************#

# Delete local files

#*******************************************************************************************************#


def remove_file(file_reference):
  # Funcao de limpeza de todos os arquivos do ambiente ( CUIDADO !!!)
  import os
  from os import listdir
  from os.path import isfile, join
  local_files = [f for f in listdir() if isfile(f)]
  for file in local_files:
   if(file_reference == file):
    os.remove(file)



#*******************************************************************************************************#

# Import csv DataFrames

#*******************************************************************************************************#


def df_csv(file_name, field_separator  , decimal_separator , file_encond ):
    arquivo_csv = pd.DataFrame(pd.read_csv(file_name, encoding = file_encond, delimiter = field_separator , decimal = decimal_separator))
    return arquivo_csv



#*******************************************************************************************************#

# Import xlsx DataFrames

#*******************************************************************************************************#

def df_xlsx(file_name):
    # Cria um dataframe colection
    df_files = {} 
    # Cria indice de cada aba
    abas = {} 
    result_set = pd.read_excel(file_name, sheet_name=None).keys()
    lista_colunas = []
    for coluna in result_set:
        lista_colunas.append({'Abas':coluna})
    data_frame_keys = DataFrame(lista_colunas)
    abas[file_name] = data_frame_keys
    # Importa todas as abas do arquivo xlsx
    for aba in abas[file_name]["Abas"]:
      df_files[file_name,aba] = pd.read_excel(file_name, sheet_name=aba)

    return  df_files 
     


#*******************************************************************************************************#

# Import all lists of files into DataFrames

#*******************************************************************************************************#
def import_dataframes(csv_import_list, xlsx_import_list):
  for key in csv_import_list:
    data_frame = csv_import_list[key]["data_frame"]
    file_name = csv_import_list[key]["file_name"]
    link_gdrive = csv_import_list[key]["link_gdrive"]
    field_separator = csv_import_list[key]["field_separator"]
    decimal_separator = csv_import_list[key]["decimal_separator"]
    file_encond = csv_import_list[key]["file_encond"]
    get_file_gdrive(link_gdrive, file_name)
    df[data_frame] = df_csv(file_name,field_separator, decimal_separator , file_encond)

  for key in xlsx_import_list:
    data_frame = xlsx_import_list[key]["data_frame"]
    file_name = xlsx_import_list[key]["file_name"]
    link_gdrive = xlsx_import_list[key]["link_gdrive"]
    get_file_gdrive(link_gdrive, file_name)
    df_temp = df_xlsx(file_name)
    for key in df_temp :
     df[data_frame + "#" + key[1] ] = df_temp[key]
  return df   





#*******************************************************************************************************#

# Analise DataFrame Colluns

#*******************************************************************************************************#

def image_formatter(im):
    data_uri = base64.b64encode(open(im, 'rb').read()).decode('utf-8').replace('\n', '')
    img_tag = '<img height="400" width="700" src="data:image/png;base64,%s">' % data_uri
    return img_tag

def IsFloat(s):
  try: 
   s = s.astype(float)
   return True
  except ValueError:
   return False

def IsInt(s):
  try: 
   f = pd.to_numeric(s, errors='coerce')
   z = pd.to_numeric(s, errors='coerce').round(0).astype(int)
   k = []
   k = abs(f - z)
   if len(k.nonzero()[0]) > 0 :
    return False
   else :
    return True
  except ValueError:
   return False
 
def tipo_variavel(s):
  if IsDate(s):
      return "Datetime"
  else :
    if IsBool(s) : 
      return "Boolean"
    else: 
      if IsInt(s) : 
        return "Integer"
      else: 
        if IsFloat(s) :
         return "Float"
        else:
          return "String"
    
def IsConst(s) :
  if tipo_variavel(s) != "Str":
   if sum(abs(s)) / len(s) != 0 :
    return False
   else :
    return True

def IsDate(s):
  if str(type(s[0])) == "<class 'pandas._libs.tslib.Timestamp'>" :
    return True
  else:
    #print(str(type(s[0])) )
    return False
  
def IsBool(s):
  if str(type(s[0])) == "<class 'bool'>" :
    return True
  else:
    #print(str(type(s[0])) )
    return False
  
  
def analise_exploratoria(frame):
  lista_colunas = []
  for coluna in frame:
      sns.set(font_scale=1.2)
      tipo = tipo_variavel(frame[coluna])
      #print(tipo + "_" + coluna)
      
      if tipo == "Datetime" :
          dado = frame[coluna].replace(np.nan,0)
          dado = dado.apply(lambda x: str(x.year) + "_" + str(x.month).zfill(2))
          dt_list = []
          y_values = []
          for key in collections.Counter(dado).most_common(40):
            #print(key)
            dt_list.append({ "Freq" : key[0], "Datas" : key[1] })
          locs, labels = plt.xticks()
          plt.setp(labels, rotation=300)
          bplot = sns.barplot(x="Freq", y="Datas", data=DataFrame(dt_list))
          bplot.set(xlabel="", ylabel='Freq. top 40')
          bplot.figure.savefig(coluna + ".jpg", format='jpeg', dpi=100)
          plt.clf()
          imagem = image_formatter(coluna + ".jpg")

      else:
         if (tipo == "Boolean") :
          plt.figure()
          dado = frame[coluna].replace(np.nan,0)
          bplot = sns.distplot( dado.astype(int) , vertical=False , kde=False, norm_hist=False , label='big')
          bplot.set(xlabel="", ylabel='Freq.')
          bplot.figure.savefig(coluna + ".jpg", format='jpeg', dpi=100)
          plt.clf()
          imagem = image_formatter(coluna + ".jpg")
         else:
          if (tipo == "Integer") :
            plt.figure()
            dado = frame[coluna].replace(np.nan,0)
            bplot = sns.distplot( dado.astype(int) , vertical=False , kde=False, norm_hist=False , label='big')
            bplot.set(xlabel="", ylabel='Freq.')
            bplot.figure.savefig(coluna + ".jpg", format='jpeg', dpi=100)
            plt.clf()
            imagem = image_formatter(coluna + ".jpg")
          else :
            if (tipo == "Float") :
              plt.figure()
              dado = frame[coluna].replace(np.nan,0)
              bplot = sns.distplot( dado.astype(np.float32) , vertical=False , kde=False, norm_hist=False , label='big')
              bplot.set(xlabel="", ylabel='Freq.')
              bplot.figure.savefig(coluna + ".jpg", format='jpeg', dpi=100)
              plt.clf()
              imagem = image_formatter(coluna + ".jpg")
            else :
              #String
              dt_list = []
              y_values = []
              for key in collections.Counter(frame[coluna]).most_common(40):
                #print(key)
                dt_list.append({ "X_labels" : key[0], "Y_values" : key[1] })
              locs, labels = plt.xticks()
              plt.setp(labels, rotation=300)
              bplot = sns.barplot(x="X_labels", y="Y_values", data=DataFrame(dt_list))
              bplot.set(xlabel="", ylabel='Freq. top 40')
              bplot.figure.savefig(coluna + ".jpg", format='jpeg', dpi=100)
              plt.clf()
              imagem = image_formatter(coluna + ".jpg")


      lista_colunas.append({'01_Colunas':coluna, '02_Tipo' : tipo_variavel(frame[coluna]), '03_Analise' : imagem})
  return DataFrame(lista_colunas) 
    

def analise_coluna(frame_keys, i):
    return HTML(DataFrame(frame_keys.iloc[i]).to_html(formatters={'image': image_formatter}, escape=False))


print("Biblioteca de funções úteis importada com sucesso!")














