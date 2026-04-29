from fastapi import FastAPI
from pydantic import BaseModel, field_validator
from datetime import datetime
import uuid

# Importamos las herramientas que creamos
from tracking import router as tracking_router, init_click_db
from tracking import generar_link_tren, wrap_tracking_link
from justification_engine import generar_justificacion_async
from profile_engine import ProfileEngine

app = FastAPI()
app.include_router(tracking_router)

# Al arrancar, crea la base de datos de clics
@app.on_event("startup")
def startup_event():
    init_click_db()

# Validación estricta del formulario
class OptimizationRequest(BaseModel):
    origen: str
    destino: str
    fecha: str
    noches: int
    valor_hora: float
    equipaje_kg: int = 8
    prioridad: str = "ahorro"

    @field_validator("fecha")
    def fecha_no_pasado(cls, v):
        fecha_obj = datetime.fromisoformat(v)
        if fecha_obj < datetime.now():
            raise ValueError("La fecha no puede estar en el pasado")
        return v

    @field_validator("equipaje_kg")
    def equipaje_valido(cls, v):
        if v < 0 or v > 200:
            raise ValueError("Equipaje fuera de rango lógico")
        return v

    @field_validator("prioridad")
    def prioridad_valida(cls, v):
        if v not in ["ahorro", "tiempo", "confort"]:
            raise ValueError("Prioridad inválida")
        return v

# Endpoint principal
@app.post("/optimizar")
async def optimizar(req: OptimizationRequest):
    request_id = str(uuid.uuid4())
    
    # 1. Analizar Prioridades
    profile_engine = ProfileEngine(req.prioridad)
    weights = profile_engine.get_weights()
    
    # 2. Acá el código llamaría a tus Providers (Vuelos, Trenes) 
    # y los pasaría por tu algoritmo COT (Omitido por brevedad de la maqueta final).
    # Simulamos el resultado para el Abogado IA:
    
    payload_ia = {
        "costo_actual": 450.0,
        "costo_recomendado": 300.0,
        "ahorro_total_eur": 150.0,
        "horas_productivas_ganadas": 3.5,
        "riesgo_actual": 0.8,
        "riesgo_recomendado": 0.2,
        "tipo_ruta_actual": "Vuelo Low-cost",
        "tipo_ruta_recomendada": "Tren Directo",
        "equipaje_kg": req.equipaje_kg
    }

    # 3. El Abogado redacta la defensa
    justificacion = await generar_justificacion_async(payload_ia)

    # 4. Generamos los links con trampa para la comisión
    link_tren_real = generar_link_tren(req.origen, req.destino, req.fecha)
    link_final = wrap_tracking_link(link_tren_real, request_id, "tren")

    return {
        "request_id": request_id,
        "recomendacion": "Tren Directo",
        "insight_texto": justificacion,
        "impacto_negocio": {
            "ahorro_total": payload_ia["ahorro_total_eur"]
        },
        "acciones": {
            "reservar_tren": link_final
        }
    }
