from fastapi import APIRouter

router = APIRouter()

@router.get('/projects')
def list_projects():
    return {'projects': []}
