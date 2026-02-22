from fastapi import FastAPI

from conversational_agent.api.routes import router
from conversational_agent.core.config import get_settings
from conversational_agent.core.logging import configure_logging

settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
app.include_router(router)
