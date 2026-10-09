# RiskFlow 🛡️

[![Render Deployment](https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge&logo=render)](https://riskflow-o3ol.onrender.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org)

🚀 **Demo en vivo (API):** <https://riskflow-o3ol.onrender.com>
📄 **Documentación interactiva (Swagger UI):** <https://riskflow-o3ol.onrender.com/docs>

Backend fintech con un **motor de reglas de riesgo configurable**, analytics de transacciones y explicación de alertas con IA.

Evolución de [BankCore](https://github.com/devzape/bankcore): además de mover dinero entre cuentas, **RiskFlow evalúa cada transacción contra reglas de riesgo guardadas en base de datos**, genera alertas automáticas, calcula estadísticas agregadas con pandas y usa un LLM para explicar en lenguaje natural por qué una transacción fue marcada como sospechosa.

---

## Features

- 🔐 **Autenticación JWT**: registro y login de usuarios. Todos los endpoints de negocio requieren token.
- 💸 **Cuentas y transferencias**: validación de saldo, monto positivo y bloqueo de transferencias a la misma cuenta. Usa locking de filas (`SELECT ... FOR UPDATE`) para evitar condiciones de carrera cuando llegan transferencias simultáneas desde la misma cuenta.
- 🚨 **Motor de reglas de riesgo configurable**: las reglas viven en la base de datos (nombre, umbral, activa/inactiva) y se evalúan en cada transacción. Reglas incluidas: `monto_alto` y `frecuencia_sospechosa`.
- 🔒 **Aislamiento por usuario**: cada usuario solo ve y opera sobre sus propias cuentas, transacciones y alertas.
- 📊 **Analytics con pandas**: volumen de transacciones por día, ranking de cuentas con más alertas y distribución de alertas por severidad.
- 🤖 **Explicación de alertas con IA**: integración asíncrona con Google Gemini. Si el servicio de IA falla, el endpoint devuelve una explicación de contingencia en vez de un error.
- 🗄️ **Migraciones con Alembic**: el esquema de la base se versiona y se aplica con `alembic upgrade head`.
- ✅ **Tests automatizados**: pytest sobre la lógica de negocio crítica (motor de reglas, autenticación).
- 🐳 **Dockerizado**: `docker-compose` levanta la API y PostgreSQL sin instalar nada localmente.
- ⚙️ **CI/CD**: GitHub Actions corre los tests en cada push y el despliegue se hace en Render.

---

## Stack

- **Backend**: FastAPI + SQLAlchemy 2.0
- **Base de datos**: PostgreSQL + Alembic
- **Autenticación**: JWT (python-jose) + Passlib (bcrypt)
- **Analytics**: pandas
- **IA generativa**: Google Gemini (SDK `google-genai`)
- **Testing**: pytest
- **Infraestructura**: Docker, Docker Compose, GitHub Actions, Render

---

## Modelo de datos

```
users (1)        ──→ (N) accounts
accounts (1)     ──→ (N) transactions
transactions (1) ──→ (N) alerts
risk_rules (1)   ──→ (N) alerts
```

- **`users`**: usuarios del sistema.
- **`accounts`**: cuentas asociadas a cada usuario, con su saldo.
- **`transactions`**: transferencias entre cuentas. Quedan en estado `completed` o `flagged`.
- **`risk_rules`**: reglas de riesgo configurables (nombre, umbral, activa/inactiva).
- **`alerts`**: se generan automáticamente cuando una transacción dispara una regla, con una severidad (`low`, `medium`, `high`).

---

## Configuración del entorno

Creá un archivo `.env` en la raíz del proyecto. Podés copiar `.env.example` y completar los valores:

```
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/riskflow
SECRET_KEY=una_clave_larga_y_aleatoria
GOOGLE_API_KEY=tu_api_key_de_google_ai_studio
```

---

## Cómo correrlo

### Opción A: Docker (recomendado)

```bash
git clone https://github.com/devzape/riskflow.git
cd riskflow
cp .env.example .env   # completar SECRET_KEY y GOOGLE_API_KEY
docker-compose up --build
```

Si las tablas no se crean solas al levantar los contenedores, aplicá las migraciones:

```bash
docker-compose exec api alembic upgrade head
```

La API queda disponible en `http://localhost:8000/docs`.

### Opción B: entorno local

```bash
git clone https://github.com/devzape/riskflow.git
cd riskflow
python -m venv venv

# Windows
venv\Scripts\Activate.ps1
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt
# crear la base "riskflow" en PostgreSQL y completar el .env
alembic upgrade head
python -m uvicorn app.main:app --reload
```

---

## Flujo de uso

1. **Registrarse y loguearse**: `POST /auth/register` y `POST /auth/login` (devuelve un JWT; en Swagger usalo con el botón *Authorize*).
2. **Crear cuentas**: `POST /accounts/`.
3. **Configurar una regla de riesgo**: `POST /risk-rules/`

   ```json
   {
     "name": "monto_alto",
     "description": "Monto superior al umbral establecido",
     "threshold": 500,
     "active": true
   }
   ```

4. **Hacer una transferencia que la dispare**: `POST /transactions/` con un monto mayor al umbral. La transacción queda con `status: "flagged"`.
5. **Ver las alertas**: `GET /alerts/` (solo las de tus propias cuentas).
6. **Pedir una explicación a la IA**: `GET /alerts/{id}/explain`.
7. **Ver el panorama general**: `GET /analytics/summary`.

---

## Tests

```bash
python -m pytest -v
```

---

## Limitaciones conocidas

Es un proyecto de portafolio, no un sistema de producción. Lo que tiene de más y de menos:

- **Las reglas son simples**: comparan contra umbrales fijos (monto, cantidad de transacciones en una ventana de 10 minutos). No hay scoring estadístico ni detección de patrones más complejos, por eso lo describo como motor de reglas y no como detección de fraude en sentido estricto.
- **La evaluación es síncrona**: las reglas se evalúan dentro del request de la transferencia, no en un proceso aparte ni sobre un flujo de eventos.
- **El saldo se maneja con un solo movimiento por transferencia**: se resta de la cuenta origen, se suma a la destino y se guarda una fila en `transactions`. No es un libro contable de doble entrada.
- **Sin roles**: cualquier usuario autenticado puede crear reglas de riesgo, y esas reglas son globales.
- **Cobertura de tests parcial**: se concentra en autenticación y motor de reglas; analytics y el endpoint de IA (que depende de un servicio externo) tienen menos cobertura.

## Posibles mejoras

- Roles (admin vs. usuario) para gestionar las reglas de riesgo.
- Reglas más sofisticadas (scoring, modelos de ML en lugar de umbrales fijos).
- Mocks de Gemini para testear el endpoint de explicación.
- Dashboard visual para los analytics.

---

Proyecto de portafolio creado por **[Benjamín Morales](https://github.com/devzape)**.