# RiskFlow 🛡️

![Render Deployment](https://img.shields.io/badge/Status-Live-brightgreen?style=for-the-badge&logo=render)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)

🚀 **Demo en vivo (API):** [https://riskflow-o3ol.onrender.com](https://riskflow-o3ol.onrender.com)  
📄 **Documentación Interactiva (Swagger UI):** [https://riskflow-o3ol.onrender.com/docs](https://riskflow-o3ol.onrender.com/docs)

Backend fintech con motor de detección de fraude en tiempo real, analytics de transacciones y explicación de alertas con IA.

Evolución de [BankCore](https://github.com/devzape/bankcore): además de gestionar la transferencia de dinero entre cuentas, **RiskFlow analiza cada transacción contra reglas de riesgo configurables**, genera alertas automáticas, calcula estadísticas agregadas con pandas y utiliza un LLM para explicar en lenguaje natural por qué una transacción fue marcada como sospechosa.

---

## Features

- 🔐 **Autenticación JWT** — registro y login seguro de usuarios.
- 💸 **Cuentas y transferencias** — validación de saldo y contabilidad de doble entrada.
- 🚨 **Motor de reglas de riesgo configurable** — reglas persistidas en base de datos evaluadas automáticamente en cada transacción (monto alto, frecuencia sospechosa, etc.).
- 📊 **Analytics con pandas** — volumen de transacciones por día, ranking de cuentas con más alertas y distribución de severidad.
- 🤖 **Explicación de alertas con IA** — integración asíncrona con la API de Google Gemini para traducir alertas técnicas a lenguaje no técnico.
- ✅ **Tests automatizados** — cobertura con `pytest` sobre la lógica de negocio crítica (motor de reglas, autenticación).
- 🐳 **Dockerizado** — entorno portable con `docker-compose` listo para levantar sin dependencias locales.
- ⚙️ **CI/CD con GitHub Actions** — ejecución automática de suite de tests en cada commit y despliegue continuo en Render.

---

## Stack Tecnológico

- **Backend**: FastAPI + SQLAlchemy 2.0
- **Base de Datos**: PostgreSQL
- **Autenticación**: JWT (python-jose) + Passlib (bcrypt)
- **Analytics**: pandas
- **IA Generativa**: Google Gemini (`google-genai` SDK)
- **Testing**: pytest
- **Infraestructura**: Docker, Docker Compose, GitHub Actions, Render

---

## Modelo de Datos

```text
users
 └── accounts
       └── transactions ──── alerts ──── risk_rules
```

- **`users`**: Usuarios del sistema.
- **`accounts`**: Cuentas bancarias asociadas a cada usuario.
- **`transactions`**: Historial de transferencias entre cuentas.
- **`risk_rules`**: Reglas de riesgo fijas o dinámicas (nombre, umbral, estado activo/inactivo).
- **`alerts`**: Alertas generadas en tiempo real cuando una transacción viola una regla.

---

## Configuración del Entorno (`.env`)

Crea un archivo `.env` en la raíz del proyecto basándote en las siguientes variables:

```env
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/riskflow
SECRET_KEY=tu_secret_key_jwt
GOOGLE_API_KEY=tu_gemini_api_key
```

---

## Cómo Correrlo

### Opción A: Docker (Recomendado)

```bash
git clone [https://github.com/devzape/riskflow.git](https://github.com/devzape/riskflow.git)
cd riskflow
cp .env.example .env   # Configurar SECRET_KEY y GOOGLE_API_KEY
docker-compose up --build
```

La API quedará disponible en `http://localhost:8000/docs`.

### Opción B: Entorno Local

```bash
python -m venv venv

# En Windows:
venv\Scripts\Activate.ps1
# En Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload
```

---

## Flujo de Uso (Paso a Paso)

1. **Registrarse y Autenticarse** → `POST /auth/register` y `POST /auth/login` (obtiene token JWT).
2. **Crear Cuentas** → `POST /accounts/`.
3. **Configurar una Regla de Riesgo** → `POST /risk-rules/`:
   ```json
   {
     "name": "monto_alto",
     "description": "Monto superior al umbral establecido",
     "threshold": 500,
     "active": true
   }
   ```
4. **Ejecutar Transferencia** → `POST /transactions/` con un monto superior al umbral (`500`). La transacción se procesará con estado `"flagged"`.
5. **Consultar Alertas** → `GET /alerts/`.
6. **Explicación con IA** → `GET /alerts/{id}/explain` (obtiene la explicación en lenguaje simple mediante Gemini).
7. **Consultar Analytics** → `GET /analytics/summary`.

---

## Pruebas Automatizadas

Para ejecutar la suite de tests locales:

```bash
python -m pytest -v
```

---

## Roadmap

- [ ] Reglas de riesgo basadas en Machine Learning (detección de anomalías de comportamiento).
- [ ] Dashboard interactivo en frontend para visualización de métricas y alertas.
- [ ] Sistema de notificaciones en tiempo real (WebSockets / Email) para alertas de severidad alta.

---

Proyecto de portafolio creado por **[Benjamín Morales](https://github.com/devzape)**.