# Database configuration
# Example: SQLAlchemy setup ?

DB_URL = "sqlite:///./local.db"  # Change for remote DB

class DatabaseConfig:
    def __init__(self, db_url=DB_URL):
        self.db_url = db_url

    def get_db_url(self):
        return self.db_url
    
class DBManager:
    def __init__(self, config: DatabaseConfig):
        self.config = config

    def connect(self):
        pass  # TODO: Implement connection logic

    def disconnect(self):
        pass

    def get_db():
        # TODO: Implement DB session logic
        pass
