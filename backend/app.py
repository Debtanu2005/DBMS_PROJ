from fastapi import FastAPI
import uvicorn
from router import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()  
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


# ================= RUN SERVER =================
if __name__ == "__main__":
    # "app:app" tells uvicorn: look in app.py for the variable named app
    uvicorn.run(
        "app:app",  # <--- CHANGED THIS LINE
        host="0.0.0.0",
        port=8000,
        reload=True
    )