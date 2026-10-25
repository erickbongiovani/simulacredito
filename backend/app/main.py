from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router


app = FastAPI(
    title='SimulaCredito',
    description='API de Gestão, Simulação e Aceleração de Financiamento',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc'

)

origins = [
    'http://localhost:5173',
    'http://127.0.0.1:5173'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
    allow_headers=['*'],
)

app.include_router(api_router, prefix='/api')

@app.get('/health', tags=['Monitoramento'])
def health_check():
    return {'status': 'healthy', 'app':'SimulaCredito'}