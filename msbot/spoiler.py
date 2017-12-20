class Spoiler:
	def __init__(self, json_input):
		self.name = json_input['name']
		self.cost = json_input['manacost']
		self.type = json_input['type']
		self.rarity = json_input['rarity']
		self.text = json_input['text']
		self.flavor = json_input['flavor']
		self.artist = json_input['artist']
		self.power = json_input['power']
		self.toughness = json_input['toughness']
		self.loyalty = json_input['loyalty']

