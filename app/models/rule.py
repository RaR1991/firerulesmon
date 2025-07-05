from datetime import datetime
from app import db
from sqlalchemy.dialects.sqlite import JSON

# Define a simple change log structure
class ChangeLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.Column(db.String(120))
    changes = db.Column(JSON) # Store changes as a JSON object

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    port = db.Column(db.String(120), nullable=True)
    protocol = db.Column(db.String(50), nullable=True)
    interface = db.Column(db.String(120), nullable=True)
    action = db.Column(db.String(50), nullable=False)
    tags = db.Column(db.String(255), nullable=True)  # Comma-separated tags
    tickets = db.relationship('Ticket', backref='rule', lazy=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.String(120), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.String(120), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    change_logs = db.relationship('ChangeLog', backref='rule', lazy=True)

    def __repr__(self):
        return f"<Rule {self.id}: {self.source} -> {self.destination} ({self.action})>"
