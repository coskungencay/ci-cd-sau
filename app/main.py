from fastapi import FastAPI

app = FastAPI(title="CI/CD + DevSecOps Demo API")


@app.get("/")
def read_root():
    return {"message": "CI/CD + DevSecOps Demo API"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": "1.0.0", "environment": "demo"}
