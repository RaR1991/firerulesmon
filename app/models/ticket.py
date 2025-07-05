from app import db

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ticket_number = db.Column(db.String(120), unique=True, nullable=False)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=False)

    def __repr__(self):
        return f"<Ticket {self.ticket_number}>"
