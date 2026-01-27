import asyncio
import os
import json
import logging
from pathlib import Path

# Configurar logging para ver detalles
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("debug_flow")

# Asegurar que podemos importar nuestros módulos
import sys
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env en el directorio /server
# Esto es necesario si el script se ejecuta desde la raíz del proyecto
dotenv_path = Path(__file__).parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path)

sys.path.append(str(Path(__file__).parent / "src"))

from glpi_mcp_server.processors.contract_processor import ContractProcessor
from glpi_mcp_server.glpi.contracts import ContractManager
from glpi_mcp_server.glpi.models import ContractData
from glpi_mcp_server.tools.utils import get_glpi_client

async def run_debug_flow():
    print("=== INICIO DE DEPURACIÓN DE FLUJO DE CONTRATO ===")
    
    # 1. Definir archivo de prueba
    test_file = Path("/home/gokushan/Documentos/Contrato_Narrativo_CONT-2026-IT-0087.pdf")
    if not test_file.exists():
        print(f"Error: No se encuentra el archivo de prueba en {test_file}")
        return

    print(f"\n[PASO 1] Procesando documento: {test_file}")
    print("----------------------------------------")
    
    # Instanciar procesador - Prymary adapter - Get text and send to LLM
    processor = ContractProcessor()
    
    # Ejecutar procesamiento (Aquí es donde se llama al LLM para procesar el contrato)
    # Poner breakpoint aquí para inspeccionar el texto extraído o la respuesta del LLM
    try:
        # Port output of primary adapter to secondary adapter
        processed_data = await processor.process(str(test_file))  
        print("\n✅ Datos extraídos exitosamente:")
        print(json.dumps(processed_data.model_dump(), indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"\n❌ Error en procesamiento: {e}")
        return

    print(f"\n[PASO 2] Creando contrato en GLPI")
    print("----------------------------------------")
    
    # Iniciar cliente GLPI
    try:
        # Match GLPI response with ProcessedContract - Domain model
        sla_data = processed_data.sla_support_hours or {}
        
        # Helper to ensure HH:MM:SS format
        def format_hour(val):
            if val is None: return None
            if isinstance(val, int): return f"{val:02d}:00:00"
            return str(val)

        contract_payload = ContractData(
            name=processed_data.contract_name,
            num=processed_data.contract_num,
            accounting_number=processed_data.accounting_number,
            begin_date=processed_data.start_date,
            end_date=processed_data.end_date,
            duration=processed_data.duration_months,
            notice=processed_data.notice_months,
            renewal=processed_data.renewal_enum,
            billing=processed_data.billing_frequency_months,
            cost=processed_data.amount,
            comment=f"Importado automáticamente.\nResumen: {processed_data.summary}\nPartes: {processed_data.parties}\nSLA Info: {processed_data.sla_support_hours}",
            states_id=1,  # Estado activo por defecto (ejemplo)
            contracttypes_id=1, # Tipo Servicios por defecto (ejemplo)
            # SLA Mapping
            week_begin_hour=format_hour(sla_data.get("week_begin_hour")),
            week_end_hour=format_hour(sla_data.get("week_end_hour")),
            use_saturday=1 if sla_data.get("use_saturday") else 0,
            saturday_begin_hour=format_hour(sla_data.get("saturday_begin_hour")),
            saturday_end_hour=format_hour(sla_data.get("saturday_end_hour")),
            use_sunday=1 if sla_data.get("use_sunday") else 0,
            sunday_begin_hour=format_hour(sla_data.get("sunday_begin_hour")),
            sunday_end_hour=format_hour(sla_data.get("sunday_end_hour")),
        )
        
        print("Datos a enviar a GLPI:")
        print(contract_payload)

        # get_glpi_client usa las variables de entorno para autenticarse
        async with await get_glpi_client() as client:
            # Adapter output to secondary adapter - Create contract in GLPI
            manager = ContractManager(client)
            
            # Crear contrato
            # Poner breakpoint aquí para inspeccionar la llamada a la API
            result = await manager.create(contract_payload)
            
            print("\n✅ Contrato creado exitosamente en GLPI:")
            print(json.dumps(result.model_dump(mode='json'), indent=2, ensure_ascii=False))
            
    except Exception as e:
        import traceback
        print(f"\n❌ Error conectando o creando en GLPI: {type(e).__name__}: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_debug_flow())
