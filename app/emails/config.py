import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schemas

# Configuración de la conexión SMTP
smtp_server = 'smtp.office365.com'
smtp_port = 587
smtp_username = 'tecnologia@soriano-ariza.com'
smtp_password = ''



def send_email(user: schemas.UserCreate, link_activation:str):
    # Creación del mensaje
    msg = MIMEMultipart()
    msg['From'] = 'tecnologia@soriano-ariza.com'
    msg['To'] = 'rsalazargw@ciencias.unam.mx'
    msg['Subject'] = 'Activación de cuenta'

    # Cuerpo del mensaje
    message = f'''
    Hola {user.name},

    Gracias por registrarte en nuestro portal. Para activar tu cuenta, por favor haz clic en el siguiente enlace:
    {link_activation}

    Si no puedes hacer clic en el enlace, copia y pega la siguiente URL en tu navegador:
    {link_activation}

    Si no has registrado una cuenta en nuestro portal, por favor ignora este mensaje.

    Saludos cordiales,
    El equipo de nuestro portal
    '''
    msg.attach(MIMEText(message, 'plain'))

    # Envío del mensaje
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, user.email, msg.as_string())


