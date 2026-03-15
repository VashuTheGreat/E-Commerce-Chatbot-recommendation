
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
conn = sqlite3.connect("checkpoint1.db", check_same_thread=False)
cursor = conn.cursor()



conn.commit()

memory = SqliteSaver(conn)