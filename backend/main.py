from fastapi import FastAPI

app = FastAPI(title="Ticketing System API")


@app.get("/")
def read_root():
    return {"message": "Ticketing API is running"}
