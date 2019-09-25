from django.contrib.auth.models import User
from adventure.models import Player, Room
from util.arronm_generator import World
from decouple import config

Room.objects.all().delete()

w = World()
num_rooms = config("GRID_ROOMS", default=100, cast=int)
width = config("GRID_WIDTH", default=20, cast=int)
height = config("GRID_HEIGHT", default=20, cast=int)
seed = config("GRID_SEED", default=None)
spawn = w.generate_rooms(width, height, num_rooms, seed)
w.print_rooms()

players = Player.objects.all()

for p in players:
  p.currentRoom=spawn.id
  p.save()
