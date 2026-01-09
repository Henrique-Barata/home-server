"""
Expense Log Routes
------------------
View and manage the expense audit trail.
"""
from flask import Blueprint, render_template
from flask_login import login_required

from ..models.expense_log import ExpenseLog

bp = Blueprint('log', __name__, url_prefix='/log')


@bp.route('/')
@login_required
def index():
    """Display recent expense activity log."""
    # Get recent 100 log entries
    logs = ExpenseLog.get_recent(limit=100)
    
    return render_template('log/index.html', logs=logs)
