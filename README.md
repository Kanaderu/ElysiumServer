# ElysiumServer

## Development Setup

### Install Dependencies

This can usually be done by installing the packages defined by the `requirements.txt` list. Running the following command should do the trick:

```bash
python -m pip install -r requirements.txt
```

### Initialization and Setup

- First create a `logs/` directory at the project root to store the logger output
- Run the usual Django setup steps. (Note: Remember that migrating is only needed if any `models.py` are updated)
```
# build database tables
python manage.py makemigrations
python manage.py migrate

# create admin user
python manage.py createsuperuser

# run development server
python manage.py runserver
``` 

## Django and uWSGI Setup

https://uwsgi-docs.readthedocs.io/en/latest/tutorials/Django_and_nginx.html

## Setting `LetsEncrypt` with Nginx

https://www.nginx.com/blog/using-free-ssltls-certificates-from-lets-encrypt-with-nginx/
