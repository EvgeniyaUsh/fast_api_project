import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.routing import APIRouter


from api.handelrs import user_router
from api.login_handler import login_router
from api.dish_handler import dish_router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request
from fastapi import FastAPI
import logging

logger = logging.getLogger("uvicorn.error")


app = FastAPI(title="fastapi_project")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )


# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     if exc.status_code == 404:
#         logger.error(f"Not Found error: {exc.detail}")
#         return JSONResponse(
#             status_code=404,
#             content={"detail": "The resource you are looking for could not be found."},
#         )
#     # Если ошибка не 404, просто возвращаем стандартный ответ для HTTPException
#     return await request.app.default_exception_handler(request, exc)


api_name = "/api"

main_router = APIRouter()
main_router.include_router(user_router, prefix="/user", tags=["user"])
main_router.include_router(login_router, prefix="/login", tags=["login"])
main_router.include_router(dish_router, prefix=f"{api_name}/dishes", tags=["dish"])
# main_router.include_router(dish_router, prefix=f"{api_name}/tags", tags=["tag"])

app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app", host="192.168.0.131", port=8000, reload=True, log_level="debug"
    )
