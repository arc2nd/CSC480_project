import psycopg2
import sys
import bcrypt

table_creation_succeeded = True
user_creation_succeeded = True

conn_string = "host='localhost' dbname='ChoreExplore' user='cxp' password='choresarereallyfun'"

def execute_commands(commands):
	conn = None
	
	try:
		print ("Connecting to database using" + conn_string)

		conn = psycopg2.connect(conn_string)

		cursor = conn.cursor()

		for command in commands:
			cursor.execute(command)
			conn.commit()

		cursor.close()

	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
		if conn:
			conn.rollback()
		return False

	finally:
		if conn:
			conn.close()
		
	return True

def create_tables():

	""" Create necessary tables in the database """

	commands = [
		"""
		CREATE TABLE roles
		(
			id SERIAL PRIMARY KEY,
			name VARCHAR(255) NOT NULL UNIQUE
		)
		""",
		"""
		CREATE TABLE users
		(
			id SERIAL PRIMARY KEY,
			role_id INT REFERENCES roles(id),
			username VARCHAR(255) NOT NULL UNIQUE,
			password VARCHAR(60) NOT NULL,
			first_name VARCHAR(255) NOT NULL,
			middle_name VARCHAR(255),
			last_name VARCHAR(255),
			email_address VARCHAR(255) UNIQUE,
			date_of_birth date,
			points INT
		)
		""",
		"""
		CREATE TABLE recurrences
		(
			id SERIAL PRIMARY KEY,
			frequency_name VARCHAR(255) NOT NULL,
			frequency_days INT NOT NULL
		)
		""",
		"""
		CREATE TABLE chores
		(
			id SERIAL PRIMARY KEY,
			assigned_to INT REFERENCES users(id),
			due_date date,
			name VARCHAR(255),
			description VARCHAR(255),
			points INT NOT NULL,
			complete BOOL NOT NULL,
			recurrence_id INT REFERENCES recurrences(id)
		)
		""",
		"""
		CREATE TABLE rewards
		(
			id SERIAL PRIMARY KEY,
			name VARCHAR(255) NOT NULL UNIQUE,
			description VARCHAR(255) NOT NULL,
			points INT NOT NULL
		)
		"""
	]

	if(execute_commands(commands)):
		return True

	return False

def seed_roles():

	""" Seed the default roles """

	commands = [
		"""
		INSERT INTO roles
			(id, name)
			VALUES
			(1, 'Administrator'),
			(2, 'Standard')
		"""
	]

	if(execute_commands(commands)):
		return True

	return False

def seed_admin_user():

	unencrypted_password = 'test'

	encrypted_password = bcrypt.hashpw(unencrypted_password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')

	""" Seed the admin user """

	commands = [
		"""
		INSERT INTO users
			(id, role_id, username, password, first_name, middle_name, last_name, email_address, date_of_birth, points)
			VALUES
			(1, 1, 'administrator', '%s', 'first', 'middle', 'last', 'test@email.com', TO_DATE('01 Jan 1945', 'DD Mon YYYY'), 0)
		""" % (encrypted_password)
	]

	if(execute_commands(commands)):
		return True

	return False

def seed_recurrences():
	""" Seed the none, daily, weekly recurrences """
	commands = [
		"""
		INSERT INTO recurrences
			(id, frequency_name, frequency_days)
			VALUES
			(1, 'daily', 1),
			(2, 'weekly', 7)
		"""
	]

	if(execute_commands(commands)):
		return True

	return False

def restart_users_sequence():

	""" Restart the user sequence at 2 since we just created Admin with 1 """
	commands = [
		"""
		ALTER SEQUENCE users_id_seq RESTART WITH 2;
		"""
	]

	if(execute_commands(commands)):
		return True

	return False

if __name__ == '__main__':
	
	if(create_tables()):
		print("Tables created. Seeding roles and admin user...")
		if(seed_roles() and seed_admin_user() and seed_recurrences()):
			print("Roles, admin user, and recurrences seeded. Updating users id sequence...")
			if(restart_users_sequence()):
				print("Updated users sequence successfully.")
	else:
		print("Failed.")
