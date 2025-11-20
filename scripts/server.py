import os
import uvicorn
from configs.env import env


def start():
    app_module = "app.main:app"
    # 0.0.0.0 is required sa render
    host = "0.0.0.0" if env.environment == "production" else "127.0.0.1"
    port = int(os.getenv("PORT", 8000))

    if env.environment == "production":
        uvicorn.run(
            app_module,
            host=host,  
            port=port, 
            workers=1,
            log_level="info",
        )
    else:
        uvicorn.run(
            app_module,
            host=host,  
            port=port,  
            reload=True,
            log_level="debug",
        )


if __name__ == "__main__":
    start()
