import random, string
import sys
sys.path.append('../data_structs')
from queue_struct import Queue


class Room:
    def __init__(self, id, name, description, x, y):
        self.id = id
        self.name = name
        self.description = description
        self.n_to = None
        self.s_to = None
        self.e_to = None
        self.w_to = None
        self.x = x
        self.y = y
    def __repr__(self):
        if self.e_to is not None:
            return f"({self.x}, {self.y}) -> ({self.e_to.x}, {self.e_to.y})"
        return f"({self.x}, {self.y})"
    def connect_rooms(self, connecting_room, direction):
        '''
        Connect two rooms in the given n/s/e/w direction
        '''
        reverse_dirs = {"n": "s", "s": "n", "e": "w", "w": "e"}
        reverse_dir = reverse_dirs[direction]
        setattr(self, f"{direction}_to", connecting_room)
        setattr(connecting_room, f"{reverse_dir}_to", self)
    def get_room_in_direction(self, direction):
        '''
        Connect two rooms in the given n/s/e/w direction
        '''
        return getattr(self, f"{direction}_to")


class World:
    def __init__(self):
        self.grid = None
        self.width = 0
        self.height = 0
        self.room_id = 0 # TODO: Update to UUID?

    def create_room(self, x, y):
        room = Room(self.room_id, "A Generic Room", "This is a generic room.", x, y)
        self.room_id += 1
        return room

    def calc_connection(self, x, y, room, direction, chance=0):
        reverse_dirs = {"n": "s", "e": "w", "s": "n", "w": "e"}
        new_room = self.grid[y][x]

        # check if there is already a room here
        if new_room:
            if getattr(new_room, f'{reverse_dirs[direction]}_to'):
                room.connect_rooms(new_room, direction)
            else:
                setattr(room, f'{direction}_to', None)
        elif random.randint(0, 99) >= chance:
            new_room = self.create_room(x, y)
            room.connect_rooms(new_room, direction)
            return new_room
        return None


    def generate_rooms(self, size_x, size_y, num_rooms, seed=None):
        self.grid = [None] * size_y
        for i in range(len(self.grid)):
            self.grid[i] = [None] * size_x
        self.width = size_x
        self.height = size_y
        self.room_id = 1

        room_count = 0
        num_rooms = num_rooms

        # set our seed to a random hash
        if not seed:
            seed = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        random.seed(seed)

        # check that we have enough space
        if (width * height) < (num_rooms * 2):
            print(f'\nYou need more space, a minimum area of {num_rooms * 2} is required')

        rooms = Queue()

        # set our start coords to mid of area
        x = width // 2
        y = height // 2

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
            chance = min(((room_count / num_rooms) * 100) + 15, 60)
            # additive = 5

            # North
            if y < (height - 1):
                new_room = self.calc_connection(x, y + 1, cur_room, 'n', chance)
                if new_room:
                    rooms.push(new_room)
            
            # East
            if x < (width - 1):
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
        
        if room_count < num_rooms:
            self.generate_rooms(size_x, size_y, num_rooms)
        else:
            print(f'\nGenerated {room_count} rooms: {seed}\n')


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
                if room is not None and room.n_to is not None:
                    str += "  |  "
                else:
                    str += "     "
            str += "#\n"
            # PRINT ROOM ROW
            str += "#"
            for room in row:
                if room is not None and room.w_to is not None:
                    str += "-"
                else:
                    str += " "
                if room is not None:
                    str += f"{room.id}".zfill(3)
                else:
                    str += "   "
                if room is not None and room.e_to is not None:
                    str += "-"
                else:
                    str += " "
            str += "#\n"
            # PRINT SOUTH CONNECTION ROW
            str += "#"
            for room in row:
                if room is not None and room.s_to is not None:
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
    num_rooms = 500
    width = 45
    height = 45
    # seed = "Bdq41Yxzssvm0ALw"
    seed = None
    w.generate_rooms(width, height, num_rooms, seed)
    w.print_rooms()

    print(f"\n\nWorld\n  height: {height}\n  width: {width},\n  num_rooms: {num_rooms}\n")