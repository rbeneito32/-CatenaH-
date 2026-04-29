import os
import json
import hashlib
import google.generativeai as genai
from typing import Dict, Optional

# Configuración de Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

def hash_payload(payload: Dict) -> str:
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()

SYSTEM_PROMPT = """
Sos un analista financiero corporativo especializado en optimización de costos.
REGLAS:
- Usá SOLO los datos numéricos provistos.
- 1 solo párrafo, máximo 50 palabras.
- Tono directo y profesional.
"""

def build_prompt(payload: Dict) -> str:
    return f"{SYSTEM_PROMPT}\n\nDatos: Ahorro €{payload['ahorro_total_eur']}, Horas ganadas: {payload['horas_productivas_ganadas']}. Justificá la opción recomendada ({payload['tipo_ruta_recomendada']}) frente a la actual ({payload['tipo_ruta_actual']})."

def generar_justificacion_fallback(payload: Dict) -> str:
    return f"La opción recomendada ahorra €{payload['ahorro_total_eur']} y mejora la productividad."

async def generar_justificacion_async(payload: Dict) -> str:
    try:
        prompt = build_prompt(payload)
        response = model.generate_content(prompt)
        texto = response.text.strip()
        return " ".join(texto.split()[:50])
    except Exception:
        return generar_justificacion_fallback(payload)
