"""
Fixed Expense Routes
--------------------
Manage fixed expenses (Rent, Internet) with effective date tracking.
"""
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..models.fixed_expense import FixedExpense, FixedExpenseType
from ..config import get_config


bp = Blueprint('fixed', __name__, url_prefix='/fixed')

# Protected types that cannot be deleted
PROTECTED_TYPES = ['Rent', 'Internet']


@bp.route('/')
@login_required
def index():
    """List all fixed expenses with history."""
    # Get all expense types (default + custom)
    all_types = FixedExpenseType.get_all_types()
    
    # Get current values and history for each type
    expense_data = {}
    for expense_type in all_types:
        current = FixedExpense.get_current_by_type(expense_type)
        history = FixedExpense.get_by_type(expense_type)
        expense_data[expense_type] = {
            'current': current,
            'current_amount': current.amount if current else 0.0,
            'history': history
        }
    
    return render_template('fixed/index.html',
                          expense_data=expense_data,
                          expense_types=all_types,
                          protected_types=PROTECTED_TYPES)


@bp.route('/update/<expense_type>', methods=['GET', 'POST'])
@login_required
def update(expense_type):
    """Update a fixed expense value with new effective date."""
    config = get_config()
    all_types = FixedExpenseType.get_all_types()
    
    if expense_type not in all_types:
        flash('Invalid expense type.', 'error')
        return redirect(url_for('fixed.index'))
    
    current = FixedExpense.get_current_by_type(expense_type)
    
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        effective_date = date.fromisoformat(request.form.get('effective_date', str(date.today())))
        paid_by = request.form.get('paid_by', config.USERS[0])
        
        # If effective date is not the first of a month, move it to the 1st of that month
        # This ensures fixed expenses apply from the first of each month
        if effective_date.day != 1:
            effective_date = effective_date.replace(day=1)
        
        # Create new record with new effective date
        new_expense = FixedExpense(
            expense_type=expense_type,
            amount=amount,
            effective_date=effective_date,
            paid_by=paid_by
        )
        new_expense.save()
        
        flash(f'{expense_type} updated! New value effective from {effective_date.strftime("%B %d, %Y")}. Paid by {paid_by}.', 'success')
        return redirect(url_for('fixed.index'))
    
    # Default effective date is first of next month
    today = date.today()
    if today.month == 12:
        default_effective = date(today.year + 1, 1, 1)
    else:
        default_effective = date(today.year, today.month + 1, 1)
    
    return render_template('fixed/form.html',
                          expense_type=expense_type,
                          current=current,
                          users=config.USERS,
                          default_effective=default_effective)


@bp.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete(expense_id):
    """Delete a fixed expense history record."""
    expense = FixedExpense.get_by_id(expense_id)
    
    if expense:
        expense.delete()
        flash('Fixed expense record deleted.', 'success')
    else:
        flash('Record not found.', 'error')
    
    return redirect(url_for('fixed.index'))


@bp.route('/toggle-paid/<int:fixed_expense_id>/<int:year>/<int:month>', methods=['POST'])
@login_required
def toggle_paid(fixed_expense_id, year, month):
    """Toggle paid status for a fixed expense in a specific month."""
    config = get_config()
    
    # Get current status
    status = FixedExpense.get_payment_status(fixed_expense_id, year, month)
    
    if status['is_paid']:
        # Mark as unpaid
        FixedExpense.mark_unpaid(fixed_expense_id, year, month)
        flash('Marked as unpaid.', 'success')
    else:
        # Mark as paid - need to get who paid it
        paid_by = request.form.get('paid_by', config.USERS[0])
        FixedExpense.mark_paid(fixed_expense_id, year, month, paid_by)
        flash(f'Marked as paid by {paid_by}.', 'success')
    
    # Redirect back to the month detail page
    return redirect(url_for('dashboard.month_detail', year=year, month=month))


@bp.route('/add-type', methods=['GET', 'POST'])
@login_required
def add_type():
    """Add a new fixed expense type."""
    if request.method == 'POST':
        type_name = request.form.get('type_name', '').strip()
        
        if not type_name:
            flash('Please enter a name for the expense type.', 'error')
            return redirect(url_for('fixed.add_type'))
        
        # Check if type already exists
        existing_types = FixedExpenseType.get_all_types()
        if type_name in existing_types:
            flash(f'"{type_name}" already exists.', 'error')
            return redirect(url_for('fixed.add_type'))
        
        # Save new type
        new_type = FixedExpenseType(name=type_name)
        new_type.save()
        
        flash(f'Fixed expense type "{type_name}" added successfully!', 'success')
        return redirect(url_for('fixed.index'))
    
    return render_template('fixed/add_type.html')


@bp.route('/delete-type/<expense_type>', methods=['POST'])
@login_required
def delete_type(expense_type):
    """Delete a custom fixed expense type and all its records."""
    if expense_type in PROTECTED_TYPES:
        flash(f'"{expense_type}" is a protected type and cannot be deleted.', 'error')
        return redirect(url_for('fixed.index'))
    
    # Delete all expenses of this type
    FixedExpense.delete_by_type(expense_type)
    
    # Delete the type itself
    FixedExpenseType.delete_by_name(expense_type)
    
    flash(f'Fixed expense type "{expense_type}" deleted.', 'success')
    return redirect(url_for('fixed.index'))

@bp.route('/payments/<int:expense_id>')
@login_required
def payments(expense_id):
    """Show payment history for a fixed expense across all months."""
    expense = FixedExpense.get_by_id(expense_id)
    if not expense:
        flash('Fixed expense not found.', 'error')
        return redirect(url_for('fixed.index'))
    
    # Get all payment records for this expense
    payment_records = FixedExpense.get_all_payments_for_expense(expense_id)
    
    # Current expense info
    current = FixedExpense.get_current_by_type(expense.expense_type)
    
    return render_template('fixed/payments.html',
                          expense_id=expense_id,
                          expense_type=expense.expense_type,
                          current_amount=current.amount if current else 0.0,
                          payment_records=payment_records)