
# Tienda de Discos

Sistema para la administración del inventario de venta de
discos de vinilo, este sistema cuenta con lo siguiente.

1. Inicio de sesión
        
        Correo electrónico y contraseña
        
2. Recuperación de contraseña.
        
        Comprobación de correo electrónico válido y existente.
        Envío de un enlace al correo electrónico del usuario, para que se pueda
        restablecer dicha contraseña.

3. Registro. 
    
        Se debe permitir el registro de nuevos usuarios, este registro debe solicitar:
        ■ Nombre completo
        ■ Nombre Usuario
        ■ Correo electrónico
        ■ Contraseña
        ■ Scopes (permisos)
        

        Una vez realizado el registro se debe enviar un correo electrónico al usuario 
        informando que se realizó un registro en el portal y que es necesario activar
        su cuenta dando click en el enlace adjunto al correo, de lo contrario su cuenta
        permanecerá inactiva. (Se debe mandar un enlace en el correo para activar la cuenta).

4. Una vez dentro del sistema, cuenta con los siguientes módulos:

    4.1 CRUD de usuarios. 
        
        Se deben poder crear, tanto administradores como usuarios, la diferencia 
        entre ambos es que los administradores pueden editar usuarios.

    4.2 CRUD de discos
        
        Creación de discos
        
        ● Nombre
        ● Álbum
        ● Artista
        ● Género
        ● Año
        ● Foto de portada
    4.3 Listado de discos
        
        ● Búsqueda por: 
           ■ Nombre
           ■ Album 
           ■ Artista
        ● Edición de cada disco
        ● Eliminación de cada disco

    4.4 Compra de un disco

        ● Nombre del disco
        ● Usuario que lo compro
        ● Precio
        ● Fecha de compra
    
    4.4 Carga masiva de discos por Excel

        ● Definición de layout
            ■ ARTISTA	
            ■ ALBUM	
            ■ GENERO	
            ■ AÑO	
            ■ PRECIO

    4.5 Descarga de inventario de discos por Excel

        ● Definición de cabeceras
            ■ ID	
            ■ ARTISTA	
            ■ ALBUM	
            ■ GENERO	
            ■ AÑO	
            ■ PRECIO

    4.6 Generación de reporte de ventas por Excel

        ● Definición de cabeceras
            ■ ID	
            ■ ALBUM	
            ■ ARTISTA	
            ■ GENERO	
            ■ AÑO	
            ■ PRECIO	
            ■ CLIENTE	
            ■ CORREO	
            ■ FECHA DE COMPRA

    4.7 Generación de reporte de ventas por PDF

        ● Definición de cabeceras
            ■ ID	
            ■ FECHA DE COMPRA
            ■ CLIENTE	
            ■ ALBUM	
            ■ ARTISTA	
            ■ PRECIO	
            ■ TOTAL

    4.8 Conexión con API de Spotify.

        Consulta para buscar discos y guardarlos en la base de datos.
         
## Screenshots

![Fast API](https://i.ibb.co/JtjLBVC/Captura-de-Pantalla-2023-06-16-a-la-s-19-26-36.png)

![Excel](https://i.ibb.co/HpWjBwp/Captura-de-Pantalla-2023-06-16-a-la-s-19-45-22.png)

![PDF](https://i.ibb.co/DGR1JLq/Captura-de-Pantalla-2023-06-16-a-la-s-19-38-41.png)
## Acknowledgements

 - [Python](https://www.python.org/downloads/)
 - [FastAPI](https://fastapi.tiangolo.com/)
 


## Layout

Layout para carga masiva de Discos
- [Layout](https://sorianoarizacom-my.sharepoint.com/:x:/g/personal/r_salazard_soriano-ariza_com/EV3D1FcM9FxGkqKP3gamUzoBwCRIhoFFwT1mN3p8GjAnUA?e=egkAsP)


## Authors

- [@rodsalazard](https://bitbucket.org/rodsalazard)


## Badges

[![MIT License](https://img.shields.io/pypi/pyversions/fastapi?color=green&logo=python)](https://www.python.org/downloads/)
[![MIT License](https://img.shields.io/pypi/v/fastapi?color=%2334D058&label=pypi%20package)](https://pypi.org/project/fastapi/)
## Color Reference

| Color             | Hex                                                                |
| ----------------- | ------------------------------------------------------------------ |
| Example Color | ![#0a192f](https://via.placeholder.com/10/0a192f?text=+) #0a192f |
| Example Color | ![#f8f8f8](https://via.placeholder.com/10/f8f8f8?text=+) #f8f8f8 |
| Example Color | ![#00b48a](https://via.placeholder.com/10/00b48a?text=+) #00b48a |
| Example Color | ![#00d1a0](https://via.placeholder.com/10/00b48a?text=+) #00d1a0 |


## Contributing

Las contribuciones siempre son bienvenidas! 😄



## Run Locally

Clone the project

```bash
  git clone https://link-to-project
```

Create a database and define the credentials in app/database/connection.py and it will automatically create the tables in database:
```bash
  DATABASE_URL = "mysql+mysqlconnector://user:password@localhost:3306/database"
```

You can create a virtual environment in a directory using Python's venv module:

```bash
  python3 -m venv env
```

Activate the new environment with:
```bash
  source ./env/bin/activate
```

After activating the environment as described above:
```bash
  pip3 install -r requirements.txt

```
It will install all the dependencies and your local FastAPI in your local environment.


Go to the project directory

```bash
  cd app
```

Start the server

```bash
    python3 -m uvicorn app:app --reload
```

To visualize the documentation:
```bash
    http://127.0.0.1:8000/docs
```



## Documentation

 - [Python](https://www.python.org/downloads/)
 - [FastAPI](https://fastapi.tiangolo.com/)
 - [Sqlalchemy](https://www.sqlalchemy.org/)   
 - [Openpyxl](https://openpyxl.readthedocs.io/en/stable/)
 - [Pandas](https://pandas.pydata.org/)
 - [FastAPI Pagination](https://github.com/uriyyo/fastapi-pagination)
 - [Database to Code (ORMs)](https://sqlmodel.tiangolo.com/db-to-code) 
 - [How to Send Emails in Python with Gmail](https://mailtrap.io/blog/python-send-email-gmail/)
 - [Spotify for Developers WEB API documentation ](https://developer.spotify.com/documentation/web-api)


## Environment Variables

Para correr este proyecto, definir las siguientes variables en tabla de la base de datos llamada _vars_:

`SECRET_KEY`

    Para obtener una cadena como esta

    "9f0c089cc405abfbe78673a6627456e5ab1553b4..."
    
    ejecuta:
    
    openssl rand -hex 32

    Necesaria para el OAuth2 con contraseña (y hashing), Bearer con tokens JWT.


`ALGORITHM`
            HS256

`ACCESS_TOKEN_EXPIRE_MINUTES`
            30

`CLIENT_ID`
        CLIENT ID PARA SPOTIFY

`CLIENT_SECRET`
        CLIENT_SECRET PARA SPOTIFY 




## Feedback

If you have any feedback, please reach out to us at r.salazard@soriano-ariza.com


## 🚀 About Me
I'm software developer 🦊

