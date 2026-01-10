"""
Budget Routes
--------------
Routes for managing monthly category budgets.
"""
import logging
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..models.budget import (
    Budget, BUDGET_CATEGORIES, 
    get_budget_status_for_month, get_all_categories_status
)
from ..config import get_config

logger = logging.getLogger(__name__)

bp = Blueprint('budget', __name__, url_prefix='/budget')


def _get_current_month_year():
    """Get current month and year."""
    today = date.today()
    return today.year, today.month


def _get_month_options():
    """Generate month options for dropdown (current + previous 12 months)."""
    today = date.today()
    options = []
    for i in range(13):
        month = today.month - i
        year = today.year
        while month < 1:
            month += 12
            year -= 1
        options.append({'year': year, 'month': month})
    return options


def _validate_budget_input(form_data: dict) -> tuple:
    """
    Validate budget form input.
    Returns (is_valid, error_message, cleaned_data).
    """
    errors = []
    
    # Category validation
    category = form_data.get('category', '').strip()
    if not category:
        errors.append("Category is required")
    elif category not in BUDGET_CATEGORIES:
        errors.append(f"Invalid category: {category}")
    
    # Amount validation
    try:
        amount_str = form_data.get('monthly_limit', '0').strip()
        monthly_limit = float(amount_str)
        if monthly_limit < 0:
            errors.append("Budget limit cannot be negative")
        elif monthly_limit > 1000000:
            errors.append("Budget limit exceeds maximum allowed (€1,000,000)")
    except ValueError:
        errors.append("Invalid budget limit amount")
        monthly_limit = 0.0
    
    # Year validation
    try:
        year = int(form_data.get('year', date.today().year))
        if year < 2020 or year > 2100:
            errors.append("Year must be between 2020 and 2100")
    except ValueError:
        errors.append("Invalid year")
        year = date.today().year
    
    # Month validation
    try:
        month = int(form_data.get('month', date.today().month))
        if month < 1 or month > 12:
            errors.append("Month must be between 1 and 12")
    except ValueError:
        errors.append("Invalid month")
        month = date.today().month
    
    notes = form_data.get('notes', '').strip()[:500]  # Limit notes length
    
    if errors:
        return False, "; ".join(errors), None
    
    return True, None, {
        'category': category,
        'monthly_limit': monthly_limit,
        'year': year,
        'month': month,
        'notes': notes
    }


@bp.route('/')
@login_required
def index():
    """Display budget overview for current or selected month."""
    # Get selected month from query params or default to current
    try:
        year = int(request.args.get('year', date.today().year))
        month = int(request.args.get('month', date.today().month))
    except ValueError:
        year, month = _get_current_month_year()
    
    # Get budget status for all categories
    category_statuses = get_all_categories_status(year, month)
    
    # Calculate totals
    total_budget = sum(s.monthly_limit for s in category_statuses.values())
    total_spent = sum(s.spent for s in category_statuses.values())
    
    # Get month name
    month_name = date(year, month, 1).strftime('%B %Y')
    
    return render_template(
        'budget/index.html',
        category_statuses=category_statuses,
        year=year,
        month=month,
        month_name=month_name,
        month_options=_get_month_options(),
        total_budget=total_budget,
        total_spent=total_spent,
        categories=BUDGET_CATEGORIES
    )


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new budget."""
    year, month = _get_current_month_year()
    
    # Pre-populate from query params if provided
    try:
        year = int(request.args.get('year', year))
        month = int(request.args.get('month', month))
    except ValueError:
        pass
    
    preset_category = request.args.get('category', '')
    
    if request.method == 'POST':
        is_valid, error, data = _validate_budget_input(request.form)
        
        if not is_valid:
            flash(f'Error: {error}', 'error')
            return render_template(
                'budget/form.html',
                budget=None,
                categories=BUDGET_CATEGORIES,
                year=year,
                month=month,
                month_options=_get_month_options()
            )
        
        # Check if budget already exists for this category/month
        existing = Budget.get_by_category_and_month(
            data['category'], data['year'], data['month']
        )
        if existing:
            flash(f'Budget for {data["category"]} already exists for {data["month"]}/{data["year"]}. Use edit instead.', 'error')
            return redirect(url_for('budget.edit', budget_id=existing.id))
        
        # Create new budget
        budget = Budget(
            category=data['category'],
            monthly_limit=data['monthly_limit'],
            year=data['year'],
            month=data['month'],
            notes=data['notes']
        )
        budget.save()
        
        flash(f'Budget for {data["category"]} added: €{data["monthly_limit"]:.2f}', 'success')
        return redirect(url_for('budget.index', year=data['year'], month=data['month']))
    
    return render_template(
        'budget/form.html',
        budget=None,
        categories=BUDGET_CATEGORIES,
        preset_category=preset_category,
        year=year,
        month=month,
        month_options=_get_month_options()
    )


@bp.route('/edit/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit(budget_id: int):
    """Edit an existing budget."""
    budget = Budget.get_by_id(budget_id)
    if not budget:
        flash('Budget not found.', 'error')
        return redirect(url_for('budget.index'))
    
    if request.method == 'POST':
        is_valid, error, data = _validate_budget_input(request.form)
        
        if not is_valid:
            flash(f'Error: {error}', 'error')
            return render_template(
                'budget/form.html',
                budget=budget,
                categories=BUDGET_CATEGORIES,
                year=budget.year,
                month=budget.month,
                month_options=_get_month_options()
            )
        
        # Check for duplicate if category/month changed
        if (data['category'] != budget.category or 
            data['year'] != budget.year or 
            data['month'] != budget.month):
            existing = Budget.get_by_category_and_month(
                data['category'], data['year'], data['month']
            )
            if existing and existing.id != budget_id:
                flash(f'Budget for {data["category"]} already exists for {data["month"]}/{data["year"]}.', 'error')
                return render_template(
                    'budget/form.html',
                    budget=budget,
                    categories=BUDGET_CATEGORIES,
                    year=budget.year,
                    month=budget.month,
                    month_options=_get_month_options()
                )
        
        # Update budget
        budget.category = data['category']
        budget.monthly_limit = data['monthly_limit']
        budget.year = data['year']
        budget.month = data['month']
        budget.notes = data['notes']
        budget.save()
        
        flash(f'Budget for {data["category"]} updated: €{data["monthly_limit"]:.2f}', 'success')
        return redirect(url_for('budget.index', year=data['year'], month=data['month']))
    
    return render_template(
        'budget/form.html',
        budget=budget,
        categories=BUDGET_CATEGORIES,
        year=budget.year,
        month=budget.month,
        month_options=_get_month_options()
    )


@bp.route('/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete(budget_id: int):
    """Delete a budget."""
    budget = Budget.get_by_id(budget_id)
    if not budget:
        flash('Budget not found.', 'error')
        return redirect(url_for('budget.index'))
    
    year, month = budget.year, budget.month
    category = budget.category
    budget.delete()
    
    flash(f'Budget for {category} deleted.', 'success')
    return redirect(url_for('budget.index', year=year, month=month))


@bp.route('/copy', methods=['POST'])
@login_required
def copy_month():
    """Copy budgets from one month to another."""
    try:
        from_year = int(request.form.get('from_year'))
        from_month = int(request.form.get('from_month'))
        to_year = int(request.form.get('to_year'))
        to_month = int(request.form.get('to_month'))
    except (ValueError, TypeError):
        flash('Invalid month selection.', 'error')
        return redirect(url_for('budget.index'))
    
    if from_year == to_year and from_month == to_month:
        flash('Source and target months are the same.', 'error')
        return redirect(url_for('budget.index'))
    
    copied = Budget.copy_month_budgets(from_year, from_month, to_year, to_month)
    
    if copied > 0:
        flash(f'Copied {copied} budget(s) to {to_month}/{to_year}.', 'success')
    else:
        flash('No budgets to copy or all categories already have budgets.', 'info')
    
    return redirect(url_for('budget.index', year=to_year, month=to_month))


@bp.route('/quick-setup', methods=['GET', 'POST'])
@login_required
def quick_setup():
    """Quick setup page to set budgets for all categories at once."""
    year, month = _get_current_month_year()
    
    try:
        year = int(request.args.get('year', year))
        month = int(request.args.get('month', month))
    except ValueError:
        pass
    
    if request.method == 'POST':
        try:
            year = int(request.form.get('year', year))
            month = int(request.form.get('month', month))
        except ValueError:
            flash('Invalid month/year.', 'error')
            return redirect(url_for('budget.quick_setup'))
        
        created = 0
        updated = 0
        
        for category in BUDGET_CATEGORIES:
            limit_str = request.form.get(f'limit_{category}', '').strip()
            if not limit_str:
                continue
            
            try:
                monthly_limit = float(limit_str)
                if monthly_limit < 0:
                    continue
            except ValueError:
                continue
            
            notes = request.form.get(f'notes_{category}', '').strip()[:500]
            
            existing = Budget.get_by_category_and_month(category, year, month)
            if existing:
                existing.monthly_limit = monthly_limit
                existing.notes = notes
                existing.save()
                updated += 1
            else:
                budget = Budget(
                    category=category,
                    monthly_limit=monthly_limit,
                    year=year,
                    month=month,
                    notes=notes
                )
                budget.save()
                created += 1
        
        if created or updated:
            flash(f'Budgets saved: {created} created, {updated} updated.', 'success')
        else:
            flash('No budgets were saved. Enter at least one budget amount.', 'info')
        
        return redirect(url_for('budget.index', year=year, month=month))
    
    # Get existing budgets for this month
    existing_budgets = {b.category: b for b in Budget.get_all_for_month(year, month)}
    
    return render_template(
        'budget/quick_setup.html',
        categories=BUDGET_CATEGORIES,
        existing_budgets=existing_budgets,
        year=year,
        month=month,
        month_options=_get_month_options(),
        month_name=date(year, month, 1).strftime('%B %Y')
    )
