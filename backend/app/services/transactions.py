from app.database.manager import WalletCurrencyDB
from mysql.connector import Error
from datetime import datetime

class TransactionManager:
    def __init__(self):
        self.db = WalletCurrencyDB()
        
    def register_operation(self,user_id, category_id,currency_id,account_id,
                               amount,type_op,description,rate_snapshot):
        """
        Registra una transacción y actualiza el saldo de la cuenta automáticamente.
        type_op: 'Ingreso', 'Egreso', 'Inversion'
        """
        connection = self.db.connect()
        if not connection:
            return {"status": "error", "message": "No se pudo conectar a la base de datos"}
        
        cursor = connection.cursor(dictionary=True)
        
        try:
            connection.start_transaction()
            # 1. Validar si la cuenta existe y pertenece al usuario
            cursor.execute("SELECT id, current_balance FROM accounts WHERE id = %s AND user_id = %s", (account_id, user_id))
            account = cursor.fetchone()
            if not account:
                raise ValueError("La cuenta no existe o no pertenece al usuario.")
        
            # 2. Insertar la transaccion
            query_tx="""
                 INSERT INTO transactions
                 (user_id, category_id, currency_id, amount, type_op, description, rate_snapshot)
                 VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
            params_tx = (user_id, account_id, category_id, currency_id, type_op, 
                     amount, description, datetime.now().date(), rate_snapshot)
        
            cursor.execute(query_tx, params_tx)
            tx_id = cursor.lastrowid
            # 3. Calcular nuevo saldo
            # modifier: Ingreso (+), Egreso/Inversion (-)
            modifer = -1 if type_op in ['Egreso', 'Inversion'] else 1
            change = float(amount) * modifer
        
            # 4. Validar el saldo suficiente para el Egreso e Inversion
            if type_op == 'Egreso' and (float(account['current_balance']) + change) < 0:
                raise ValueError("Saldo insuficiente para realizar esta transacción.")
            elif type_op == 'Inversion' and (float(account['current_balance']) + change) < 0:
                raise ValueError("Saldo insuficiente para realizar esta inversión.")
        
            
        
            # 5. Actulizar el Balance de la Cuenta  
            query_acc = "UPDATE accounts SET current_balance = current_balance + %s WHERE id = %s"
            self.db.execute_query(query_acc, (change, account_id))
        
            connection.commit()
            print(f"✅{type_op} registrado con exito, Saldo de la cuenta Actulizado") 
            return {
                "status": "success",
                "message": f"{type_op} registrado con éxito,",
                "transaction_id": tx_id,
                "new_balance": float(account['current_balance']) + change
            }
    
        except (Error,ValueError) as ve:
            connection.rollback()  
            print(f"❌ Error al registrar la transacción: {ve}")  
            return {
                "status": "error",
                "message": str(ve)}
        finally:
            cursor.close()
            connection.close()
    
    def get_history(self,user_id,limit=10):
        """Obtiene el historial reciente con nombres de categorías y monedas."""
        query = """
        SELECT t.id, t.type, t.amount, t.description, t.transaction_date, 
                   c.name as category, m.code as currency
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            JOIN currencies m ON t.currency_id = m.id
            WHERE t.user_id = %s
            ORDER BY t.transaction_date DESC
            LIMIT %s
        """
        return self.db.fetch_all(query, (user_id, limit))
    
    def get_expenses_by_category(self,user_id):
        """Obtiene la suma de egresos agrupados por categoría para el mes actual."""
        query = """
        SELECT c.name as category, SUM(t.amount) as total
        FROM transactions t
        JOIN categories c ON t.category_id = c.id
        WHERE t.user_id = %s 
          AND t.type = 'Egreso'
          AND MONTH(t.transaction_date) = MONTH(CURRENT_DATE())
        GROUP BY c.name
    """
        return self.db.fetch_all(query, (user_id,))