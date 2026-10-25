from fastapi import APIRouter
from app.api.v1.endpoints import simulations

api_router = APIRouter()

# Registra as rotas de simulação sob o prefixo /simulations
api_router.include_router(
    simulations.router, 
    prefix="/simulations", 
    tags=["simulations"]
)


#@app.post('/compare')
#def compare_simulations(
#    request: ComparisonRequest, 
#    db: Session = Depends(get_db),
#    current_user: User = Depends(get_current_user)
#):

# api_router.include_router(
#     users.router,
#     prefix='/users',
#     tags=["users"],
#     dependencies=[Depends(get_current_user)]
# )