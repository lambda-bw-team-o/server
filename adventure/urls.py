from django.conf.urls import url
from . import api

urlpatterns = [
    url('init', api.initialize),
    url('move', api.move),
    url('say', api.say),
    url('rooms', api.rooms),
    url('attack', api.attack),
    url('respawn', api.respawn),
    url('cloak', api.cloak),
    url('scores', api.scoreboard)
]
