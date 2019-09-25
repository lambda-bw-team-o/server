import random, string

from data_structs.queue_struct import Queue
from adventure.models import Room

import util.name
import util.desc


class World:
    def __init__(self):
        self.grid = None
        self.width = 0
        self.height = 0
        self.room_id = 1 # TODO: Update to UUID?

    def create_room(self, x, y):
        gen_title = util.name.gen(4, 6)
        gen_desc = util.desc.gen(gen_title)
        room = Room(self.room_id, title=gen_title, description=gen_desc)
        room.setCoords(x, y)
        # room.id = self.room_id
        self.room_id += 1
        return room

    def calc_connection(self, x, y, room, direction, chance=0):
        reverse_dirs = {"n": "s", "e": "w", "s": "n", "w": "e"}
        new_room = self.grid[y][x]

        # check if there is already a room here
        if new_room:
            if getattr(new_room, f'{reverse_dirs[direction]}_to'):
                room.connectRooms(new_room, direction)
                new_room.connectRooms(room, reverse_dirs[direction])
            else:
                setattr(room, f'{direction}_to', 0)
                room.save()
        elif random.randint(0, 99) >= chance:
            new_room = self.create_room(x, y)
            # room.connect_rooms(new_room, direction)
            room.connectRooms(new_room, direction)
            new_room.connectRooms(room, reverse_dirs[direction])
            # print('DIRECTION:', getattr(room, f'{direction}_to'))
            return new_room
        return None


    def generate_rooms(self, size_x, size_y, num_rooms, seed=None):
        self.grid = [None] * size_y
        for i in range(len(self.grid)):
            self.grid[i] = [None] * size_x
        self.width = size_x
        self.height = size_y

        room_count = 0
        num_rooms = num_rooms

        # set our seed to a random hash
        if not seed:
            seed = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        random.seed(seed)

        # check that we have enough space
        if (size_x * size_y) < (num_rooms * 2):
            print(f'\nYou need more space, a minimum area of {num_rooms * 2} is required')

        rooms = Queue()

        # set our start coords to mid of area
        x = size_x // 2
        y = size_y // 2

        # create our spawn room
        spawn = self.create_room(x, y)

        # add our spawn to the queue 
        rooms.push(spawn)

        # while there are rooms in our queue
        while len(rooms) > 0:
            cur_room = rooms.pop()

            # skip if current room is None
            if cur_room is None:
                continue
            
            # set x, y to current room values
            x = cur_room.x
            y = cur_room.y

            # add to grid if room doesn't exist, increment room_count
            if self.grid[y][x] is None:
                self.grid[y][x] = cur_room
                room_count += 1
            else:
                continue
            
            # create connection chance
            # weighted by desired room_count
            chance = min((room_count / num_rooms) * 100, 60)

            # TODO: Randomize direction we check first
            # TODO: If room has 1` connection already, decrease chance for second

            # North
            if y < (size_y - 1):
                new_room = self.calc_connection(x, y + 1, cur_room, 'n', chance)
                if new_room:
                    rooms.push(new_room)
            
            # East
            if x < (size_x - 1):
                new_room = self.calc_connection(x + 1, y, cur_room, 'e', chance)
                if new_room:
                    rooms.push(new_room)

            # South
            if y > 0:
                new_room = self.calc_connection(x, y - 1, cur_room, 's', chance)
                if new_room:
                    rooms.push(new_room)

            # West
            if x > 0:
                new_room = self.calc_connection(x - 1, y, cur_room, 'w', chance)
                if new_room:
                    rooms.push(new_room)
            cur_room.save()
        
        if room_count < num_rooms:
            self.generate_rooms(size_x, size_y, num_rooms)
        else:
            print(f'\nGenerated {room_count} rooms: {seed}\n')
            return spawn


    def print_rooms(self):
        '''
        Print the rooms in room_grid in ascii characters.
        '''

        # Add top border
        str = "# " * ((3 + self.width * 5) // 2) + "\n"

        # The console prints top to bottom but our array is arranged
        # bottom to top.
        #
        # We reverse it so it draws in the right direction.
        reverse_grid = list(self.grid) # make a copy of the list
        reverse_grid.reverse()
        for row in reverse_grid:
            # PRINT NORTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.n_to is not 0:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"
            # PRINT ROOM ROW
            str += "#"
            for room in row:
                if room is not None and room.w_to is not 0:
                    str += "-"
                else:
                    str += " "
                if room is not None:
                    str += f"{room.id}".zfill(3)
                else:
                    str += "   "
                if room is not None and room.e_to is not 0:
                    str += "-"
                else:
                    str += " "
            str += "#\n"
            # PRINT SOUTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.s_to is not 0:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"

        # Add bottom border
        str += "# " * ((3 + self.width * 5) // 2) + "\n"

        # Print string
        print(str)


if __name__ == "__main__":
    w = World()
    num_rooms = 100
    width = 20
    height = 20
    seed = "6krEsMHo5orSitJR"
    # seed = None
    w.generate_rooms(width, height, num_rooms, seed)
    w.print_rooms()

    print(f"\n\nWorld\n  height: {height}\n  width: {width},\n  num_rooms: {num_rooms}\n")
