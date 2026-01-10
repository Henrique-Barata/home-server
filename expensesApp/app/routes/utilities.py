"""
Utilities Expense Routes
------------------------
CRUD operations for utility expenses (Electricity, Gas, Water).
Internet is shown but managed in Fixed Expenses.
"""
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..models.expense import UtilityExpense
from ..models.expense_log import ExpenseLog
from ..models.fixed_expense import FixedExpense
from ..config import get_config


bp = Blueprint('utilities', __name__, url_prefix='/utilities')


@bp.route('/')
@login_required
def index():
    """List all utility expenses with year filtering and breakdown by type."""
    config = get_config()
    
    # Get selected year or default to current year
    current_year = date.today().year
    selected_year = request.args.get('year', current_year, type=int)
    
    # Get all expenses and filter by year
    all_expenses = UtilityExpense.get_all()
    expenses = [e for e in all_expenses if e.expense_date.year == selected_year]
    
    # Get current Internet value from fixed expenses
    internet_current = FixedExpense.get_current_by_type('Internet')
    internet_amount = internet_current.amount if internet_current else 0.0
    
    # Calculate totals by type
    type_totals = {}
    for utility_type in config.UTILITY_TYPES:
        if utility_type == 'Internet':
            type_totals[utility_type] = internet_amount
        else:
            type_totals[utility_type] = sum(e.amount for e in expenses if e.utility_type == utility_type)
    
    total = sum(type_totals.values())
    
    # Get available years from expenses
    available_years = sorted(set(e.expense_date.year for e in all_expenses), reverse=True)
    if not available_years:
        available_years = [current_year]
    
    return render_template('utilities/index.html',
                          expenses=expenses,
                          utility_types=[t for t in config.UTILITY_TYPES if t != 'Internet'],
                          users=config.USERS,
                          type_totals=type_totals,
                          internet_amount=internet_amount,
                          total=total,
                          selected_year=selected_year,
                          available_years=available_years)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new utility expense."""
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
        utility_type = request.form.get('utility_type', '')
        # Utility expenses are always shared, individual_only not allowed
        individual_only = False
        
        expense = UtilityExpense(
            name=name,
            amount=amount,
            paid_by=paid_by,
            expense_date=expense_date,
            utility_type=utility_type,
            individual_only=individual_only
        )
        expense.save()
        
        # Log the action
        ExpenseLog.log_expense(
            action=ExpenseLog.ACTION_ADDED,
            expense_type=f'Utility - {utility_type}',
            paid_by=paid_by,
            amount=amount,
            expense_date=expense_date,
            description=name,
            expense_id=expense.id
        )
        
        flash('Utility expense added successfully!', 'success')
        return redirect(url_for('utilities.index'))
    
    # Exclude Internet from add form - it's managed in Fixed Expenses
    utility_types = [t for t in config.UTILITY_TYPES if t != 'Internet']
    
    return render_template('utilities/form.html',
                          expense=None,
                          utility_types=utility_types,
                          users=config.USERS,
                          today=default_date,
                          selected_date=default_date if year and month else None,
                          month_name='January February March April May June July August September October November December'.split()[month - 1] if month else None)


@bp.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit(expense_id):
    """Edit existing utility expense."""
    config = get_config()
    expense = UtilityExpense.get_by_id(expense_id)
    
    if not expense:
        flash('Expense not found.', 'error')
        return redirect(url_for('utilities.index'))
    
    if request.method == 'POST':
        expense.name = request.form.get('name', '').strip()
        expense.amount = float(request.form.get('amount', 0))
        expense.paid_by = request.form.get('paid_by', '')
        expense.expense_date = date.fromisoformat(request.form.get('expense_date', str(date.today())))
        expense.utility_type = request.form.get('utility_type', '')
        # Utility expenses are always shared, individual_only not allowed
        expense.individual_only = False
        expense.save()
        flash('Utility expense updated successfully!', 'success')
        return redirect(url_for('utilities.index'))
    
    utility_types = [t for t in config.UTILITY_TYPES if t != 'Internet']
    
    return render_template('utilities/form.html',
                          expense=expense,
                          utility_types=utility_types,
                          users=config.USERS,
                          today=date.today())


@bp.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete(expense_id):
    """Delete utility expense."""
    expense = UtilityExpense.get_by_id(expense_id)
    
    if expense:
        expense.delete()
        flash('Utility expense deleted.', 'success')
    else:
        flash('Expense not found.', 'error')
    
    return redirect(url_for('utilities.index'))
