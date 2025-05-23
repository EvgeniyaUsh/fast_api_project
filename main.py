import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

from api.handelrs import user_router
from api.login_handler import login_router
from api.dish_handler import dish_router

app = FastAPI(title="fastapi_project")

api_name = "/api"

main_router = APIRouter()
main_router.include_router(user_router, prefix="/user", tags=["user"])
main_router.include_router(login_router, prefix="/login", tags=["login"])
main_router.include_router(dish_router, prefix=f"{api_name}/dishes", tags=["dish"])
# main_router.include_router(dish_router, prefix=f"{api_name}/tags", tags=["tag"])

app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run(app, host="192.168.0.188", port=8000)
