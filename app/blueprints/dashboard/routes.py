from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from app.models.rule import Rule
from app.models.ticket import Ticket
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    total_rules = db.session.query(Rule).count()
    active_rules = db.session.query(Rule).filter_by(is_active=True).count()
    disabled_rules = db.session.query(Rule).filter_by(is_active=False).count()

    # Rules modified this week
    one_week_ago = datetime.utcnow() - timedelta(weeks=1)
    rules_modified_this_week = db.session.query(Rule).filter(Rule.updated_at >= one_week_ago).count()

    # Rules without tickets
    rules_without_tickets = db.session.query(Rule).outerjoin(Ticket).filter(Ticket.id == None).count()

    # Rule insights by Action
    action_counts = db.session.query(Rule.action, func.count(Rule.id)).group_by(Rule.action).all()
    total_action_rules = sum([count for action, count in action_counts])
    rule_action_data = {action: round((count / total_action_rules) * 100) for action, count in action_counts} if total_action_rules > 0 else {}

    # Rule insights by Interface/Zone
    interface_counts = db.session.query(Rule.interface, func.count(Rule.id)).group_by(Rule.interface).all()
    total_interface_rules = sum([count for interface, count in interface_counts])
    rule_zone_data = {interface: round((count / total_interface_rules) * 100) for interface, count in interface_counts} if total_interface_rules > 0 else {}

    # Rule insights by Protocol/Port (simplified for now, can be expanded)
    protocol_port_counts = db.session.query(Rule.protocol, Rule.port, func.count(Rule.id)).group_by(Rule.protocol, Rule.port).all()
    total_protocol_port_rules = sum([count for proto, port, count in protocol_port_counts])
    rule_protocol_data = {}
    if total_protocol_port_rules > 0:
        for proto, port, count in protocol_port_counts:
            key = f"{proto}/{port}" if port else proto
            rule_protocol_data[key] = round((count / total_protocol_port_rules) * 100)

    # Rules modified today
    today = datetime.utcnow().date()
    rules_modified_today = db.session.query(Rule).filter(func.date(Rule.updated_at) == today).count()

    # Top 5 Most Modified Rules (based on recent updates)
    top_modified_rules = db.session.query(Rule).order_by(Rule.updated_at.desc()).limit(5).all()

    return render_template('dashboard.html', 
                           total_rules=total_rules,
                           active_rules=active_rules,
                           disabled_rules=disabled_rules,
                           rules_modified_this_week=rules_modified_this_week,
                           rules_without_tickets=rules_without_tickets,
                           rule_action_data=rule_action_data,
                           rule_zone_data=rule_zone_data,
                           rule_protocol_data=rule_protocol_data,
                           rules_modified_today=rules_modified_today,
                           top_modified_rules=top_modified_rules)
