from fastapi import FastAPI

def create_app():

    app = FastAPI()

    app.state.UPLOAD_FOLDER = "uploads"

    from app.routes import router
    app.include_router(router)

    return app


app = create_app()