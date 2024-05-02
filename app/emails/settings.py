import os
import base64
import pickle
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError
from schemas.User import UserCreate

SCOPES = [
        "https://www.googleapis.com/auth/gmail.send"
    ]
flow = InstalledAppFlow.from_client_secrets_file('emails/credentials.json', SCOPES)
# creds = flow.run_local_server(port=0)
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)
else:
    creds = flow.run_local_server(port=0)
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)


service = build('gmail', 'v1', credentials=creds)

def send_email(user: UserCreate, link_activation:str):

    message = MIMEMultipart()

    # Agrega la parte de texto
    msg = f'''
    <html>
        <body>
            <img src="https://admin.soriano-ariza.com/storage/1711067829_65fcd2b592db5.png" alt="Imagen" style="display: block; margin: 0 auto;width:30%">
            <p>Hola {user.name},</p>
            <p>Gracias por registrarte en nuestro portal. Para activar tu cuenta, por favor haz clic en el siguiente enlace:</p>
            <a href="{link_activation}">Activar cuenta</a>
            <br/><br/>
            <p>Si no puedes hacer clic en el enlace, copia y pega la siguiente URL en tu navegador:</p>
            <a href="{link_activation}">{link_activation}</a>
            <br/><br/>
            <p>Si no has registrado una cuenta en nuestro portal, por favor ignora este mensaje.</p>
            <br/><br/>
            <p>Saludos cordiales.</p>
            <p>El equipo de SA&A</p>
        </body>
    </html>
    '''

    html = f'''<html>
              <head>
                <style></style>
              </head>
              <body>
                <table width="100%" bgcolor="#f5f5f5" cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse;">
                  <tr>
                    <td>
                      <table width="600" align="center" cellpadding="0" cellspacing="0" border="0" style="border-collapse: collapse;">
                      <tr>
                        <td>
                          <img src="https://admin.soriano-ariza.com/storage/1711067829_65fcd2b592db5.png" alt="Imagen" style="display: block; margin: 0 auto;width:65%">
                        </td>
                      </tr>
                        <tr>
                          <td style="background-color: #fff; padding: 40px; border-radius: 5px;">
                            <p>Hola <strong>{user.name}</strong>.</p>
                            <p>Gracias por registrarte en nuestro portal. Para activar tu cuenta, por favor haz clic en el siguiente enlace:</p>
                            <p style="text-align: center;">
                              <a href="{link_activation}" style="display: inline-block; background-color: #009f86; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Activar cuenta</a>
                            </p>
                            <br/>
                            <p>Si no puedes hacer clic en el enlace, copia y pega la siguiente URL en tu navegador:</p>
                            <p style="text-align: center;">
                              <a href="{link_activation}" style="color: #009f86; text-decoration: none;">{link_activation}</a>
                            </p>
                            <br/>
                            <p>Si no has registrado una cuenta en nuestro portal, por favor ignora este mensaje.</p>
                            <br/>
                            <p>Saludos cordiales.</p>
                            <p>El equipo de SA&A</p>
                            <br>
                            <br>
                            <img src="https://admin.soriano-ariza.com/storage/1711067829_65fcd2b592db5.png" alt="Imagen" style="display: block; margin: 0 auto;width:35%">
                          </td>
                        </tr>
                      </table>
                    </td>
                  </tr>
                </table>
              </body>
            </html>
    '''
    my_css = """<style>
      body {
            font-family: Arial, sans-serif;
            color: #333;
            background-color: #000;
            line-height: 1.6;
            margin: 0;
            padding: 0;
          }
          
          /* Estilos responsivos */
          @media only screen and (max-width: 600px) {
            /* Ajuste para dispositivos móviles */
            body {
              font-size: 16px !important;
            }
          }
    </style>"""

    msg = html.replace('<style></style>', my_css)
    message.attach(MIMEText(msg, 'html'))

    # Agrega la parte de imagen
    # with open('image.png', 'rb') as f:
    #     img_data = f.read()
    # image = MIMEImage(img_data, name='image.png')
    # message.attach(image)


    message['to'] = user.email
    message['subject'] = 'Activación de cuenta'
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'sent message to {message} Message Id: {message["id"]}')
    except HTTPError as error:
        print(F'Ah ocurrido un error: {error}')
        message = None



os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'