import json

class Notification:

  def __init__(self, database, notification_id):
    self.notification_id = notification_id
    self.database = database

  def __eq__(self, other):
    return self.notification_id == other.notification_id

  def serialize(self):
    result = self.database.conn.execute('SELECT * FROM notifications WHERE notification_id = ?', (self.get_id(),)).fetchone()
    if result is None:
      return "[]"
    result = dict(result)
    result['json_data'] = json.loads(result['json_data'])
    return json.dumps(result)

  def get_id(self):
    return self.notification_id

  def get_student(self):
    result = self.database.conn.execute('SELECT student_id FROM notifications WHERE notification_id = ?', (self.get_id(),)).fetchone()
    return self.database.get_student(result['student_id'])

  def get_type(self):
    result = self.database.conn.execute('SELECT type FROM notifications WHERE notification_id = ?', (self.get_id(),)).fetchone()
    return result['type']

  def set_type(self, type):
    self.database.conn.execute('UPDATE notifications SET type = ? WHERE notification_id = ?', (type, self.get_id()))
    self.database.conn.commit()

  def get_json_data(self):
    result = self.database.conn.execute('SELECT json_data FROM notifications WHERE notification_id = ?', (self.get_id(),)).fetchone()
    return result['json_data']

  def set_json_data(self, data):
    self.database.conn.execute('UPDATE notifications SET json_data = ? WHERE notification_id = ?', (data, self.get_id()))
    self.database.conn.commit()

  def get_time_stamp(self):
    result = self.database.conn.execute('SELECT time_stamp FROM notifications WHERE notification_id = ?', (self.get_id(),)).fetchone()
    return result['json_data']

  def set_time_stamp(self, time_stamp):
    self.database.conn.execute('UPDATE notifications SET time_stamp = ? WHERE notification_id = ?', (time_stamp, self.get_id()))
    self.database.conn.commit()

  def delete(self):
    self.database.conn.execute('DELETE FROM notifications WHERE notification_id = ?', (self.get_id(),))
    self.database.conn.commit()
