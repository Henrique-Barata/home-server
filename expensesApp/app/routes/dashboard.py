"""
Dashboard Routes
----------------
Main dashboard with monthly expense overview and detailed views.
"""
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from ..models.expense import FoodExpense, UtilityExpense, StuffExpense, OtherExpense
from ..models.fixed_expense import FixedExpense, FixedExpenseType
from ..models.settlement import Settlement
from ..config import get_config


bp = Blueprint('dashboard', __name__)


@bp.route('/')
@login_required
def index():
    """
    Main dashboard showing monthly expense summary.
    Displays: Rent, Utilities, Food, Stuff, Other, Total per month.
    """
    config = get_config()
    
    # Get selected year or default to current year
    current_year = date.today().year
    selected_year = request.args.get('year', current_year, type=int)
    
    # Get sort parameters
    sort_by = request.args.get('sort', 'month')
    sort_order = request.args.get('order', 'asc')
    
    # Generate data for all 12 months
    months_data = []
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Get all fixed expense types
    fixed_types = FixedExpenseType.get_all_types()
    
    for month in range(1, 13):
        # Get all fixed expenses
        fixed_total = 0.0
        fixed_breakdown = {}
        for ft in fixed_types:
            value = FixedExpense.get_value_for_month(ft, selected_year, month)
            fixed_breakdown[ft] = value
            fixed_total += value
        
        # Get utilities total (excluding Internet which is in fixed)
        utilities_total = UtilityExpense.get_total_by_month(selected_year, month)
        
        # Get other expense totals
        food_total = FoodExpense.get_total_by_month(selected_year, month)
        stuff_total = StuffExpense.get_total_by_month(selected_year, month)
        other_total = OtherExpense.get_total_by_month(selected_year, month)
        
        # Calculate total
        month_total = fixed_total + utilities_total + food_total + stuff_total + other_total
        
        months_data.append({
            'month': month,
            'name': month_names[month - 1],
            'fixed': fixed_total,
            'fixed_breakdown': fixed_breakdown,
            'utilities': utilities_total,
            'food': food_total,
            'stuff': stuff_total,
            'other': other_total,
            'total': month_total
        })
    
    # Apply sorting
    if sort_by != 'month':
        reverse = sort_order == 'desc'
        if sort_by in ['fixed', 'utilities', 'food', 'stuff', 'other', 'total']:
            months_data.sort(key=lambda x: x[sort_by], reverse=reverse)
    elif sort_order == 'desc':
        months_data.reverse()
    
    # Calculate per-person totals for the selected year
    person_totals = {}
    person_monthly = {}
    for person in config.USERS:
        yearly_total = 0
        monthly_data = []
        for m in range(1, 13):
            food = FoodExpense.get_total_by_person_and_month(person, selected_year, m)
            utility = UtilityExpense.get_total_by_person_and_month(person, selected_year, m)
            stuff = StuffExpense.get_total_by_person_and_month(person, selected_year, m)
            other = OtherExpense.get_total_by_person_and_month(person, selected_year, m)
            month_total = food + utility + stuff + other
            yearly_total += month_total
            monthly_data.append({
                'month': m,
                'name': month_names[m - 1],
                'food': food,
                'utilities': utility,
                'stuff': stuff,
                'other': other,
                'total': month_total
            })
        person_totals[person] = yearly_total
        person_monthly[person] = monthly_data
    
    # Calculate balance between users
    balance_data = calculate_balance(config.USERS, selected_year)
    
    # Get settlements for the year
    all_settlements = Settlement.get_all()
    year_settlements = [s for s in all_settlements 
                        if s.settlement_date.year == selected_year]
    
    # Calculate yearly total
    yearly_total = sum(m['total'] for m in months_data if m['total'] > 0)
    
    # Available years for selection (current year ± 2)
    available_years = list(range(current_year - 2, current_year + 2))
    
    return render_template('dashboard/index.html',
                          months_data=months_data,
                          person_totals=person_totals,
                          person_monthly=person_monthly,
                          balance_data=balance_data,
                          settlements=year_settlements,
                          selected_year=selected_year,
                          available_years=available_years,
                          yearly_total=yearly_total,
                          current_month=date.today().month,
                          sort_by=sort_by,
                          sort_order=sort_order,
                          users=config.USERS)


def calculate_balance(users, year):
    """
    Calculate expense balance between users.
    Returns who owes whom and how much.
    """
    if len(users) != 2:
        return None
    
    person1, person2 = users[0], users[1]
    
    # Get total expenses paid by each person
    totals = {}
    for person in users:
        food = sum(FoodExpense.get_total_by_person_and_month_shared_only(person, year, m) 
                   for m in range(1, 13))
        utility = sum(UtilityExpense.get_total_by_person_and_month_shared_only(person, year, m) 
                      for m in range(1, 13))
        stuff = sum(StuffExpense.get_total_by_person_and_month_shared_only(person, year, m) 
                    for m in range(1, 13))
        other = sum(OtherExpense.get_total_by_person_and_month_shared_only(person, year, m) 
                    for m in range(1, 13))
        totals[person] = food + utility + stuff + other
    
    # Calculate settlements
    settlement_balance = Settlement.get_balance_between(person1, person2, year)
    
    # Calculate who paid more
    total_expenses = totals[person1] + totals[person2]
    fair_share = total_expenses / 2
    
    # Difference each person is from fair share
    diff1 = totals[person1] - fair_share  # Positive = overpaid
    
    # Apply settlements: positive means person2 owes person1, so subtract it
    adjusted_diff1 = diff1 - settlement_balance
    
    return {
        'person1': person1,
        'person2': person2,
        'total1': totals[person1],
        'total2': totals[person2],
        'fair_share': fair_share,
        'settlement_total': abs(settlement_balance),
        'settlement_direction': f"{person1} → {person2}" if settlement_balance > 0 else f"{person2} → {person1}",
        'balance': adjusted_diff1,
        'owes': person2 if adjusted_diff1 > 0 else person1,
        'owed_to': person1 if adjusted_diff1 > 0 else person2,
        'amount_owed': abs(adjusted_diff1)
    }


@bp.route('/month/<int:year>/<int:month>')
@login_required
def month_detail(year, month):
    """
    Detailed view of all expenses for a specific month.
    Shows breakdown by category with individual expense lists.
    """
    config = get_config()
    
    month_names = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    if month < 1 or month > 12:
        flash('Invalid month.', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Get all fixed expense types
    fixed_types = FixedExpenseType.get_all_types()
    
    # Get fixed expenses for this month
    # Fixed expenses are applied on the 1st of each month, using the current effective value
    fixed_expenses = []
    fixed_total = 0.0
    fixed_payments = FixedExpense.get_all_payments_for_month(year, month)
    
    for ft in fixed_types:
        # Get the value that's effective for this month
        amount = FixedExpense.get_value_for_month(ft, year, month)
        if amount > 0:
            # Get the current expense record to get paid_by info
            current_expense = FixedExpense.get_current_by_type(ft)
            if current_expense:
                # Get payment status for this expense
                payment_status = fixed_payments.get(current_expense.id, {
                    'is_paid': 0,
                    'paid_by': None,
                    'paid_date': None
                })
                
                # Create a virtual expense for display (on first of month)
                expense_for_display = FixedExpense(
                    expense_type=ft,
                    amount=amount,
                    effective_date=date(year, month, 1),
                    paid_by=current_expense.paid_by,
                    id=current_expense.id
                )
                expense_for_display.is_paid = payment_status['is_paid']
                expense_for_display.paid_by_person = payment_status['paid_by']
                expense_for_display.paid_date = payment_status['paid_date']
                
                fixed_expenses.append(expense_for_display)
                fixed_total += amount
    
    # Get all expenses for this month
    food_expenses = FoodExpense.get_by_month(year, month)
    utility_expenses = UtilityExpense.get_by_month(year, month)
    stuff_expenses = StuffExpense.get_by_month(year, month)
    other_expenses = OtherExpense.get_by_month(year, month)
    settlements = Settlement.get_by_month(year, month)
    
    # Calculate totals
    food_total = sum(e.amount for e in food_expenses)
    utility_total = sum(e.amount for e in utility_expenses)
    stuff_total = sum(e.amount for e in stuff_expenses)
    other_total = sum(e.amount for e in other_expenses)
    
    grand_total = fixed_total + food_total + utility_total + stuff_total + other_total
    
    # Per-person breakdown
    person_data = {}
    for person in config.USERS:
        person_data[person] = {
            'fixed': sum(e.amount for e in fixed_expenses if e.paid_by == person),
            'food': sum(e.amount for e in food_expenses if e.paid_by == person),
            'utilities': sum(e.amount for e in utility_expenses if e.paid_by == person),
            'stuff': sum(e.amount for e in stuff_expenses if e.paid_by == person),
            'other': sum(e.amount for e in other_expenses if e.paid_by == person),
        }
        person_data[person]['total'] = sum(person_data[person].values())
    
    return render_template('dashboard/month_detail.html',
                          year=year,
                          month=month,
                          month_name=month_names[month - 1],
                          fixed_expenses=fixed_expenses,
                          fixed_total=fixed_total,
                          food_expenses=food_expenses,
                          food_total=food_total,
                          utility_expenses=utility_expenses,
                          utility_total=utility_total,
                          stuff_expenses=stuff_expenses,
                          stuff_total=stuff_total,
                          other_expenses=other_expenses,
                          other_total=other_total,
                          settlements=settlements,
                          grand_total=grand_total,
                          person_data=person_data,
                          users=config.USERS)


@bp.route('/person/<person>')
@login_required
def person_detail(person):
    """
    Detailed view of expenses for a specific person.
    Shows all their expenses filtered by month/category.
    """
    config = get_config()
    
    if person not in config.USERS:
        flash('Invalid user.', 'error')
        return redirect(url_for('dashboard.index'))
    
    current_year = date.today().year
    selected_year = request.args.get('year', current_year, type=int)
    selected_month = request.args.get('month', 0, type=int)  # 0 = all months
    
    month_names = [
        'All Months', 'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ]
    
    # Get expenses
    if selected_month > 0:
        food_expenses = [e for e in FoodExpense.get_by_month(selected_year, selected_month) 
                         if e.paid_by == person]
        utility_expenses = [e for e in UtilityExpense.get_by_month(selected_year, selected_month) 
                            if e.paid_by == person]
        stuff_expenses = [e for e in StuffExpense.get_by_month(selected_year, selected_month) 
                          if e.paid_by == person]
        other_expenses = [e for e in OtherExpense.get_by_month(selected_year, selected_month) 
                          if e.paid_by == person]
    else:
        # Get all expenses for the year for this person
        food_expenses = [e for e in FoodExpense.get_all() 
                         if e.paid_by == person and e.expense_date.year == selected_year]
        utility_expenses = [e for e in UtilityExpense.get_all() 
                            if e.paid_by == person and e.expense_date.year == selected_year]
        stuff_expenses = [e for e in StuffExpense.get_all() 
                          if e.paid_by == person and e.expense_date.year == selected_year]
        other_expenses = [e for e in OtherExpense.get_all() 
                          if e.paid_by == person and e.expense_date.year == selected_year]
    
    # Calculate totals
    food_total = sum(e.amount for e in food_expenses)
    utility_total = sum(e.amount for e in utility_expenses)
    stuff_total = sum(e.amount for e in stuff_expenses)
    other_total = sum(e.amount for e in other_expenses)
    grand_total = food_total + utility_total + stuff_total + other_total
    
    # Available years
    available_years = list(range(current_year - 2, current_year + 2))
    
    return render_template('dashboard/person_detail.html',
                          person=person,
                          year=selected_year,
                          month=selected_month,
                          month_name=month_names[selected_month],
                          food_expenses=food_expenses,
                          food_total=food_total,
                          utility_expenses=utility_expenses,
                          utility_total=utility_total,
                          stuff_expenses=stuff_expenses,
                          stuff_total=stuff_total,
                          other_expenses=other_expenses,
                          other_total=other_total,
                          grand_total=grand_total,
                          available_years=available_years,
                          month_names=month_names)


@bp.route('/settlement', methods=['GET', 'POST'])
@login_required
def settlement():
    """Add a new settlement payment."""
    config = get_config()
    
    if request.method == 'POST':
        payer = request.form.get('payer')
        receiver = request.form.get('receiver')
        amount = float(request.form.get('amount', 0))
        settlement_date = date.fromisoformat(request.form.get('settlement_date', str(date.today())))
        notes = request.form.get('notes', '')
        
        if payer == receiver:
            flash('Payer and receiver must be different.', 'error')
            return redirect(url_for('dashboard.settlement'))
        
        if amount <= 0:
            flash('Amount must be greater than 0.', 'error')
            return redirect(url_for('dashboard.settlement'))
        
        new_settlement = Settlement(
            payer=payer,
            receiver=receiver,
            amount=amount,
            settlement_date=settlement_date,
            notes=notes
        )
        new_settlement.save()
        
        flash(f'Settlement recorded: {payer} paid {receiver} €{amount:.2f}', 'success')
        return redirect(url_for('dashboard.index'))
    
    return render_template('dashboard/settlement.html',
                          users=config.USERS,
                          today=date.today())


@bp.route('/settlement/delete/<int:settlement_id>', methods=['POST'])
@login_required
def delete_settlement(settlement_id):
    """Delete a settlement."""
    settlement = Settlement.get_by_id(settlement_id)
    
    if settlement:
        settlement.delete()
        flash('Settlement deleted.', 'success')
    else:
        flash('Settlement not found.', 'error')
    
    return redirect(url_for('dashboard.index'))
