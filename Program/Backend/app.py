from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import ENVIRONMENT, STATIC_DIR, HOST, PORT
from routes import chat_router, vendas_router

def create_app() -> FastAPI:
    """Cria e configura a aplicação FastAPI."""
    app = FastAPI(
        title="CodeSellers Vendas API",
        description="API para o sistema de vendas CodeSellers.",
        version="1.0.0"
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Permite qualquer origem
        allow_credentials=True,
        allow_methods=["*"],  # Permite todos os métodos (GET, POST, etc)
        allow_headers=["*"],  # Permite todos os cabeçalhos
    )
    
    # Incluir rotas
    app.include_router(chat_router)
    app.include_router(vendas_router)
    
    # Montar arquivos estáticos em produção
    if ENVIRONMENT == "production" and STATIC_DIR:
        app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
    
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=HOST, port=PORT) 