import bcrypt
from app.database.manager import WalletCurrencyDB
from mysql.connector import Error as SQLError

class AuthManager:
    def __init__(self):
        self.db = WalletCurrencyDB()
        
    def register_user(self, username, email, password):
        try:
            # validacion de entrada
            if not username or not email or len(password) < 6:
                return {"status": "error", "message": "Datos de registro inválidos o contraseña muy corta."}
            
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        
            query = """
            INSERT INTO users (username,email, password_hash)
            VALUES (%s, %s)
            """
            user_id = self.db.execute_query(query, (username,email, hashed_password.decode('utf-8')))
        
            if user_id:
                print(f"✅ Usuario '{username}' registrado con éxito.")
                return user_id
            else:
                print(f"❌ Error al registrar el usuario '{username}'.")
            return None
         
        except SQLError as e:
            if e.errno == 1062:  # Duplicate entry
                print(f"❌ El usuario '{username}' ya existe.")
                return {"status": "error", "message": "El usuario ya existe."}
            return {"status": "error", "message": f"Error de base de datos: {str(e)}"}
        except Exception as e:
            return {"status": "error", "message": f"Error inesperado: {str(e)}"}
    
    
    def login(self,username,password):
        try:
            query = "SELECT * FROM users WHERE username = %s"
            user = self.db.fetch_one(query, (username,))
        
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                return {"status": "🔓success", "user": {"id": user['id'], "username": user['username']}}
            elif not user:
                return {"status": "error", "message": "Usuario no encontrado."}
            else:
                return {"status": "error", "message": "Usuario o contraseña incorrectos."}
        except Exception as e:
            return {"status": "error", "message": f"Error en el proceso de autenticación.: {str(e)}"}
                
                
    
#--- Prueba delo Modulo ---
if __name__ == "__main__":
    auth = AuthManager()
    
    # Registrar un nuevo usuario
    user_data = auth.login("desarrollo", "desarrollo123")
    
    if user_data:
        print(f"Usuario autenticado: {user_data['username']} - {user_data['email']}")
        