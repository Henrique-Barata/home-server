"""
Travel Routes
--------------
Routes for managing travels and travel expenses.
Provides full CRUD for travel trips and their expenses.
"""
import logging
from datetime import date, datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..models.travel import Travel, TravelExpense, TRAVEL_EXPENSE_CATEGORIES
from ..models.expense_log import ExpenseLog
from ..config import get_config

logger = logging.getLogger(__name__)

bp = Blueprint('travel', __name__, url_prefix='/travel')


def _validate_travel_input(form_data: dict) -> tuple[bool, str]:
    """
    Validate travel form input.
    
    Args:
        form_data: Dictionary of form data
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    name = form_data.get('name', '').strip()
    if not name:
        return False, "Travel name is required"
    if len(name) > 200:
        return False, "Travel name must be 200 characters or less"
    
    try:
        start_date = datetime.strptime(form_data.get('start_date', ''), '%Y-%m-%d').date()
        end_date = datetime.strptime(form_data.get('end_date', ''), '%Y-%m-%d').date()
        
        if end_date < start_date:
            return False, "End date cannot be before start date"
    except ValueError:
        return False, "Invalid date format"
    
    return True, ""


def _validate_expense_input(form_data: dict, users: list) -> tuple[bool, str]:
    """
    Validate travel expense form input.
    
    Args:
        form_data: Dictionary of form data
        users: List of valid users
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    name = form_data.get('name', '').strip()
    if not name:
        return False, "Description is required"
    if len(name) > 200:
        return False, "Description must be 200 characters or less"
    
    try:
        amount = float(form_data.get('amount', 0))
        if amount <= 0:
            return False, "Amount must be greater than 0"
        if amount > 1000000:
            return False, "Amount exceeds maximum allowed value"
    except (ValueError, TypeError):
        return False, "Invalid amount value"
    
    paid_by = form_data.get('paid_by', '').strip()
    if not paid_by:
        return False, "Who paid is required"
    if paid_by not in users:
        return False, f"Invalid person: {paid_by}"
    
    category = form_data.get('category', '').strip()
    if not category:
        return False, "Category is required"
    if category not in TRAVEL_EXPENSE_CATEGORIES:
        return False, f"Invalid category: {category}"
    
    try:
        datetime.strptime(form_data.get('expense_date', ''), '%Y-%m-%d')
    except ValueError:
        return False, "Invalid date format"
    
    return True, ""


# ============== Travel Routes ==============

@bp.route('/')
@login_required
def index():
    """List all travels."""
    logger.debug("Listing all travels")
    config = get_config()
    
    try:
        # Get selected year or default to current year
        current_year = date.today().year
        selected_year = request.args.get('year', current_year, type=int)
        
        travels = Travel.get_by_year(selected_year)
        
        # Get totals for each travel
        travel_data = []
        for travel in travels:
            travel_data.append({
                'travel': travel,
                'total': travel.get_total(),
                'category_totals': travel.get_totals_by_category(),
                'person_totals': travel.get_totals_by_person()
            })
        
        # Get available years
        all_travels = Travel.get_all()
        available_years = sorted(set(
            t.start_date.year for t in all_travels if t.start_date
        ), reverse=True)
        if not available_years:
            available_years = [current_year]
        
        # Calculate yearly total
        yearly_total = sum(td['total'] for td in travel_data)
        
        logger.info(f"Retrieved {len(travels)} travels for year {selected_year}")
        
        return render_template('travel/index.html',
                              travel_data=travel_data,
                              categories=TRAVEL_EXPENSE_CATEGORIES,
                              selected_year=selected_year,
                              available_years=available_years,
                              yearly_total=yearly_total,
                              users=config.USERS)
    except Exception as e:
        logger.error(f"Error listing travels: {e}", exc_info=True)
        flash("❌ Error loading travels", 'error')
        return redirect(url_for('dashboard.index'))


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Add a new travel."""
    if request.method == 'POST':
        is_valid, error_msg = _validate_travel_input(request.form)
        if not is_valid:
            logger.warning(f"Travel validation failed: {error_msg}")
            flash(f"❌ {error_msg}", 'error')
            return render_template('travel/travel_form.html', travel=None)
        
        try:
            travel = Travel(
                name=request.form.get('name', '').strip(),
                start_date=datetime.strptime(
                    request.form.get('start_date'),
                    '%Y-%m-%d'
                ).date(),
                end_date=datetime.strptime(
                    request.form.get('end_date'),
                    '%Y-%m-%d'
                ).date(),
                notes=request.form.get('notes', '').strip()
            )
            
            travel_id = travel.save()
            
            # Log the action
            ExpenseLog.log_expense(
                action='added',
                expense_type='travel',
                paid_by='',
                amount=0,
                expense_date=travel.start_date,
                description=f"Travel created: {travel.name}",
                expense_id=travel_id
            )
            
            logger.info(f"Added travel {travel_id}: {travel.name}")
            flash(f"✅ Travel '{travel.name}' created successfully!", 'success')
            return redirect(url_for('travel.detail', travel_id=travel_id))
            
        except Exception as e:
            logger.error(f"Error adding travel: {e}", exc_info=True)
            flash(f"❌ Error creating travel: {str(e)}", 'error')
    
    return render_template('travel/travel_form.html',
                          travel=None,
                          today=date.today())


@bp.route('/<int:travel_id>')
@login_required
def detail(travel_id):
    """View travel details with all expenses."""
    config = get_config()
    
    travel = Travel.get_by_id(travel_id)
    if not travel:
        logger.warning(f"Travel {travel_id} not found")
        flash("❌ Travel not found", 'error')
        return redirect(url_for('travel.index'))
    
    try:
        expenses_by_category = travel.get_expenses_by_category()
        category_totals = travel.get_totals_by_category()
        person_totals = travel.get_totals_by_person()
        total = travel.get_total()
        
        logger.info(f"Viewing travel {travel_id}: {travel.name}")
        
        return render_template('travel/detail.html',
                              travel=travel,
                              expenses_by_category=expenses_by_category,
                              categories=TRAVEL_EXPENSE_CATEGORIES,
                              category_totals=category_totals,
                              person_totals=person_totals,
                              total=total,
                              users=config.USERS)
    except Exception as e:
        logger.error(f"Error loading travel {travel_id}: {e}", exc_info=True)
        flash("❌ Error loading travel details", 'error')
        return redirect(url_for('travel.index'))


@bp.route('/<int:travel_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(travel_id):
    """Edit a travel."""
    travel = Travel.get_by_id(travel_id)
    if not travel:
        logger.warning(f"Attempted to edit non-existent travel {travel_id}")
        flash("❌ Travel not found", 'error')
        return redirect(url_for('travel.index'))
    
    if request.method == 'POST':
        is_valid, error_msg = _validate_travel_input(request.form)
        if not is_valid:
            logger.warning(f"Travel edit validation failed: {error_msg}")
            flash(f"❌ {error_msg}", 'error')
            return render_template('travel/travel_form.html', travel=travel)
        
        try:
            travel.name = request.form.get('name', '').strip()
            travel.start_date = datetime.strptime(
                request.form.get('start_date'),
                '%Y-%m-%d'
            ).date()
            travel.end_date = datetime.strptime(
                request.form.get('end_date'),
                '%Y-%m-%d'
            ).date()
            travel.notes = request.form.get('notes', '').strip()
            
            travel.save()
            
            logger.info(f"Updated travel {travel_id}: {travel.name}")
            flash(f"✅ Travel '{travel.name}' updated successfully!", 'success')
            return redirect(url_for('travel.detail', travel_id=travel_id))
            
        except Exception as e:
            logger.error(f"Error updating travel {travel_id}: {e}", exc_info=True)
            flash(f"❌ Error updating travel: {str(e)}", 'error')
    
    return render_template('travel/travel_form.html',
                          travel=travel,
                          today=date.today())


@bp.route('/<int:travel_id>/delete', methods=['POST'])
@login_required
def delete(travel_id):
    """Delete a travel and all its expenses."""
    travel = Travel.get_by_id(travel_id)
    if not travel:
        logger.warning(f"Attempted to delete non-existent travel {travel_id}")
        flash("❌ Travel not found", 'error')
        return redirect(url_for('travel.index'))
    
    try:
        name = travel.name
        total = travel.get_total()
        
        # Log the deletion before deleting
        ExpenseLog.log_expense(
            action='deleted',
            expense_type='travel',
            paid_by='',
            amount=total,
            expense_date=travel.start_date,
            description=f"Travel deleted: {name}",
            expense_id=travel_id
        )
        
        travel.delete()
        
        logger.info(f"Deleted travel {travel_id}: {name}")
        flash(f"✅ Travel '{name}' deleted successfully!", 'success')
        
    except Exception as e:
        logger.error(f"Error deleting travel {travel_id}: {e}", exc_info=True)
        flash(f"❌ Error deleting travel: {str(e)}", 'error')
    
    return redirect(url_for('travel.index'))


# ============== Travel Expense Routes ==============

@bp.route('/<int:travel_id>/expense/add', methods=['GET', 'POST'])
@login_required
def add_expense(travel_id):
    """Add an expense to a travel."""
    config = get_config()
    
    travel = Travel.get_by_id(travel_id)
    if not travel:
        logger.warning(f"Attempted to add expense to non-existent travel {travel_id}")
        flash("❌ Travel not found", 'error')
        return redirect(url_for('travel.index'))
    
    # Get pre-selected category from query params
    selected_category = request.args.get('category', '')
    
    if request.method == 'POST':
        is_valid, error_msg = _validate_expense_input(request.form, config.USERS)
        if not is_valid:
            logger.warning(f"Travel expense validation failed: {error_msg}")
            flash(f"❌ {error_msg}", 'error')
            return render_template('travel/expense_form.html',
                                  travel=travel,
                                  expense=None,
                                  categories=TRAVEL_EXPENSE_CATEGORIES,
                                  selected_category=selected_category,
                                  users=config.USERS,
                                  today=date.today())
        
        try:
            expense = TravelExpense(
                travel_id=travel_id,
                name=request.form.get('name', '').strip(),
                amount=float(request.form.get('amount', 0)),
                paid_by=request.form.get('paid_by', '').strip(),
                category=request.form.get('category', '').strip(),
                expense_date=datetime.strptime(
                    request.form.get('expense_date'),
                    '%Y-%m-%d'
                ).date(),
                notes=request.form.get('notes', '').strip()
            )
            
            expense_id = expense.save()
            
            # Log the action
            ExpenseLog.log_expense(
                action='added',
                expense_type=f'travel-{expense.category}',
                paid_by=expense.paid_by,
                amount=expense.amount,
                expense_date=expense.expense_date,
                description=f"[{travel.name}] {expense.name}",
                expense_id=expense_id
            )
            
            logger.info(f"Added travel expense {expense_id}: €{expense.amount:.2f} to travel {travel_id}")
            flash(f"✅ Expense '€{expense.amount:.2f} - {expense.name}' added!", 'success')
            return redirect(url_for('travel.detail', travel_id=travel_id))
            
        except Exception as e:
            logger.error(f"Error adding travel expense: {e}", exc_info=True)
            flash(f"❌ Error adding expense: {str(e)}", 'error')
    
    return render_template('travel/expense_form.html',
                          travel=travel,
                          expense=None,
                          categories=TRAVEL_EXPENSE_CATEGORIES,
                          selected_category=selected_category,
                          users=config.USERS,
                          today=date.today())


@bp.route('/<int:travel_id>/expense/<int:expense_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_expense(travel_id, expense_id):
    """Edit a travel expense."""
    config = get_config()
    
    travel = Travel.get_by_id(travel_id)
    if not travel:
        logger.warning(f"Travel {travel_id} not found")
        flash("❌ Travel not found", 'error')
        return redirect(url_for('travel.index'))
    
    expense = TravelExpense.get_by_id(expense_id)
    if not expense or expense.travel_id != travel_id:
        logger.warning(f"Expense {expense_id} not found or doesn't belong to travel {travel_id}")
        flash("❌ Expense not found", 'error')
        return redirect(url_for('travel.detail', travel_id=travel_id))
    
    if request.method == 'POST':
        is_valid, error_msg = _validate_expense_input(request.form, config.USERS)
        if not is_valid:
            logger.warning(f"Travel expense edit validation failed: {error_msg}")
            flash(f"❌ {error_msg}", 'error')
            return render_template('travel/expense_form.html',
                                  travel=travel,
                                  expense=expense,
                                  categories=TRAVEL_EXPENSE_CATEGORIES,
                                  users=config.USERS,
                                  today=date.today())
        
        try:
            old_amount = expense.amount
            
            expense.name = request.form.get('name', '').strip()
            expense.amount = float(request.form.get('amount', 0))
            expense.paid_by = request.form.get('paid_by', '').strip()
            expense.category = request.form.get('category', '').strip()
            expense.expense_date = datetime.strptime(
                request.form.get('expense_date'),
                '%Y-%m-%d'
            ).date()
            expense.notes = request.form.get('notes', '').strip()
            
            expense.save()
            
            # Log the update
            ExpenseLog.log_expense(
                action='updated',
                expense_type=f'travel-{expense.category}',
                paid_by=expense.paid_by,
                amount=expense.amount,
                expense_date=expense.expense_date,
                description=f"[{travel.name}] Changed from €{old_amount:.2f} to €{expense.amount:.2f}: {expense.name}",
                expense_id=expense_id
            )
            
            logger.info(f"Updated travel expense {expense_id}: €{expense.amount:.2f}")
            flash(f"✅ Expense updated successfully!", 'success')
            return redirect(url_for('travel.detail', travel_id=travel_id))
            
        except Exception as e:
            logger.error(f"Error updating travel expense {expense_id}: {e}", exc_info=True)
            flash(f"❌ Error updating expense: {str(e)}", 'error')
    
    return render_template('travel/expense_form.html',
                          travel=travel,
                          expense=expense,
                          categories=TRAVEL_EXPENSE_CATEGORIES,
                          selected_category=expense.category,
                          users=config.USERS,
                          today=date.today())


@bp.route('/<int:travel_id>/expense/<int:expense_id>/delete', methods=['POST'])
@login_required
def delete_expense(travel_id, expense_id):
    """Delete a travel expense."""
    travel = Travel.get_by_id(travel_id)
    if not travel:
        logger.warning(f"Travel {travel_id} not found")
        flash("❌ Travel not found", 'error')
        return redirect(url_for('travel.index'))
    
    expense = TravelExpense.get_by_id(expense_id)
    if not expense or expense.travel_id != travel_id:
        logger.warning(f"Expense {expense_id} not found or doesn't belong to travel {travel_id}")
        flash("❌ Expense not found", 'error')
        return redirect(url_for('travel.detail', travel_id=travel_id))
    
    try:
        name = expense.name
        amount = expense.amount
        
        # Log the deletion before deleting
        ExpenseLog.log_expense(
            action='deleted',
            expense_type=f'travel-{expense.category}',
            paid_by=expense.paid_by,
            amount=amount,
            expense_date=expense.expense_date,
            description=f"[{travel.name}] {name}",
            expense_id=expense_id
        )
        
        expense.delete()
        
        logger.info(f"Deleted travel expense {expense_id}: €{amount:.2f} - {name}")
        flash(f"✅ Expense '€{amount:.2f} - {name}' deleted!", 'success')
        
    except Exception as e:
        logger.error(f"Error deleting travel expense {expense_id}: {e}", exc_info=True)
        flash(f"❌ Error deleting expense: {str(e)}", 'error')
    
    return redirect(url_for('travel.detail', travel_id=travel_id))
