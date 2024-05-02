import os
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql.expression import or_
from sqlalchemy import cast, DateTime
from passlib.hash import bcrypt
from datetime import datetime, date

from fastapi import HTTPException, status, File, UploadFile
from email_validator import validate_email, EmailNotValidError
from fastapi_pagination import paginate, Params
from typing import Optional

from schemas.User import User as UserSchema, UserDisc
from schemas.Sale import SaleDiscUser
from models.Disc import Disc
from models.Sale import Sale
from models.User import User
from PIL import Image as PILimage
import xlsxwriter
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


def buy_disc(db: Session, disc_id: int, current_user:UserSchema):
    """
    Compra de un disco por usuario loggeado, guarda fecha y hora de compra.
    """
    db_discs_user = db.query(Sale).filter(Sale.disc_id == disc_id,Sale.user_id == current_user.id).all()
    if db_discs_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Este disco ya lo compraste.")
    db_sale = Sale(user_id = current_user.id, disc_id = disc_id, created_at=datetime.now(),updated_at=datetime.now())
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

def user_discs(db: Session, user_id: int, page: int = 0, size: int = 10, search: str = None):
    """
    Obtener los discos del usuario actual apartir de la tabla ventas
    """
    sales = (
        db.query(Sale)
        .filter(Sale.user_id == user_id)
        .filter(Sale.deleted_at.is_(None))
        .all()
    )
    if not sales:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No tiene compras.")

    disc_ids = [sale.disc_id for sale in sales]

    query = (
        db.query(Disc)
        .filter(Disc.id.in_(disc_ids))
        .filter(Disc.deleted_at.is_(None))
        .filter(Sale.deleted_at.is_(None))
    )
    if search:
        query = query.filter(
            or_(
                Disc.album.ilike(f"%{search}%"),
                Disc.artist.ilike(f"%{search}%")
            )
        )
    discs = query.all()    
    user_discs = []

    for disc in discs:
        sale = next((s for s in sales if s.disc_id == disc.id), None)
        user_disc = UserDisc(
            id=disc.id,
            file_id=disc.file_id,
            album=disc.album,
            artist=disc.artist,
            genre=disc.genre,
            year=disc.year,
            price=disc.price,
            cover_picture = disc.cover_picture,
            purchase_date = sale.created_at if sale else None
        )
        user_discs.append(user_disc)

    return paginate(user_discs)


def sales(db: Session, search: str, since: Optional[date] = None,to: Optional[date] = None):
    """
    La función "ventas" recupera datos de ventas de una base de datos según los criterios de búsqueda y
    el rango de fechas, y devuelve los resultados en un formato paginado.
    
    :param db: El parámetro `db` es de tipo `Session`, que es una instancia de una sesión de SQLAlchemy.
    Se utiliza para interactuar con la base de datos y ejecutar consultas
    :type db: Session
    :param search: El parámetro "búsqueda" se utiliza para filtrar las ventas según un término de
    búsqueda. Busca el término dado en el nombre del álbum, el nombre del artista y el nombre de usuario
    :type search: str
    :param since: El parámetro "desde" se utiliza para filtrar las ventas según la fecha de inicio. Es
    un parámetro opcional de tipo "fecha", lo que significa que puede aceptar un valor de fecha o
    "Ninguno". Si se proporciona un valor de fecha, las ventas se filtrarán para incluir solo aquellas
    que se crearon en o
    :type since: Optional[date]
    :param to: El parámetro `to` es un parámetro opcional que representa la fecha de finalización del
    período de ventas. Se utiliza para filtrar las ventas según su fecha de creación. Si se proporciona,
    solo se incluirán en el resultado las ventas creadas antes o en la fecha "hasta"
    :type to: Optional[date]
    :return: una lista paginada de objetos SaleDiscUser.
    """
    query = db.query(Sale).\
            join(Disc).\
            join(User).\
            filter(Sale.deleted_at.is_(None)).\
            filter(Disc.deleted_at.is_(None)).\
            filter(User.deleted_at.is_(None)).\
            options(selectinload(Sale.disc)).\
            options(selectinload(Sale.user)).\
            order_by(Sale.id)

    if search:
        query = query.filter(
            or_(
                Disc.album.ilike(f"%{search}%"),
                Disc.artist.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%")
            )
        )

    if since and to:
        # Convertir las fechas a objetos de tipo datetime para que incluyan la hora
        since_datetime = datetime.combine(since, datetime.min.time())
        to_datetime = datetime.combine(to, datetime.max.time())

        query = query.filter(
            Sale.created_at.between(since_datetime, to_datetime)
        )

    sales = query.all()    
    sale_disc_user_list = []
    for sale in sales:
        sale_disc_user = SaleDiscUser(
            id=sale.id,
            disc_id=sale.disc.id,
            album=sale.disc.album,
            artist=sale.disc.artist,
            genre=sale.disc.genre,
            year=sale.disc.year,
            price=float(sale.disc.price),
            cover_picture=sale.disc.file.file_path if sale.disc.file else None,
            purchase_date=sale.created_at,
            user_id=sale.user.id,
            name=sale.user.name,
            username=sale.user.username,
            email=sale.user.email
        )
        sale_disc_user_list.append(sale_disc_user)

    return paginate(sale_disc_user_list)


def download_sales(db: Session, search: Optional[str] = None,since: Optional[date] = None,to: Optional[date] = None):
    query = db.query(Sale).\
            join(Disc).\
            join(User).\
            filter(Sale.deleted_at.is_(None)).\
            filter(Disc.deleted_at.is_(None)).\
            filter(User.deleted_at.is_(None)).\
            options(selectinload(Sale.disc)).\
            options(selectinload(Sale.user)).\
            order_by(Sale.id)

    if search:
        query = query.filter(
            or_(
                Disc.album.ilike(f"%{search}%"),
                Disc.artist.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%")
            )
        )

    if since and to:
        # Convertir las fechas a objetos de tipo datetime para que incluyan la hora
        since_datetime = datetime.combine(since, datetime.min.time())
        to_datetime = datetime.combine(to, datetime.max.time())

        query = query.filter(
            Sale.created_at.between(since_datetime, to_datetime)
        )

    sales = query.all()    
    sales_disc_user_list = []
    for sale in sales:
        sale_disc_user = SaleDiscUser(
            id=sale.id,
            disc_id=sale.disc.id,
            album=sale.disc.album,
            artist=sale.disc.artist,
            genre=sale.disc.genre,
            year=sale.disc.year,
            price=float(sale.disc.price),
            cover_picture=sale.disc.file.file_path if sale.disc.file else None,
            purchase_date=sale.created_at,
            user_id=sale.user.id,
            name=sale.user.name,
            username=sale.user.username,
            email=sale.user.email
        )
        sales_disc_user_list.append(sale_disc_user)

    if not os.path.exists("exports/excel/sales"):
        os.makedirs("exports/excel/sales")

    # Crear el nombre del archivo de acuerdo al filtro aplicado
    timestamp = datetime.now().strftime('%d_%m_%Y_%H%M%S')
    filename = f"ventas_{timestamp}"
    filepath = f"exports/excel/sales/{filename}.xlsx"
    # Crear el workbook y la hoja
    workbook = xlsxwriter.Workbook(filepath)
    worksheet = workbook.add_worksheet('Lista de Ventas')

    # Combinar las celdas A1 a A4
    worksheet.merge_range('A1:I5', '')

    img = PILimage.open('static/images/image.png')
    img_resized = img.resize((300, 300))
    img_width, img_height = img_resized.size
    worksheet.set_column('A:A', img_width/7)
    worksheet.set_row(0, img_height/15)
    worksheet.set_row(1, img_height/15)
    worksheet.set_row(2, img_height/15)
    worksheet.set_row(3, img_height/15)
    worksheet.insert_image('A1', 'static/images/image_logo.png')

    worksheet.set_column('A:A', 10)
    worksheet.set_column('B:B', 55)
    worksheet.set_column('C:C', 55)
    worksheet.set_column('D:D', 15)
    worksheet.set_column('E:E', 15)
    worksheet.set_column('F:F', 15)
    worksheet.set_column('G:G', 25)
    worksheet.set_column('H:H', 30)
    worksheet.set_column('I:I', 25)

    bold = workbook.add_format({'bg_color': '#009f86', 'align': 'center','color':"white"})
    worksheet.write('A6','ID',bold)
    worksheet.write('B6','ALBUM',bold)
    worksheet.write('C6','ARTISTA',bold)
    worksheet.write('D6','GENERO',bold)
    worksheet.write('E6','AÑO',bold)
    worksheet.write('F6','PRECIO',bold)
    worksheet.write('G6','CLIENTE',bold)
    worksheet.write('H6','CORREO',bold)
    worksheet.write('I6','FECHA DE COMPRA',bold)


    total = 0
    for idx, sale in enumerate(sales_disc_user_list):
        row = idx + 7
        center = workbook.add_format({'align': 'center'})
        currency_format = workbook.add_format({'num_format': '$#,##0.00','align': 'center'})
        worksheet.write(f'A{row}',sale.id,center)
        worksheet.write(f'B{row}',sale.album,center)
        worksheet.write(f'C{row}',sale.artist,center)
        worksheet.write(f'D{row}',sale.genre,center)
        worksheet.write(f'E{row}',sale.year,center)
        worksheet.write(f'F{row}',sale.price,currency_format)
        worksheet.write(f'G{row}',sale.name,center)
        worksheet.write(f'H{row}',sale.email,center)
        worksheet.write(f'I{row}',sale.purchase_date.strftime('%d/%m/%Y %H:%M:%S'),center)
        total += sale.price

    bold = workbook.add_format({'bg_color': '#009f86', 'align': 'center','color':"white"})
    last_row = len(sales_disc_user_list) + 7
    worksheet.write(f'A{last_row}','',center)
    worksheet.write(f'B{last_row}','',center)
    worksheet.write(f'C{last_row}','',center)
    worksheet.write(f'D{last_row}','',center)
    worksheet.write(f'E{last_row}','TOTAL',bold)
    worksheet.write(f'F{last_row}',total,currency_format)
    worksheet.write(f'G{last_row}','',center)
    worksheet.write(f'H{last_row}','',center)
    worksheet.write(f'I{last_row}','',center)

    worksheet.title = "Ventas"
    workbook.close()

    return {"message": "Archivo excel generado correctamente.", "file_path": filepath}


def generate_sales_report(db: Session, search: Optional[str] = None,since: Optional[date] = None,to: Optional[date] = None):
    # Obtener la lista de ventas del mes actual
    # month_sales = db.query(Sale).filter(
    #     Sale.created_at.month == datetime.now().month
    # ).all()

    query = db.query(Sale).\
            join(Disc).\
            join(User).\
            filter(Sale.deleted_at.is_(None)).\
            filter(Disc.deleted_at.is_(None)).\
            filter(User.deleted_at.is_(None)).\
            options(selectinload(Sale.disc)).\
            options(selectinload(Sale.user)).\
            order_by(Sale.id)
            # filter(cast(Sale.created_at, DateTime).month == datetime.now().month).\

    if search:
        query = query.filter(
            or_(
                Disc.album.ilike(f"%{search}%"),
                Disc.artist.ilike(f"%{search}%"),
                User.name.ilike(f"%{search}%")
            )
        )

    if since and to:
        # Convertir las fechas a objetos de tipo datetime para que incluyan la hora
        since_datetime = datetime.combine(since, datetime.min.time())
        to_datetime = datetime.combine(to, datetime.max.time())

        query = query.filter(
            Sale.created_at.between(since_datetime, to_datetime)
        )

    sales = query.all()    
    month_sales = []
    for sale in sales:
        sale_disc_user = SaleDiscUser(
            id=sale.id,
            disc_id=sale.disc.id,
            album=sale.disc.album,
            artist=sale.disc.artist,
            genre=sale.disc.genre,
            year=sale.disc.year,
            price=float(sale.disc.price),
            cover_picture=sale.disc.file.file_path if sale.disc.file else None,
            purchase_date=sale.created_at,
            user_id=sale.user.id,
            name=sale.user.name,
            username=sale.user.username,
            email=sale.user.email
        )
        month_sales.append(sale_disc_user)

    # Crear el PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    # Definir los estilos
    # pdfmetrics.registerFont(TTFont('Roboto', 'fonts/Roboto-Regular.ttf'))
    # pdfmetrics.registerFont(TTFont('Roboto-Bold', 'fonts/Roboto-Bold.ttf'))

    # styles = {
    #     'title': {
    #         'fontName': 'Roboto-Bold',
    #         'fontSize': 20,
    #         'leading': 24,
    #         'alignment': 1, # centrado
    #         'spaceAfter': 20,
    #     },
    #     'header': {
    #         'fontName': 'Roboto-Bold',
    #         'fontSize': 12,
    #         'leading': 14,
    #         'textColor': colors.white,
    #         'bgColor': colors.green,
    #         'alignment': 1, # centrado
    #     },
    #     'cell': {
    #         'fontName': 'Roboto',
    #         'fontSize': 10,
    #         'leading': 12,
    #         'alignment': 1, # centrado
    #     }
    # }
    styles = getSampleStyleSheet()

    # Crear los elementos del PDF
    Story = []

    # Título
    # title = Paragraph('Ventas del mes actual 1', styles['title'])
    # Story.append(title)

    # Imagen
    

    # Tabla
    data = [['ID','FECHA','CLIENTE','ALBUM','ARTISTA','PRECIO']]
    total = 0
    for idx,sale in enumerate(month_sales):
        index = f'{idx+1}'
        purchase_date = sale.purchase_date.strftime('%d/%m/%Y')
        client = sale.name
        album = sale.album
        artist = sale.artist
        price = f"${sale.price:,.2f}"
        total += sale.price
        data.append([index,purchase_date,client,album,artist,price])

    data.append(['','','','','Total',f"${total:,.2f}"])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#009f86')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#FFFFFF')),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#000000')),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),

        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),

        ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
        ('TOPPADDING', (0, 0), (-1, 0), 1),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 5),
        ('TOPPADDING', (0, 1), (-1, -1), 5),

        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F2F2F2')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#BDBDBD')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, -1), (-1, -1), 7)
    ]))

    
    
    # Título del PDF
    title = Paragraph("Ventas", styles['Title'])

    image = Image('static/images/image.png', width=200, height=55)
    image.hAlign = 'CENTER'

    Story.append(image)
    Story.append(title)
    Story.append(Spacer(1, 24))
    Story.append(table)

    # Crear el documento PDF
    timestamp = datetime.now().strftime('%d_%m_%Y_%H%M%S')
    filename = f"reporte_de_ventas_{timestamp}"
    filepath = f"exports/pdf/sales/{filename}.pdf"
    pdf_doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    pdf_doc.build(Story)

    return {"message": "Archivo pdf generado correctamente.", "file_path": filepath}
