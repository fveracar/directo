#!apt-get update # to update ubuntu to correctly run apt install
#!apt install chromium-chromedriver #relacionado con las funciones de captura de pantalla
#!cp /usr/lib/chromium-browser/chromedriver /usr/bin #relacionado con las funciones de captura de pantalla
import requests
#from requests_html import HTMLSession
import pandas as pd
import numpy as np
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import re
import datetime as dt
import pytz as tz #timezone
import streamlit as st
import gspread
import json
import tempfile
import os
import time
from tld import get_fld
import urllib.request
import sys
sys.path.insert(0,'/usr/lib/chromium-browser/chromedriver')
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image
from keybert import KeyBERT


############################   DECLARACIÓN DE FUNCIONES  ###############################
########################################################################################

#========> FUNCIÓN 1 <===========
#Esta función envía un email

def envio_email(r):
  from email.mime.text import MIMEText
  from email.mime.application import MIMEApplication
  from email.mime.multipart import MIMEMultipart
  from smtplib import SMTP
  import smtplib
  import sys

  recipients = [email_destinatario] 
  emaillist = [elem.strip().split(',') for elem in recipients]
  msg = MIMEMultipart()
  msg['Subject'] = 'ALERTA: "' + query_list[i] + '" ' + r
  msg['From'] = st.secrets["email_remitente"]
  password = st.secrets["password_email_remitente"]

  html = """\
  <html>
    <head></head>
    <body>
      <h1>
      ALERTA: "{query_list}" {r}
      </h1>
    </body>
  </html>
  """.format(query_list=query_list[i], r=r)
  
  part1 = MIMEText(html, 'html')
  msg.attach(part1)

  server = smtplib.SMTP('smtp.gmail.com', 587)
  server.starttls()
  server.login(msg['From'], password)
  server.sendmail(msg['From'], emaillist , msg.as_string())

#=============>FUNCIÓN 2 <===================
#Función para realizar la petición de rastreo y extraer los datos del rastreo y ejecutar la función datos_rastreo para los resultados de búsqueda.
def rastreo_busqueda (elemento_html, nombre_expander, user_agent):
  #Construcción de la URL de búsqueda para rastrear los resultados
  url= 'https://www.google.es/search?q=' + query_list[i] + '&gl=' + gl + '&pws=' + pws + '&num=' + add_selectbox_top + '&hl=' + hl + '&uule=' + uule[j][0] + ''    
  
  resultados_busqueda = [] #creamos un array vacío para introducir después cada resultado de búsqueda 
  
  headers = {"user-agent" : user_agent}

  #Declaración para saber si hay errores 
  try:
      session = HTMLSession()
      response = session.get(url, headers=headers)
      
  except requests.exceptions.RequestException as e:
      print(e)

  #Petición para los resultados de búsqueda en Móvil
  resultado = response.html.xpath(elemento_html) #buscamos la clase que contiene los resultados de búsqueda

  #bucle para incluir cada resultado de búsqueda en el array
  for r in range(len(resultado)):
      x = resultado[r]
      resultados_busqueda.append(x)

  df_resultados = pd.DataFrame (resultados_busqueda, columns=['Resultados'],) #convertimos el array que contiene los resultados de búsqueda en un dataframe

  lista_wk = ss.worksheets() #sacamos una lista de todas las hojas que hay en la spreadsheet
  lista_titulos_wk = [worksheet.title for worksheet in lista_wk] #creamos una lista con todos los títulos de cada hoja dentro de la spreadsheet, ya que la anterior lista contiene más datos además del título.

  #verificamos si ya están creadas las hojas correspondientes en la spreadsheet de cada cansulta que se está rastreando
  if query_list[i] + " - " + uule[j][1] not in lista_titulos_wk: #si la hoja de la consulta no está en la lista de hojas entonces la creamos.
    ss.add_worksheet(title=query_list[i] + " - " + uule[j][1], rows= 1000 , cols= 24)

  #Definimos las hojas donde vamos a trasladar los datos de cada consulta
  wk = ss.worksheet(title=query_list[i] + " - " + uule[j][1]) #hoja donde vamos a trasladar los datos del dataframe de los resultados de búsqueda
  df_resultados = pd.DataFrame (resultados_busqueda, columns=['Resultados'],) #convertimos el array que contiene los resultados de búsqueda en un dataframe
  
  #llamamos a la función datos_rastreo
  datos_rastreo(
      hoja_resultados= wk,  
      df_r = df_resultados, 
      texto_resultado_query='no se ha encontrado en los resultados de búsqueda', 
      nombre_expander= nombre_expander,
      url=url,
      user_agent=user_agent,
      )

#=============>FUNCIÓN 3 <===================
#Función para realizar la petición de rastreo y extraer los datos del rastreo y ejecutar la función datos_rastreo para los resultados de carrusel.
def rastreo_carrusel (elemento_html, nombre_expander, user_agent):
  #Construcción de la URL de búsqueda para rastrear los resultados
  url= 'https://www.google.es/search?q=' + query_list[i] + '&gl=' + gl + '&pws=' + pws + '&num=' + add_selectbox_top + '&hl=' + hl + '&uule=' + uule[j][0] + ''    
  
  resultados_busqueda = [] #creamos un array vacío para introducir después cada resultado de búsqueda 
  
  headers = {"user-agent" : user_agent}
  
  #Declaración para saber si hay errores 
  try:
      session = HTMLSession()
      response = session.get(url, headers=headers)
      
  except requests.exceptions.RequestException as e:
      print(e)

  #Petición para los resultados de búsqueda en Móvil
  resultado = response.html.xpath(elemento_html) #buscamos la clase que contiene los resultados de búsqueda

  #bucle para incluir cada resultado de búsqueda en el array
  for r in range(len(resultado)):
      x = resultado[r]
      resultados_busqueda.append(x)

  df_resultados = pd.DataFrame (resultados_busqueda, columns=['Resultados'],) #convertimos el array que contiene los resultados de búsqueda en un dataframe

  lista_wk = ss.worksheets() #sacamos una lista de todas las hojas que hay en la spreadsheet
  lista_titulos_wk = [worksheet.title for worksheet in lista_wk] #creamos una lista con todos los títulos de cada hoja dentro de la spreadsheet, ya que la anterior lista contiene más datos además del título.

  #verificamos si ya están creadas las hojas correspondientes en la spreadsheet de cada consulta que se está rastreando
  if query_list[i] + " - " + uule[j][1] not in lista_titulos_wk: #si la hoja de la consulta no está en la lista de hojas entonces la creamos.
    ss.add_worksheet(title=query_list[i] + " - " + uule[j][1], rows= 1000 , cols= 24)

  #Definimos las hojas donde vamos a trasladar los datos de cada consulta
  wk = ss.worksheet(title=query_list[i] + " - " + uule[j][1]) #hoja donde vamos a trasladar los datos del dataframe de los resultados de búsqueda
  df_resultados = pd.DataFrame (resultados_busqueda, columns=['Resultados'],) #convertimos el array que contiene los resultados de búsqueda en un dataframe
  
  #llamamos a la función datos_rastreo
  datos_rastreo(
      hoja_resultados= wk,  
      df_r = df_resultados, 
      texto_resultado_query='no se ha encontrado en los resultados de búsqueda', 
      nombre_expander= nombre_expander,
      url=url,
      user_agent=user_agent,
      )

#========> FUNCIÓN 4 <===========
#Esta función actualiza la spreadsheet con los resultados y pinta dichos resultados + entidades + factores SEO + Capturas en streamlit
def datos_rastreo (hoja_resultados, df_r, texto_resultado_query, nombre_expander, url, user_agent):
  #limpiamos el rango donde almacenamos los resultados del rastreo en la spreadsheet
  rango_resultados = hoja_resultados.range('A1:B50')
  for celda in rango_resultados:
    celda.value = ''
  hoja_resultados.update_cells(rango_resultados) 

  #pasamos los datos del dataframe a la hoja
  df_r.index = df_r.index + 1 #establecemos el índice del Dataframe en 1 en vez de en 0 que es el que viene por defecto.
  set_with_dataframe(hoja_resultados,df_r, row=1, col=1, include_index=True) #pasamos los datos del dataframe de los resultados de búsqueda a la hoja correspondiente
  
  #condicional para actualizar la spreadsheet con los resultados y pintar dichos resultados + entidades + factores SEO + Capturas en streamlit en función del tipo de búsqueda y dispositivo elegido.
  if nombre_expander == nombre_expander_b_m:
    update_hoja_resultados (hoja_resultados=hoja_resultados, df_r=df_r, texto_resultado_query=texto_resultado_query, nombre_expander=nombre_expander, url=url, num_col_hora=3, num_col_query=4, num_col_resultado=5, rango='C:E', indice=3)
    if df_r.empty != True:
      if entidades_active == True: 
        entidades(df_r=df_r, contenido_json=contenido_json)
      comparativa_seo(query=query_list[i], df_resultados=df_r, user_agent=user_agent)
    capturaMobile(url=url)
  elif nombre_expander == nombre_expander_c_m:
    update_hoja_resultados (hoja_resultados=hoja_resultados, df_r=df_r, texto_resultado_query=texto_resultado_query, nombre_expander=nombre_expander,url=url, num_col_hora=6, num_col_query=7, num_col_resultado=8, rango='F:H', indice=6)
    if df_r.empty != True: 
      if entidades_active == True: 
        entidades(df_r=df_r, contenido_json=contenido_json)
      comparativa_seo(query=query_list[i], df_resultados=df_r, user_agent=user_agent)
    capturaMobile(url=url)
  elif nombre_expander == nombre_expander_b_d:
    update_hoja_resultados (hoja_resultados=hoja_resultados, df_r=df_r, texto_resultado_query=texto_resultado_query, nombre_expander=nombre_expander,url=url, num_col_hora=9, num_col_query=10, num_col_resultado=11, rango='I:K', indice=9)
    if df_r.empty != True: 
      if entidades_active == True: 
        entidades(df_r=df_r, contenido_json=contenido_json)
      comparativa_seo(query=query_list[i], df_resultados=df_r, user_agent=user_agent)
    capturaDesktop(url)
  elif nombre_expander == nombre_expander_c_d:
    update_hoja_resultados (hoja_resultados=hoja_resultados, df_r=df_r, texto_resultado_query=texto_resultado_query, nombre_expander=nombre_expander,url=url, num_col_hora=12, num_col_query=13, num_col_resultado=14, rango='L:N', indice=12)
    if df_r.empty != True: 
      if entidades_active == True: 
        entidades(df_r=df_r, contenido_json=contenido_json)
      comparativa_seo(query=query_list[i], df_resultados=df_r, user_agent=user_agent)
    capturaDesktop(url)


#===========>FUNCIÓN 5 <===============
#Función anidada dentro de la función almacenamiento rastreo. Función para actualizar las celdas de la hoja de spreadsheet con los datos obtenidos del rastreo.
def update_hoja_resultados (hoja_resultados, df_r, texto_resultado_query, nombre_expander, num_col_hora, num_col_query, num_col_resultado, rango, indice, url):
  
  tabla_resultados = hoja_resultados.batch_get(['A2:B'])

  if len(tabla_resultados[0]) == 0:
    pos=0
    st.write('no ha devuelto resultados o no existe carrusel para esta búsqueda')
    resultado_query = texto_resultado_query
  else:
    for resultado in tabla_resultados[0]:
      patron_limpio=patron_seleccionado[0][2:len(patron_seleccionado[0])-2]
      if patron_limpio in resultado[1]:
        st.write(nombre_expander)
        st.write(f'Posición:{resultado[0]} - Url:{resultado[1]}')
        pos = resultado[0]
        resultado_query=resultado[1]
        break
      else:
        pos=0
        resultado_query = texto_resultado_query

  #si no está posicionando enviamos una alerta por email
  if pos==0 and email_destinatario != "":
    envio_email(resultado_query)
  
  #Almacenamiento histórico de posiciones de los resultados
  now = tz.utc.localize(dt.datetime.now()) #almacenamos la hora actual
  hora_madrid = now.astimezone(tz.timezone('Europe/Madrid'))#almacenamos la hora de madrid.
  if query_list[i] not in hoja_resultados.col_values(indice+1): #si la query no está incluida en la columna de la tabla correspondiente
    hoja_resultados.update_cell(1, num_col_hora, 'Hora') #creamos la columna hora en la primera columna vacía
    hoja_resultados.update_cell(1, num_col_query, query_list[i]) #a continuación creamos la columna para registrar la posición con el nombre de la query
    hoja_resultados.update_cell(1, num_col_resultado, 'Página posicionada') # a continuación creamos la columna para registrar el resultado de abc
    hoja_resultados.update_cell(2, num_col_hora, str(hora_madrid.strftime('%Y-%m-%d %H:%M:%S')))#a continuación registramos la hora en su columna correspondiente
    hoja_resultados.update_cell(2, num_col_query, pos) # a continuación registramos la posicion en la fila y columna correspondiente. 
    hoja_resultados.update_cell(2, num_col_resultado, resultado_query) #a continuación registramos el resultado de abc en la fila y columna correspondiente.
  else: #si está incluida
    valores_col_query = hoja_resultados.col_values(indice) #Averiguamos la cantidad de valores que hay en la columna para saber cual es la siguiente celda vacía
    hoja_resultados.update_cell(len(valores_col_query)+1, num_col_hora, str(hora_madrid.strftime('%Y-%m-%d %H:%M:%S'))) #registramos la hora en la misma fila y en la columna anterior.
    hoja_resultados.update_cell(len(valores_col_query)+1, num_col_query, pos) #actualizamos la siguiente celda vacía en la columna de la query el valor de la posición
    hoja_resultados.update_cell(len(valores_col_query)+1, num_col_resultado, resultado_query) #registramos el snippet
  
  df_historico = pd.DataFrame(hoja_resultados.get(rango)) #definimos el dataframe con los datos del histórico

  #CREACIÓN DE TABLAS Y GRÁFICOS RESULTADOS DE BÚSQUEDA
  df_historico.columns = df_historico.iloc[0]
  dfFinal = df_historico.drop([0], axis=0)
  n_filas=len(dfFinal)-15 #restamos el total de filas menos el número de filas que queremos mostrar en la gráfica y obtendremos el número de filas que queremos eliminar
  dfFinal_grafica=dfFinal.iloc[n_filas:] #eliminamos las n filas primeras donde n es el resultado de drop_filas
  with st.expander(nombre_expander, expanded=False):
    st.text('Posición último rastreo: ' + str(pos)+ '\nla url de búsqueda es: ' + url)
    st.subheader('Resultados búsqueda')
    st.table(df_r)#Pintamos el dataframe con los resultados de la última búsqueda
    st.subheader('Histórico de posiciones')
    st.write(dfFinal) #pintamos el dataframe del histórico
    st.subheader('Gráfico de posiciones')
    st.vega_lite_chart(dfFinal_grafica,{
        'height': 300,
        #'width': 800,
        'mark': {'type':'line', 'point':True, 'tooltip':True},
        'encoding':{
            'x': {'field':'Hora','axis':{'labelAngle': '-45'}, 'sort':'false'},
            'y': {'field': query_list[i], 'type':'quantitative'}
        },
    },use_container_width = True)

#===========>FUNCIÓN 6 <===============
#Obtención entidades
def entidades (df_r, contenido_json):
  from google.cloud import language_v1
  from google.cloud.language_v1 import enums

  from google.cloud import language
  from google.cloud.language import types

  import matplotlib.pyplot as plt
  from matplotlib.pyplot import figure

  #convertimos el dict en un JSON
  uploaded_file = json.dumps(contenido_json)

  #guardamos el JSON en un archivo temporal para poder llamar al path donde se encuentra el archivo JSON en GOOGLE_APPLICATION_CREDENTIALS
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as fp:
    #fp.write(uploaded_file.getvalue())
    fp.write(uploaded_file)
  try:
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = fp.name
    #st.write('Found', fp.name)
    with open(fp.name) as a:
      #st.write(a.read())
      client = language_v1.LanguageServiceClient()
  finally:
    os.unlink(fp.name)

  import requests
  from requests_html import HTMLSession

  url = df_r.iloc[0]['Resultados']
  try:
      session = HTMLSession()
      response = session.get(url)
      
  except requests.exceptions.RequestException as e:
      st.write(e)

  #dominios objetivo
  dominio_abc = 'abc.es'
  dominio_voz = 'lavozdigital.es'
  dominio_hoy = 'hoy.es'
  dominio_rioja = 'larioja.com'
  dominio_correo = 'elcorreo.com'
  dominio_norteCastilla = 'elnortedecastilla.es'
  dominio_diarioVasco = 'diariovasco.com'
  dominio_comercio = 'elcomercio.es'
  dominio_ideal = 'ideal.es'
  dominio_sur = 'diariosur.es'
  dominio_provincias = 'lasprovincias.es'
  dominio_montanes = 'eldiariomontanes.es'
  dominio_verdad = 'laverdad.es'
  dominio_leon = 'leonoticias.com'
  dominio_burgos = 'burgosconecta.es'

  #dominios competencia
  dominio_mundo = 'elmundo.es'
  dominio_pais = 'elpais.com'
  dominio_vanguardia = 'lavanguardia.com'
  dominio_noticiasburgos = 'noticiasburgos.es'
  dominio_canal54 = 'canal54.es'
  dominio_burgosdeporte = 'burgosdeporte.com'
  dominio_revistaforofos = 'revistaforofos.com'
  dominio_deia = 'deia.eus'
  dominio_noticiasdealava = 'noticiasdealava.eus'
  dominio_gasteizhoy = 'gasteizhoy.com'
  dominio_laopiniondemurcia = 'laopiniondemurcia.es'
  dominio_murciaplaza = 'murciaplaza.com'
  dominio_cadenaser = 'cadenaser.com'
  dominio_eldiario = 'eldiario.es'
  dominio_tribunavalladolid = 'tribunavalladolid.com'
  dominio_diariopalentino = 'diariopalentino.es'
  dominio_tribunapalencia = 'tribunapalencia.com'
  dominio_eldiasegovia = 'eldiasegovia.es'
  dominio_segoviaudaz = 'segoviaudaz.es'
  dominio_segoviaaldia = 'segoviaaldia.es'
  dominio_lacronicadesalamanca = 'lacronicadesalamanca.com'
  dominio_lagacetadesalamanca = 'lagacetadesalamanca.es'
  dominio_salamanca24horas = 'salamanca24horas.com'
  dominio_salamancartvaldia = 'salamancartvaldia.es'
  dominio_diariodeleon = 'diariodeleon.es' #devuelve vacio
  dominio_ileon = 'ileon.com'
  dominio_lanuevacronica = 'lanuevacronica.com'
  dominio_digitaldeleon = 'digitaldeleon.com'
  dominio_tribunaleon = 'tribunaleon.com'
  dominio_diariodeburgos = 'diariodeburgos.es'
  dominio_burgosnoticias = 'burgosnoticias.com'
  dominio_diariodevalladolid_elmundo = 'diariodevalladolid.elmundo.es'
  dominio_eladelantado = 'eladelantado.com'
  dominio_tribunasalamanca = 'tribunasalamanca.com'
  dominio_eldiadevalladolid = 'eldiadevalladolid.com'

  #elementos HTML para la extracción del texto de la noticia
  elemento_abc = '.cuerpo-texto > p'
  elemento_ppll = '.voc-paragraph'
  elemento_mundo = '.content > p'
  elemento_pais = '.article_body > p'
  elemento_vanguardia = '.amp-scribble-content > p'
  elemento_burgosnoticias = '#zonaAmpliarTexto1 > p'
  elemento_noticiasburgos = '.post > p'
  elemento_canal54 = '.fl-rich-text > p'
  elemento_burgosdeporte = '.td-post-content > p'
  elemento_revistaforofos = '.theiaPostSlider_preloadedSlide > p'
  elemento_deia_noticiasdealava = '.cuerpo_noticia >span > p'
  elemento_gasteizhoy = '.articulotexto > p'
  elemento_laopiniondemurcia = '.article-body > p'
  elemento_murciaplaza = '.html-content > p'
  elemento_cadenaser = '.cuerpo > p'
  elemento_eldiario = '.second-col > p'
  elemento_tribunavalladolid_tribunapalencia_tribunaleon_tribunasalamanca = '.article--content > p'
  elemento_diariopalentino_eldiasegovia_diariodeburgos_eldiadevalladolid = '.CuerpoNoticiaFicha > span > p'
  elemento_segoviaudaz = '.td-post-content > p'
  elemento_segoviaaldia = '.new_text > p'
  elemento_lacronicadesalamanca = '.entry-content > p'
  elemento_lagacetadesalamanca = '.paragraph > p'
  elemento_salamanca24horas = '.c-mainarticle__body > p'
  elemento_salamancartvaldia = '.e_texto > p'
  elemento_diariodeleon = '.content-body > div > p'
  elemento_ileon_burgosnoticias = '#zonaAmpliarTexto1 > p'
  elemento_lanuevacronica = '.parrafo'
  elemento_digitaldeleon = '.post-content-bd > p'
  elemento_diariodevalladolid_elmundo = '.content-data'
  elemento_eladelantado = '.td-post-content > p'
  
    
  with st.expander('Entidades'):
    st.header('Texto de la página')
    st.write (url)
    
    #Realizamos un condicional para saber de qué dominio se trata la URL y extraer el elemento correspondiente a ese dominio.
    if dominio_abc in url:
      p =  response.html.find(elemento_abc) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_mundo in url:
      p =  response.html.find(elemento_mundo) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_pais in url:
      p =  response.html.find(elemento_pais) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_vanguardia in url:
      p =  response.html.find(elemento_vanguardia) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_voz in url:
      p =  response.html.find(elemento_abc) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_noticiasburgos in url:
      p =  response.html.find(elemento_noticiasburgos) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_canal54 in url:
      p =  response.html.find(elemento_canal54) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_burgosdeporte in url:
      p =  response.html.find(elemento_burgosdeporte) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_revistaforofos in url:
      p =  response.html.find(elemento_revistaforofos) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_deia in url or dominio_noticiasdealava in url:
      p =  response.html.find(elemento_deia_noticiasdealava) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_gasteizhoy in url:
      p =  response.html.find(elemento_gasteizhoy) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_laopiniondemurcia in url:
      p = response.html.find(elemento_laopiniondemurcia) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_murciaplaza in url:
      p = response.html.find(elemento_murciaplaza) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_cadenaser in url:
      p = response.html.find(elemento_cadenaser) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_eldiario in url:
      p = response.html.find(elemento_eldiario) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_tribunavalladolid in url or dominio_tribunapalencia in url or dominio_tribunaleon in url or dominio_tribunasalamanca in url:
      p =  response.html.find(elemento_tribunavalladolid_tribunapalencia_tribunaleon_tribunasalamanca) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_diariopalentino in url or dominio_eldiasegovia in url or dominio_diariodeburgos in url or dominio_eldiadevalladolid in url:
      p =  response.html.find(elemento_diariopalentino_eldiasegovia_diariodeburgos_eldiadevalladolid) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_segoviaudaz in url:
      p =  response.html.find(elemento_segoviaudaz) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_segoviaaldia in url:
      p =  response.html.find(elemento_segoviaaldia) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_lacronicadesalamanca in url:
      p =  response.html.find(elemento_lacronicadesalamanca) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_lagacetadesalamanca in url:
      p =  response.html.find(elemento_lagacetadesalamanca) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_salamanca24horas in url:
      p =  response.html.find(elemento_salamanca24horas) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.  
    elif dominio_salamancartvaldia in url:
      p =  response.html.find(elemento_salamancartvaldia) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.  
    elif dominio_diariodeleon in url:
      p =  response.html.find(elemento_diariodeleon) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_ileon in url or dominio_burgosnoticias in url:
      p =  response.html.find(elemento_ileon_burgosnoticias) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_lanuevacronica in url:
      p =  response.html.find(elemento_lanuevacronica) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_digitaldeleon in url:
      p =  response.html.find(elemento_digitaldeleon) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_diariodevalladolid_elmundo in url:
      p =  response.html.find(elemento_diariodevalladolid_elmundo) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_eladelantado in url:
      p =  response.html.find(elemento_eladelantado) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable.
    elif dominio_hoy in url or dominio_rioja in url or dominio_correo in url or dominio_norteCastilla in url or dominio_diarioVasco in url or dominio_comercio in url or dominio_ideal in url or dominio_sur in url or dominio_provincias in url or dominio_montanes in url or dominio_verdad in url or dominio_leon in url or dominio_burgos in url:
      p =  response.html.find(elemento_ppll) #buscamos los elementos <p> de dentro de la clase cuerpo-texto.
      array = [] #creamos un array vacio.
      for i in range(len(p)): #recorremos todos los <p> de dentro de la clase cuerpo-texto para almacenarlos en el array vacio que acabamos de crear
        array.append(p[i].text)
      texto = " ".join(array) #concatenamos todos los textos (valores) del array para almacenar el texto completo de la noticia en una variable. 
    else:
      st.write('El dominio de la URL: ' + url + ' \nno se encuentra entre nuestros dominios objetivo o la competencia directa, y por lo tanto, no se puede extraer el texto. \nSi deseas incluir este dominio para su análisis, por favor, ponte en contacto con fvera@vocento.com')
      texto = ''
      
    if texto != '':    
      st.write(texto)

      col1, col2 = st.beta_columns(2)

      with col1:
        st.header('Entidades')
        # tipos disponibles: PLAIN_TEXT, HTML
        type_ = enums.Document.Type.PLAIN_TEXT

        #opcional. si no se define el idioma se detecta automáticamente
        language = "es"
        document = {"content": texto, "type": type_, "language": language}

        # valores disponibles: NONE, UTF8, UTF16, UTF32
        encoding_type = enums.EncodingType.UTF8

        response = client.analyze_entities(document, encoding_type=encoding_type)

        # Bucle para recoger la entidades devueltas por la API
        for entity in response.entities:
            st.write(u"Entity Name: {}".format(entity.name))

            # Obtenemos tipo de entidad
            st.write(u"Entity type: {}".format(enums.Entity.Type(entity.type).name))

            # Obtenemos el salience score asociado con la entidad en un rango de [0, 1.0]
            st.write(u"Salience score: {}".format(round(entity.salience,3)))

            # Bucle sobre cada metadata asociada con la entidad
            for metadata_name, metadata_value in entity.metadata.items():
                st.write(u"{}: {}".format(metadata_name, metadata_value))


            # Loop over the mentions of this entity in the input document.
            #for mention in entity.mentions:
                #st.write(u"Mention text: {}".format(mention.text.content))

                # Get the mention type, e.g. PROPER for proper noun
                #st.write(
                    #u"Mention type: {}".format(enums.EntityMention.Type(mention.type).name)
                #)'''
            st.write('\n')

      with col2:
        ####################################### Analizamos el sentimiento del texto
        st.header('Análisis del texto')
        document = types.Document(
            content=texto,
            type=enums.Document.Type.PLAIN_TEXT)

        # Detectamos el sentimiento del texto
        sentiment = client.analyze_sentiment(document=document).document_sentiment
        sscore = round(sentiment.score,4)
        smag = round(sentiment.magnitude,4)

        if sscore < 1 and sscore < -0.5:
          sent_label = "Muy Negativo"
        elif sscore < 0 and sscore > -0.5:
          sent_label = "Negativo"
        elif sscore == 0:
          sent_label = "Neutral"
        elif sscore > 1 and sscore > 1.5:
          sent_label = "Muy Positivo"
        elif sscore > 0 and sscore < 1.5:
          sent_label = "Positivo"

        st.subheader('Sentiment Score: {} es {}'.format(sscore,sent_label))

        predictedY =[sscore] 
        UnlabelledY=[0,1,0]

        if sscore < 0:
            plotcolor = 'red'
        else:
            plotcolor = 'green'

        plt.scatter(predictedY, np.zeros_like(predictedY),color=plotcolor,s=100)

        plt.yticks([])
        plt.subplots_adjust(top=0.9,bottom=0.8)
        plt.xlim(-1,1)
        plt.xlabel('Negativo                                                            Positivo')
        plt.title("Tipo de Sentimiento")
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot(plt.show())

        # detectamos magnitud del sentimiento
        if smag >= 0 and smag < 1:
          sent_m_label = "Sin Emoción"
        elif smag >= 2:
          sent_m_label = "Emoción Alta"
        elif smag >= 1 and smag < 2:
          sent_m_label = "Emoción Baja"

        st.subheader('Sentiment Magnitude: {} es {}'.format(smag, sent_m_label))

        predictedY =[smag] 
        UnlabelledY=[0,1,0]

        if smag > 0 and smag < 2:
            plotcolor = 'red'
        else:
            plotcolor = 'green'

        plt.scatter(predictedY, np.zeros_like(predictedY),color=plotcolor,s=100)

        plt.yticks([])
        plt.subplots_adjust(top=0.9,bottom=0.8)
        plt.xlim(0,5)
        plt.xlabel('Emoción Baja                                                          Emoción Alta')
        plt.title("Análisis Sentiment Magnitude")
        st.set_option('deprecation.showPyplotGlobalUse', False)
        st.pyplot(plt.show())

  extrac_keybert(texto=texto)

#===========>FUNCIÓN 7 <===============
#Comparativa SEO
def comparativa_seo(query, df_resultados, user_agent):
  headers = {"user-agent" : user_agent_movil}
  #creamos listas vacías para ir introduciendo todos los datos del scrapeo por cada resultado
  list_positions = []
  list_urls = []
  list_titles = []
  list_query_title = []
  list_char_titles = []
  list_metadescriptions = []
  list_query_meta_desc = []
  list_char_metadescriptions = []
  list_lists_h1 = []
  list_h1_totals = []
  list_lists_h2 = []
  list_h2_totals = []
  list_lists_h3 = []
  list_h3_totals = []
  list_lists_h4 = []
  list_h4_totals = []
  list_lists_h5 = []
  list_h5_totals = []
  list_lists_h6 = []
  list_h6_totals = []
  list_num_img = []
  list_alt_img = []
  list_query_alt_img = []
  list_title_img = []
  list_query_title_img = []
  list_links = []
  list_links_total = []
  lists_internos = []
  lists_externos = []
  list_internos_total = []
  list_externos_total = []
  list_canonicals = []
  list_meta_robots = []
  list_meta_author = []
  list_meta_publisher = []
  list_meta_lang = []
  list_schema_total = []
  list_parrafos_total = []
  list_query_parrafo = []
  list_total_count = []
  list_palabras_texto = []
  list_overall_score = []
  list_fcp = []
  list_fid = []
  list_lcp = []
  list_cls = []


  #maketrans de str para eliminar tildes y poder encontrar coincidencias de la query dentro de otros strings sin que diferencie con y sin tilde.
  a,b = 'áéíóúÁÉÍÓÚ','aeiouAEIOU'
  trans = str.maketrans(a,b)
  query = query.translate(trans)#quitamos tildes a la query

  
  #iniciamos el scrpaeo de cada resultado
  for i in range (len(df_resultados)):
    url= df_resultados.loc[i+1,'Resultados']
    list_urls.append(url)
    position = i + 1
    list_positions.append(position)

    try:
        session = HTMLSession()
        response = session.get(url, headers=headers)
        
    except requests.exceptions.RequestException as e:
        print(e)


    #title
    try:
      if title_active == True:
        with st.spinner('Titles en progreso...'):
          title = response.html.find('title', first=True).text
          list_titles.append(title)

          #query en title. Para ello pasamos todo a minúsculas y que no haya diferencia entre mayus y minus. Lo mismo con las tildes.
          title = title.translate(trans)#quitamos tildes al title
          if query.lower() in title.lower():
            query_in_title = 'Sí'
            list_query_title.append(query_in_title)
          else:
            query_in_title = 'No'
            list_query_title.append(query_in_title)

          #caracteres title
          char_title = len(title)
          list_char_titles.append(char_title)
    except:
      list_titles.append('-')
      list_query_title.append('-')
      list_char_titles.append(0)

    #metadescripción
    if metadescriptions_active == True:
      with st.spinner('Metadescripciones en progreso...'):
        meta_desc = response.html.xpath('//meta[@name="description"]/@content')
        if len(meta_desc) != 0:
          list_metadescriptions.append(meta_desc[0])

          #caracteres en metadescripción
          char_metadescription = len(meta_desc[0])
          list_char_metadescriptions.append(char_metadescription)

          #query en metadescription. Quitamos tildes y pasamos todo a minúsculas en la condición
          meta_desc[0] = meta_desc[0].translate(trans) #quitamos tildes a la meta descripción
          if query.lower() in meta_desc[0].lower():
            query_in_meta_desc = 'Sí'
            list_query_meta_desc.append(query_in_meta_desc)
          else:
            query_in_meta_desc = 'No'
            list_query_meta_desc.append(query_in_meta_desc)
        else:
          list_metadescriptions.append("")
          list_char_metadescriptions.append(0)
          list_query_meta_desc.append("No")
    

    #encabezados
    if encabezados_active == True:
      with st.spinner('Encabezados en progreso...'):
        #h1
        list_h1 = response.html.find('h1')
        
        list_h1_texto = []
        for h1 in range(len(list_h1)):
          list_h1_texto.append(list_h1[h1].text)
        list_lists_h1.append(list_h1_texto)
        
        list_h1_total = len(list_h1)
        list_h1_totals.append(list_h1_total)

        #h2
        list_h2 = response.html.find('h2')
        
        list_h2_texto = []
        for h2 in range(len(list_h2)):
          list_h2_texto.append(list_h2[h2].text)
        list_lists_h2.append(list_h2_texto)
        
        list_h2_total = len(list_h2)
        list_h2_totals.append(list_h2_total)

        #h3
        list_h3 = response.html.find('h3')
        
        list_h3_texto = []
        for h3 in range(len(list_h3)):
          list_h3_texto.append(list_h3[h3].text)
        list_lists_h3.append(list_h3_texto)
        
        list_h3_total = len(list_h3)
        list_h3_totals.append(list_h3_total)

        #h4
        list_h4 = response.html.find('h4')
        
        list_h4_texto = []
        for h4 in range(len(list_h4)):
          list_h4_texto.append(list_h4[h4].text)
        list_lists_h4.append(list_h4_texto)
        
        list_h4_total = len(list_h4)
        list_h4_totals.append(list_h4_total)

        #h5
        list_h5 = response.html.find('h5')
        
        list_h5_texto = []
        for h5 in range(len(list_h5)):
          list_h5_texto.append(list_h5[h5].text)
        list_lists_h5.append(list_h5_texto)
        
        list_h5_total = len(list_h5)
        list_h5_totals.append(list_h5_total)

        #h6
        list_h6 = response.html.find('h6')
        
        list_h6_texto = []
        for h6 in range(len(list_h6)):
          list_h6_texto.append(list_h6[h6].text)
        list_lists_h6.append(list_h6_texto)
        
        list_h6_total = len(list_h6)
        list_h6_totals.append(list_h6_total)

    #imágenes
    if imagenes_active == True:
      with st.spinner('Imágenes en progreso...'):
        #número de imágenes
        num_img= response.html.find('img', first=False)
        num_img_amp = response.html.find('amp-img', first=False)
        num_img_total = len(num_img) + len(num_img_amp)
        list_num_img.append(num_img_total)

        #alt imágenes
        alt_img = response.html.xpath('//amp-img/@alt')
        list_alt_img.append(alt_img)

        #Comprobamos si hay algún ALT que contenga la query. En caso de que uno la contenga añadimos un "sí" a la lista y rompemos el bucle. Si no, añadimos un "No" a la lista para ese resultado de búsqueda.
        img=0
        query_in_alt = False
        for img in range(len(list_alt_img[i])):
          alt_img_limpio = list_alt_img[i][img].translate(trans) #quitamos tildes de los ALT de las imágenes
          if query.lower() in alt_img_limpio.lower():
            query_in_alt = True
            list_query_alt_img.append('Sí')
            break
          
        if query_in_alt == False:
          list_query_alt_img.append('No')

        #title imágenes
        title_img = response.html.xpath('//amp-img/@title')
        list_title_img.append(title_img)

        #Comprobamos si hay algún title de imagen que contenga la query. En caso de que uno la contenga añadimos un "sí" a la lista y rompemos el bucle. Si no, añadimos un "No" a la lista para ese resultado de búsqueda.
        img=0
        query_in_img_title = False
        for img in range(len(list_title_img[i])):
          title_img_limpio = list_title_img[i][img].translate(trans) #quitamos tildes de los titles de las imágenes 
          if query.lower() in title_img_limpio.lower():
            query_in_img_title = True
            list_query_title_img.append('Sí')
            break

        if query_in_img_title == False:
          list_query_title_img.append('No')

    #Enlaces
    if enlaces_active == True:
      with st.spinner('Enlaces en progreso...'):
        #Enlaces. Obtener totales y enlaces únicos. Los separamos en internos y externos. Lo almacenamos todo en listas.
        links = response.html.absolute_links 
        links=list(links) #list(links) sirve para convertir un "Conjunto" en una "lista". La variable links es un conjunto.
        list_links.append(links) 
        links_total= len(links)
        list_links_total.append(links_total)

        dominio_raiz = get_fld(df_resultados.loc[i+1,'Resultados']) #extraemos el dominio raiz
          
        list_internos = []
        list_externos = []
        
        for link in range(len(list_links[i])):
          dominio_raiz_link = get_fld(list_links[i][link], fail_silently=True)
          if dominio_raiz == dominio_raiz_link:
            list_internos.append(list_links[i][link]) 
          else:
            list_externos.append(list_links[i][link])
            
        lists_internos.append(list_internos)
        lists_externos.append(list_externos)

        internos_total = len(list_internos)
        list_internos_total.append(internos_total)

        externos_total = len(list_externos)      
        list_externos_total.append(externos_total)
    
    #metas
    if metas_active == True:
      with st.spinner('Metas en progreso...'):
        #url canonical
        canonical = response.html.xpath("//link[@rel='canonical']/@href")
        list_canonicals.append(canonical)

        #metarobots
        meta_robots = response.html.xpath("//meta[@name='robots']/@content")
        list_meta_robots.append(meta_robots)

        #meta author
        meta_author = response.html.xpath("//meta[@name='author']/@content")
        list_meta_author.append(meta_author)

        #meta publisher
        meta_publisher = response.html.xpath("//meta[@name='publisher']/@content")
        list_meta_publisher.append(meta_publisher)

        #meta lang
        meta_lang = response.html.xpath("//meta[@name='lang']/@content")
        list_meta_lang.append(meta_lang)

    if schema_active == True:
      #schema JSON
      with st.spinner('Schemas en progreso...'):
        schema_json = response.html.xpath('//script[@type="application/ld+json"]')
        list_schema=[]
        for s in range(len(schema_json)):
          list_schema.append(schema_json[s].text)
          
        list_schema_total.append(list_schema)

    if texto_active == True:
      with st.spinner('Párrafos en progreso...'):
        #párrafos
        parrafo = response.html.find('p')
        list_parrafos=[]
        for p in range(len(parrafo)):
          list_parrafos.append(parrafo[p].text)
          
        list_parrafos_total.append(list_parrafos)

        #Comprobamos si hay algún párrafo que contenga la query. En caso de que uno la contenga añadimos un "sí" a la lista y rompemos el bucle. Si no, añadimos un "No" a la lista para ese resultado de búsqueda.
        query_in_parrafo = False
        for parrafo in range(len(list_parrafos_total[i])):
          parrafo_limpio = list_parrafos_total[i][parrafo].translate(trans) #quitamos las tildes del párrafo
          if query.lower() in parrafo_limpio.lower():
            query_in_parrafo = True
            list_query_parrafo.append('Sí')
            break

        if query_in_parrafo == False:
          list_query_parrafo.append('No')

        #contamos el número de veces que aparece la query en el texto y el número de palabras total
        total_count = 0
        total_palabras_parrafo = 0
        for parrafo in range(len(list_parrafos_total[i])):
          parrafo_limpio = list_parrafos_total[i][parrafo].translate(trans)
          parrafo_minusculas = parrafo_limpio.lower()
          subtotal = parrafo_minusculas.count(query)
          total_count = total_count + subtotal
          palabras_parrafo = len(re.findall(r'\w+', parrafo_minusculas))
          total_palabras_parrafo = total_palabras_parrafo + palabras_parrafo
        
        list_total_count.append(total_count)
        list_palabras_texto.append(total_palabras_parrafo)

 
  with st.spinner('Pintando data en progreso...'):
    #montamos los expanders y las tablas con toda la información scrapeada y guardada en listas.
    pd.set_option('display.max_colwidth', None)

    #Expander con los datos de los titles
    if title_active == True:
      with st.expander('Titles'):
        df_titles = pd.DataFrame()
        df_titles['position'] = list_positions
        df_titles['urls'] = list_urls
        df_titles['title'] = list_titles
        df_titles['query in title'] = list_query_title
        df_titles['char title'] = list_char_titles
        st.table(df_titles.set_index('position'))

    #Expander con los datos de las metadescripciones
    if metadescriptions_active == True:
      with st.expander('Metadescripciones'):
        df_descriptions = pd.DataFrame()
        df_descriptions['position'] = list_positions
        df_descriptions['urls'] = list_urls
        df_descriptions['descriptions'] = list_metadescriptions
        df_descriptions['query in desc'] = list_query_meta_desc
        df_descriptions['char desc'] = list_char_metadescriptions
        st.table(df_descriptions.set_index('position'))

    #Expander con los datos de los encabezados
    if encabezados_active == True:
      with st.expander('Encabezados'):
        df_encabezados_totales = pd.DataFrame()
        df_encabezados_totales['position'] = list_positions
        df_encabezados_totales['urls'] = list_urls
        df_encabezados_totales['h1'] = list_h1_totals
        df_encabezados_totales['h2'] = list_h2_totals
        df_encabezados_totales['h3'] = list_h3_totals
        df_encabezados_totales['h4'] = list_h4_totals
        df_encabezados_totales['h5'] = list_h5_totals
        df_encabezados_totales['h6'] = list_h6_totals
        st.table(df_encabezados_totales.set_index('position'))

        st.header('<H1>')
        for listaH1 in range(len(list_lists_h1)):
          st.subheader('Resultado ' + str(listaH1+1) + ' - Total <h1>: ' + str(len(list_lists_h1[listaH1])))
          st.write('URL: ' + df_resultados.loc[listaH1+1,'Resultados'])

          for H1 in range(len(list_lists_h1[listaH1])):
            st.text(str(H1+1) + '.- ' + list_lists_h1[listaH1][H1])

          for H1 in range(len(list_lists_h1[listaH1])):
            query_in_h1 = False
            if query in list_lists_h1[listaH1][H1]:
              query_in_h1= True
              st.text('La query está incluida en el <h1>')
              break  
          
        st.header('<H2>')
        for listaH2 in range(len(list_lists_h2)):
          st.subheader('Resultado ' + str(listaH2+1) + ' - Total <h2>: ' + str(len(list_lists_h2[listaH2])))
          st.write('URL: ' + df_resultados.loc[listaH2+1,'Resultados'])

          for H2 in range(len(list_lists_h2[listaH2])):
            st.text(str(H2+1) + '.- ' + list_lists_h2[listaH2][H2])

        st.header('<H3>')
        for listaH3 in range(len(list_lists_h3)):
          st.subheader('Resultado ' + str(listaH3+1) + ' - Total <h3>: ' + str(len(list_lists_h3[listaH3])))
          st.write('URL: ' + df_resultados.loc[listaH3+1,'Resultados'])

          for H3 in range(len(list_lists_h3[listaH3])):
            st.text(str(H3+1) + '.- ' + list_lists_h3[listaH3][H3])

        st.header('<H4>')
        for listaH4 in range(len(list_lists_h4)):
          st.subheader('Resultado ' + str(listaH4+1) + ' - Total <h4>: ' + str(len(list_lists_h4[listaH4])))
          st.write('URL: ' + df_resultados.loc[listaH4+1,'Resultados'])

          for H4 in range(len(list_lists_h4[listaH4])):
            st.text(str(H4+1) + '.- ' + list_lists_h4[listaH4][H4])

        st.header('<H5>')
        for listaH5 in range(len(list_lists_h5)):
          st.subheader('Resultado ' + str(listaH5+1) + ' - Total <h5>: ' + str(len(list_lists_h5[listaH5])))
          st.write('URL: ' + df_resultados.loc[listaH5+1,'Resultados'])

          for H5 in range(len(list_lists_h5[listaH5])):
            st.text(str(H5+1) + '.- ' + list_lists_h5[listaH5][H5])

        st.header('<H6>')
        for listaH6 in range(len(list_lists_h6)):
          st.subheader('Resultado ' + str(listaH6+1) + ' - Total <h6>: ' + str(len(list_lists_h6[listaH6])))
          st.write('URL: ' + df_resultados.loc[listaH6+1,'Resultados'])

          for H6 in range(len(list_lists_h6[listaH6])):
            st.text(str(H6+1) + '.- ' + list_lists_h6[listaH6][H6])

    #Expander con los datos del texto
    if texto_active == True:
      with st.expander('Texto'):
        df_texto = pd.DataFrame()
        df_texto['position'] = list_positions
        df_texto['urls'] = list_urls
        #df_texto['cuerpo texto'] = list_parrafos_total
        df_texto['query in texto'] = list_query_parrafo
        df_texto['total query in texto'] = list_total_count
        df_texto['Palabras texto'] = list_palabras_texto
        st.table(df_texto.set_index('position'))

        for list_p in range (len(list_parrafos_total)):
          st.subheader('Texto Resultado' + str(list_p+1))
          st.write('URL: ' + df_resultados.loc[list_p+1,'Resultados'])
          for parrafo in range(len(list_parrafos_total[list_p])):
            st.write(list_parrafos_total[list_p][parrafo])

    #Expander con los datos de las imágenes
    if imagenes_active == True: 
      with st.expander('Imágenes'):
        df_imagenes = pd.DataFrame()
        df_imagenes['position'] = list_positions
        df_imagenes['urls'] = list_urls
        df_imagenes['img'] = list_num_img
        #df_imagenes['alt img'] = list_alt_img
        df_imagenes['query in alt'] = list_query_alt_img
        #df_imagenes['title img'] = list_title_img
        df_imagenes['query in title img'] = list_query_title_img
        st.table(df_imagenes.set_index('position'))

        for list_alt in range(len(list_alt_img)):
          st.subheader('ALT imágenes Resultado' + str(list_alt+1))
          st.write('URL: ' + df_resultados.loc[list_alt+1,'Resultados'])
          for alt in range(len(list_alt_img[list_alt])):
            st.text(str(alt+1) + '.- ' + list_alt_img[list_alt][alt])

        for list_t_img in range(len(list_title_img)):
          st.subheader('Titles imágenes Resultado' + str(list_t_img+1))
          st.write('URL: ' + df_resultados.loc[list_alt+1,'Resultados'])
          for t_img in range(len(list_title_img[list_t_img])):
            st.text(str(t_img+1) + '.- ' + list_title_img[list_t_img][t_img])

    #Expander con los datos de los enlaces
    if enlaces_active == True:
      with st.expander('Enlaces'):  
        #pintamos una tabla con los totales
        df_enlaces = pd.DataFrame()
        df_enlaces['position'] = list_positions
        df_enlaces['urls'] = list_urls
        df_enlaces['Total enlaces'] = list_links_total
        df_enlaces['Enlaces internos'] = list_internos_total
        df_enlaces['Enlaces externos'] = list_externos_total
        st.table(df_enlaces.set_index('position'))

        #bucle para pintar los enlaces unitariamente y generar un listado debajo de la tabla de totales
        for list_link in range(len(list_links)):
          st.header('Enlaces del resultado ' + str(list_link+1))
          st.subheader('Total de enlaces: ' + str(len(list_links[list_link])))
          st.write('URL: ' + df_resultados.loc[list_link+1,'Resultados'])
          st.subheader('Enlaces internos:')

          for link_interno in range(len(lists_internos[list_link])):
            st.write(str(link_interno+1) + '.- ' + lists_internos[list_link][link_interno])
          
          st.subheader('Enlaces externos:')
          for link_externo in range(len(lists_externos[list_link])):        
            st.write(str(link_externo+1) + '.- ' + lists_externos[list_link][link_externo])

    #Expander con los datos de las diferentes metas
    if metas_active == True:
      with st.expander('Metas'):
        df_metas = pd.DataFrame()
        df_metas['position'] = list_positions
        df_metas['urls'] = list_urls
        df_metas['canonical'] = list_canonicals
        df_metas['robots'] = list_meta_robots
        df_metas['author'] = list_meta_author
        df_metas['publisher'] = list_meta_publisher
        df_metas['lang'] = list_meta_lang
        st.table(df_metas.set_index('position'))

    #Expander con los datos de los schemas
    if schema_active == True:
      with st.expander('Schemas'):    
        df_schemas = pd.DataFrame()
        df_schemas['position'] = list_positions
        df_schemas['urls'] = list_urls
        df_schemas['Schema'] = list_schema_total
        #st.table(df_schemas.set_index('position'))

        for list_sch in range(len(list_schema_total)):
          st.subheader('Schema Resultado ' + str(list_sch+1))
          st.write('URL: ' + df_resultados.loc[list_sch+1,'Resultados'])
          st.write('Total de schemas implementados en la página: ' + str(len(list_schema_total[list_sch])))

          for sch in range(len(list_schema_total[list_sch])):
            try:
              st.text('Schema ' + str(sch+1))
              json_sch = json.loads(list_schema_total[list_sch][sch])
              st.json(json_sch)
            except:
              st.write('hubo un error al extraer los datos estructurados. Revísalo de forma manual.')
    

  if cwv_active == True:
    #CORE WEB VITALS (lo hacemos aparte del resto porque la llamada a la API se demora bastante, así se puede ir analizando el resto de factores SEO)
    with st.spinner('Esperando a las CORE WEB VITALS'):
      my_bar = st.progress(0)
      for i in range (len(df_resultados)):
        url= df_resultados.loc[i+1,'Resultados']
        key = st.secrets["key_core"]
        strategy_mobile = 'mobile'
        url_core = 'https://www.google.com/pagespeedonline/v5/runPagespeed?url=' + url + '&=strategy' + strategy_mobile + '&key=' + key
        
        try:
          response_core = urllib.request.urlopen(url_core)
          data_core = json.loads(response_core.read())
        except:
          st.write('Hubo un error en la petición')
        
        try:
          overall_score = round(data_core["lighthouseResult"]["categories"]["performance"]["score"] * 100)
        except:
          st.write('KeyError')

        try:
          fcp = data_core["loadingExperience"]["metrics"]["FIRST_CONTENTFUL_PAINT_MS"]["percentile"] /1000
        except:
          st.write('KeyError')
        
        try:
          fid = data_core["loadingExperience"]["metrics"]["FIRST_INPUT_DELAY_MS"]["percentile"] /1000
        except:
          st.write('KeyError')

        try:
          lcp = data_core["loadingExperience"]["metrics"]["LARGEST_CONTENTFUL_PAINT_MS"]["percentile"] /1000
        except:
          st.write('KeyError')

        try:
          cls = data_core["loadingExperience"]["metrics"]["CUMULATIVE_LAYOUT_SHIFT_SCORE"]["percentile"] /100
        except:
          st.write('KeyError')

        list_overall_score.append(overall_score)
        list_fcp.append(fcp)
        list_fid.append(fid)
        list_lcp.append(lcp)
        list_cls.append(cls)

        my_bar.progress(round(100/len(df_resultados))*(i+1))
        
    my_bar.empty()
    #Expander con los datos de los CORE WEB VITALS
    with st.expander('CORE WEB VITALS'):
      df_core_web_vitals = pd.DataFrame()
      df_core_web_vitals['position'] = list_positions
      df_core_web_vitals['urls'] = list_urls
      df_core_web_vitals['Score']= list_overall_score
      df_core_web_vitals['FCP'] = list_fcp
      df_core_web_vitals['LCP'] = list_lcp
      df_core_web_vitals['CLS'] = list_cls
      df_core_web_vitals['FID'] = list_fid
      st.table(df_core_web_vitals.set_index('position'))

#===========>FUNCIÓN 8 <===============
#Capturas de pantalla Mobile
def capturaMobile(url):
  with st.expander('Captura de pantalla'):
    with st.spinner('Generando captura de pantalla...'):
      placeholder = st.empty()
      url= url
      mobile_emulation = {
        "deviceMetrics": { "width": 400 },
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19" 
        }
      chrome_options = webdriver.ChromeOptions()
      chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
      chrome_options.add_argument('--headless')
      chrome_options.add_argument('--no-sandbox')
      chrome_options.add_argument('--disable-dev-shm-usage')
      wd = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
      wd.get(url)

      try:
        #buscamos el botón de "Acepto" del mensaje de coockies de google
        texto_boton = wd.find_element(By.XPATH,"//form/input[@value='Acepto']")
        #hacemos click en el botón para aceptar las cookies y nos muestre los resultados para poder hacer la captura de pantalla
        texto_boton.click()
      except:
        placeholder.write('Cookies aceptadas')

      height = wd.execute_script(
          "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight )")

      wd.close()

      # realizamos la captura con el "alto" que hemos obtenido
      chrome_options = webdriver.ChromeOptions()
      chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
      chrome_options.add_argument('--no-sandbox')
      chrome_options.add_argument(f'--window-size=1024,{height}')
      chrome_options.add_argument('--headless')
      chrome_options.add_argument("--hide-scrollbars")
      chrome_options.add_argument('--disable-gpu')
      chrome_options.add_argument('--ignore-certificate-errors')

      wd = webdriver.Chrome(chrome_options=chrome_options)
      wd.get(url)

      try:
        #buscamos el botón de "Acepto" del mensaje de coockies de google
        texto_boton = wd.find_element(By.XPATH,"//form/input[@value='Acepto']")
        #hacemos click en el botón para aceptar las cookies y nos muestre los resultados para poder hacer la captura de pantalla
        texto_boton.click()
      except:
        placeholder.write('Cookies aceptadas')

      wd.save_screenshot('abc-mobile.png')
      image = Image.open('abc-mobile.png')
      placeholder.image(image)

#===========>FUNCIÓN 8 <===============
#Capturas de pantalla Desktop
def capturaDesktop(url):
  with st.expander('Captura de pantalla'):
    with st.spinner('Generando captura de pantalla...'):
      placeholder = st.empty()
      url= url
      chrome_options = webdriver.ChromeOptions()
      chrome_options.add_argument('--headless')
      chrome_options.add_argument('--no-sandbox')
      chrome_options.add_argument('--disable-dev-shm-usage')
      chrome_options.add_argument('--disable-cookie-encryption')
      wd = webdriver.Chrome('chromedriver',chrome_options=chrome_options)
      wd.get(url)

      try:
        texto_boton=wd.find_element(By.ID,"L2AGLb")#buscamos el botón de aceptar cookies
        texto_boton.click()#hacemos click en el botón "Acepto"
      except:
        placeholder.write('Cookies aceptadas')


      height = wd.execute_script(
          "return Math.max( document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight )")
      print(height)
      wd.close()

      # realizamos la captura con el "alto" que hemos obtenido
      chrome_options = webdriver.ChromeOptions()
      chrome_options.add_argument('--no-sandbox')
      chrome_options.add_argument(f'--window-size=1920,{height}')
      chrome_options.add_argument('--headless')
      chrome_options.add_argument("--hide-scrollbars")
      chrome_options.add_argument('--disable-gpu')
      chrome_options.add_argument('--ignore-certificate-errors')
      chrome_options.add_argument('--disable-cookie-encryption')

      wd = webdriver.Chrome(chrome_options=chrome_options)
      wd.get(url)

      try:
        texto_boton=wd.find_element(By.ID,"L2AGLb")#buscamos el botón de aceptar cookies
        texto_boton.click()#hacemos click en el botón "Acepto"
      except:
        placeholder.write('Cookies aceptadas')

      wd.save_screenshot('abc-desktop.png')
      image = Image.open('abc-desktop.png')
      placeholder.image(image)

#===========>FUNCIÓN 9 <===============
#extracción de palabras/frases clave del texto

def extrac_keybert(texto):
  with st.expander('Palabras/frases clave del texto'):
    with st.spinner('Generando extracción...'):
      kw_model = KeyBERT(model='paraphrase-multilingual-mpnet-base-v2')
      data=kw_model.extract_keywords(texto,keyphrase_ngram_range=(1, 5),use_mmr=True, diversity=0.5, top_n=10)

      df = pd.DataFrame(data, columns=['Keyword','Relevancia'])
      df['Relevancia'] = df['Relevancia'].apply(lambda x: format(x, '.2%'))
    st.dataframe(df.sort_values('Relevancia', ascending=False).set_index('Keyword'))
  




############################  FIN DECLARACIÓN DE FUNCIONES  ###############################
###########################################################################################

############################### CONFIGURACIÓN PÁGINA Y SIDEBAR STREAMLIT #####################################
##############################################################################################################

#configuración de la página streamlit
st.set_page_config(
    page_title='Monitorización en Directo | Vocento',
    layout="wide",  #que ocupe el ancho completo
)

#añadimos un título a la página de streamlit
st.title('Monitorización en Directo')

with st.sidebar.form("my_form"):
  #input email donde recibir las alertas
  email_destinatario= st.text_input('Email para recibir alertas')

  #Definimos patrones para rastrear diferentes dominios
  patrones = {
      ".*abc.es.*": "ABC",
      ".*sevilla.abc.es.*": "ABC Sevilla",
      ".*lavozdigital.es.*" : "La Voz Digital",
      ".*elcorreo.com.*": "El Correo",
      ".*hoy.es.*": "HOY",
      ".*larioja.com.*": "La Rioja",
      ".*elnortedecastilla.es.*": "El Norte de Castilla",
      ".*diariovasco.com.*": "El Diario Vasco",
      ".*ideal.es.*": "IDEAL",
      ".*diariosur.es.*": "SUR",
      ".*elcomercio.es.*": "El Comercio",
      ".*lasprovincias.es.*": "Las Provincias",
      ".*eldiariomontanes.es.*": "El Diario Montañés",      
      ".*laverdad.es.*": "La Verdad",
      ".*leonoticias.com.*": "Leonoticias",
      ".*burgosconecta.es.*": "Burgosconecta",
  }
  #Añadimos selectbox al sidebar para seleccionar dominio a rastrear en base a los patrones definidos
  patron_seleccionado = st.selectbox('Dominio a monitorizar', list(patrones.items()), 1 , format_func=lambda o: o[1])
  
  #Condicional para saber que Credenciales JSON usar
  if patron_seleccionado[1] == "ABC Sevilla":
    #creamos un dict con el contenido de las credenciales de json
    contenido_json = {
      "type": st.secrets["type_sev"],
      "project_id": st.secrets["project_id_sev"],
      "private_key_id": st.secrets["private_key_id_sev"],
      "private_key": st.secrets["private_key_sev"] ,
      "client_email": st.secrets["client_email_sev"],
      "client_id": st.secrets["client_id_sev"],
      "auth_uri": st.secrets["auth_uri_sev"],
      "token_uri": st.secrets["token_uri_sev"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_sev"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_sev"]
    }
  elif patron_seleccionado[1] == 'ABC':
    contenido_json = {
      "type": st.secrets["type_abc"],
      "project_id": st.secrets["project_id_abc"],
      "private_key_id": st.secrets["private_key_id_abc"],
      "private_key": st.secrets["private_key_abc"] ,
      "client_email": st.secrets["client_email_abc"],
      "client_id": st.secrets["client_id_abc"],
      "auth_uri": st.secrets["auth_uri_abc"],
      "token_uri": st.secrets["token_uri_abc"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_abc"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_abc"]
    }
  elif patron_seleccionado[1] == 'La Voz Digital':
    contenido_json = {
      "type": st.secrets["type_voz"],
      "project_id": st.secrets["project_id_voz"],
      "private_key_id": st.secrets["private_key_id_voz"],
      "private_key": st.secrets["private_key_voz"] ,
      "client_email": st.secrets["client_email_voz"],
      "client_id": st.secrets["client_id_voz"],
      "auth_uri": st.secrets["auth_uri_voz"],
      "token_uri": st.secrets["token_uri_voz"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_voz"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_voz"]
    }
  elif patron_seleccionado[1] == 'El Correo':
    contenido_json = {
      "type": st.secrets["type_ecr"],
      "project_id": st.secrets["project_id_ecr"],
      "private_key_id": st.secrets["private_key_id_ecr"],
      "private_key": st.secrets["private_key_ecr"] ,
      "client_email": st.secrets["client_email_ecr"],
      "client_id": st.secrets["client_id_ecr"],
      "auth_uri": st.secrets["auth_uri_ecr"],
      "token_uri": st.secrets["token_uri_ecr"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_ecr"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_ecr"]
    } 
  elif patron_seleccionado[1] == 'HOY':
    contenido_json = {
      "type": st.secrets["type_hoy"],
      "project_id": st.secrets["project_id_hoy"],
      "private_key_id": st.secrets["private_key_id_hoy"],
      "private_key": st.secrets["private_key_hoy"] ,
      "client_email": st.secrets["client_email_hoy"],
      "client_id": st.secrets["client_id_hoy"],
      "auth_uri": st.secrets["auth_uri_hoy"],
      "token_uri": st.secrets["token_uri_hoy"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_hoy"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_hoy"]
    }
  elif patron_seleccionado[1] == 'La Rioja':
    contenido_json = {
      "type": st.secrets["type_lrj"],
      "project_id": st.secrets["project_id_lrj"],
      "private_key_id": st.secrets["private_key_id_lrj"],
      "private_key": st.secrets["private_key_lrj"] ,
      "client_email": st.secrets["client_email_lrj"],
      "client_id": st.secrets["client_id_lrj"],
      "auth_uri": st.secrets["auth_uri_lrj"],
      "token_uri": st.secrets["token_uri_lrj"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_lrj"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_lrj"]
    } 
  elif patron_seleccionado[1] == 'El Norte de Castilla':
    contenido_json = {
      "type": st.secrets["type_enc"],
      "project_id": st.secrets["project_id_enc"],
      "private_key_id": st.secrets["private_key_id_enc"],
      "private_key": st.secrets["private_key_enc"] ,
      "client_email": st.secrets["client_email_enc"],
      "client_id": st.secrets["client_id_enc"],
      "auth_uri": st.secrets["auth_uri_enc"],
      "token_uri": st.secrets["token_uri_enc"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_enc"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_enc"]
    }
  elif patron_seleccionado[1] == 'El Diario Vasco':
    contenido_json = {
      "type": st.secrets["type_edv"],
      "project_id": st.secrets["project_id_edv"],
      "private_key_id": st.secrets["private_key_id_edv"],
      "private_key": st.secrets["private_key_edv"] ,
      "client_email": st.secrets["client_email_edv"],
      "client_id": st.secrets["client_id_edv"],
      "auth_uri": st.secrets["auth_uri_edv"],
      "token_uri": st.secrets["token_uri_edv"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_edv"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_edv"]
    }  
  elif patron_seleccionado[1] == 'IDEAL':
    contenido_json = {
      "type": st.secrets["type_ide"],
      "project_id": st.secrets["project_id_ide"],
      "private_key_id": st.secrets["private_key_id_ide"],
      "private_key": st.secrets["private_key_ide"] ,
      "client_email": st.secrets["client_email_ide"],
      "client_id": st.secrets["client_id_ide"],
      "auth_uri": st.secrets["auth_uri_ide"],
      "token_uri": st.secrets["token_uri_ide"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_ide"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_ide"]
    }   
  elif patron_seleccionado[1] == 'SUR':
    contenido_json = {
      "type": st.secrets["type_sur"],
      "project_id": st.secrets["project_id_sur"],
      "private_key_id": st.secrets["private_key_id_sur"],
      "private_key": st.secrets["private_key_sur"] ,
      "client_email": st.secrets["client_email_sur"],
      "client_id": st.secrets["client_id_sur"],
      "auth_uri": st.secrets["auth_uri_sur"],
      "token_uri": st.secrets["token_uri_sur"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_sur"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_sur"]
    }   
  elif patron_seleccionado[1] == 'El Comercio':
    contenido_json = {
      "type": st.secrets["type_ecm"],
      "project_id": st.secrets["project_id_ecm"],
      "private_key_id": st.secrets["private_key_id_ecm"],
      "private_key": st.secrets["private_key_ecm"] ,
      "client_email": st.secrets["client_email_ecm"],
      "client_id": st.secrets["client_id_ecm"],
      "auth_uri": st.secrets["auth_uri_ecm"],
      "token_uri": st.secrets["token_uri_ecm"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_ecm"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_ecm"]
    }   
  elif patron_seleccionado[1] == 'Las Provincias':
    contenido_json = {
      "type": st.secrets["type_lpv"],
      "project_id": st.secrets["project_id_lpv"],
      "private_key_id": st.secrets["private_key_id_lpv"],
      "private_key": st.secrets["private_key_lpv"] ,
      "client_email": st.secrets["client_email_lpv"],
      "client_id": st.secrets["client_id_lpv"],
      "auth_uri": st.secrets["auth_uri_lpv"],
      "token_uri": st.secrets["token_uri_lpv"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_lpv"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_lpv"]
    }   
  elif patron_seleccionado[1] == 'El Diario Montañés':
    contenido_json = {
      "type": st.secrets["type_edm"],
      "project_id": st.secrets["project_id_edm"],
      "private_key_id": st.secrets["private_key_id_edm"],
      "private_key": st.secrets["private_key_edm"] ,
      "client_email": st.secrets["client_email_edm"],
      "client_id": st.secrets["client_id_edm"],
      "auth_uri": st.secrets["auth_uri_edm"],
      "token_uri": st.secrets["token_uri_edm"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_edm"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_edm"]
    }   
  elif patron_seleccionado[1] == 'La Verdad':
    contenido_json = {
      "type": st.secrets["type_lvd"],
      "project_id": st.secrets["project_id_lvd"],
      "private_key_id": st.secrets["private_key_id_lvd"],
      "private_key": st.secrets["private_key_lvd"] ,
      "client_email": st.secrets["client_email_lvd"],
      "client_id": st.secrets["client_id_lvd"],
      "auth_uri": st.secrets["auth_uri_lvd"],
      "token_uri": st.secrets["token_uri_lvd"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_lvd"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_lvd"]
    }   
  elif patron_seleccionado[1] == 'Leonoticias':
    contenido_json = {
      "type": st.secrets["type_leo"],
      "project_id": st.secrets["project_id_leo"],
      "private_key_id": st.secrets["private_key_id_leo"],
      "private_key": st.secrets["private_key_leo"] ,
      "client_email": st.secrets["client_email_leo"],
      "client_id": st.secrets["client_id_leo"],
      "auth_uri": st.secrets["auth_uri_leo"],
      "token_uri": st.secrets["token_uri_leo"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_leo"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_leo"]
    }   
  elif patron_seleccionado[1] == 'Burgosconecta':
    contenido_json = {
      "type": st.secrets["type_bur"],
      "project_id": st.secrets["project_id_bur"],
      "private_key_id": st.secrets["private_key_id_bur"],
      "private_key": st.secrets["private_key_bur"] ,
      "client_email": st.secrets["client_email_bur"],
      "client_id": st.secrets["client_id_bur"],
      "auth_uri": st.secrets["auth_uri_bur"],
      "token_uri": st.secrets["token_uri_bur"],
      "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url_bur"],
      "client_x509_cert_url": st.secrets["client_x509_cert_url_bur"]
    }  

  #convertimos el dict en un JSON
  uploaded_file = json.dumps(contenido_json)

  #guardamos el JSON en un archivo temporal para poder llamar al path donde se encuentra el archivo JSON
  with tempfile.NamedTemporaryFile(mode='w', delete=False) as fp:
    fp.write(uploaded_file)
  try:
    print('antes de llegar a gc')
    gc = gspread.service_account(filename=fp.name) 
    sh = gc.open_by_url(st.secrets["sheet"])
  finally:
    os.unlink(fp.name)
  

  #Añadimos selectbox para seleccionar qué tipos de resultados queremos monitorizar
  tipos_resultados = st.multiselect('Tipo de resultado a monitorizar', ['Búsqueda','Carrusel noticias'])

  #Añadimos selectbox al sidebar para seleccionar que resultados queremos en función del tipo de dispositivo 
  dispositivo = st.multiselect('Dispositivo', ['Móvil', 'Desktop'])

  #añadimos a la barra lateral un selectbox para elegir el número de posiciones que queremos rastrear top10, top20, top30
  add_selectbox_top = st.selectbox(
      "¿Cuantas posiciones de los resultados quieres monitorizar?",
      ('10','20','30')
      )

  #Definimos una serie de ubicaciones para localizar la búsqueda
  uules = {
      "w+CAIQICIFU3BhaW4=": "España",
      "w+CAIQICIiUHJvdmluY2Ugb2YgQSBDb3J1bmEsR2FsaWNpYSxTcGFpbg==": "A Coruna",
      "w+CAIQICImUHJvdmluY2Ugb2YgQWxhdmEsQmFzcXVlIENvdW50cnksU3BhaW4=": "Álava",
      "w+CAIQICIsUHJvdmluY2Ugb2YgQWxiYWNldGUsQ2FzdGlsZS1MYSBNYW5jaGEsU3BhaW4=": "Albacete",
      "w+CAIQICIjUHJvdmluY2Ugb2YgQWxpY2FudGUsVmFsZW5jaWEsU3BhaW4=": "Alicante",
      "w+CAIQICIjUHJvdmluY2Ugb2YgQWxtZXJpYSxBbmRhbHVzaWEsU3BhaW4=": "Almería",
      "w+CAIQICIjUHJvdmluY2Ugb2YgQXN0dXJpYXMsQXN0dXJpYXMsU3BhaW4=": "Asturias",
      "w+CAIQICIoUHJvdmluY2Ugb2YgQXZpbGEsQ2FzdGlsZSBhbmQgTGVvbixTcGFpbg==": "Ávila",
      "w+CAIQICIlUHJvdmluY2Ugb2YgQmFkYWpveixFeHRyZW1hZHVyYSxTcGFpbg==": "Badajoz",
      "w+CAIQICIzUHJvdmluY2Ugb2YgQmFsZWFyaWMgSXNsYW5kcyxCYWxlYXJpYyBJc2xhbmRzLFNwYWlu": "Islas Baleares",
      "w+CAIQICIlUHJvdmluY2Ugb2YgQmFyY2Vsb25hLENhdGFsb25pYSxTcGFpbg==": "Barcelona",
      "w+CAIQICInUHJvdmluY2Ugb2YgQmlzY2F5LEJhc3F1ZSBDb3VudHJ5LFNwYWlu": "Vizcaya",
      "w+CAIQICIpUHJvdmluY2Ugb2YgQnVyZ29zLENhc3RpbGUgYW5kIExlb24sU3BhaW4=": "Burgos",
      "w+CAIQICIlUHJvdmluY2Ugb2YgQ2FjZXJlcyxFeHRyZW1hZHVyYSxTcGFpbg==": "Cáceres",
      "w+CAIQICIhUHJvdmluY2Ugb2YgQ2FkaXosQW5kYWx1c2lhLFNwYWlu": "Cádiz",
      "w+CAIQICIlUHJvdmluY2Ugb2YgQ2FudGFicmlhLENhbnRhYnJpYSxTcGFpbg==": "Cantabria",
      "w+CAIQICIkUHJvdmluY2Ugb2YgQ2FzdGVsbG9uLFZhbGVuY2lhLFNwYWlu": "Castellón",
      "w+CAIQICIvUHJvdmluY2Ugb2YgQ2l1ZGFkIFJlYWwsQ2FzdGlsZS1MYSBNYW5jaGEsU3BhaW4=": "Ciudad Real",
      "w+CAIQICIjUHJvdmluY2Ugb2YgQ29yZG9iYSxBbmRhbHVzaWEsU3BhaW4=": "Córdoba",
      "w+CAIQICIqUHJvdmluY2Ugb2YgQ3VlbmNhLENhc3RpbGUtTGEgTWFuY2hhLFNwYWlu": "Cuenca",
      "w+CAIQICIpUHJvdmluY2Ugb2YgR2lwdXprb2EsQmFzcXVlIENvdW50cnksU3BhaW4=": "Gipuzkoa",
      "w+CAIQICIjUHJvdmluY2Ugb2YgR3JhbmFkYSxBbmRhbHVzaWEsU3BhaW4=": "Granada",
      "w+CAIQICIvUHJvdmluY2Ugb2YgR3VhZGFsYWphcmEsQ2FzdGlsZS1MYSBNYW5jaGEsU3BhaW4=": "Guadalajara",
      "w+CAIQICIiUHJvdmluY2Ugb2YgSHVlbHZhLEFuZGFsdXNpYSxTcGFpbg==": "Huelva",
      "w+CAIQICIfUHJvdmluY2Ugb2YgSHVlc2NhLEFyYWdvbixTcGFpbg==": "Huesca",
      "w+CAIQICIgUHJvdmluY2Ugb2YgSmFlbixBbmRhbHVzaWEsU3BhaW4=": "Jaén",
      "w+CAIQICIjUHJvdmluY2Ugb2YgTGEgUmlvamEsTGEgUmlvamEsU3BhaW4=": "La Rioja",
      "w+CAIQICIrUHJvdmluY2Ugb2YgTGFzIFBhbG1hcyxDYW5hcnkgSXNsYW5kcyxTcGFpbg==": "Las Palmas",
      "w+CAIQICInUHJvdmluY2Ugb2YgTGVvbixDYXN0aWxlIGFuZCBMZW9uLFNwYWlu": "León",
      "w+CAIQICIiUHJvdmluY2Ugb2YgTGxlaWRhLENhdGFsb25pYSxTcGFpbg==": "Lleida",
      "w+CAIQICIeUHJvdmluY2Ugb2YgTHVnbyxHYWxpY2lhLFNwYWlu": "Lugo",
      "w+CAIQICIfUHJvdmluY2Ugb2YgTWFkcmlkLE1hZHJpZCxTcGFpbg==": "Madrid",
      "w+CAIQICIiUHJvdmluY2Ugb2YgTWFsYWdhLEFuZGFsdXNpYSxTcGFpbg==": "Málaga",
      "w+CAIQICIfUHJvdmluY2Ugb2YgTXVyY2lhLE11cmNpYSxTcGFpbg==": "Murcia",
      "w+CAIQICIhUHJvdmluY2Ugb2YgTmF2YXJyZSxOYXZhcnJlLFNwYWlu": "Navarra",
      "w+CAIQICIrUHJvdmluY2Ugb2YgUGFsZW5jaWEsQ2FzdGlsZSBhbmQgTGVvbixTcGFpbg==": "Palencia",
      "w+CAIQICIkUHJvdmluY2Ugb2YgUG9udGV2ZWRyYSxHYWxpY2lhLFNwYWlu": "Pontevedra",
      "w+CAIQICIiUHJvdmluY2Ugb2YgR2lyb25hLENhdGFsb25pYSxTcGFpbg==": "Girona",
      "w+CAIQICIhUHJvdmluY2Ugb2YgT3VyZW5zZSxHYWxpY2lhLFNwYWlu": "Orense",
      "w+CAIQICIsUHJvdmluY2Ugb2YgU2FsYW1hbmNhLENhc3RpbGUgYW5kIExlb24sU3BhaW4=": "Salamanca",
      "w+CAIQICI3UHJvdmluY2Ugb2YgU2FudGEgQ3J1eiBkZSBUZW5lcmlmZSxDYW5hcnkgSXNsYW5kcyxTcGFpbg==": "Santa Cruz de Tenerife",
      "w+CAIQICIqUHJvdmluY2Ugb2YgU2Vnb3ZpYSxDYXN0aWxlIGFuZCBMZW9uLFNwYWlu": "Segovia",
      "w+CAIQICIjUHJvdmluY2Ugb2YgU2V2aWxsYSxBbmRhbHVzaWEsU3BhaW4=": "Sevilla",
      "w+CAIQICIoUHJvdmluY2Ugb2YgU29yaWEsQ2FzdGlsZSBhbmQgTGVvbixTcGFpbg==": "Soria",
      "w+CAIQICIlUHJvdmluY2Ugb2YgVGFycmFnb25hLENhdGFsb25pYSxTcGFpbg==": "Tarragona",
      "w+CAIQICIfUHJvdmluY2Ugb2YgVGVydWVsLEFyYWdvbixTcGFpbg==": "Teruel",
      "w+CAIQICIqUHJvdmluY2Ugb2YgVG9sZWRvLENhc3RpbGUtTGEgTWFuY2hhLFNwYWlu": "Toledo",
      "w+CAIQICIjUHJvdmluY2Ugb2YgVmFsZW5jaWEsVmFsZW5jaWEsU3BhaW4=": "Valencia",
      "w+CAIQICItUHJvdmluY2Ugb2YgVmFsbGFkb2xpZCxDYXN0aWxlIGFuZCBMZW9uLFNwYWlu": "Valladolid",
      "w+CAIQICIpUHJvdmluY2Ugb2YgWmFtb3JhLENhc3RpbGUgYW5kIExlb24sU3BhaW4=": "Zamora",
      "w+CAIQICIhUHJvdmluY2Ugb2YgWmFyYWdvemEsQXJhZ29uLFNwYWlu": "Zaragoza",
  }
  #añadimos selectbox al sidebar para seleccionar la ubicación donde queremos realizar la búsqueda
  uule = st.multiselect('Ubicación de la búsqueda', list(uules.items()), format_func=lambda o: o[1])

  #Definimos los datos para el selectbox de frecuencia de rastreo
  import random
  frecuencias = {
      random.randrange(5*60,10*60): "Cada 5-10 minutos",
      random.randrange(10*60,15*60): "Cada 10-15 minutos",
      random.randrange(30*60,45*60): "Cada 30-45 minutos",  
  }
  #añadimos al sidebar el selectbox las frecuencia de rastreo definidas
  frecuencia = st.selectbox('Frecuencia de rastreo', list(frecuencias.items()), 0 , format_func=lambda o: o[1])

  st.write('Análisis competencia:')

  #lista de checks para extraer factores SEO
  entidades_active = st.checkbox('Entidades', value= True, help= 'Check para extraer las entidades del primer resultado')
  keybert_active = st.checkbox('Frases clave*', value= False, help= 'Check para extraer las palabras/frases clave más relevantes del texto del primer resultado. Si se activa, el tiempo de rastreo aumenta considerablemente.')
  title_active = st.checkbox('Titles', value= True, help='Check para extraer todos los Titles de cada resultado')
  metadescriptions_active = st.checkbox('Meta Descriptions', value= True, help='Check para extraer todas las Meta Descriptions de cada resultado')
  encabezados_active = st.checkbox ('Encabezados', value= True, help= 'Check para extraer todos los encabezados de cada resultado')
  texto_active = st.checkbox ('Texto', value= True, help= 'Check para extraer todos los textos de cada resultado')
  imagenes_active = st.checkbox ('Imágenes', value= True, help= 'Check para extraer todos los datos de imágenes de cada resultado')
  enlaces_active = st.checkbox ('Enlaces', value= True, help= 'Check para extraer todos los enlaces internos y externos de cada resultado')
  metas_active = st.checkbox ('Metas', value= True, help= 'Check para extraer ciertas metas de cada resultado')
  schema_active = st.checkbox ('Schema', value= True, help= 'Check para extraer los datos estructurados de cada resultado')
  cwv_active = st.checkbox('Core Web Vitals*', value= False, help='Check para obtener FCP, LCP, CLS y FID de cada resultado. Si se activa, el tiempo de rastreo aumenta considerablemente')

  #abrimos la spreadsheet donde se almacenan los resultados de búsqueda y los históricos
  ss = gc.open_by_url(st.secrets["sheet"])
  sheet = ss.sheet1 #definimos la hoja1 de la spreadsheet
  lista_wk = ss.worksheets() #sacamos una lista de todas las hojas que hay en la spreadsheet
  lista_titulos_wk = [worksheet.title for worksheet in lista_wk] #creamos una lista con todos los títulos de cada hoja dentro de la spreadsheet, ya que la anterior lista contiene más datos además del título.

  #añadimos a la barra lateral de la página de streamlit un text area para introducir las búsquedas a monitorizar
  busquedas = st.text_area(label= 'Búsquedas a monitorizar:', help='Introduce las búsquedas a monitorizar (una por línea)', height=100)
  query_list = busquedas.split("\n")

  submit_button = st.form_submit_button(label='Iniciar')


#añadimos al sidebar el selectbox para seleccionar históricos menos la hoja 1
historicos = st.sidebar.selectbox("Históricos", lista_titulos_wk[1:], index=0) 

#creamos el botón para borrar el histórico seleccionado en el selectbox e incluimos el código a ejecutar si el botón es pulsado
if st.sidebar.button('borrar histórico'):
  wk_del_historico = ss.worksheet(historicos) #definimos la hoja a borrar
  ss.del_worksheet(wk_del_historico) #borramos la hoja
  st.write(wk_del_historico.title + ' borrado correctamente') #ponemos mensaje de confirmación
  st.experimental_rerun()

#Si el campo de tipo de resultado está vacío paramos el script y mostramos un mensaje de advertencia
if not tipos_resultados:
  st.warning('Por favor, introduce un tipo de resultado')
  st.stop()

#Si el campo de dispositivo está vacío paramos el script y mostramos un mensaje de advertencia
if not dispositivo:
  st.warning('Por favor, introduce un tipo de dispositivo')
  st.stop()

#Si el campo de ubicación está vacío paramos el script y mostramos un mensaje de advertencia
if not uule:
  st.warning('Por favor, introduce una ubicación')
  st.stop()

#si el text area donde definimos las busquedas está vacio paramos la ejecución, si no, que siga corriendo el código.
if not busquedas:
  st.warning('Por favor, introduce las búsquedas que quieres monitorizar en el area de texto para comenzar.')
  st.stop()
else:
  for query in query_list:
    if query == '':
      st.error('Por favor, elimina la linea en blanco que has generado en el text area')
      st.stop()
  st.text(query_list)




############################### FIN CONFIGURACIÓN PÁGINA Y SIDEBAR STREAMLIT #################################
##############################################################################################################



############################### RASTREO ######################################################################
##############################################################################################################

#variables para construir la URL de búsqueda y que no necesitan ser cambiados en el sidebar.
gl = 'ES'  #Restringe las búsquedas al país elegido. “ES” es el valor para España.
pws = '0'  #Con este parámetro a cero no se realiza una búsqueda personalizada.
hl = 'es'  #definimos el lenguaje de la interfaz

#variables para nombrar los desplegables
nombre_expander_b_m = 'BÚSQUEDA MÓVIL'
nombre_expander_c_m = 'CARRUSEL DE NOTICIAS MÓVIL'
nombre_expander_b_d = 'BÚSQUEDA DESKTOP'
nombre_expander_c_d = 'CARRUSEL DE NOTICIAS DESKTOP'

#creamos un bucle para rastrear los resultados de búsqueda, obtener la posición, almacenar el histórico y crear el gráfico por cada búsqueda definida en el text area del sidebar
for i in range (len(query_list)):

  for j in range (len(uule)):

    user_agent_movil = 'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36'
    user_agent_desktop = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0'

    elemento_html_busqueda_desktop = '//*[@class="yuRUbf"]/a/@href'
    elemento_html_busqueda_movil= '//*[contains(@class, "C8nzq")]/@href'
    elemento_html_carrusel= '//*[contains(@class, "WlydOe")]/@href'

    st.header('Consulta: ' + query_list[i] + ' - ' + 'Ubicación: ' + uule [j][1])#establecemos la consulta como cabecera de los resultados visuales en streamlit

    if dispositivo == ['Móvil'] and tipos_resultados == ['Búsqueda']:
      rastreo_busqueda (elemento_html= elemento_html_busqueda_movil, nombre_expander=nombre_expander_b_m, user_agent=user_agent_movil)
    elif dispositivo == ['Móvil'] and tipos_resultados == ['Carrusel noticias']:
      rastreo_carrusel (elemento_html=elemento_html_carrusel, nombre_expander=nombre_expander_c_m, user_agent=user_agent_movil)
    elif dispositivo == ['Móvil'] and 'Búsqueda' in tipos_resultados and 'Carrusel noticias' in tipos_resultados:
      rastreo_busqueda (elemento_html= elemento_html_busqueda_movil, nombre_expander=nombre_expander_b_m, user_agent=user_agent_movil)
      rastreo_carrusel (elemento_html=elemento_html_carrusel, nombre_expander=nombre_expander_c_m, user_agent=user_agent_movil)
    elif dispositivo == ['Desktop'] and tipos_resultados == ['Búsqueda']:
      rastreo_busqueda (elemento_html=elemento_html_busqueda_desktop, nombre_expander=nombre_expander_b_d, user_agent=user_agent_desktop)
    elif dispositivo == ['Desktop'] and tipos_resultados == ['Carrusel noticias']:
      rastreo_carrusel (elemento_html=elemento_html_carrusel, nombre_expander=nombre_expander_c_d, user_agent=user_agent_desktop)
    elif dispositivo == ['Desktop'] and 'Búsqueda' in tipos_resultados and 'Carrusel noticias' in tipos_resultados:
      rastreo_busqueda (elemento_html=elemento_html_busqueda_desktop, nombre_expander=nombre_expander_b_d, user_agent=user_agent_desktop)
      rastreo_carrusel (elemento_html=elemento_html_carrusel, nombre_expander=nombre_expander_c_d, user_agent=user_agent_desktop)
    elif 'Móvil' in dispositivo and 'Desktop' in dispositivo and tipos_resultados==['Búsqueda']:
      rastreo_busqueda (elemento_html= elemento_html_busqueda_movil, nombre_expander=nombre_expander_b_m, user_agent=user_agent_movil)
      rastreo_busqueda (elemento_html=elemento_html_busqueda_desktop, nombre_expander=nombre_expander_b_d, user_agent=user_agent_desktop)
    elif 'Móvil' in dispositivo and 'Desktop' in dispositivo and tipos_resultados==['Carrusel noticias']:
      rastreo_carrusel (elemento_html=elemento_html_carrusel, nombre_expander=nombre_expander_c_m, user_agent=user_agent_movil)
      rastreo_carrusel (elemento_html=elemento_html_carrusel, nombre_expander=nombre_expander_c_d, user_agent=user_agent_desktop)
    elif 'Móvil' in dispositivo and 'Desktop' in dispositivo and 'Búsqueda' in tipos_resultados and 'Carrusel noticias' in tipos_resultados:
      rastreo_busqueda (elemento_html= elemento_html_busqueda_movil, nombre_expander=nombre_expander_b_m, user_agent=user_agent_movil)
      rastreo_busqueda (elemento_html=elemento_html_busqueda_desktop, nombre_expander=nombre_expander_b_d, user_agent=user_agent_desktop)
      rastreo_carrusel (elemento_html=elemento_html_carrusel, nombre_expander=nombre_expander_c_m, user_agent=user_agent_movil)
      rastreo_carrusel (elemento_html=elemento_html_carrusel, nombre_expander=nombre_expander_c_d, user_agent=user_agent_desktop)
  time.sleep(random.randrange(10,15))



  
############################### FIN RASTREO ##################################################################
##############################################################################################################

#Generamos cuenta atrás hasta próximo rastreo
with st.empty():
  t= frecuencia[0]
  while t:
    mins, secs = divmod(t, 60)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)
    st.write('Tiempo restante hasta el próximo rastreo: ' + timeformat)
    time.sleep(1)
    t-=1
st.experimental_rerun()

