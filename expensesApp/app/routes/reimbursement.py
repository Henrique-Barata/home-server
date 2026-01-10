"""
Reimbursement Routes
--------------------
Routes for managing reimbursements (refunds).
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime, date
from ..models import Reimbursement, User
from ..models.expense_log import ExpenseLog

bp = Blueprint('reimbursement', __name__, url_prefix='/reimbursement')


@bp.route('/')
@bp.route('/list')
def list_reimbursements():
    """List all reimbursements."""
    reimbursements = Reimbursement.get_all()
    users = User.get_all()
    
    return render_template('reimbursement/index.html',
                         reimbursements=reimbursements,
                         users=users)


@bp.route('/add', methods=['GET', 'POST'])
def add_reimbursement():
    """Add a new reimbursement."""
    users = User.get_all()
    
    if request.method == 'POST':
        try:
            reimbursement = Reimbursement(
                name=request.form.get('name', ''),
                amount=float(request.form.get('amount', 0)),
                reimbursed_to=request.form.get('reimbursed_to', ''),
                original_expense_type=request.form.get('original_expense_type'),
                original_expense_id=request.form.get('original_expense_id') or None,
                reimbursement_date=datetime.strptime(
                    request.form.get('reimbursement_date', str(date.today())),
                    '%Y-%m-%d'
                ).date(),
                notes=request.form.get('notes', '')
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
            
            flash(f"✅ Reimbursement of ${reimbursement.amount:.2f} added successfully!", 'success')
            return redirect(url_for('reimbursement.list_reimbursements'))
            
        except ValueError as e:
            flash(f"❌ Invalid input: {str(e)}", 'error')
        except Exception as e:
            flash(f"❌ Error adding reimbursement: {str(e)}", 'error')
    
    return render_template('reimbursement/form.html',
                         users=users,
                         reimbursement=None)


@bp.route('/<int:reimbursement_id>/edit', methods=['GET', 'POST'])
def edit_reimbursement(reimbursement_id):
    """Edit an existing reimbursement."""
    reimbursement = Reimbursement.get_by_id(reimbursement_id)
    
    if not reimbursement:
        flash("❌ Reimbursement not found!", 'error')
        return redirect(url_for('reimbursement.list_reimbursements'))
    
    users = User.get_all()
    
    if request.method == 'POST':
        try:
            reimbursement.name = request.form.get('name', '')
            reimbursement.amount = float(request.form.get('amount', 0))
            reimbursement.reimbursed_to = request.form.get('reimbursed_to', '')
            reimbursement.original_expense_type = request.form.get('original_expense_type')
            reimbursement.original_expense_id = request.form.get('original_expense_id') or None
            reimbursement.reimbursement_date = datetime.strptime(
                request.form.get('reimbursement_date', str(date.today())),
                '%Y-%m-%d'
            ).date()
            reimbursement.notes = request.form.get('notes', '')
            
            reimbursement.save()
            
            # Log the update
            ExpenseLog.log_reimbursement(
                action='update',
                reimbursement_id=reimbursement_id,
                reimbursed_to=reimbursement.reimbursed_to,
                amount=reimbursement.amount,
                description=reimbursement.name
            )
            
            flash(f"✅ Reimbursement updated successfully!", 'success')
            return redirect(url_for('reimbursement.list_reimbursements'))
            
        except ValueError as e:
            flash(f"❌ Invalid input: {str(e)}", 'error')
        except Exception as e:
            flash(f"❌ Error updating reimbursement: {str(e)}", 'error')
    
    return render_template('reimbursement/form.html',
                         users=users,
                         reimbursement=reimbursement)


@bp.route('/<int:reimbursement_id>/delete', methods=['POST'])
def delete_reimbursement(reimbursement_id):
    """Delete a reimbursement."""
    reimbursement = Reimbursement.get_by_id(reimbursement_id)
    
    if not reimbursement:
        flash("❌ Reimbursement not found!", 'error')
        return redirect(url_for('reimbursement.list_reimbursements'))
    
    try:
        amount = reimbursement.amount
        name = reimbursement.name
        
        # Log the deletion before deleting
        ExpenseLog.log_reimbursement(
            action='delete',
            reimbursement_id=reimbursement_id,
            reimbursed_to=reimbursement.reimbursed_to,
            amount=amount,
            description=name
        )
        
        reimbursement.delete()
        flash(f"✅ Reimbursement '{name}' deleted successfully!", 'success')
        
    except Exception as e:
        flash(f"❌ Error deleting reimbursement: {str(e)}", 'error')
    
    return redirect(url_for('reimbursement.list_reimbursements'))


@bp.route('/by-person/<person>')
def by_person(person):
    """Get reimbursements for a specific person."""
    reimbursements = Reimbursement.get_by_person(person)
    total = Reimbursement.get_total_reimbursed(person)
    
    return render_template('reimbursement/person.html',
                         person=person,
                         reimbursements=reimbursements,
                         total=total)
