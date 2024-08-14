import os

from pydantic import BaseSettings, Field

# fields validation
# base settings as class for defining configuration and field for defining fields with their validations
class Settings(BaseSettings):
    """
    Base Settings Class for Configuration Definition
    
    This class is used to define configuration settings for the application.
    """
    #The url is already defined in the docker-compose.yml
    db_url: str = Field(..., env='DATABASE_URL')


settings = Settings()
