from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def decision_making_status():
    return {"message": "Decision module is active"}
