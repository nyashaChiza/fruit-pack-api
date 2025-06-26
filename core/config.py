from decouple import config

class Settings(object):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    SECRET_KEY: str = config('SECRET_KEY', 'jgcxkvhfxtrzrzrztcxryxycvjvj')
    STRIPE_SECRET_KEY: str = config("STRIPE_SECRET_KEY", "dljskbfhsjfsn")
    STRIPE_WEBHOOK_SECRET: str = config("STRIPE_WEBHOOK_SECRET","ljhdld")

    class Config:
        env_file = ".env"

settings = Settings()




