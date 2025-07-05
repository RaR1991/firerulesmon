from app import db
from app.models.rule import Rule, ChangeLog
from app.models.ticket import Ticket
from faker import Faker
import random
import json

def seed_rules(num_rules=200):
    fake = Faker()
    actions = ['Allow', 'Deny']
    protocols = ['TCP', 'UDP', 'ICMP']
    ports = ['80', '443', '22', '21', '23', '53', '8080', '3389', '1433', 'any']
    interfaces = ['Zone A', 'Zone B', 'Zone C', 'DMZ', 'Internal', 'External']
    tags_list = ['web', 'database', 'ssh', 'vpn', 'internal', 'external', 'critical', 'legacy']

    print(f"Seeding {num_rules} firewall rules...")

    for _ in range(num_rules):
        num_tags = random.randint(0, 3)
        selected_tags = random.sample(tags_list, num_tags) if num_tags > 0 else []

        rule = Rule(
            source=fake.ipv4_public() if random.random() < 0.7 else fake.ipv4_private(),
            destination=fake.ipv4_public() if random.random() < 0.7 else fake.ipv4_private(),
            port=random.choice(ports),
            protocol=random.choice(protocols),
            interface=random.choice(interfaces),
            action=random.choice(actions),
            tags=', '.join(selected_tags),
            created_by=fake.user_name(),
            updated_by=fake.user_name(),
            notes=fake.sentence() if random.random() < 0.5 else None,
            is_active=fake.boolean(chance_of_getting_true=80)
        )
        db.session.add(rule)
        db.session.flush() # Flush to get the rule.id

        # Add tickets
        if random.random() < 0.8: # 80% chance to have tickets
            num_tickets = random.randint(1, 3)
            for _ in range(num_tickets):
                ticket = Ticket(ticket_number=fake.bothify(text='TICKET-########'), rule_id=rule.id)
                db.session.add(ticket)
        
        # Add initial change log entry
        log_entry = ChangeLog(rule_id=rule.id, user=rule.created_by, changes=json.dumps({'action': 'create'}))
        db.session.add(log_entry)

    db.session.commit()
    print(f"Successfully seeded {num_rules} firewall rules.")

def seed_users():
    from app.models.user import User, UserRole
    from app import bcrypt

    print("Seeding users...")

    if not User.query.filter_by(username='admin').first():
        hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
        admin_user = User(username='admin', password_hash=hashed_password, role=UserRole.ADMIN)
        db.session.add(admin_user)

    if not User.query.filter_by(username='editor').first():
        hashed_password = bcrypt.generate_password_hash('editor').decode('utf-8')
        editor_user = User(username='editor', password_hash=hashed_password, role=UserRole.EDITOR)
        db.session.add(editor_user)

    if not User.query.filter_by(username='viewer').first():
        hashed_password = bcrypt.generate_password_hash('viewer').decode('utf-8')
        viewer_user = User(username='viewer', password_hash=hashed_password, role=UserRole.VIEWER)
        db.session.add(viewer_user)

    db.session.commit()
    print("Successfully seeded users.")
