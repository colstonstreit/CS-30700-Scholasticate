import json

class Profile_Picture:
  def __init__(self, database, picture_id):
    self.database = database
    self.picture_id = picture_id

  def __eq__(self, object):
    return self.picture_id == object.picture_id

  def serialize(self):
    result = self.database.conn.execute('SELECT * FROM profile_pictures WHERE picture_id = ?', (self.get_id(),)).fetchone()
    if result is None:
      return "[]"
    return json.dumps(dict(result))

  def get_id(self):
    return self.picture_id

  def get_string(self):
    result = self.database.conn.execute('SELECT picture_string FROM profile_pictures WHERE picture_id = ?', (self.get_id(),)).fetchone()
    return result['picture_string']

  def set_string(self, string):
    self.database.conn.execute('UPDATE profile_pictures SET picture_string = ? WHERE picture_id = ?', (string, self.get_id()))
    self.database.conn.commit()

  def delete(self):
    self.database.conn.execute('DELETE FROM profile_pictures WHERE picture_id = ?', (self.get_id(),))
    self.database.conn.commit()