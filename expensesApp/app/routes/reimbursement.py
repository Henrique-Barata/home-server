"""
Reimbursement Routes
--------------------
Routes for managing reimbursements (refunds).
A reimbursement represents money returned when an item is refunded.
It reduces the reimbursed_to person's account balance.
"""
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime, date
from ..models import Reimbursement
from ..models.expense_log import ExpenseLog
from ..config import get_config

# Set up logging for this module
logger = logging.getLogger(__name__)

bp = Blueprint('reimbursement', __name__, url_prefix='/reimbursement')


def _get_users():
    """Get configured users from config."""
    config = get_config()
    return config.USERS


def _validate_reimbursement_input(form_data: dict, users: list) -> tuple[bool, str]:
    """
    Validate reimbursement form input.
    
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
    
    reimbursed_to = form_data.get('reimbursed_to', '').strip()
    if not reimbursed_to:
        return False, "Who received the money is required"
    if reimbursed_to not in users:
        return False, f"Invalid person: {reimbursed_to}"
    
    date_str = form_data.get('reimbursement_date', '')
    if not date_str:
        return False, "Date is required"
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return False, "Invalid date format"
    
    # Validate optional expense type
    expense_type = form_data.get('original_expense_type', '')
    valid_types = ['', 'food', 'utilities', 'stuff', 'other']
    if expense_type and expense_type not in valid_types:
        return False, f"Invalid expense type: {expense_type}"
    
    return True, ""


@bp.route('/')
@bp.route('/list')
@login_required
def list_reimbursements():
    """List all reimbursements."""
    logger.debug("Listing all reimbursements")
    
    try:
        reimbursements = Reimbursement.get_all()
        users = _get_users()
        
        logger.info(f"Retrieved {len(reimbursements)} reimbursements")
        
        return render_template('reimbursement/index.html',
                             reimbursements=reimbursements,
                             users=users)
    except Exception as e:
        logger.error(f"Error listing reimbursements: {e}", exc_info=True)
        flash("❌ Error loading reimbursements", 'error')
        return redirect(url_for('dashboard.index'))


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_reimbursement():
    """Add a new reimbursement."""
    users = _get_users()
    
    if request.method == 'POST':
        # Validate input
        is_valid, error_msg = _validate_reimbursement_input(request.form, users)
        if not is_valid:
            logger.warning(f"Reimbursement validation failed: {error_msg}")
            flash(f"❌ {error_msg}", 'error')
            return render_template('reimbursement/form.html',
                                 users=users,
                                 reimbursement=None)
        
        try:
            reimbursement = Reimbursement(
                name=request.form.get('name', '').strip(),
                amount=float(request.form.get('amount', 0)),
                reimbursed_to=request.form.get('reimbursed_to', '').strip(),
                original_expense_type=request.form.get('original_expense_type') or None,
                original_expense_id=request.form.get('original_expense_id') or None,
                reimbursement_date=datetime.strptime(
                    request.form.get('reimbursement_date', str(date.today())),
                    '%Y-%m-%d'
                ).date(),
                notes=request.form.get('notes', '').strip()
            )
            
            reimbursement_id = reimbursement.save()
            
            # Log the reimbursement
            ExpenseLog.log_reimbursement(
                action='add',
                reimbursement_id=reimbursement_id,
                reimbursed_to=reimbursement.reimbursed_to,
                amount=reimbursement.amount,
                description=reimbursement.name
            )
            
            logger.info(f"Added reimbursement {reimbursement_id}: €{reimbursement.amount:.2f} to {reimbursement.reimbursed_to}")
            flash(f"✅ Reimbursement of €{reimbursement.amount:.2f} added successfully!", 'success')
            return redirect(url_for('reimbursement.list_reimbursements'))
            
        except ValueError as e:
            logger.warning(f"Invalid input for reimbursement: {e}")
            flash(f"❌ Invalid input: {str(e)}", 'error')
        except Exception as e:
            logger.error(f"Error adding reimbursement: {e}", exc_info=True)
            flash(f"❌ Error adding reimbursement: {str(e)}", 'error')
    
    return render_template('reimbursement/form.html',
                         users=users,
                         reimbursement=None)


@bp.route('/<int:reimbursement_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_reimbursement(reimbursement_id):
    """Edit an existing reimbursement."""
    reimbursement = Reimbursement.get_by_id(reimbursement_id)
    
    if not reimbursement:
        logger.warning(f"Attempted to edit non-existent reimbursement {reimbursement_id}")
        flash("❌ Reimbursement not found!", 'error')
        return redirect(url_for('reimbursement.list_reimbursements'))
    
    users = _get_users()
    
    if request.method == 'POST':
        # Validate input
        is_valid, error_msg = _validate_reimbursement_input(request.form, users)
        if not is_valid:
            logger.warning(f"Reimbursement edit validation failed: {error_msg}")
            flash(f"❌ {error_msg}", 'error')
            return render_template('reimbursement/form.html',
                                 users=users,
                                 reimbursement=reimbursement)
        
        try:
            old_amount = reimbursement.amount
            
            reimbursement.name = request.form.get('name', '').strip()
            reimbursement.amount = float(request.form.get('amount', 0))
            reimbursement.reimbursed_to = request.form.get('reimbursed_to', '').strip()
            reimbursement.original_expense_type = request.form.get('original_expense_type') or None
            reimbursement.original_expense_id = request.form.get('original_expense_id') or None
            reimbursement.reimbursement_date = datetime.strptime(
                request.form.get('reimbursement_date', str(date.today())),
                '%Y-%m-%d'
            ).date()
            reimbursement.notes = request.form.get('notes', '').strip()
            
            reimbursement.save()
            
            # Log the update
            ExpenseLog.log_reimbursement(
                action='update',
                reimbursement_id=reimbursement_id,
                reimbursed_to=reimbursement.reimbursed_to,
                amount=reimbursement.amount,
                description=f"Changed from €{old_amount:.2f} to €{reimbursement.amount:.2f}: {reimbursement.name}"
            )
            
            logger.info(f"Updated reimbursement {reimbursement_id}: €{reimbursement.amount:.2f}")
            flash(f"✅ Reimbursement updated successfully!", 'success')
            return redirect(url_for('reimbursement.list_reimbursements'))
            
        except ValueError as e:
            logger.warning(f"Invalid input for reimbursement edit: {e}")
            flash(f"❌ Invalid input: {str(e)}", 'error')
        except Exception as e:
            logger.error(f"Error updating reimbursement {reimbursement_id}: {e}", exc_info=True)
            flash(f"❌ Error updating reimbursement: {str(e)}", 'error')
    
    return render_template('reimbursement/form.html',
                         users=users,
                         reimbursement=reimbursement)


@bp.route('/<int:reimbursement_id>/delete', methods=['POST'])
@login_required
def delete_reimbursement(reimbursement_id):
    """Delete a reimbursement."""
    reimbursement = Reimbursement.get_by_id(reimbursement_id)
    
    if not reimbursement:
        logger.warning(f"Attempted to delete non-existent reimbursement {reimbursement_id}")
        flash("❌ Reimbursement not found!", 'error')
        return redirect(url_for('reimbursement.list_reimbursements'))
    
    try:
        amount = reimbursement.amount
        name = reimbursement.name
        reimbursed_to = reimbursement.reimbursed_to
        
        # Log the deletion before deleting
        ExpenseLog.log_reimbursement(
            action='delete',
            reimbursement_id=reimbursement_id,
            reimbursed_to=reimbursed_to,
            amount=amount,
            description=name
        )
        
        reimbursement.delete()
        
        logger.info(f"Deleted reimbursement {reimbursement_id}: €{amount:.2f} - {name}")
        flash(f"✅ Reimbursement '{name}' deleted successfully!", 'success')
        
    except Exception as e:
        logger.error(f"Error deleting reimbursement {reimbursement_id}: {e}", exc_info=True)
        flash(f"❌ Error deleting reimbursement: {str(e)}", 'error')
    
    return redirect(url_for('reimbursement.list_reimbursements'))


@bp.route('/by-person/<person>')
@login_required
def by_person(person):
    """Get reimbursements for a specific person."""
    users = _get_users()
    
    # Validate person is a valid user
    if person not in users:
        logger.warning(f"Attempted to view reimbursements for invalid person: {person}")
        flash("❌ Invalid person specified", 'error')
        return redirect(url_for('reimbursement.list_reimbursements'))
    
    try:
        reimbursements = Reimbursement.get_by_person(person)
        total = Reimbursement.get_total_reimbursed(person)
        
        logger.info(f"Retrieved {len(reimbursements)} reimbursements for {person} (total: €{total:.2f})")
        
        return render_template('reimbursement/by_person.html',
                             person=person,
                             reimbursements=reimbursements,
                             total=total or 0.0,
                             users=users)
    except Exception as e:
        logger.error(f"Error getting reimbursements for {person}: {e}", exc_info=True)
        flash(f"❌ Error loading reimbursements for {person}", 'error')
        return redirect(url_for('reimbursement.list_reimbursements'))
