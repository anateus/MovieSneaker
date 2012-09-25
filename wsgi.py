# This file is for dotcloud to be able to launch the flask app

import sys
sys.path.append('/home/dotcloud/current')
sys.path.append('/home/dotcloud/current/MovieSneaker')

from MovieSneaker import app as application
