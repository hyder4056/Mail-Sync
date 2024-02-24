import uvicorn
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI

# from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.cors import CORSMiddleware
from src.common.misc_routes import router as misc_router
from src.constants import VERSION
from src.env_config import LOG_LEVEL, RUNTIME_ENVIRONMENT, SERVER_HOST, SERVER_PORT
from src.example_module.containers import Container
from src.example_module.routes import router as example_router
from src.logger.asgi_access_log import AsgiAccessLogMiddleware


def init_routers(fastapi_app: FastAPI):
    # add your routers here
    fastapi_app.include_router(misc_router)
    fastapi_app.include_router(example_router)


def init_openapi(fastapi_app: FastAPI):
    fastapi_app.title = "DEX FastAPI boilerplate"
    fastapi_app.version = VERSION
    fastapi_app.summary = "Boilerplate for FastAPI"
    fastapi_app.description = (
        "<a href='https://github.com/optimizely/dex-fastapi-boilerplate' target='_blank'>Github repository</a>"
    )


def create_app():
    # new_app = FastAPI(dependencies=[Depends(get_global_dependency)])  # if you want to use a global dependency
    new_app = FastAPI(
        root_path="" if RUNTIME_ENVIRONMENT == "local" else "/dex-fastapi-boilerplate"
    )  # assuming it is deployed in /dex-fastapi-boilerplate

    # add your middlewares here. Some Sample middlewares are given below

    # redirect all http requests to https. Uncomment if necessary
    # new_app.add_middleware(HTTPSRedirectMiddleware)

    # Sample middleware to add a header to all responses
    # @new_app.middleware("http")
    # async def add_x_opti_header(request, call_next):
    #     response = await call_next(request)
    #     response.headers["X-Process-Time"] = "0.0"
    #     return response

    # add your CORS settings here. This is a sample CORS middleware. Update this as per your needs.
    origins = [
        "http://localhost:3000",
    ]

    new_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    new_app.add_middleware(AsgiAccessLogMiddleware)
    new_app.add_middleware(CorrelationIdMiddleware, validator=bool)
    init_routers(new_app)
    init_openapi(new_app)
    container = Container()
    new_app.container = container
    return new_app


app = create_app()


if __name__ == "__main__":
    uvicorn_log_config = uvicorn.config.LOGGING_CONFIG
    for logger_name, logger_config in uvicorn_log_config["loggers"].items():
        logger_config.pop("handlers", [])
        logger_config["propagate"] = logger_name != "uvicorn.access"
    uvicorn.run(
        "main:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        reload=(RUNTIME_ENVIRONMENT == "local"),
        log_level=LOG_LEVEL.lower(),
        log_config=uvicorn_log_config,
    )
