import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

class WalletCurrencyDB:
        def __init__(self):
                self.host = os.getenv('DB_HOST')
                self.user = os.getenv('DB_USER')
                self.password = os.getenv('DB_PASSWORD')
                self.database = os.getenv('DB_NAME')
                self.connection = None
        
        def connect(self):
            try:
                if self.connection is None or not self.connection.is_connected():
                    self.connection = mysql.connector.connect(
                        host = self.host,
                        user = self.user,
                        password = self.password,
                        database = self.database
                    )
                    return self.connection
            except Error as e:
                print(f"❌ Error de conexión a la base de datos: {e}")
                return None
        
        def execute_query(self, query, params=None):
            conn = self.connect()
            if conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute(query, params)
                    conn.commit()
                    return cursor.lastrowid
                except Error as e:
                    print(f"❌ Error al ejecutar la consulta: {e}")
                    return None
                finally:
                    cursor.close()
        
        def fetch_one(self, query, params=None):
            conn = self.connect()
            if conn:
                cursor = conn.cursor(dictionary=True)
                try:
                    cursor.execute(query, params)
                    return cursor.fetchone()
                finally:
                    cursor.close()
        
        def close(self):
            if self.connection and self.connection.is_connected():
                self.connection.close()
          
             