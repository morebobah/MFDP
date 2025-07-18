from fastapi import APIRouter, Request

router = APIRouter(tags=['Health page'])

@router.get("/health", summary='Are you ok?', include_in_schema=False)
def home_page():
    return {'message': 'I am OK!'}