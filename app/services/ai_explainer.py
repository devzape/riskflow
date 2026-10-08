import os
from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


def explain_alert(transaction: dict, rule: dict) -> str:
    prompt = f"""Sos un analista de riesgo fintech. Explicá en 2-3 oraciones, en español y en lenguaje simple para alguien sin conocimientos técnicos, por qué esta transacción fue marcada como sospechosa.

Transacción:
- Monto: {transaction['amount']}
- Cuenta origen: {transaction['origin_account_id']}
- Cuenta destino: {transaction['destination_account_id']}
- Fecha/hora: {transaction['timestamp']}

Regla que se disparó:
- Nombre: {rule['name']}
- Descripción: {rule['description']}
- Umbral configurado: {rule['threshold']}

Respondé solo con la explicación, sin saludos ni frases introductorias."""

    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt,
    )
    return response.text