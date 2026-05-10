from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import math

# ─────────────────────────────────────────────
#  Configuración de la aplicación
# ─────────────────────────────────────────────
app = FastAPI(
    title="Métodos Numéricos — Bisección y Secante",
    description=(
        "Backend desarrollado para la asignatura Análisis Numérico.\n\n"
        "**Grupo:** Félix Samudio, José Urrunaga, Jeremy Gonzalez\n\n"
        "**Métodos implementados:**\n"
        "- `/biseccion` — Método de Bisección\n"
        "- `/secante`   — Método de la Secante\n\n"
        "Cada endpoint recibe parámetros en JSON y devuelve las iteraciones completas, "
        "el resultado final y un mensaje explicativo."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  Utilidad: evaluar f(x) de forma segura
# ─────────────────────────────────────────────
FUNCIONES_PERMITIDAS = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "exp": math.exp, "log": math.log, "log10": math.log10,
    "sqrt": math.sqrt, "pi": math.pi, "e": math.e,
    "abs": abs,
}

def evaluar(expresion: str, x: float) -> float:
    """Evalúa una expresión matemática como string en x."""
    return eval(expresion, {"__builtins__": {}}, {**FUNCIONES_PERMITIDAS, "x": x})


# ═══════════════════════════════════════════════════════════════
#  ENDPOINT 1 — MÉTODO DE BISECCIÓN
# ═══════════════════════════════════════════════════════════════

class BiseccionEntrada(BaseModel):
    funcion: str = "x**2 - 5"
    a: float = 2.0
    b: float = 3.0
    tolerancia: float = 0.001
    max_iteraciones: int = 50

    class Config:
        json_schema_extra = {
            "example": {
                "funcion": "x**2 - 5",
                "a": 2.0,
                "b": 3.0,
                "tolerancia": 0.001,
                "max_iteraciones": 50,
            }
        }


class IteracionBiseccion(BaseModel):
    iteracion: int
    a: float
    b: float
    c: float
    f_a: float
    f_b: float
    f_c: float
    error: Optional[float]


class BiseccionRespuesta(BaseModel):
    entrada: dict
    iteraciones: List[IteracionBiseccion]
    raiz_aproximada: float
    iteraciones_totales: int
    error_final: float
    convergencia: bool
    mensaje: str


@app.post(
    "/biseccion",
    response_model=BiseccionRespuesta,
    summary="Método de Bisección",
    tags=["Métodos Numéricos"],
    description=(
        "**Método de Bisección** — divide el intervalo [a, b] a la mitad en cada "
        "iteración y se queda con el sub-intervalo donde ocurre el cambio de signo "
        "(Teorema de Bolzano), convergiendo hacia la raíz de f(x) = 0.\n\n"
        "**Fórmula:** `c = (a + b) / 2`\n\n"
        "**Ejemplo del informe:** f(x) = x² − 5, intervalo [2, 3] → raíz ≈ 2.2344"
    ),
)
def biseccion(datos: BiseccionEntrada):
    f = lambda x: evaluar(datos.funcion, x)

    fa = f(datos.a)
    fb = f(datos.b)

    # Validaciones previas
    if fa * fb > 0:
        return {
            "entrada": datos.dict(),
            "iteraciones": [],
            "raiz_aproximada": 0.0,
            "iteraciones_totales": 0,
            "error_final": 0.0,
            "convergencia": False,
            "mensaje": (
                f"❌ Error: f(a)={fa:.6f} y f(b)={fb:.6f} tienen el mismo signo. "
                "No se garantiza una raíz en el intervalo [a, b]. "
                "Por el Teorema de Bolzano se requiere f(a)·f(b) < 0."
            ),
        }

    iteraciones = []
    c_anterior = None

    for i in range(1, datos.max_iteraciones + 1):
        c = (datos.a + datos.b) / 2.0
        fc = f(c)

        error = abs(c - c_anterior) if c_anterior is not None else None

        iteraciones.append(
            IteracionBiseccion(
                iteracion=i,
                a=round(datos.a, 6),
                b=round(datos.b, 6),
                c=round(c, 6),
                f_a=round(fa, 6),
                f_b=round(fb, 6),
                f_c=round(fc, 6),
                error=round(error, 8) if error is not None else None,
            )
        )

        # Criterio de parada
        if error is not None and error < datos.tolerancia:
            return BiseccionRespuesta(
                entrada=datos.dict(),
                iteraciones=iteraciones,
                raiz_aproximada=round(c, 8),
                iteraciones_totales=i,
                error_final=round(error, 8),
                convergencia=True,
                mensaje=(
                    f"✅ Convergencia alcanzada en {i} iteraciones. "
                    f"La raíz aproximada de f(x) = {datos.funcion} es x ≈ {round(c, 6)}. "
                    f"Error final: {round(error, 8)} (tolerancia: {datos.tolerancia}). "
                    "El método dividió el intervalo sucesivamente, quedándose siempre "
                    "con el sub-intervalo donde f cambia de signo."
                ),
            )

        # Actualizar intervalo
        if fa * fc < 0:
            datos.b = c
            fb = fc
        else:
            datos.a = c
            fa = fc

        c_anterior = c

    # Se alcanzó el máximo de iteraciones
    c_final = iteraciones[-1].c
    error_final = iteraciones[-1].error or 0.0
    return BiseccionRespuesta(
        entrada=datos.dict(),
        iteraciones=iteraciones,
        raiz_aproximada=round(c_final, 8),
        iteraciones_totales=datos.max_iteraciones,
        error_final=round(error_final, 8),
        convergencia=False,
        mensaje=(
            f"⚠️ Se alcanzó el máximo de {datos.max_iteraciones} iteraciones sin "
            f"converger a la tolerancia {datos.tolerancia}. "
            f"Mejor aproximación obtenida: x ≈ {round(c_final, 6)}. "
            "Considera aumentar max_iteraciones o reducir la tolerancia."
        ),
    )


# ═══════════════════════════════════════════════════════════════
#  ENDPOINT 2 — MÉTODO DE LA SECANTE
# ═══════════════════════════════════════════════════════════════

class SecanteEntrada(BaseModel):
    funcion: str = "x**3 - x - 2"
    x0: float = 1.0
    x1: float = 2.0
    tolerancia: float = 0.0001
    max_iteraciones: int = 50

    class Config:
        json_schema_extra = {
            "example": {
                "funcion": "x**3 - x - 2",
                "x0": 1.0,
                "x1": 2.0,
                "tolerancia": 0.0001,
                "max_iteraciones": 50,
            }
        }


class IteracionSecante(BaseModel):
    iteracion: int
    x_n1: float   # xₙ₋₁
    x_n: float    # xₙ
    f_x_n1: float
    f_x_n: float
    x_nuevo: float
    error: Optional[float]


class SecanteRespuesta(BaseModel):
    entrada: dict
    iteraciones: List[IteracionSecante]
    raiz_aproximada: float
    iteraciones_totales: int
    error_final: float
    convergencia: bool
    mensaje: str


@app.post(
    "/secante",
    response_model=SecanteRespuesta,
    summary="Método de la Secante",
    tags=["Métodos Numéricos"],
    description=(
        "**Método de la Secante** — aproxima la derivada de f usando la pendiente "
        "de la recta que pasa por (xₙ₋₁, f(xₙ₋₁)) y (xₙ, f(xₙ)), sin necesidad "
        "de calcular f'(x) analíticamente.\n\n"
        "**Fórmula:** `xₙ₊₁ = xₙ − f(xₙ)·(xₙ − xₙ₋₁) / (f(xₙ) − f(xₙ₋₁))`\n\n"
        "**Convergencia:** superlineal (orden ≈ 1.618, número áureo)\n\n"
        "**Ejemplo del informe:** f(x) = x³ − x − 2, x₀=1, x₁=2 → raíz ≈ 1.5214"
    ),
)
def secante(datos: SecanteEntrada):
    f = lambda x: evaluar(datos.funcion, x)

    x_prev = datos.x0
    x_curr = datos.x1
    iteraciones = []

    for i in range(1, datos.max_iteraciones + 1):
        f_prev = f(x_prev)
        f_curr = f(x_curr)
        denominador = f_curr - f_prev

        # Verificar denominador nulo
        if abs(denominador) < 1e-12:
            return SecanteRespuesta(
                entrada=datos.dict(),
                iteraciones=iteraciones,
                raiz_aproximada=round(x_curr, 8),
                iteraciones_totales=i,
                error_final=0.0,
                convergencia=False,
                mensaje=(
                    f"❌ Error en iteración {i}: el denominador f(xₙ) − f(xₙ₋₁) ≈ 0. "
                    "El método falla porque la recta secante es casi horizontal. "
                    "Elige valores iniciales x₀ y x₁ más cercanos a la raíz."
                ),
            )

        # Fórmula del método de la Secante
        x_nuevo = x_curr - f_curr * (x_curr - x_prev) / denominador
        error = abs(x_nuevo - x_curr)

        iteraciones.append(
            IteracionSecante(
                iteracion=i,
                x_n1=round(x_prev, 6),
                x_n=round(x_curr, 6),
                f_x_n1=round(f_prev, 6),
                f_x_n=round(f_curr, 6),
                x_nuevo=round(x_nuevo, 6),
                error=round(error, 8),
            )
        )

        # Criterio de parada
        if error < datos.tolerancia:
            return SecanteRespuesta(
                entrada=datos.dict(),
                iteraciones=iteraciones,
                raiz_aproximada=round(x_nuevo, 8),
                iteraciones_totales=i,
                error_final=round(error, 8),
                convergencia=True,
                mensaje=(
                    f"✅ Convergencia alcanzada en {i} iteraciones. "
                    f"La raíz aproximada de f(x) = {datos.funcion} es x ≈ {round(x_nuevo, 6)}. "
                    f"Error final: {round(error, 8)} (tolerancia: {datos.tolerancia}). "
                    "El método trazó rectas secantes sucesivas hasta que la distancia "
                    "entre aproximaciones consecutivas fue menor a la tolerancia. "
                    f"Convergencia superlineal (orden ≈ 1.618)."
                ),
            )

        # Avanzar
        x_prev = x_curr
        x_curr = x_nuevo

    error_final = iteraciones[-1].error or 0.0
    return SecanteRespuesta(
        entrada=datos.dict(),
        iteraciones=iteraciones,
        raiz_aproximada=round(x_curr, 8),
        iteraciones_totales=datos.max_iteraciones,
        error_final=round(error_final, 8),
        convergencia=False,
        mensaje=(
            f"⚠️ Se alcanzó el máximo de {datos.max_iteraciones} iteraciones sin "
            f"converger a la tolerancia {datos.tolerancia}. "
            f"Mejor aproximación: x ≈ {round(x_curr, 6)}. "
            "Verifica que los valores iniciales estén cerca de la raíz."
        ),
    )


# ─────────────────────────────────────────────
#  Ruta raíz — información general
# ─────────────────────────────────────────────
@app.get("/", tags=["Info"])
def inicio():
    return {
        "proyecto": "Métodos Numéricos con FastAPI",
        "grupo": "Félix Samudio, José Urrunaga, Jeremy Gonzalez",
        "curso": "Análisis Numérico — Ingeniería en Informática",
        "endpoints_disponibles": {
            "/biseccion": "Método de Bisección — POST",
            "/secante": "Método de la Secante — POST",
            "/docs": "Documentación interactiva Swagger UI",
            "/redoc": "Documentación ReDoc",
        },
        "descripcion": (
            "Backend que implementa dos métodos numéricos para encontrar raíces "
            "de ecuaciones no lineales f(x) = 0. "
            "Acepta cualquier función matemática como string."
        ),
    }
