from flask import Blueprint, render_template, request, redirect, url_for, flash, abort, Response
from flask_login import login_required, current_user
from app import db
from app.models.rule import Rule, ChangeLog
from app.models.ticket import Ticket
from app.models.user import UserRole
from .forms import RuleForm
from sqlalchemy import or_, and_
from functools import wraps
import json
import csv
import io
from datetime import datetime, timedelta
from sqlalchemy.orm import aliased

rules_bp = Blueprint('rules', __name__, url_prefix='/rules')

def _get_filtered_rules():
    query = Rule.query
    search_term = request.args.get('search', '').strip()
    
    # General search filter
    if search_term:
        # Search across Rule fields
        rule_search_conditions = or_(
            Rule.source.ilike(f'%{search_term}%'),
            Rule.destination.ilike(f'%{search_term}%'),
            Rule.port.ilike(f'%{search_term}%'),
            Rule.protocol.ilike(f'%{search_term}%'),
            Rule.interface.ilike(f'%{search_term}%'),
            Rule.action.ilike(f'%{search_term}%'),
            Rule.tags.ilike(f'%{search_term}%')
        )
        
        # Search across Ticket numbers (if any)
        ticket_search_condition = Rule.tickets.any(Ticket.ticket_number.ilike(f'%{search_term}%'))
        
        # Combine rule fields search and ticket search
        query = query.filter(or_(rule_search_conditions, ticket_search_condition))

    filters = {
        'source': request.args.get('source'),
        'destination': request.args.get('destination'),
        'port': request.args.get('port'),
        'protocol': request.args.get('protocol'),
        'interface': request.args.get('interface'),
        'action': request.args.get('action'),
        'tags': request.args.get('tags'),
        'tickets': request.args.get('tickets') # Changed from ticket_number to tickets
    }

    for key, value in filters.items():
        if value: # Only apply filter if value is not empty
            if key == 'tickets':
                # Filter by ticket numbers (comma-separated)
                ticket_numbers_list = [t.strip() for t in value.split(',') if t.strip()]
                if ticket_numbers_list:
                    # Use Rule.tickets.any() to filter rules that have any of the specified tickets
                    ticket_conditions = [Ticket.ticket_number.ilike(f'%{tn}%') for tn in ticket_numbers_list]
                    query = query.filter(Rule.tickets.any(or_(*ticket_conditions)))
            else:
                query = query.filter(getattr(Rule, key).ilike(f'%{value}%'))

    # Timeframe filtering
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')

    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            query = query.filter(Rule.updated_at >= start_date)
        except ValueError:
            flash('Invalid start date format. Please use YYYY-MM-DD.', 'error')

    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
            # Add one day to end_date to include the entire end day
            query = query.filter(Rule.updated_at <= end_date + timedelta(days=1))
        except ValueError:
            flash('Invalid end date format. Please use YYYY-MM-DD.', 'error')

    # Return the query and the filters dictionary (which now includes 'tickets' key)
    return query, filters

def check_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in role:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@rules_bp.route('/')
@login_required
def rules_explorer():
    query, filters = _get_filtered_rules()

    sort_by = request.args.get('sort_by', 'updated_at')
    sort_order = request.args.get('sort_order', 'desc')

    if hasattr(Rule, sort_by):
        if sort_order == 'asc':
            query = query.order_by(getattr(Rule, sort_by).asc())
            new_sort_order = 'desc'
        else:
            query = query.order_by(getattr(Rule, sort_by).desc())
            new_sort_order = 'asc'

    # Pagination
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    if per_page not in [10, 25, 50, 100]:
        per_page = 10
        
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    rules = pagination.items

    return render_template('rules_explorer.html', 
                           rules=rules, 
                           pagination=pagination,
                           search_query=request.args.get('search', ''), 
                           filters=filters, 
                           new_sort_order=new_sort_order)

@rules_bp.route('/<int:rule_id>')
@login_required
def rule_detail(rule_id):
    rule = Rule.query.get_or_404(rule_id)
    return render_template('rule_detail.html', rule=rule)

@rules_bp.route('/create', methods=['GET', 'POST'])
@login_required
@check_role([UserRole.EDITOR, UserRole.ADMIN])
def create_rule():
    form = RuleForm()
    if form.validate_on_submit():
        new_rule = Rule(
            source=form.source.data,
            destination=form.destination.data,
            port=form.port.data,
            protocol=form.protocol.data,
            interface=form.interface.data,
            action=form.action.data,
            tags=form.tags.data,
            notes=form.notes.data,
            is_active=form.is_active.data,
            created_by=current_user.username,
            updated_by=current_user.username
        )
        db.session.add(new_rule)
        db.session.commit()

        if form.tickets.data:
            ticket_numbers = [t.strip() for t in form.tickets.data.split(',')]
            for ticket_number in ticket_numbers:
                ticket = Ticket(ticket_number=ticket_number, rule_id=new_rule.id)
                db.session.add(ticket)
        
        log_entry = ChangeLog(rule_id=new_rule.id, user=current_user.username, changes=json.dumps({'action': 'create'}))
        db.session.add(log_entry)
        db.session.commit()

        flash('Rule created successfully!', 'success')
        return redirect(url_for('rules.rules_explorer'))
    return render_template('rule_form.html', form=form)

@rules_bp.route('/edit/<int:rule_id>', methods=['GET', 'POST'])
@login_required
@check_role([UserRole.EDITOR, UserRole.ADMIN])
def edit_rule(rule_id):
    rule = Rule.query.get_or_404(rule_id)
    form = RuleForm(obj=rule)
    if form.validate_on_submit():
        changes = {}
        for field in form:
            if field.name not in ['csrf_token', 'submit', 'tickets']:
                if getattr(rule, field.name) != field.data:
                    changes[field.name] = {'old': getattr(rule, field.name), 'new': field.data}
                setattr(rule, field.name, field.data)

        rule.updated_by = current_user.username

        if form.tickets.data is not None:
            new_ticket_numbers = set(t.strip() for t in form.tickets.data.split(',') if t.strip())
            existing_ticket_objects = {t.ticket_number: t for t in rule.tickets}
            existing_ticket_numbers = set(existing_ticket_objects.keys())

            tickets_to_add = new_ticket_numbers - existing_ticket_numbers
            tickets_to_remove = existing_ticket_numbers - new_ticket_numbers

            if tickets_to_add or tickets_to_remove:
                changes['tickets'] = {
                    'old': list(existing_ticket_numbers),
                    'new': list(new_ticket_numbers)
                }

            for ticket_number in tickets_to_add:
                ticket = Ticket(ticket_number=ticket_number, rule_id=rule.id)
                db.session.add(ticket)

            for ticket_number in tickets_to_remove:
                db.session.delete(existing_ticket_objects[ticket_number])

        if changes:
            log_entry = ChangeLog(rule_id=rule.id, user=current_user.username, changes=json.dumps(changes))
            db.session.add(log_entry)

        db.session.commit()
        flash('Rule updated successfully!', 'success')
        return redirect(url_for('rules.rule_detail', rule_id=rule.id))
    
    form.tickets.data = ', '.join([t.ticket_number for t in rule.tickets])
    return render_template('rule_form.html', form=form)

@rules_bp.route('/export/csv')
@login_required
def export_rules_csv():
    query, _ = _get_filtered_rules()
    rules = query.all()

    si = io.StringIO()
    cw = csv.writer(si)

    # CSV Header
    headers = [
        "ID", "Source", "Destination", "Port", "Protocol", "Interface",
        "Action", "Tags", "Tickets", "Notes", "Is Active",
        "Created At", "Created By", "Updated At", "Updated By"
    ]
    cw.writerow(headers)

    # CSV Data
    for rule in rules:
        tickets = ", ".join([t.ticket_number for t in rule.tickets])
        cw.writerow([
            rule.id, rule.source, rule.destination, rule.port, rule.protocol,
            rule.interface, rule.action, rule.tags, tickets, rule.notes,
            "Yes" if rule.is_active else "No",
            rule.created_at.strftime('%Y-%m-%d %H:%M:%S'), rule.created_by,
            rule.updated_at.strftime('%Y-%m-%d %H:%M:%S'), rule.updated_by
        ])

    output = si.getvalue()
    response = Response(output, mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=firewall_rules.csv"
    return response

@rules_bp.route('/export/json')
@login_required
def export_rules_json():
    query, _ = _get_filtered_rules()
    rules = query.all()

    rules_data = []
    for rule in rules:
        rules_data.append({
            "id": rule.id,
            "source": rule.source,
            "destination": rule.destination,
            "port": rule.port,
            "protocol": rule.protocol,
            "interface": rule.interface,
            "action": rule.action,
            "tags": rule.tags,
            "tickets": [t.ticket_number for t in rule.tickets],
            "notes": rule.notes,
            "is_active": rule.is_active,
            "created_at": rule.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "created_by": rule.created_by,
            "updated_at": rule.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
            "updated_by": rule.updated_by
        })

    response = Response(json.dumps(rules_data, indent=4), mimetype="application/json")
    response.headers["Content-Disposition"] = "attachment; filename=firewall_rules.json"
    return response
