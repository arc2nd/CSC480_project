import psycopg2
import sys

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

def clean_database():

	""" Delete all the database tables """

	commands = [
		"""
		DROP SCHEMA public CASCADE;
		""",
		"""
		CREATE SCHEMA public;
		""",
		"""
		GRANT ALL ON SCHEMA public TO cxp;
		""",
		"""
		ALTER SCHEMA public OWNER TO cxp
		""",
		"""
		GRANT ALL ON SCHEMA public TO public;
		"""
	]

	if(execute_commands(commands)):
		return True

	return False

if __name__ == '__main__':
	
	if(clean_database()):
		print("Dropped all tables in the schema.")
	else:
		print("Failed.")