# RiskFlow 🛡️

![Render Deployment](https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge&logo=render)

🚀 **Demo en vivo (API):** [https://riskflow-o3ol.onrender.com](https://riskflow-o3ol.onrender.com)  
📄 **Documentación Interactiva (Swagger UI):** [https://riskflow-o3ol.onrender.com/docs](https://riskflow-o3ol.onrender.com/docs)

Backend fintech con motor de detección de fraude en tiempo real, analytics de transacciones y explicación de alertas con IA.

Evolución de [BankCore](https://github.com/devzape/bankcore): además de mover dinero entre cuentas, **RiskFlow analiza cada transacción contra reglas de riesgo configurables**, genera alertas automáticas, calcula estadísticas agregadas con pandas, y usa un LLM para explicar en lenguaje natural por qué una transacción fue marcada como sospechosa.

## Features

- 🔐 **Autenticación JWT** — registro y login de usuarios.
- 💸 **Cuentas y transferencias** — con validación de saldo y doble entrada.
- 🚨 **Motor de reglas de riesgo configurable** — reglas almacenadas en base de datos (no hardcodeadas), evaluadas automáticamente en cada transacción. Incluye detección de monto alto y frecuencia sospechosa.
- 📊 **Analytics con pandas** — volumen de transacciones por día, ranking de cuentas con más alertas, distribución de alertas por severidad.
- 🤖 **Explicación de alertas con IA** — cada alerta puede explicarse en lenguaje natural usando Gemini.
- ✅ **Tests automatizados** — pytest sobre la lógica de negocio crítica (motor de reglas, auth).
- 🐳 **Dockerizado** — levantá todo con un solo comando, sin instalar PostgreSQL localmente.
- ⚙️ **CI/CD con GitHub Actions** — tests corren automáticamente en cada push.

## Stack

- **Backend**: FastAPI + SQLAlchemy
- **Base de datos**: PostgreSQL
- **Autenticación**: JWT (python-jose) + bcrypt
- **Analytics**: pandas
- **IA**: Google Gemini (google-genai)
- **Tests**: pytest
- **Infra**: Docker, docker-compose, GitHub Actions

## Modelo de datos
users
  └── accounts
        └── transactions ──── alerts ──── risk_rules

- **users**: cuentas de usuario del sistema.
- **accounts**: cuentas bancarias, cada una ligada a un usuario.
- **transactions**: transferencias entre cuentas.
- **risk_rules**: reglas de riesgo configurables (nombre, umbral, activa/inactiva).
- **alerts**: generadas automáticamente cuando una transacción dispara una regla.

## Cómo correrlo

### Opción A: Docker (recomendado)

```bash
git clone https://github.com/devzape/riskflow.git
cd riskflow
cp .env.example .env   # completar SECRET_KEY y GOOGLE_API_KEY
docker-compose up --build
```

La API queda disponible en `http://localhost:8000/docs`.

### Opción B: entorno local

```bash
python -m venv venv
venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt
# crear base "riskflow" en PostgreSQL y completar .env
uvicorn app.main:app --reload
```

## Ejemplo de uso

1. **Registrarse y loguearse** → `POST /auth/register`, `POST /auth/login` (devuelve un JWT).
2. **Crear cuentas** → `POST /accounts/`.
3. **Configurar una regla de riesgo** → `POST /risk-rules/`:
```json
   {"name": "monto_alto", "description": "Monto superior al umbral", "threshold": 500, "active": true}
```
4. **Hacer una transferencia que la dispare** → `POST /transactions/` con un monto que supere el umbral. La transacción queda con `status: "flagged"`.
5. **Ver la alerta generada** → `GET /alerts/`.
6. **Pedirle a la IA que la explique** → `GET /alerts/{id}/explain`.
7. **Ver el panorama general** → `GET /analytics/summary`.

## Tests

```bash
python -m pytest -v
```

## Roadmap / posibles mejoras

- Reglas de riesgo más sofisticadas (detección de patrones, ML en vez de reglas fijas).
- Dashboard visual para analytics (en vez de solo JSON).
- Notificaciones en tiempo real cuando se genera una alerta de severidad alta.

---

Proyecto de portafolio — [Benjamin Morales](https://github.com/devzape)