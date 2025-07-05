from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Optional

class RuleForm(FlaskForm):
    source = StringField('Source', validators=[DataRequired()])
    destination = StringField('Destination', validators=[DataRequired()])
    port = StringField('Port')
    protocol = StringField('Protocol')
    interface = StringField('Interface')
    action = SelectField('Action', choices=[('allow', 'Allow'), ('deny', 'Deny'), ('reject', 'Reject')], validators=[DataRequired()])
    tags = StringField('Tags')
    tickets = StringField('Tickets (comma-separated)')
    notes = TextAreaField('Notes')
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Save Rule')
