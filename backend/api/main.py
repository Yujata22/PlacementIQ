from fastapi import FastAPI

app = FastAPI(
    title="PlacementIQ API",
    description="Inbound container placement and service-level optimization platform.",
    version="0.1.0",
)

@app.get("/health")
def health():
    return {"status": "ok"}
