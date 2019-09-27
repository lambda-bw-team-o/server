from decouple import config
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pusher import Pusher
from django.core import serializers
from django.db.models import F
from django.http import HttpResponse
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view
import json
import random
import datetime
import pytz

# instantiate pusher
pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))


@api_view(["GET"])
@csrf_exempt
def initialize(request):
    user = request.user
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    playerObjs = room.players(player_id)
    return JsonResponse({
        'uuid': uuid,
        'position': [room.x, room.y],
        'combat': { 'protected': room.safe, 'health': player.health, 'cloaked': player.cloaked },
        'name':player.user.username,
        'title':room.title,
        'description':room.description,
        'players': playerObjs
    }, safe=True)


# @csrf_exempt
@api_view(["POST"])
def move(request):
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    now = pytz.utc.localize(datetime.datetime.utcnow())

    # check cloak timer to see if they can take action
    if player.cloak_timer and (now - player.cloak_timer) < datetime.timedelta(minutes=30):
        # Unable to move while cloak is active
        return JsonResponse({'status': f'Unable to move while cloaked and maintenance is ongoing. Try again later.'})

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
        return JsonResponse({
            'name':player.user.username,
            'position': [nextRoom.x, nextRoom.y],
            'combat': { 'protected': nextRoom.safe, 'health': player.health, 'cloaked': player.cloaked },
            'title': nextRoom.title,
            'description': nextRoom.description,
            'players': playerObjs,
            'error_msg':""
        }, safe=True)
    else:
        playerObjs = room.players(player_id)
        return JsonResponse({
            'name':player.user.username,
            'position': [room.x, room.y],
            'combat': { 'protected': room.safe, 'health': player.health, 'cloaked': player.cloaked },
            'title':room.title,
            'description':room.description,
            'players': playerObjs,
            'error_msg':"You cannot move that way."
        }, safe=True)


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


@csrf_exempt
@api_view(["POST"])
def attack(request):
    # TODO: Check that enemy is in the same room
    player = request.user.player
    enemy = Player.objects.get(id=request.data['enemy'])
    combat_timer = pytz.utc.localize(datetime.datetime.utcnow())

    # check that enemy is in the same room
    if player.room() != enemy.room():
        return JsonResponse({'status': f'Target vessel does not appear to be within attack range.'})

    # check cloak timer to see if they can take action
    if player.cloak_timer and (combat_timer - player.cloak_timer) < datetime.timedelta(minutes=30):
        return JsonResponse({'status': f'Unable to attack while cloaked and maintenance is ongoing. Try again later.'})

    if player.health <= 0:
        return JsonResponse({'status': "Weapons systems are offline, your ship is destroyed. Try respawning."})
    
    # check if enemy has cloaked
    if enemy.cloaked:
        return JsonResponse({'status': 'Their ship disappears right before your eyes, it\'s a miss!'})

    # Check if room is a safe zone
    if player.room().safe:
        return JsonResponse({'status': 'As you begin your fire sequence a patrol ship flies nearby. You scramble to cancel the command.'})

    # set combat timers
    player.combat_timer = combat_timer
    enemy.combat_timer = combat_timer

    # Check if enemy ship is already destroyed
    if enemy.health <= 0:
        return JsonResponse({'status': 'As you call to fire up your lasers, scans come back indicating your target has previously been destroyed.'})

    hit_chance = 50
    hit_damage = 1

    # Check if player is cloaked
    if player.cloaked:
        hit_chance += 20
        hit_damage += 1
        player.cloak = False
        pusher.trigger(f'p-channel-{enemy.uuid}', u'combat', {'message': f'{player.user.username} has decloaked and is attacking your ship!'})

    # Roll attack
    if random.randint(0, 99) <= hit_chance:
        # It's a hit!
        enemy.health -= hit_damage
        # TODO: Send new health
        pusher.trigger(f'p-channel-{enemy.uuid}', u'combat', {'message': f'{player.user.username} has hit your ship.'})

        if enemy.health <= 0:
            # enemy.currentRoom = 1 # opting for manual respawn instead of auto
            enemy.score  -= 1
            if enemy.score < 0:
                enemy.score = 0
            enemy.save()
            # Increase players score
            player.score += 1
            player.save()
            pusher.trigger(f'p-channel-{enemy.uuid}', u'combat', {'message': f'{player.user.username} has destroyed your ship!'})
            return JsonResponse({'score': player.score, 'status': 'You have destroyed the target vessel.'})
        else:
            enemy.save()
            # respond hit
            return JsonResponse({'status': 'A direct hit!'})
    else:
        # respond miss
        pusher.trigger(f'p-channel-{enemy.uuid}', u'combat', {'message': f'{player.user.username} has fired on your ship and missed!'})
        return JsonResponse({'status': 'What a miss, you sure showed that space of space!'})

@api_view(["POST"])
@csrf_exempt
def cloak(request):
    player = request.user.player
    now = pytz.utc.localize(datetime.datetime.utcnow())

    if player.cloaked == False:
        if player.health <=0:
            return JsonResponse({'status': 'Your cloaking device is offline. Try respawning.'})

        # check if recently (1 minutes) in combat
        if player.combat_timer and (now - player.combat_timer) < datetime.timedelta(minutes=1):
            return JsonResponse({'status': 'Power diverted to shields and maneuvering while in combat.'})

        player.cloaked = True
        player.cloak_timer = now
        player.save()
        return JsonResponse({'status': 'Cloaked successfully, maintenance will commence while cloaked. Minimum of 30 minutes required.'})
    else:
        # uncloak
        if (now - player.cloak_timer) < datetime.timedelta(minutes=30):
            return JsonResponse({'status': f'Unable to uncloak while maintenance is ongoing. Try again later.'})
        
        player.cloaked = False
        room = player.room()
        # Pusher ship uncloaked
        playerUUIDs = room.playerUUIDs(player.id)
        for p_uuid in playerUUIDs:
            pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has uncloaked in the vicinity.'})
        player.save()
        return JsonResponse({'status': f'Successfully uncloaked, all maintenance has been completed!'})

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
    return JsonResponse({
        'uuid': player.uuid,
        'position': [room.x, room.y],
        'combat': { 'protected': room.safe, 'health': player.health, 'cloaked': player.cloaked },
        'name': player.user.username,
        'title': room.title,
        'description': room.description,
        'players': playerObjs
    }, safe=True)

@csrf_exempt
@api_view(["GET"])
def scoreboard(request):
    scores = list(Player.objects.annotate(name=F('user__username')).values('name', 'score').order_by('-score'))
    return JsonResponse({"scores": scores})

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
