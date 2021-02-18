<div align="center">
  <h1>eHealth Backend</h1>
</div>

## Requirements

This Project is developed using **Flask** and **SQLAlchemy**.
<br />

## Structure

```

├── app.py                  # Application entry point
├── sql                     # SQL dump to init database and tables
├── config.py               # includes configurations for DB                                        
├── src
│    └── API ENDPOINTS
│    │    └── api.py                   # REST api definition
│    │    └── endpoint_name.py         # Core functions
│    │exceptions
│    │    └── app_exception.py         # Execptions are written over here
├── test
│    └── postman                       # Includes Postman tests
├────models.py                         # SQLAlchemy models
├────serializer.py                     # Serializing the input and output data  
```
<br />


## How to run project locally

Clone the repository:

```
$ https://gitlab.com/harshil.99/ehealth_backend.git
```

Installing the Requirements::

```
$ cd ehealth_backend
$ source path/to/env/activate
$ python -m pip install -r requirements.txt
```

Setting up Postgres:

```

CREATE SUPERUSER:

    $ createuser --interactive <username>

CREATE USER:
    
    $ sudo -u postgres psql

    postgres=# CREATE USER <username> with PASSWORD '<password>';
    
        IF Output == CREATE ROLE, then exit from the postgres terminal by pressing "\q"

    postgres=# \q 

CREATE DB:
    
    $ sudo -u postgres createdb <db_name>  #default name = "eHealth"


CHECK THE CONNECTION:

    default hostname: 127.0.0.1
    default port: 5432
    default db_name: eHealth

    $ psql postgresql://<username>:<password>@<hostname>:<port>/<db_name>

```

## If the the connection is established successfully change add the postgres connection url in  the app.py file 

`See the example below with username=admin, password=admin, host=localhost, port=5423, db_name=eHealth`

```
postgresql://admin:admin@localhost:5432/eHealth

```

3. Creating Database schema named `eHealth` <br />
   
   -  python manage.py db init
   -  python manage.py db migrate
   -  python manage.py db upgrade
   
        
   
4. Run app <br />
`python app.py`
   
<br />
