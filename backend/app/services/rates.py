import os
import requests
import urllib3
from bs4 import BeautifulSoup
from requests.exceptions import RequestException, Timeout
from dotenv import load_dotenv
from datetime import datetime
from app.database.manager import WalletCurrencyDB 

# Desactivar advertencias de SSL para sitios gubernamentales
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
load_dotenv()

class RatesProvider:
        def __init__(self):
                self.db =WalletCurrencyDB()
                self.headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
        def get_bcv_rates(self):
            """Obtiene las tasas de cambio del BCV y las guarda en la base de datos."""
            url = 'https://www.bcv.org.ve/tasas-de-cambio'
            try:
                response = requests.get(url, headers=self.headers,verify=False,timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Usamos bloques try individuales para cada moneda por si una falta en el HTML
                try:
                    usd = soup.find('div', text='Dolar').find('strong').text.strip().replace(',', '.')
                    euro = soup.find('div', text='Euro').find('strong').text.strip().replace(',', '.')
                
                    return {
                        'USD': float(usd),
                        'EUR': float(euro),
                        'timestamp': datetime.now()
                    }
                except AttributeError as e:
                    raise Exception(f"Error al parsear las tasas del BCV: {e}")
                
            except (RequestException, Timeout) as e:
                print(f"❌ Error de red al contactar al BCV: {e}")
                return None
            except Exception as e:
                print(f"❌ Error inesperado en scraping: {e}")
                return None
        
        def get_binance_p2p_average(self):
            """Obtiene las tasas de cambio de Binance P2P y las guarda en la base de datos."""
            url = "https://api.binance.com/api/v3/ticker/price?symbol=USDTBID" # Ejemplo o par similar
        # Nota: Para P2P real se usa otro endpoint más complejo, 
        # aquí simularemos el retorno de una tasa promedio de 39.50 por ahora.
            return 39.50
        
        def update_rates(self):
            rates = self.get_bcv_rates()
            if not rates:
                print("No se pudieron obtener las tasas del BCV.")
                return
            if self.db_connect():
                ahora = rates['timestamp']
                query = "INSERT INTO exchange_rates (currency_id, source, rate_value,updated_at) VALUES (%s, %s, %s,%s)"
                
                self.db.execute(query, (2, 'BCV', rates['USD'],ahora))
                self.db.execute(query, (3, 'BCV', rates['EUR'],ahora))
                
                binance_value = self.get_binance_p2p_average()
                self.db.execute(query, (2, 'Binance P2P', binance_value,ahora))
                
                print(f"--- Registro Histórico wallet_Currency ---")
                print(f"Fecha/Hora: {ahora.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"USD BCV: {rates['USD']} | EUR BCV: {rates['EUR']} | Binance: {binance_value}")
                print(f"------------------------------------------")
                print(f"✅ Tasas actualizadas correctamente.")
                

if __name__ == "__main__":
    provider = RatesProvider()
    provider.update_rates()