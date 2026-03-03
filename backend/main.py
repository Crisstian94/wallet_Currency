from fastapi import FastAPI,HTTPException,Depends,status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List,Optional
import os
import datetime

# Modulos
from app.services.auth import AuthManager
from app.services.transactions import TransactionManager
from app.services.rates import RatesProvider
from app.utils.pdf_gen import ReportGenerator


app = FastAPI(
    title="wallet_Ocurrency API",
    description="Backend para el administrador financiero multimoneda",
    version="1.0.0"
)
#Configuracion de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Permitir todas las fuentes (ajustar según sea necesario)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
    
)

#--- Modelo de Datos Pydantic ---
class loginRequest(BaseModel):
    username: str
    password: str

class TransactionCreate(BaseModel):
    user_id: int
    account_id: int
    category_id: int
    currency_id: int
    amount: float
    type_op: str # 'Ingreso', 'Egreso', 'Inversion'
    description: str
    rate_snapshot: float

# --- INSTANCIAS DE SERVICIOS ---
auth_service = AuthManager()
tx_service = TransactionManager()
rates_service = RatesProvider()
pdf_service = ReportGenerator()

# -- RUTAS --

@app.get("/", tags=["General"])
def read_root():
        return {"message": "Bienvenido a la API de wallet_Ocurrency"}

@app.post("/login", tags=["Auth"])
async def login(request: loginRequest):
    try:
        result = auth_service.login(request.username, request.password)
        if result["status"] == "error":
            raise HTTPException(status_code=401, detail=result["message"])
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error interno en el servidor de autenticación.")
    
    
    
@app.get("/rates/update", tags=["Rates"])
def update_rates():
    """
    Ruta para forzar la actualización de tasas desde el BCV/Binance
    """
    try:
        rates_service.update_rates()
        return {"status": "success", "message": "Tasas actualizadas correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transactions/register", tags=["Transactions"])
async def register_tx(tx: TransactionCreate):
    # Validamos que el monto sea positivo
    if tx.amount <= 0:
        raise HTTPException(status_code=400, detail="El monto debe ser mayor a cero.")
    
    try:
        result =tx_service.register_operation(
            tx.user_id,
            tx.account_id,
            tx.category_id,
            tx.currency_id,
            tx.amount,
            tx.type_op,
            tx.description,
            tx.rate_snapshot        
        )
    
        if result["status"] =="error":
            # Si el error es "Saldo insuficiente", enviamos 400 (Bad Request)
            status_code = 400 if "Saldo" in result["message"] else 500
            raise HTTPException(status_code=status_code, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fallo crítico al registrar la operación.: {str(e)}")

@app.get("/dashboard/summary/{user_id}", tags=["Dashboard"])
def get_summary(user_id: int):
    balances = tx_service.get_user_balance_global(user_id)
    return{"balance":balances}


@app.get("/dashboard/expenses-chart/{user_id}", tags=["Dashboard"])
async def expenses_chart(user_id: int):
    data = tx_service.get_expenses_by_category(user_id)
    # Formateamos para que el frontend lo reciba fácil
    labels = [item['category'] for item in data]
    values = [float(item['total']) for item in data]
    return {"labels": labels, "datasets": [{"data": values}]}


#--- Ruta para generar el reporte PDF ---
@app.get("/report/generate/{user_id}", tags=["Reports"])
def generate_report(user_id: int,username:str):
    # 1. Obtener la data  real de la base de datos
    history = tx_service.get_user_transaction_history(user_id, limit=50)
    
    if not history:
        raise HTTPException(status_code=404, detail="No se encontraron transacciones para el usuario")
    # 2. Generar el Archivo Temporal
    temp_dir ="temp"
    file_name = f"report_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join("temp", file_name)
    
    # 3. validar que el directorio exista
    try:
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            print(f"✅ Directorio '{temp_dir}' creado exitosamente.")
    except OSError as e:
        print(f"❌ Error al crear el directorio temporal '{temp_dir}': {e}")
        raise HTTPException(status_code=500, 
            detail=f"Error interno del servidor al preparar el reporte: {str(e)}"
            )
    
    try:
        pdf_service.generate_transaction_report(username,history,file_path)
    except Exception as e:
        print(f"❌ Error al generar el PDF: {e}")
        raise HTTPException(status_code=500, 
                            detail=f"Error al generar el reporte PDF: {e}")
    
  
    
    # 4. Retornar el archivo para descarga
    return FileResponse(
        path=file_path, 
        filename=f"Reporte_Wallet{username}.pdf", 
        media_type='application/pdf'
        )