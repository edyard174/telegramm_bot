import sqlite3

class BotDB:

	def __init__(self, db_file):
		"""Информация соединения с БД"""
		self.conn = sqlite3.connect(db_file)
		self.cursor = self.conn.cursor()

	def user_exists(self, user_id):
		"""Проверяем, есть ли юзер вБД"""
		result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
		return bool(len(result.fetchall()))

	def get_user_id(self, user_id):
		"""Получаем id юзера в базе по его user_id в телеграмме"""
		result = self.cursor.execute("SELECT id FROM users WHERE user_id = ?", (user_id,))
		return result.fetchone()[0]

	def add_user(self, user_id):
		"""Добовляем юзера в БД"""
		self.cursor.execute("INSERT INTO users ('user_id') VALUES (?)", (user_id,))
		return self.conn.commit()

	def add_record(self, user_id, operation, value):
		"""Создаем запись о расходе/доходе"""
		self.cursor.execute("INSERT INTO record ('user_id', 'operation', 'value') VALUES (?,?,?)", (self.get_user_id(user_id),
								operation == '+', value))
		return self.conn.commit()

	def get_records(self, user_id, within = "*"):
		"""Получаем историю операций за определеный период"""

		if(within == 'day'):
			result = self.cursor.execute(f"""SELECT * FROM record WHERE user_id = {self.get_user_id(user_id)}
											AND date BETWEEN datetime('now', 'start of day') 
											AND datetime('now', 'localtime') ORDER BY date""")

		elif(within == 'month'):
			"""За последний месяц"""
			result = self.cursor.execute(f"""SELECT * FROM record WHERE user_id = {self.get_user_id(user_id)} 
											AND date BETWEEN datetime('now', '-6 days') AND datetime('now', 'localtime') 
											ORDER BY date""")

		elif(within == 'year'):
			"""За год"""
			result = self.cursor.execute(f"""SELECT * FROM record WHERE user_id = {self.get_user_id(user_id)} 
											AND date BETWEEN datetime('now', 'start of month') AND datetime('now', 'localtime')
											 ORDER BY date""")

		else:
			result = self.cursor.execute(f"SELECT * FROM record WHERE user_id = {self.get_user_id(user_id)} ORDER BY date")

		return result.fetchall()


	def close(self):
		"""ЗАкрытие соединиения с БД"""
		self.conn.close()