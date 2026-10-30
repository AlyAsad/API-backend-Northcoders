from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.responses import JSONResponse

from routes.events import router as events_router
from routes.auth_api import router as auth_router
from routes.user import router as user_router

app = FastAPI(title="Events booking API", debug=True)
app.include_router(events_router)
app.include_router(auth_router)
app.include_router(user_router)


#overriding 422 to 400 since it makes more sense
@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": exc.errors()[0]})

@app.exception_handler(HTTPException)
def handle_http_exception(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"error": f"{exc.status_code}: {exc.detail}"})