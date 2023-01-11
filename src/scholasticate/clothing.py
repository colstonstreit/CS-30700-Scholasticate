import json

class Clothing:
	def __init__(self, database, clothing_id):
		self.database = database
		self.clothing_id = clothing_id

	def __eq__(self, other):
		return self.clothing_id == other.clothing_id

	def serialize(self):
		result = self.database.conn.execute('SELECT * FROM wearing_clothings WHERE wearing_clothing_id = ?', (self.clothing_id,)).fetchone()
		if result is None:
			return "[]"
		return json.dumps(dict(result))

	def get_id(self):
		return self.clothing_id

	def get_article(self):
		result = self.database.conn.execute('SELECT article FROM wearing_clothings WHERE wearing_clothing_id = ?', (self.clothing_id,)).fetchone()
		return result['article']

	def get_brand(self):
		result = self.database.conn.execute('SELECT brand FROM wearing_clothings WHERE wearing_clothing_id = ?', (self.clothing_id,)).fetchone()
		if result['brand'] is None:
			return None
		else:
			return result['brand']
	
	def get_color(self):
		result = self.database.conn.execute('SELECT color_red, color_green, color_blue FROM wearing_clothings WHERE wearing_clothing_id = ?', (self.clothing_id,)).fetchone()
		return (result['color_red'], result['color_green'], result['color_blue'])
	
	def delete(self):
		self.database.conn.execute('DELETE FROM wearing_clothings WHERE wearing_clothing_id = ?', (self.get_id(), ))
		self.database.conn.commit()
		
