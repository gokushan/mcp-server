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
    
    # Confirmación manual simulada (opcional en debug real, aquí lo hacemos directo)
    # Mapear los datos procesados a los datos que espera GLPI
    # Nota: ContractProcessor devuelve ProcessedContract, ContractManager espera ContractData
    # Hacemos un mapeo básico para el ejemplo
    
    # Match GLPI response with ProcessedContract - Domain model
    contract_payload = ContractData(
        name=processed_data.contract_name,
        num=processed_data.contract_num,
        accounting_number=processed_data.accounting_number,
        begin_date=processed_data.start_date,
        duration=processed_data.duration_months,
        notice=processed_data.notice_months,
        renewal=processed_data.renewal_enum,
        billing=processed_data.billing_frequency_months,
        cost=processed_data.amount,
        comment=f"Importado automáticamente.\nResumen: {processed_data.summary}\nPartes: {processed_data.parties}\nSLA Info: {processed_data.sla_support_hours}",
        states_id=1,  # Estado activo por defecto (ejemplo)
        contracttypes_id=1 # Tipo Servicios por defecto (ejemplo)
    )
    
    print("Datos a enviar a GLPI:")
    print(contract_payload)

    # Iniciar cliente GLPI
    try:
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
        print(f"\n❌ Error conectando o creando en GLPI: {e}")

if __name__ == "__main__":
    asyncio.run(run_debug_flow())
