import multiprocessing

bind = "0.0.0.0:5001"
workers = multiprocessing.cpu_count() * 2 + 1

# Choose one as appropriate.
# worker_class = "sync"
worker_class = "gthread" # Python 3 only.
# worker_class = "gevent"
# worker_class = "eventlet"
# worker_class = "tornado"

# Change to false to disable daemonising.
# daemon = True
daemon = False

# Change to specify the user gunicorn will run as.
# user = "nobody"
# Change to specify the group gunicorn will run as.
# group = "nogroup"

# SSL settings.
# If you are running the server without a reverse proxy (nginx or apache), this is highly recommended.

# keyfile = "ssl/server.key"
# certfile = "ssl/server.crt"

#accesslog = "/var/skier/log/access.log"
#errorlog = "/var/skier/log/error.log"


def when_ready(server):
    print("Server ready on address {}.".format(bind))