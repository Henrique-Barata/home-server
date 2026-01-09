"""
Stuff Expense Routes
--------------------
CRUD operations for stuff/items with custom categories.
"""
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..models.expense import StuffExpense
from ..models.expense_log import ExpenseLog
from ..models.stuff_type import StuffType
from ..config import get_config


bp = Blueprint('stuff', __name__, url_prefix='/stuff')


@bp.route('/')
@login_required
def index():
    """List all stuff expenses with filtering by type, year, and sorting."""
    config = get_config()
    
    # Get filter, sort, and year parameters
    filter_type = request.args.get('type', '')
    sort_by = request.args.get('sort', 'amount')  # Default sort by amount (highest first)
    current_year = date.today().year
    selected_year = request.args.get('year', current_year, type=int)
    
    # Get expenses (filtered or all)
    if filter_type:
        all_expenses = StuffExpense.get_by_type(filter_type)
    else:
        all_expenses = StuffExpense.get_all()
    
    # Filter by year
    expenses = [e for e in all_expenses if e.expense_date.year == selected_year]
    
    # Get all stuff types for filter dropdown
    stuff_types = StuffType.get_all()
    
    # Sort main expenses list
    if sort_by == 'date':
        expenses.sort(key=lambda x: x.expense_date, reverse=True)
    elif sort_by == 'amount':
        expenses.sort(key=lambda x: x.amount, reverse=True)
    elif sort_by == 'name':
        expenses.sort(key=lambda x: x.name)
    elif sort_by == 'alpha':
        expenses.sort(key=lambda x: x.stuff_type)
    else:  # default to amount
        expenses.sort(key=lambda x: x.amount, reverse=True)
    
    # Group expenses by category
    expenses_by_category = {}
    category_totals = {}
    for expense in expenses:
        category = expense.stuff_type
        if category not in expenses_by_category:
            expenses_by_category[category] = []
            category_totals[category] = 0
        expenses_by_category[category].append(expense)
        category_totals[category] += expense.amount
    
    # Sort expenses within each category (maintain the sort applied above)
    for category in expenses_by_category:
        if sort_by == 'date':
            expenses_by_category[category].sort(key=lambda x: x.expense_date, reverse=True)
        elif sort_by == 'amount':
            expenses_by_category[category].sort(key=lambda x: x.amount, reverse=True)
        elif sort_by == 'name':
            expenses_by_category[category].sort(key=lambda x: x.name)
        elif sort_by == 'alpha':
            expenses_by_category[category].sort(key=lambda x: x.stuff_type)
        else:  # default to amount
            expenses_by_category[category].sort(key=lambda x: x.amount, reverse=True)
    
    # Sort categories by total amount (highest first)
    if sort_by == 'alpha':
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[0])  # Alphabetical
    else:
        sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)  # Amount
    
    # Calculate totals by person
    person_totals = {}
    for person in config.USERS:
        total_amount = sum(e.amount for e in expenses if e.paid_by == person)
        person_totals[person] = total_amount
    
    total = sum(e.amount for e in expenses)
    
    # Get available years from all expenses
    available_years = sorted(set(e.expense_date.year for e in StuffExpense.get_all()), reverse=True)
    if not available_years:
        available_years = [current_year]
    
    return render_template('stuff/index.html',
                          expenses=expenses,
                          expenses_by_category=expenses_by_category,
                          category_totals=category_totals,
                          sorted_categories=sorted_categories,
                          stuff_types=stuff_types,
                          users=config.USERS,
                          person_totals=person_totals,
                          total=total,
                          filter_type=filter_type,
                          sort_by=sort_by,
                          selected_year=selected_year,
                          available_years=available_years)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add new stuff expense."""
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
        # Get or create stuff type
        type_name = request.form.get('stuff_type', '').strip()
        new_type = request.form.get('new_type', '').strip()
        
        if new_type:
            stuff_type = StuffType.get_or_create(new_type)
            type_name = stuff_type.name
        
        name = request.form.get('name', '').strip()
        amount = float(request.form.get('amount', 0))
        paid_by = request.form.get('paid_by', '')
        expense_date = date.fromisoformat(request.form.get('expense_date', str(default_date)))
        individual_only = request.form.get('individual_only') == 'on'
        
        expense = StuffExpense(
            name=name,
            amount=amount,
            paid_by=paid_by,
            expense_date=expense_date,
            stuff_type=type_name,
            individual_only=individual_only
        )
        expense.save()
        
        # Log the action
        ExpenseLog.log_expense(
            action=ExpenseLog.ACTION_ADDED,
            expense_type=f'Stuff - {type_name}',
            paid_by=paid_by,
            amount=amount,
            expense_date=expense_date,
            description=name,
            expense_id=expense.id
        )
        
        flash('Stuff expense added successfully!', 'success')
        return redirect(url_for('stuff.index'))
    
    stuff_types = StuffType.get_all()
    
    return render_template('stuff/form.html',
                          expense=None,
                          stuff_types=stuff_types,
                          users=config.USERS,
                          today=default_date,
                          selected_date=default_date if year and month else None,
                          month_name='January February March April May June July August September October November December'.split()[month - 1] if month else None)


@bp.route('/edit/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit(expense_id):
    """Edit existing stuff expense."""
    config = get_config()
    expense = StuffExpense.get_by_id(expense_id)
    
    if not expense:
        flash('Expense not found.', 'error')
        return redirect(url_for('stuff.index'))
    
    if request.method == 'POST':
        type_name = request.form.get('stuff_type', '').strip()
        new_type = request.form.get('new_type', '').strip()
        
        if new_type:
            stuff_type = StuffType.get_or_create(new_type)
            type_name = stuff_type.name
        
        expense.name = request.form.get('name', '').strip()
        expense.amount = float(request.form.get('amount', 0))
        expense.paid_by = request.form.get('paid_by', '')
        expense.expense_date = date.fromisoformat(request.form.get('expense_date', str(date.today())))
        expense.stuff_type = type_name
        expense.individual_only = request.form.get('individual_only') == 'on'
        expense.save()
        flash('Stuff expense updated successfully!', 'success')
        return redirect(url_for('stuff.index'))
    
    stuff_types = StuffType.get_all()
    
    return render_template('stuff/form.html',
                          expense=expense,
                          stuff_types=stuff_types,
                          users=config.USERS,
                          today=date.today())


@bp.route('/delete/<int:expense_id>', methods=['POST'])
@login_required
def delete(expense_id):
    """Delete stuff expense."""
    expense = StuffExpense.get_by_id(expense_id)
    
    if expense:
        expense.delete()
        flash('Stuff expense deleted.', 'success')
    else:
        flash('Expense not found.', 'error')
    
    return redirect(url_for('stuff.index'))


@bp.route('/types')
@login_required
def manage_types():
    """Manage stuff types/categories."""
    stuff_types = StuffType.get_all()
    return render_template('stuff/types.html', stuff_types=stuff_types)


@bp.route('/types/add', methods=['POST'])
@login_required
def add_type():
    """Add new stuff type."""
    name = request.form.get('name', '').strip()
    
    if name:
        existing = StuffType.get_by_name(name)
        if existing:
            flash('Type already exists.', 'error')
        else:
            new_type = StuffType(name=name)
            new_type.save()
            flash(f'Type "{name}" added successfully!', 'success')
    else:
        flash('Type name cannot be empty.', 'error')
    
    return redirect(url_for('stuff.manage_types'))


@bp.route('/types/delete/<int:type_id>', methods=['POST'])
@login_required
def delete_type(type_id):
    """Delete stuff type."""
    stuff_type = StuffType.get_by_id(type_id)
    
    if stuff_type:
        stuff_type.delete()
        flash(f'Type "{stuff_type.name}" deleted.', 'success')
    else:
        flash('Type not found.', 'error')
    
    return redirect(url_for('stuff.manage_types'))
