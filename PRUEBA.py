
import sqlite3



conexion=sqlite3.connect("/NOMBRE1.db") 


cursor = conexion.cursor()

cursor.execute("INSERT INTO fish VALUES ('Sammy', 'shark', 1)")
cursor.execute("INSERT INTO fish VALUES ('Jamie', 'cuttlefish', 7)")
print(conexion.total_changes)
conexion.commit() 
conexion.close() 