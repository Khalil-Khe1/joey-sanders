# Startup
from fastapi import FastAPI

app = FastAPI()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

# Routes
from app.api.v1 import v1_router
app.include_router(v1_router, prefix="/api/v1")

# Cron
from fastapi_utilities import repeat_every

@app.on_event('startup')
@repeat_every(seconds=1)
async def print_hello():
    # Cron should ping the corresponding endpoint
    #print("hello")
    return

@app.on_event('startup')
@repeat_every(seconds=300)
async def ping_alive():
    print('Alive')

@app.get("/")
def root():
    return {"message": "Minimal test"}