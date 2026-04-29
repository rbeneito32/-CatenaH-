import os
import json
import hashlib
import asyncio
from typing import Dict, Optional
from openai import AsyncOpenAI

try:
    import redis.asyncio as redis
    REDIS_URL = os.getenv("REDIS_URL")
    redis_client = redis.from_url(REDIS_URL) if REDIS_URL else None
except:
    redis_client = None

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
CACHE_TTL = 60 * 60 * 24

def hash_payload(payload: Dict) -> str:
    raw = json.dumps(payload, sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()

async def cache_get(key: str) -> Optional[str]:
    if redis_client:
        return await redis_client.get(key)
    return None

async def cache_set(key: str, value: str):
    if redis_client:
        await redis_client.set(key, value, ex=CACHE_TTL)

SYSTEM_PROMPT = """
Sos un analista financiero corporativo especializado en optimización de costos operativos de viajes.
REGLAS ESTRICTAS:
- Usá SOLO los datos numéricos provistos.
- PROHIBIDO inventar precios, tiempos o beneficios.
- NO supongas nada que no esté en el input.
- NO agregues ejemplos ficticios.
FORMATO:
- 1 solo párrafo
- Máximo 50 palabras
- Español
- Tono directo, profesional, sin marketing
- Explicá por qué la opción recomendada es superior económicamente y operativamente
"""

def build_user_prompt(payload: Dict) -> str:
    return f"""
Datos de comparación:
- Costo opción actual: €{payload['costo_actual']}
- Costo opción recomendada: €{payload['costo_recomendado']}
- Ahorro total: €{payload['ahorro_total_eur']}
- Horas productivas ganadas: {payload['horas_productivas_ganadas']}
- Riesgo operativo actual: €{payload['riesgo_actual']}
- Riesgo operativo recomendado: €{payload['riesgo_recomendado']}
Generar justificación.
"""

def generar_justificacion_fallback(payload: Dict) -> str:
    return (
        f"La opción actual implica €{payload['costo_actual']} frente a €{payload['costo_recomendado']}, "
        f"generando un sobrecosto de €{payload['ahorro_total_eur']}. "
        f"La alternativa recomendada reduce riesgo operativo y mejora la productividad."
    )

async def generar_justificacion_async(payload: Dict) -> str:
    cache_key = f"justif:{hash_payload(payload)}"
    cached = await cache_get(cache_key)
    if cached:
        return cached.decode() if isinstance(cached, bytes) else cached

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.2,
            max_tokens=120,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(payload)}
            ],
        )
        texto = response.choices[0].message.content.strip()
        palabras = texto.split()
        if len(palabras) > 50:
            texto = " ".join(palabras[:50])
            
        await cache_set(cache_key, texto)
        return texto
    except Exception:
        return generar_justificacion_fallback(payload)
