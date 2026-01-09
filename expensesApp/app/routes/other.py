"""
Other Expense Routes
--------------------
CRUD operations for miscellaneous expenses.
"""
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..models.expense import OtherExpense
from ..models.expense_log import ExpenseLog
from ..config import get_config


bp = Blueprint('other', __name__, url_prefix='/other')


@bp.route('/')
@login_required
def index():
    """List all other expenses with year filtering."""
    config = get_config()
    
    # Get selected year or default to current year
    current_year = date.today().year
    selected_year = request.args.get('year', current_year, type=int)
    
    # Get all expenses and filter by year
    all_expenses = OtherExpense.get_all()
    expenses = [e for e in all_expenses if e.expense_date.year == selected_year]
    
    # Calculate totals by person (for selected year)
    person_totals = {}
    for person in config.USERS:
        total = sum(e.amount for e in expenses if e.paid_by == person)
        person_totals[person] = total
    
    total = sum(person_totals.values())
    
    # Get available years from expenses
    available_years = sorted(set(e.expense_date.year for e in all_expenses), reverse=True)
    if not available_years:
        available_years = [current_year]
    
    return render_template('other/index.html',
                          expenses=expenses,
                          users=config.USERS,
                          person_totals=person_totals,
                          total=total,
                          selected_year=selected_year,
                          available_years=available_years)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new other expense."""
    config = get_config()
    
    # Get year and month from query parameters if available
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    
    # Calculate default date (first day of month or today)
    if year and month:
        default_date = date(year, month, 1)
    else:
        default_date = date.today()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        amount = float(request.form.get('amount', 0))
        paid_by = request.form.get('paid_by', '')
        expense_date = date.fromisoformat(request.form.get('expense_date', str(default_date)))
        individual_only = request.form.get('individual_only') == 'on'
        
        expense = OtherExpense(
            name=name,
            amount=amount,
            paid_by=paid_by,
            expense_date=expense_date,
            individual_only=individual_only
        )
        expense.save()
        
        # Log the action
        ExpenseLog.log_expense(
            action=ExpenseLog.ACTION_ADDED,
            expense_type='Other',
            paid_by=paid_by,
            amount=amount,
            expense_date=expense_date,
            description=name,
            expense_id=expense.id
        )
        
        flash('Other expense added successfully!', 'success')
        return redirect(url_for('other.index'))
    
    return render_template('other/form.html',
                          expense=None,
                          users=config.USERS,
                          today=default_date,
                          selected_date=default_date if year and month else None,
                          month_name='January February March April May June July August September October November December'.split()[month - 1] if month else None)


@bp.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit(expense_id):
    """Edit existing other expense."""
    config = get_config()
    expense = OtherExpense.get_by_id(expense_id)
    
    if not expense:
        flash('Expense not found.', 'error')
        return redirect(url_for('other.index'))
    
    if request.method == 'POST':
        expense.name = request.form.get('name', '').strip()
        expense.amount = float(request.form.get('amount', 0))
        expense.paid_by = request.form.get('paid_by', '')
        expense.expense_date = date.fromisoformat(request.form.get('expense_date', str(date.today())))
        expense.individual_only = request.form.get('individual_only') == 'on'
        expense.save()
        flash('Other expense updated successfully!', 'success')
        return redirect(url_for('other.index'))
    
    return render_template('other/form.html',
                          expense=expense,
                          users=config.USERS,
                          today=date.today())


@bp.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete(expense_id):
    """Delete other expense."""
    expense = OtherExpense.get_by_id(expense_id)
    
    if expense:
        expense.delete()
        flash('Other expense deleted.', 'success')
    else:
        flash('Expense not found.', 'error')
    
    return redirect(url_for('other.index'))
