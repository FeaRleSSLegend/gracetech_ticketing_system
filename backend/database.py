# Initialising the database connection and engine
from sqlalchemy import create_engine
from sqlalchemy import event

engine = create_engine('sqlite:///ticketdatabase.db')

@event.listen
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    # Enabling foreign key constraints
    cursor.execute('pragma foreign_keys=ON')
    cursor.close()

# tables will be created in indvidual files in models/

