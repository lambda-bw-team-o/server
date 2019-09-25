from django.contrib.auth.models import User
from adventure.models import Player, Room
from util.arronm_generator import World


Room.objects.all().delete()

w = World()
num_rooms = 50
width = 20
height = 20
seed = "Bdq41Yxzssvm0ALw"
# seed = None
spawn = w.generate_rooms(width, height, num_rooms, seed)
w.print_rooms()

players=Player.objects.all()
for p in players:
  p.currentRoom=spawn.id
  p.save()
