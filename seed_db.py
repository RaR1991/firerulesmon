from app import create_app, db
from app.models.rule import Rule, ChangeLog
from app.models.ticket import Ticket
from app.models.user import User, UserRole
from app import bcrypt
from app.utils.seed import seed_rules, seed_users

# Create the Flask app context
app = create_app()
app.app_context().push()

# Seed the database
seed_rules(num_rules=200)
seed_users()

print("Database seeding complete.")
