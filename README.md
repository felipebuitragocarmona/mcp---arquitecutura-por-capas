**Students Architecture**

Proyecto de ejemplo que implementa una API REST y una interfaz MCP para gestionar estudiantes.

**Autor:** MsC Felipe Buitrago Carmona

**Afiliación:** Departamento de sistemas e informática, Facultad de Inteligencia Artificial e Ingeniería, Universidad de Caldas

**Descripción:**
- Arquitectura en capas: `presentation` (REST + MCP), `business` (servicio), `data` (repositorios), `models` (DTOs y entidades).
- Soporta persistencia en JSON y SQLite y selección dinámica mediante `.env`.

**Requisitos**
- Python 3.12+ (entorno virtual recomendado)
- Dependencias listadas en `requirements.txt`.

**Instalación rápida**
1. Crear y activar un virtualenv:

```powershell
python -m venv venv
& venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

**Configuración (.env)**
- Copiar o crear un archivo `.env` en la raíz con valores como:

```
FASTMCP_STATELESS_HTTP=true
REPO_TYPE=json      # o sqlite
JSON_PATH=students.json
SQLITE_PATH=students.db
API_PORT=5000
MCP_PORT=9000
```

Cambiar `REPO_TYPE` entre `json` y `sqlite` selecciona la implementación de persistencia.

Nota: después de cambiar `.env` reiniciar el servidor para que la fábrica de repositorios lo lea.

**Ejecutar API REST (desarrollo)**

```powershell
venv\Scripts\python.exe -m uvicorn main_api_rest_server:app --reload --port 5000
```

**Ejecutar servidor MCP**

```powershell
venv\Scripts\python.exe main_mcp_server.py
```

**Rutas principales (REST)**
- `GET /students` — listar estudiantes
- `POST /students` — crear estudiante
- `GET /students/{id}` — obtener estudiante
- `PUT /students/{id}` — actualizar
- `DELETE /students/{id}` — eliminar

Ejemplo `curl` para crear un estudiante:

```bash
curl -X POST http://localhost:5000/students -H "Content-Type: application/json" -d '{"name":"Ana","email":"ana@example.com","age":21,"career":"Ingenieria","semester":4}'
```

**Notas útiles**
- Si usas depurador (p.ej. PyCharm) y ves un `TypeError` relacionado con `loop_factory`, el arranque contiene una compatibilidad para `asyncio.run` en `main_api_rest_server.py`.
- Pydantic muestra una advertencia si usas `orm_mode` con v2; se recomienda usar `from_attributes` cuando se migre a Pydantic v2.

**Configuración Claude Desktop**
Instalar Claude Desktop, luego ir a la parte inferior izquierda, donde aparece el nombre de usuario, luego sección `Configuración`, luego sección `Desarrollador`, `Editar Configuración`, y pegar el siguiente JSON.

``` json
{
  "mcpServers": {
    "students_architecture": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:9000/mcp",
        "--allow-http"
      ],
      "env": {
        "MCP_TRANSPORT_STRATEGY": "http-only"
      }
    }
  },
  "preferences": {
    "coworkScheduledTasksEnabled": false,
    "sidebarMode": "chat",
    "coworkWebSearchEnabled": true,
    "ccdScheduledTasksEnabled": false
  }
}
```

**Contacto**
MsC Felipe Buitrago Carmona
felipe.buitrago@ucaldas.edu.co
Departamento de sistemas e informática
Universidad de Caldas
