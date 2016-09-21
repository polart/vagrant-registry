import multiprocessing


bind = "unix:/tmp/gunicorn.sock"
workers = multiprocessing.cpu_count() * 2 + 1

pidfile = "/tmp/gunicorn.pid"

# Log settings for Gunicorn, not Django
loglevel = "info"
errorlog = '/logs/gunicorn/gunicorn.log'
