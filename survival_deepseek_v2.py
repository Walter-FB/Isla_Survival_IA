import subprocess
from transformers import AutoTokenizer
import os
import re

# ---------------- CONFIGURACIÓN GENERAL ---------------- #
MODEL = "deepseek-r1:7b"
HISTORIA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historia.txt")

PERSONAJES = [
    {
        "nombre": "El Capitán",
        "rol": "Líder del grupo",
        "personalidad": "Eres El Capitán, un líder natural que intenta mantener el orden y guiar al grupo con firmeza. Eres práctico, directo, y te frustra la improvisación sin sentido.",
    },
    {
        "nombre": "El Sabio",
        "rol": "Filósofo y observador",
        "personalidad": "Eres El Sabio, un pensador profundo que reflexiona sobre cada decisión. A menudo haces referencias a leyendas antiguas o a la moral de las acciones.",
    },
    {
        "nombre": "El Artista",
        "rol": "Excéntrico creativo",
        "personalidad": "Eres El Artista, excéntrico y teatral. Te expresás en forma poética, usás metáforas, y actuás por instinto. Amás el caos si es bello. Respondes como si fueras un artista dentro de la isla",
    }
]

MASTER = {
    "nombre": "El Narrador",
    "rol": "Voz del mundo",
    "personalidad": "Eres El Narrador, la voz omnisciente que observa lo que hacen los personajes y describe cómo responde el entorno. No repitas sus frases. No menciones que son IAs. Crea una narrativa rica, coherente y realista. Luego, inventa un nuevo evento desafiante. Necesito que la respuesta que des sea SOLO lo que diría un narrador, solo narra nada más",
}

EVENTO_INICIAL = "Estás atrapado en una isla desierta junto a los demás. Un mono ladrón aparece de repente y se lleva el único pendrive que contiene el script de rescate. ¿Qué haces?"

# ---------------- FUNCIONES AUXILIARES ---------------- #
tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/deepseek-coder-1.3b-base")

def contar_tokens(texto):
    return len(tokenizer.encode(texto))

def hablar_con_ollama(prompt: str) -> (str, int, int):
    tokens_input = contar_tokens(prompt)
    try:
        result = subprocess.run(
            ["ollama", "run", MODEL],
            input=prompt.encode("utf-8"),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=200
        )
        output = result.stdout.decode("utf-8", errors="ignore").strip()
        tokens_output = contar_tokens(output)
        return output, tokens_input, tokens_output
    except Exception as e:
        return f"Error: {str(e)}", tokens_input, 0

def cargar_historia():
    if os.path.exists(HISTORIA_PATH):
        with open(HISTORIA_PATH, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def guardar_historia(historia):
    print(f"Intentando guardar historia en {HISTORIA_PATH}...")
    print(f"Contenido a guardar (primeros 100 caracteres): {historia[:100]}...")
    try:
        with open(HISTORIA_PATH, "w", encoding="utf-8") as f:
            f.write(historia.strip())
        print(f"✅ Historia guardada exitosamente en {HISTORIA_PATH}")
    except Exception as e:
        print(f"❌ Error al guardar historia: {str(e)}")

def extraer_respuesta_final(texto, mostrar_think=False):
    """
    Extrae el texto fuera del bloque <think>...</think>.
    Si mostrar_think es True, imprime el contenido interno.
    """
    match = re.search(r"<think>(.*?)</think>", texto, re.DOTALL)
    if match:
        pensamiento = match.group(1).strip()
        if mostrar_think:
            print(f"\n🤖 [THINK]:\n{pensamiento}\n{'-'*60}")
        # Retorna lo que viene después del </think>
        resto = texto.split("</think>")[-1].strip()
        return resto
    return texto.strip()

# ---------------- FUNCIONES PRINCIPALES ---------------- #
def procesar_personaje(personaje, evento_actual):
    prompt = f"""
Eres {personaje['nombre']}, {personaje['rol']}.
{personaje['personalidad']}

Situación actual:
{evento_actual}

IMPORTANTE: Responde EN PRIMERA PERSONA como si TÚ MISMO fueras este personaje atrapado en la isla. NO hables sobre ningún narrador. Simplemente describe lo que TÚ harías en esta situación.

Describe brevemente qué hacés o decidís frente a esta situación. Habla como {personaje['nombre']}.
"""
    print(f"🎭 [{personaje['nombre']}] está actuando...")
    respuesta, tin, tout = hablar_con_ollama(prompt)
    respuesta_filtrada = extraer_respuesta_final(respuesta, mostrar_think=True)

    print(f"🗯️🗯️🗯️ RESPUESTA 🗯️🗯️🗯️ de {personaje['nombre']}:\n{respuesta_filtrada}")
    print(f"🧾 TOKENS usados — input: {tin} / output: {tout} / total: {tin + tout}")
    print("-" * 60)
    return f"- {personaje['nombre']}: {respuesta_filtrada}", tin + tout


def procesar_narrador(historia, resumen_acciones):
    prompt_narrador = f"""
Eres {MASTER['nombre']}, {MASTER['rol']}.
{MASTER['personalidad']}

Historia previa:
{historia.strip()}

Acciones de los personajes en esta ronda:
{resumen_acciones}

### INSTRUCCIONES:
1. Narrá lo que sucede en la isla como consecuencia de esas acciones.
2. Luego, crea un nuevo evento que los desafíe en la próxima ronda.

### RESPUESTA DEL NARRADOR (solo texto narrativo, no repitas esto):
"""
    print("🧙‍♂️ [Narrador] está escribiendo la historia...")
    narracion, tin, tout = hablar_con_ollama(prompt_narrador)
    narracion_filtrada = extraer_respuesta_final(narracion, mostrar_think=False)
    print(f"\n📝 TUYO:\n{narracion_filtrada}")
    print(f"🧾 TOKENS usados — input: {tin} / output: {tout} / total: {tin + tout}")
    print("=" * 60)
    return narracion_filtrada, tin + tout

# ---------------- MAIN ---------------- #
def main():
    try:
        historia = cargar_historia()
        evento_actual = EVENTO_INICIAL if not historia else historia.split("Nuevo evento:")[-1].strip()
        resumen_acciones = []
        total_tokens = 0

        for personaje in PERSONAJES:
            try:
                resumen, tokens_usados = procesar_personaje(personaje, evento_actual)
                resumen_acciones.append(resumen)
                total_tokens += tokens_usados
            except Exception as e:
                print(f"Error procesando personaje {personaje['nombre']}: {str(e)}")
                resumen_acciones.append(f"- {personaje['nombre']}: [Error en respuesta]")

        acciones_texto = "\n".join(resumen_acciones)
        
        try:
            narracion, tokens_narrador = procesar_narrador(historia, acciones_texto)
            total_tokens += tokens_narrador
        except Exception as e:
            print(f"Error procesando narrador: {str(e)}")
            narracion = "El narrador no pudo continuar la historia debido a un error técnico."

        nuevo_contenido = f"\n\nRonda:\n{acciones_texto}\n\nNarrador:\n{narracion}"
        historia += nuevo_contenido
        
        # Guardar incluso si hay errores parciales
        guardar_historia(historia)
        print(f"\n📊 CONSUMO TOTAL DE TOKENS EN ESTA RONDA: {total_tokens}")
        
        # Crear una copia de seguridad del archivo
        try:
            with open(f"{HISTORIA_PATH}.backup", "w", encoding="utf-8") as f:
                f.write(historia.strip())
            print("✅ Copia de seguridad creada")
        except Exception as e:
            print(f"❌ Error al crear copia de seguridad: {str(e)}")
            
    except Exception as e:
        print(f"Error general en la ejecución: {str(e)}")
        # Intentar guardar lo que se tenga hasta el momento
        try:
            if 'historia' in locals() and 'nuevo_contenido' in locals():
                guardar_historia(historia)
                print("✅ Se guardó la historia parcial antes de terminar")
        except:
            print("❌ No se pudo guardar ninguna historia")

if __name__ == "__main__":
    main()