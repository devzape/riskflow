import logging
import os
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


def _get_client() -> genai.Client:
    """Instancia el cliente de Gemini validando la API Key."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY no está configurada en las variables de entorno.")
    return genai.Client(api_key=api_key)


async def explain_alert(transaction: dict, rule: dict) -> str:
    """Genera una explicación automatizada para una alerta de riesgo usando Gemini API."""
    system_instruction = (
        "Sos un analista de riesgo fintech experto. Explicá en 2-3 oraciones, "
        "en español y en lenguaje simple para alguien sin conocimientos técnicos, "
        "por qué esta transacción fue marcada como sospechosa. "
        "Respondé solo con la explicación, sin saludos ni frases introductorias."
    )

    prompt = f"""Analiza la siguiente transacción que disparó una regla de riesgo:

Transacción:
- Monto: {transaction.get('amount', 'N/A')}
- Cuenta origen: {transaction.get('origin_account_id', 'N/A')}
- Cuenta destino: {transaction.get('destination_account_id', 'N/A')}
- Fecha/hora: {transaction.get('timestamp', 'N/A')}

Regla que se disparó:
- Nombre: {rule.get('name', 'N/A')}
- Descripción: {rule.get('description', 'N/A')}
- Umbral configurado: {rule.get('threshold', 'N/A')}"""

    try:
        client = _get_client()

        response = await client.aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,
            ),
        )
        return response.text.strip()

    except Exception as exc:
        logger.error("Error al generar la explicación con Gemini API: %s", exc)
        return (
            f"La transacción superó el umbral de {rule.get('threshold', 'N/A')} "
            f"configurado en la regla '{rule.get('name', 'N/A')}', "
            "por lo que se generó una alerta automática para revisión."
        )