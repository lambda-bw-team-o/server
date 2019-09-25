import random
import util.name

bodies = ["super planet", "planet", "moon", "asteroid"]

body_categories = {
  "super planet": ["frozen", "scorched", "toxic", "irradiated", "barren", "gaseous"],
  "planet": ["frozen", "scorched", "toxic", "irradiated", "barren"],
  "moon": ["frozen", "scorched", "toxic", "irradiated", "barren"],
  "asteroid": ["frozen", "barren", "irradiated"]
}

attributes = {
  "frozen": {
    "name": [
      "Frozen",
      "Icebound",
      "Arctic",
      "Glacial",
      "Sub-zero",
      "Icy",
      "Frostbound",
      "Freezing",
      "Hiemal",
      "Hyperborean"
    ],
    "weather": [
      "Powder Snow",
      "Drifting Snowstorms",
      "Harsh, Icy Winds",
      "Frozen Clouds",
      "Migratory Blizzards",
      "Occasional Snowfall",
      "Outbreaks of Frozen Rain",
      "Raging Snowstorms",
      "Supercooled Storms",
      "Frequent Blizzards",
      "Icy Tempests"
    ]
  },
  "scorched": {
    "name": [
      "Charred",
      "Arid",
      "Scorched",
      "Hot",
      "Fiery",
      "Boiling",
      "High Temperature",
      "Torrid",
      "Incandescent",
      "Scalding"
    ],
    "weather": [
      "Direct Sunlight",
      "A Heated Atmosphere",
      "Unending Sunlight",
      "Atmospheric Heat Instabilities",
      "Burning Air",
      "Occasional Ash Storms",
      "Superheated Gas Pockets",
      "Wandering Hot Spots"
    ]
  },
  "toxic": {
    "name": [
      "Toxic",
      "Poisonous",
      "Noxious",
      "Corrosive",
      "Acidic",
      "Caustic",
      "Acrid",
      "Blighted",
      "Miasmatic",
      "Rotting"
    ],
    "weather": [
      "Acid Rain",
      "Caustic Moisture",
      "Corrosive Humidity",
      "Choking Clouds",
      "Poison Rain",
      "Stinging Puddles",
      "Toxic Clouds",
      "Acidic Dust Pockets",
      "Alkaline Cloudbursts",
      "Dangerously Toxic Rain",
      "Poison Flurries",
      "Toxic Outbreaks",
      "Occasional Acid Storms",
      "Frequent Toxic Floods",
      "Acid Deluges",
      "Bone-Stripping Acid Storms",
      "Caustic Floods",
      "Corrosive Rainstorms",
      "Torrential Acid",
    ]
  },
  "irradiated": {
    "name": [
      "Irradiated",
      "Radioactive",
      "Contaminated",
      "Nuclear",
      "Isotopic",
      "Decaying",
      "Gamma-Intensive",
      "Supercritical",
      "High Energy"
    ],
    "weather": [
      "Contaiminated Puddles",
      "Gamma Dust",
      "Irradiated Winds",
      "A Nuclidic Atmosphere",
      "Radioactive Dust Storms",
      "Unstable Fog",
      "Volatile Windstorms",
      "Irradiated Downpours",
      "Ocassional Radiation Outbursts",
      "Enormous Nuclear Storms",
      "Extreme Radioactivity",
      "Gamma Cyclones",
      "Roaring Nuclear Wind"
    ]
  },
  "barren": {
    "name": [
      "Barren",
      "Desert",
      "Rocky",
      "Bleak",
      "Parched",
      "Abandoned",
      "Dusty",
      "Desolate",
      "Wind-swept"
    ],
    "weather": [
      "Unclouded Skies",
      "Intermittent Wind Blasting",
      "Parched Sands",
      "Sporadic Grit Storms",
      "A Blasted Atmosphere",
      "Dust-Choked Winds",
      "Ceaseless Drought",
      "Infrequent Dust Storms",
      "Freezing Night Winds"
    ]
  },
  "lush": {
    "name": [
      "Rainy",
      "Verdant",
      "Viridescent",
      "Paradise",
      "Temperate",
      "Humid",
      "Overgrown",
      "Flourishing",
      "Bountiful"
    ],
    "weather": [
      "Light Showers",
      "Mild Rain",
      "Boiling Puddles",
      "Superheated Drizzle",
      "Choking Humidity",
      "Dangerously Hot Fog",
      "Occasional Scalding Cloudbursts",
      "Lethal Humidity Outbreaks",
      "Boiling Superstorms",
      "Intense Heatbursts",
      "Boiling Monsoons",
      "Superheated Rainstorms",
      "Blistering Floods",
      "Torrid Deluges"
    ]
  },
  "gaseous": {
    "name": [
      "Aeriform",
      "Effervescent",
      "Atmospheric-Dense",
      "Crushing",
      "Gaseous",
      "Pressurized",
      "Condensed"
    ],
    "weather": [
      "Helium Downpours",
      "Occasional Hurricanes",
      "Perpetual Typhoons",
      "Pressurized Monsoons",
      "Extreme Windstorms",
      "Volatile Cyclones",
      "Roaring Wind",
      "Bone-Crushing Gravity",
      "Molten Glass Storms"
    ]
  }
}

def gen(planet):
  vowels = ['a', 'e', 'i', 'o', 'u']
  body = random.choice(bodies)

  if body != 'asteroid':
    category = random.choice(body_categories[body]) if random.randint(0, 99) > 1 else "lush"
  else:
    category = random.choice(body_categories[body])
  
  cat_name = random.choice(attributes[category]['name']).lower()
  prefix = 'an' if cat_name[:1] in vowels else 'a'
  weather = random.choice(attributes[category]['weather']).lower()

  return f'{planet} is {prefix} {cat_name} {body}, with {weather}'


if __name__ == "__main__":
  for i in range(100):
    name = util.name.gen(4, 6)
    print(gen(name))
