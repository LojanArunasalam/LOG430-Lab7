import logging
from models.user_model import User

logging.basicConfig(level=logging.DEBUG, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging = logging.getLogger(__name__)

class UserRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, id):
        logging.debug(f"Fetching user with id {id}")
        user = self.session.query(User).filter_by(id=id).first()
        if not user:
            logging.warning(f"No user found with id {id}")
            return None
        logging.debug(f"Fetched successfully user with id {id}")
        return user
    
    def get_all_users(self):
        logging.debug("Fetching all users")
        users = self.session.query(User).all()
        if not users:
            logging.warning("No users found")
            return None
        logging.debug(f"Fetched successfully {len(users)} users")
        return users
    
    def get_user_by_email(self, email):
        logging.debug(f"Fetching user with email {email}")
        user = self.session.query(User).filter_by(email=email).first()
        if not user:
            logging.warning(f"No user found with email {email}")
            return None
        logging.debug(f"Fetched successfully user with email {email}")
        return user
    
    def add_user(self, user):
        logging.debug(f"Adding user {user.name}")
        self.session.add(user)
        self.session.commit()
        logging.debug(f"User {user.name} added successfully")
        
    def update_user(self, user):
        logging.debug(f"Updating user {user.id}")
        existing_user = self.get_by_id(user.id)
        if not existing_user:
            logging.error(f"User with id {user.id} does not exist")
            return None
        existing_user.name = user.name
        existing_user.email = user.email
        existing_user.phone = user.phone
        existing_user.address = user.address
        self.session.commit()
        logging.debug(f"User {user.id} updated successfully")
        return existing_user
        
    def delete_user(self, user_id):
        logging.debug(f"Deleting user with id {user_id}")
        user = self.get_by_id(user_id)
        if not user:
            logging.error(f"User with id {user_id} does not exist")
            return None
        self.session.delete(user)
        self.session.commit()
        logging.debug(f"User with id {user_id} deleted successfully")
        return user