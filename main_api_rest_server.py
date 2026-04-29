from fastapi import FastAPI
import os
import asyncio
import inspect
from dotenv import load_dotenv
from presentation.rest.routes import router

# Cargar variables del archivo .env
load_dotenv()

app = FastAPI(title="Students API")
app.include_router(router)


if __name__ == "__main__":
    # Leer variable desde .env
    port = int(os.getenv("API_PORT", 5000))

    print("=" * 40)
    print("Starting REST API...")
    print(f"API_PORT loaded: {port}")
    print("=" * 40)

    # Importar uvicorn después de asegurar la compatibilidad
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=False
    )