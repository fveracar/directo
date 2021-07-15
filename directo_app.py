import requests
from requests_html import HTMLSession
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

st.set_page_config(
    page_title='Monitorización en Directo | Vocento',
)

#creamos un dict con el contenido de las credenciales de json
contenido_json = {
  "type": st.secrets["type"],
  "project_id": st.secrets["project_id"],
  "private_key_id": st.secrets["private_key_id"],
  "private_key": st.secrets["private_key"],
  "client_email": st.secrets["client_email"],
  "client_id": st.secrets["client_id"],
  "auth_uri": st.secrets["auth_uri"],
  "token_uri": st.secrets["token_uri"],
  "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
  "client_x509_cert_url": st.secrets["auth_provider_x509_cert_url"]
}

#convertimos el dict en un JSON
uploaded_file = json.dumps(contenido_json)

#guardamos el JSON en un archivo temporal para poder llamar al path donde se encuentra el archivo JSON
with tempfile.NamedTemporaryFile(mode='w', delete=False) as fp:
  fp.write(uploaded_file)
try:
  gc = gspread.service_account(filename=fp.name) 
  sh = gc.open_by_url(st.secrets["sheet"])
finally:
  os.unlink(fp.name)

############################   DECLARACIÓN DE FUNCIONES  ###############################
########################################################################################

#========> FUNCIÓN 1 <===========
#Esta función envía un email

def envio_email(r):
  #Enviamos los resultados en un email
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
#Función para realizar la petición de rastreo y extraer los datos del rastreo y ejecutar la función almacenamiento_rastreo para los resultados de búsqueda.
def rastreo_busqueda (elemento_html, nombre_expander, user_agent):
  user_agent_movil = 'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36'
  user_agent_desktop = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0'
  #Construcción de la URL de búsqueda para rastrear los resultados
  url= 'https://www.google.es/search?q=' + query_list[i] + '&gl=' + gl + '&pws=' + pws + '&num=' + add_selectbox_top + '&hl=' + hl + '&uule=' + uule[j][0] + ''    
  resultados_busqueda = [] #creamos un array vacío para introducir después cada resultado de búsqueda 
  #peticion_busqueda (user_agent = user_agent_movil, elemento_html= elemento_html, url=url, resultados_busqueda=resultados_busqueda)
  headers = {"user-agent" : user_agent}
  #Declaración para saber si hay errores 
  try:
      session = HTMLSession()
      response = session.get(url, headers=headers)
      
  except requests.exceptions.RequestException as e:
      print(e)

  #Petición para los resultados de búsqueda en Móvil
  resultado = response.html.find(elemento_html) #buscamos la clase que contiene los resultados de búsqueda

  #bucle para incluir cada resultado de búsqueda en el array
  for r in range(len(resultado)):
      x = resultado[r].text
      resultados_busqueda.append(x)

  pd.set_option("display.max_colwidth", None) #configuramos el pandas para que muestre el ancho de columna entero
  df_resultados = pd.DataFrame (resultados_busqueda, columns=['Resultados'],) #convertimos el array que contiene los resultados de búsqueda en un dataframe

  lista_wk = ss.worksheets() #sacamos una lista de todas las hojas que hay en la spreadsheet
  lista_titulos_wk = [worksheet.title for worksheet in lista_wk] #creamos una lista con todos los títulos de cada hoja dentro de la spreadsheet, ya que la anterior lista contiene más datos además del título.

  #verificamos si ya están creadas las hojas correspondientes en la spreadsheet de cada cansulta que se está rastreando
  if query_list[i] + " - " + uule[j][1] not in lista_titulos_wk: #si la hoja de la consulta no está en la lista de hojas entonces la creamos.
    ss.add_worksheet(title=query_list[i] + " - " + uule[j][1], rows= 1000 , cols= 24)

  #Definimos las hojas donde vamos a trasladar los datos de cada consulta
  wk = ss.worksheet(title=query_list[i] + " - " + uule[j][1]) #hoja donde vamos a trasladar los datos del dataframe de los resultados de búsqueda
  df_resultados = pd.DataFrame (resultados_busqueda, columns=['Resultados'],) #convertimos el array que contiene los resultados de búsqueda en un dataframe
  almacenamiento_rastreo(
      hoja_resultados= wk,  
      df_r = df_resultados, 
      texto_resultado_query='no se ha encontrado en los resultados de búsqueda', 
      nombre_expander= nombre_expander,
      url=url,
      )

#=============>FUNCIÓN 3 <===================
#Función para realizar la petición de rastreo y extraer los datos del rastreo y ejecutar la función almacenamiento_rastreo para los resultados de carrusel.
def rastreo_carrusel (elemento_html, nombre_expander, user_agent):
  user_agent_movil = 'Mozilla/5.0 (Linux; Android 7.0; SM-G930V Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.125 Mobile Safari/537.36'
  user_agent_desktop = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0'
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
  resultado = response.html.find(elemento_html) #buscamos la clase que contiene los resultados de búsqueda

  #bucle para incluir cada resultado de búsqueda en el array
  for r in range(len(resultado)):
      x = resultado[r].absolute_links
      resultados_busqueda.append(x)

  pd.set_option("display.max_colwidth", None) #configuramos el pandas para que muestre el ancho de columna entero
  df_resultados = pd.DataFrame (resultados_busqueda, columns=['Resultados'],) #convertimos el array que contiene los resultados de búsqueda en un dataframe

  lista_wk = ss.worksheets() #sacamos una lista de todas las hojas que hay en la spreadsheet
  lista_titulos_wk = [worksheet.title for worksheet in lista_wk] #creamos una lista con todos los títulos de cada hoja dentro de la spreadsheet, ya que la anterior lista contiene más datos además del título.

  #verificamos si ya están creadas las hojas correspondientes en la spreadsheet de cada consulta que se está rastreando
  if query_list[i] + " - " + uule[j][1] not in lista_titulos_wk: #si la hoja de la consulta no está en la lista de hojas entonces la creamos.
    ss.add_worksheet(title=query_list[i] + " - " + uule[j][1], rows= 1000 , cols= 24)

  #Definimos las hojas donde vamos a trasladar los datos de cada consulta
  wk = ss.worksheet(title=query_list[i] + " - " + uule[j][1]) #hoja donde vamos a trasladar los datos del dataframe de los resultados de búsqueda
  df_resultados = pd.DataFrame (resultados_busqueda, columns=['Resultados'],) #convertimos el array que contiene los resultados de búsqueda en un dataframe
  almacenamiento_rastreo(
      hoja_resultados= wk,  
      df_r = df_resultados, 
      texto_resultado_query='no se ha encontrado en los resultados de búsqueda', 
      nombre_expander= nombre_expander,
      url=url,
      )

#========> FUNCIÓN 4 <===========
#Esta función almacena los resultados y los históricos en la Spreadsheet y pinta las tablas y gráficos en streamlit ejecutando la función update_hoja_resultados.
def almacenamiento_rastreo (hoja_resultados, df_r, texto_resultado_query, nombre_expander,url):
  #limpiamos el rango donde almacenamos los resultados del rastreo
  rango_resultados = hoja_resultados.range('A1:B50')
  for celda in rango_resultados:
    celda.value = ''
  hoja_resultados.update_cells(rango_resultados) 

  #pasamos los datos del dataframe a la hoja
  df_r.index = df_r.index + 1 #establecemos el índice del Dataframe en 1 en vez de en 0 que es el que viene por defecto.
  set_with_dataframe(hoja_resultados,df_r, row=1, col=1, include_index=True) #pasamos los datos del dataframe de los resultados de búsqueda a la hoja correspondiente
  
  #condicional para saber qué tipo de búsqueda está rastreando y pegar los valores en un rango concreto de la spreadsheet en función del tipo de búsqueda.
  if nombre_expander == nombre_expander_b_m:
    update_hoja_resultados (hoja_resultados=hoja_resultados, df_r=df_r, texto_resultado_query=texto_resultado_query, nombre_expander=nombre_expander, url=url, num_col_hora=3, num_col_query=4, num_col_resultado=5, rango='C:E', indice=3)
  elif nombre_expander == nombre_expander_c_m:
    update_hoja_resultados (hoja_resultados=hoja_resultados, df_r=df_r, texto_resultado_query=texto_resultado_query, nombre_expander=nombre_expander,url=url, num_col_hora=6, num_col_query=7, num_col_resultado=8, rango='F:H', indice=6)
    entidades(df_r=df_r)
  elif nombre_expander == nombre_expander_b_d:
    update_hoja_resultados (hoja_resultados=hoja_resultados, df_r=df_r, texto_resultado_query=texto_resultado_query, nombre_expander=nombre_expander,url=url, num_col_hora=9, num_col_query=10, num_col_resultado=11, rango='I:K', indice=9)
  elif nombre_expander == nombre_expander_c_d:
    update_hoja_resultados (hoja_resultados=hoja_resultados, df_r=df_r, texto_resultado_query=texto_resultado_query, nombre_expander=nombre_expander,url=url, num_col_hora=12, num_col_query=13, num_col_resultado=14, rango='L:N', indice=12)
    entidades(df_r=df_r)


#===========>FUNCIÓN 5 <===============
#Función anidada dentro de la función almacenamiento rastreo. Función para actualizar las celdas de la hoja de spreadsheet con los datos obtenidos del rastreo.
def update_hoja_resultados (hoja_resultados, df_r, texto_resultado_query, nombre_expander, num_col_hora, num_col_query, num_col_resultado, rango, indice, url):
  patron = re.compile(patron_seleccionado[0]) #creamos el patrón para buscar la url entre los resultados usando regex para obtener el valor de la posición.
  #creamos un for para recorrer las celdas con los resultados del rastreo y buscar dentro de ella si contiene la expresion elegida en el menú. 
  columna_resultados = hoja_resultados.col_values(2) #averiguamos cuantas celdas tienen contenido en la columna 2 para saber la duración del for
  for n in range (len(columna_resultados)):
    encontrarPatron = patron.search(hoja_resultados.cell(n+1,2).value) #buscamos el patrón en cada celda de la columna dos
    if encontrarPatron != None: #Si la encuentra nos da el valor de la celda que contiene la posición. Sumamos 1 porque la primera celda de la columna está vacía.
      pos = hoja_resultados.cell(n+1,1).value
      resultado_query = hoja_resultados.cell(n+1,2).value
      break #si encuentra la expresión salimos del condicional
    else:
      pos = 0 #Si no, la posición será 0.
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
  with st.beta_expander(nombre_expander, expanded=True):
    st.text('Posición último rastreo: ' + str(pos)+ '\nla url de búsqueda es: ' + url)
    st.subheader('Resultados búsqueda')
    st.dataframe(df_r)#Pintamos el dataframe con los resultados de la última búsqueda
    st.subheader('Histórico de posiciones')
    st.dataframe(dfFinal) #pintamos el dataframe del histórico
    st.subheader('Gráfico de posiciones')
    st.vega_lite_chart(dfFinal,{
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
def entidades (df_r):
  from google.cloud import language_v1
  from google.cloud.language_v1 import enums

  from google.cloud import language
  from google.cloud.language import types

  import matplotlib.pyplot as plt
  from matplotlib.pyplot import figure

  #creamos un dict con el contenido de las credenciales de json
  contenido_json = {
    "type": st.secrets["type"],
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "auth_uri": st.secrets["auth_uri"],
    "token_uri": st.secrets["token_uri"],
    "auth_provider_x509_cert_url": st.secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": st.secrets["auth_provider_x509_cert_url"]
  }

  #convertimos el dict en un JSON
  uploaded_file = json.dumps(contenido_json)

  #guardamos el JSON en un archivo temporal para poder llamar al path donde se encuentra el archivo JSON
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

  #elementos HTML para la extracción del texto de la noticia
  elemento_abc = '.cuerpo-texto > p'
  elemento_ppll = '.voc-paragraph'
  elemento_mundo = '.content > p'
  elemento_pais = '.article_body > p'
  elemento_vanguardia = '.amp-scribble-content > p'

  
    
  with st.beta_expander('Entidades'):
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
        elif smag > 2:
          sent_m_label = "Emoción Alta"
        elif smag > 1 and smag < 2:
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

#input email donde recibir las alertas
email_destinatario= st.sidebar.text_input('Email para recibir alertas')

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
patron_seleccionado = st.sidebar.selectbox('Dominio a monitorizar', list(patrones.items()), 1 , format_func=lambda o: o[1])

#Añadimos selectbox para seleccionar qué tipos de resultados queremos monitorizar
tipos_resultados = st.sidebar.multiselect('Tipo de resultado a monitorizar', ['Búsqueda','Carrusel noticias'] )

#Añadimos selectbox al sidebar para seleccionar que resultados queremos en función del tipo de dispositivo 
dispositivo = st.sidebar.multiselect('Dispositivo', ['Móvil', 'Desktop'])

#añadimos a la barra lateral un selectbox para elegir el número de posiciones que queremos rastrear top10, top20, top30
add_selectbox_top = st.sidebar.selectbox(
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
uule = st.sidebar.multiselect('Ubicación de la búsqueda', list(uules.items()), format_func=lambda o: o[1])

#Definimos los datos para el selectbox de frecuencia de rastreo
import random
frecuencias = {
    random.randrange(5*60,10*60): "Cada 5-10 minutos",
    random.randrange(10*60,15*60): "Cada 10-15 minutos",
    random.randrange(30*60,45*60): "Cada 30-45 minutos",  
}
#añadimos al sidebar el selectbox las frecuencia de rastreo definidas
frecuencia = st.sidebar.selectbox('Frecuencia de rastreo', list(frecuencias.items()), 0 , format_func=lambda o: o[1])

#abrimos la spreadsheet donde se almacenan los resultados de búsqueda y los históricos
ss = gc.open_by_url(st.secrets["sheet"])
sheet = ss.sheet1 #definimos la hoja1 de la spreadsheet
lista_wk = ss.worksheets() #sacamos una lista de todas las hojas que hay en la spreadsheet
lista_titulos_wk = [worksheet.title for worksheet in lista_wk] #creamos una lista con todos los títulos de cada hoja dentro de la spreadsheet, ya que la anterior lista contiene más datos además del título.

#añadimos al sidebar el selectbox para seleccionar históricos menos la hoja 1
historicos = st.sidebar.selectbox("Históricos", lista_titulos_wk[1:], index=0) 

#creamos el botón para borrar el histórico seleccionado en el selectbox e incluimos el código a ejecutar si el botón es pulsado
if st.sidebar.button('borrar histórico'):
  wk_del_historico = ss.worksheet(historicos) #definimos la hoja a borrar
  ss.del_worksheet(wk_del_historico) #borramos la hoja
  st.write(wk_del_historico.title + ' borrado correctamente') #ponemos mensaje de confirmación
  st.experimental_rerun()

#añadimos a la barra lateral de la página de streamlit un text area para introducir las búsquedas a monitorizar
busquedas = st.sidebar.text_area('Introduce las búsquedas a monitorizar (una por línea)', height=100)
query_list = busquedas.split("\n")

#Si el campo de tipo de resultado está vacío paramos el script y mostramos un mensaje de advertencia
if tipos_resultados == []:
  st.warning('Por favor, introduce un tipo de resultado')
  st.stop()

#Si el campo de dispositivo está vacío paramos el script y mostramos un mensaje de advertencia
if dispositivo == []:
  st.warning('Por favor, introduce un tipo de dispositivo')
  st.stop()

#Si el campo de ubicación está vacío paramos el script y mostramos un mensaje de advertencia
if uule == []:
  st.warning('Por favor, introduce una ubicación')
  st.stop()

#si el text area donde definimos las busquedas está vacio paramos la ejecución, si no, que siga corriendo el código.
if busquedas == "":
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

    elemento_html_busqueda_desktop = '.yuRUbf'
    elemento_html_busqueda_movil= '.KJDcUb'
    elemento_html_carrusel= '.WlydOe'

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



  
############################### FIN RASTREO ##################################################################
##############################################################################################################

#Generamos cuenta atrás hasta próximo rastreo
import time
with st.empty():
  t= frecuencia[0]
  while t:
    mins, secs = divmod(t, 60)
    timeformat = '{:02d}:{:02d}'.format(mins, secs)
    st.write('Tiempo restante hasta el próximo rastreo: ' + timeformat)
    time.sleep(1)
    t-=1
st.experimental_rerun()
