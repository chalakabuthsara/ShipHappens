import uvicorn


def main() -> None:
    """Run the FastAPI app in development mode with auto-reload."""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8080,
        reload=True,
    )
