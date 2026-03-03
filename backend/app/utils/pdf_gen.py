from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime

class ReportGenerator:
    def __init__(self, app_name="wallet_currency"):
        self.app_name = app_name
    
    def generate_transaction_report(self,user_name,transactions,output_path):
        """
        Crea un PDF con el historial de movimientos.
        transactions: Lista de diccionarios con la data.
        """
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        sytles = getSampleStyleSheet()
        elements = []
        
        # 1.Encabezado
        title = Paragraph(f"<b>{self.app_name}</b> - Reporte Financiero", styles['Title'])
        elements.append(title)
        
        info = Paragraph(f"Usuario: {user_name}<br/>Fecha de generación: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal'])
        elements.append(info)
        elements.append(Spacer(1, 20))
        
        # 2.Tabla de Movimientos
        # Encabezados
        data = [["Fecha", "Tipo", "Categoría", "Monto", "Moneda", "Descripción"]]
        
        for tx in transactions:
            data.append([
                str(tx['transaction_date']),
                tx['type'],
                tx['category'],
                f"{tx['amount']:.2f}",
                tx['currency'],
                tx['description'][:20] + ("..." if len(tx['description']) > 20 else tx['description'])
                ])

        # 3. Estilo de la tabla
        table = Table(data, colWidths=[80, 50, 80, 60, 50, 150])
        sytle = TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.grey),
            ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ])
        table.setStyle(sytle)
        elements.append(table)
        
        # 4. Generar el PDF
        doc.build(elements)
        return output_path
        print(f"✅ Reporte generado en: {output_path}")    