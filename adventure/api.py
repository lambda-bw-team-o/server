from decouple import config
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pusher import Pusher
from django.core import serializers
from django.http import HttpResponse
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view
import json
import random

# instantiate pusher
pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@csrf_exempt
@api_view(["GET"])
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    # players = room.playerNames(player_id)
    playerObjs = room.players(player_id)
    return JsonResponse({'uuid': uuid, 'protected': room.safe, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players': playerObjs}, safe=True)


@csrf_exempt
@api_view(["POST"])
def move(request):
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player

    # if player cloak timer < 30 minutes
    # Unable to move while cloak is active

    if player.health <= 0:
        return JsonResponse({'status': "You are unable to move while your ship is destroyed. Try respawning."})

    player_id = player.id
    player_uuid = player.uuid
    direction = request.data['direction']
    room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        playerObjs = nextRoom.players(player_id)

        for p_uuid in currentPlayerUUIDs:
            pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        for p_uuid in nextPlayerUUIDs:
            pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'protected': nextRoom.safe, 'title':nextRoom.title, 'description':nextRoom.description, 'players': playerObjs, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'protected': room.safe, 'title':room.title, 'description':room.description, 'players': playerObjs, 'error_msg':"You cannot move that way."}, safe=True)


@csrf_exempt
@api_view(["POST"])
def say(request):
    player = request.user.player
    
    if player.health <= 0:
        return JsonResponse({'status': "Communication is down while your ship is destroyed. Try respawning."})
    
    message = request.data['message']
    room = player.room()
    playerUUIDs = room.playerUUIDs(player.id)
    for p_uuid in playerUUIDs:
        pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username}: {message}.'})
    return JsonResponse({'status': 'success', 'message': message}, safe=True)

# import datetime
# import pytz
# pytz.utc.localize(datetime.datetime.utcnow())
@csrf_exempt
@api_view(["POST"])
def attack(request):
    player = request.user.player
    enemy = Player.objects.get(id=request.data['enemy'])
    # Check if enemy ship is already destroyed
    if enemy.health <= 0:
        return JsonResponse({'status': 'As you call to fire up your lasers, your scans come back indicating your target has previously been destroyed.'})

    # Check if room is a safe zone
    if player.room().safe:
        return JsonResponse({'status': 'As you begin your fire sequence a patrol ship flies nearby. You scramble to cancel the command.'})

    # Check cloak timer
    # Check if they're cloaked

    # Roll attack
    if random.randint(0, 99) >= 50:
        # It's a hit!
        enemy.health -= 1
        pusher.trigger(f'p-channel-{enemy.uuid}', u'broadcast', {'combat': f'{player.user.username} has hit your ship.'})

        if enemy.health <= 0:
            # enemy.currentRoom = 1 # opting for manual respawn instead of auto
            enemy.score  -= 1
            if enemy.score < 0:
                enemy.score = 0
            enemy.save()
            # Increase players score
            player.score += 1
            player.save()
            pusher.trigger(f'p-channel-{enemy.uuid}', u'broadcast', {'combat': f'{player.user.username} has destroyed your ship!'})
            return JsonResponse({'score': player.score, 'status': 'You have destroyed the target vessel.'})
        else:
            enemy.save()
            # respond hit
            return JsonResponse({'status': 'A direct hit!'})
    else:
        # respond miss
        pusher.trigger(f'p-channel-{enemy.uuid}', u'broadcast', {'combat': f'{player.user.username} has fired on your ship and missed!'})
        return JsonResponse({'status': 'What a miss, you sure showed that space of space!'})

# def cloak

@csrf_exempt
@api_view(["POST"])
def respawn(request):
    player = request.user.player

    # check if health is zero
    if player.health != 0:
        return JsonResponse({'status': 'You frantically run around hitting every big red button you see, alas there is no self destruct to be found.'})
    
    # Send player back to respawn
    player.currentRoom = 1
    player.health = 5
    player.save()
    room = player.room()
    playerObjs = room.players(player.id)
    return JsonResponse({'uuid': player.uuid, 'protected': room.safe, 'name': player.user.username, 'title': room.title, 'description': room.description, 'players': playerObjs}, safe=True)


@csrf_exempt
@api_view(["GET"])
def rooms(request):
    data = list(Room.objects.values())
    return JsonResponse({
        "grid": {
            "width": config("GRID_WIDTH", default=20, cast=int),
            "height": config("GRID_HEIGHT", default=20, cast=int),
            "num_rooms": len(Room.objects.all())
        },
        "rooms": data
    })
