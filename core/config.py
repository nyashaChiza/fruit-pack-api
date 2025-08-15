from decouple import config

class Settings(object):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    SECRET_KEY: str = config('SECRET_KEY', 'jgcxkvhfxtrzrzrztcxryxycvjvj')
    PAYSTACK_SECRET_KEY: str = config("PAYSTACK_SECRET_KEY", "sljksbbsb")
    PAYSTACK_ENDPOINT: str = config("PAYSTACK_ENDPOINT","https://api.paystack.co/transaction/initialize")
    PAYSTACK_VERIFY: str = config("PAYSTACK_VERIFY","https://api.paystack.co/transaction/verify/")


    class Config:
        env_file = ".env"

settings = Settings()




