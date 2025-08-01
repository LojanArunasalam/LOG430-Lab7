from repository import UserRepository
class UserService: 
    def __init__(self, session):
        self.session = session
        self.user_repository = UserRepository(session)

    def get_user_by_id(self, id):
        user = self.user_repository.get_by_id(id)
        return user
    
    def get_all_users(self):
        users = self.user_repository.get_all_users()
        return users

    def get_user_by_email(self, email):
        user = self.user_repository.get_user_by_email(email)
        return user

    def add_user(self, user):
        # Check if email already exists
        existing_user = self.user_repository.get_user_by_email(user.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        self.user_repository.add_user(user)
        return user
    
    def update_user(self, user):
        updated_user = self.user_repository.update_user(user)
        return updated_user
    
    def delete_user(self, user_id):
        deleted_user = self.user_repository.delete_user(user_id)
        return deleted_user