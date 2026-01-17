DeepSeek Survival — Juego de Rol Multiagente con LLMs

Este proyecto es una simulación de juego de rol con 3 agentes IA en una isla desierta. Cada personaje utiliza deepseek: 7B, estos mismos tiene una personalidad definida y responde a eventos precondicionados por su personalidad predefinida. Un narrador IA interpreta sus decisiones y genera una historia continua, creando nuevos desafíos cada ronda.
Tambien tiene cada respuesta su contador de tokens, este proyecto tenia la finalidad de explorar el potencial de las ia comunicandose entre si, quedo un proyecto medio raro pero divertido
---

## 👥 Personajes

- **El Capitán** – Líder lógico y estructurado.
- **El Sabio** – Filósofo reflexivo y moralista.
- **El Artista** – Creativo, excéntrico y teatral.
- **El Narrador** – Voz omnisciente que responde con narrativa y nuevos eventos.

---

## 🚀 Tecnologías usadas

- Python 3.11
- Ollama (con modelo `deepseek-r1:7b`)
- Transformers (token counting)
- Generación automática de narrativa
- Uso de tokens para medir consumo

---

## 🛠️ Cómo ejecutarlo

1. Tener instalado `ollama` y haber cargado el modelo:

```bash
ollama run deepseek-r1:7b
una ves teniendo eso correr: python survival.py 
(advertencia las ia utilizan el motor interno de la pc, no el gpu debido a que mi pc no alcanzaba con el requerimiento que exigia 7B

Si lo corren se generara un txt en la misma carpeta con un resumen del evento ocurrido y las acciones de los personajes en cuestion.
