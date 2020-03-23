# Vagrant Registry

Vagrant Registry is a private self-hosted alternative to [Vagrant Cloud](https://app.vagrantup.com/).

Features:
- user management
- private/public boxes
- upload/download boxes via web app
- boxes are stored on a local drive

![My Boxes](./docs/images/my_boxes.png "My Boxes")

![Box Details](./docs/images/box_details.png "Box Details")

![Box Versions](./docs/images/box_versions.png  "Box Versions")

## Usage
### Public boxes

To use public boxes from Vagrant Registry specify box name and URL, for example
```
$ vagrant init polart/jessie64 http://localhost:3000/polart/jessie64
$ vagrant up
```

### Private boxes

Log in into Vagrant Registry using [Vagrant Registry plugin](https://github.com/polart/vagrant-registry-plugin)
```
$ vagrant registry login http://localhost:3000
```

Init and launch a box
```
$ vagrant init polart/jessie64 http://localhost:3000/polart/jessie64
$ vagrant up
```

<p align="center"><img src="img/vr.gif?raw=true"/></p>

## Production deploy

Vagrant Registry is distributed as a single docker file and available 
on Docker registry [polart/vagrant-registry](https://hub.docker.com/r/polart/vagrant-registry)

Generate a secret key 
```
$ export SECRET_KEY=$(LC_ALL=C tr -dc 'A-Za-z0-9!#$%&' </dev/urandom | head -c 50 ; echo)
```

Create directories for logs and boxes files
```
$ mkdir -p \
    /var/vr/logs/nginx \
    /var/vr/logs/supervisord \
    /var/vr/logs/gunicorn \
    /var/vr/logs/django \
    /var/vr/protected_media
```

Create superuser
```
$ docker exec -it vagrant-registry python3 /code/api/manage.py createsuperuser
```

Start Vagrant Registry
```
$ docker run \
    --rm -d\
    -e SECRET_KEY \
    -v /var/vr/logs/:/logs/ \
    -v /var/vr/protected_media/:/code/api/protected_media/ \
    -v vr-db:/var/lib/postgresql \
    -p 8080:80 \
    --name vagrant-registry \
    polart/vagrant-registry:0.1.2
```

Make sure to run Vagrant Registry behind [reverse proxy](https://en.wikipedia.org/wiki/Reverse_proxy)

## Development

Vagrant Registry is written with Python/Django and ReactJS.

Make sure you have installed Docker and Docker Compose.

Apply DB migrations
```
$ make migrate
```

Create superuser
```
$ make create_superuser
```

Install Yarn packages
```
$ make install_client
```

Start React app and Django server
```
$ make start
```

Open 
- http://localhost:3000 - web app
- http://localhost:3000/admin/ - Django admin
- http://localhost:3000/api/docs/ - API docs

Run tests
```
$ make test
```
