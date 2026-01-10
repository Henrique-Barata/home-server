"""
Search Routes
--------------
Search across all expense types.
"""
import logging
from datetime import date, datetime
from typing import List, Dict, Any
from flask import Blueprint, render_template, request
from flask_login import login_required

from ..models.expense import FoodExpense, UtilityExpense, StuffExpense, OtherExpense
from ..models.fixed_expense import FixedExpense
from ..models.reimbursement import Reimbursement
from ..models.travel import Travel, TravelExpense
from ..models.database import db
from ..config import get_config

logger = logging.getLogger(__name__)

bp = Blueprint('search', __name__, url_prefix='/search')


# Search result types
EXPENSE_TYPES = {
    'food': {'name': 'Food', 'icon': '🍕', 'model': FoodExpense, 'table': 'food_expenses'},
    'utilities': {'name': 'Utilities', 'icon': '💡', 'model': UtilityExpense, 'table': 'utility_expenses'},
    'stuff': {'name': 'Stuff', 'icon': '📦', 'model': StuffExpense, 'table': 'stuff_expenses'},
    'other': {'name': 'Other', 'icon': '📝', 'model': OtherExpense, 'table': 'other_expenses'},
    'travel': {'name': 'Travel', 'icon': '✈️', 'model': TravelExpense, 'table': 'travel_expenses'},
    'reimbursement': {'name': 'Reimbursement', 'icon': '💰', 'model': Reimbursement, 'table': 'reimbursements'},
}


def _search_standard_expenses(query: str, expense_type: str, table: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search in standard expense tables (food, utilities, stuff, other)."""
    sql = f"""
        SELECT id, name, amount, paid_by, expense_date, created_at
        FROM {table}
        WHERE name LIKE ? OR paid_by LIKE ?
        ORDER BY expense_date DESC
        LIMIT ?
    """
    pattern = f'%{query}%'
    rows = db.fetch_all(sql, (pattern, pattern, limit))
    
    results = []
    type_info = EXPENSE_TYPES[expense_type]
    for row in rows:
        results.append({
            'type': expense_type,
            'type_name': type_info['name'],
            'icon': type_info['icon'],
            'id': row['id'],
            'name': row['name'],
            'amount': row['amount'],
            'paid_by': row['paid_by'],
            'date': row['expense_date'],
            'url': f"/{expense_type}/{row['id']}/edit"
        })
    return results


def _search_travel_expenses(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search in travel expenses."""
    sql = """
        SELECT te.id, te.name, te.amount, te.paid_by, te.expense_date, te.travel_id,
               t.name as travel_name
        FROM travel_expenses te
        JOIN travels t ON te.travel_id = t.id
        WHERE te.name LIKE ? OR te.paid_by LIKE ? OR t.name LIKE ?
        ORDER BY te.expense_date DESC
        LIMIT ?
    """
    pattern = f'%{query}%'
    rows = db.fetch_all(sql, (pattern, pattern, pattern, limit))
    
    results = []
    for row in rows:
        results.append({
            'type': 'travel',
            'type_name': 'Travel',
            'icon': '✈️',
            'id': row['id'],
            'name': f"{row['travel_name']}: {row['name']}",
            'amount': row['amount'],
            'paid_by': row['paid_by'],
            'date': row['expense_date'],
            'url': f"/travel/{row['travel_id']}"
        })
    return results


def _search_reimbursements(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search in reimbursements."""
    sql = """
        SELECT id, name, amount, reimbursed_to, reimbursement_date
        FROM reimbursements
        WHERE name LIKE ? OR reimbursed_to LIKE ? OR notes LIKE ?
        ORDER BY reimbursement_date DESC
        LIMIT ?
    """
    pattern = f'%{query}%'
    rows = db.fetch_all(sql, (pattern, pattern, pattern, limit))
    
    results = []
    for row in rows:
        results.append({
            'type': 'reimbursement',
            'type_name': 'Reimbursement',
            'icon': '💰',
            'id': row['id'],
            'name': row['name'],
            'amount': row['amount'],
            'paid_by': row['reimbursed_to'],  # Using 'paid_by' field for consistency
            'date': row['reimbursement_date'],
            'url': f"/reimbursement/{row['id']}/edit"
        })
    return results


def _search_travels(query: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Search travels by name or notes."""
    sql = """
        SELECT id, name, start_date, end_date, notes
        FROM travels
        WHERE name LIKE ? OR notes LIKE ?
        ORDER BY start_date DESC
        LIMIT ?
    """
    pattern = f'%{query}%'
    rows = db.fetch_all(sql, (pattern, pattern, limit))
    
    results = []
    for row in rows:
        # Get total for this travel
        total_result = db.fetch_one(
            "SELECT COALESCE(SUM(amount), 0) as total FROM travel_expenses WHERE travel_id = ?",
            (row['id'],)
        )
        total = total_result['total'] if total_result else 0.0
        
        results.append({
            'type': 'travel_trip',
            'type_name': 'Travel Trip',
            'icon': '🧳',
            'id': row['id'],
            'name': row['name'],
            'amount': total,
            'paid_by': f"{row['start_date']} to {row['end_date']}",
            'date': row['start_date'],
            'url': f"/travel/{row['id']}"
        })
    return results


def search_all(query: str, types: List[str] = None, limit: int = 100) -> Dict[str, Any]:
    """
    Search across all expense types.
    
    Args:
        query: Search string (will be searched with LIKE %query%)
        types: List of expense types to search (None = all)
        limit: Maximum total results
        
    Returns:
        Dict with results list and metadata
    """
    if not query or len(query.strip()) < 2:
        return {'results': [], 'total': 0, 'query': query}
    
    query = query.strip()
    all_types = types or ['food', 'utilities', 'stuff', 'other', 'travel', 'reimbursement']
    
    results = []
    limit_per_type = max(10, limit // len(all_types))
    
    for expense_type in all_types:
        if expense_type == 'travel':
            results.extend(_search_travels(query, limit_per_type))
            results.extend(_search_travel_expenses(query, limit_per_type))
        elif expense_type == 'reimbursement':
            results.extend(_search_reimbursements(query, limit_per_type))
        elif expense_type in EXPENSE_TYPES:
            table = EXPENSE_TYPES[expense_type]['table']
            results.extend(_search_standard_expenses(query, expense_type, table, limit_per_type))
    
    # Sort all results by date (most recent first)
    results.sort(key=lambda x: x['date'] if x['date'] else '', reverse=True)
    
    # Limit total results
    results = results[:limit]
    
    # Calculate totals
    total_amount = sum(r['amount'] for r in results)
    
    return {
        'results': results,
        'total': len(results),
        'total_amount': total_amount,
        'query': query
    }


def _get_users():
    """Get list of users from config."""
    config = get_config()
    return config.USERS


@bp.route('/')
@login_required
def index():
    """Search page."""
    query = request.args.get('q', '').strip()
    
    # Get filter options
    selected_types = request.args.getlist('type')
    if not selected_types:
        selected_types = None  # Search all types
    
    # Date range filters (optional)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    person = request.args.get('person', '')
    
    search_results = {'results': [], 'total': 0, 'total_amount': 0, 'query': query}
    
    if query:
        search_results = search_all(query, selected_types)
        
        # Apply additional filters
        if date_from:
            search_results['results'] = [
                r for r in search_results['results']
                if r['date'] and str(r['date']) >= date_from
            ]
        if date_to:
            search_results['results'] = [
                r for r in search_results['results']
                if r['date'] and str(r['date']) <= date_to
            ]
        if person:
            search_results['results'] = [
                r for r in search_results['results']
                if person.lower() in str(r['paid_by']).lower()
            ]
        
        # Recalculate totals after filtering
        search_results['total'] = len(search_results['results'])
        search_results['total_amount'] = sum(r['amount'] for r in search_results['results'])
        
        logger.info(f"Search for '{query}': {search_results['total']} results")
    
    return render_template(
        'search/index.html',
        query=query,
        results=search_results['results'],
        total=search_results['total'],
        total_amount=search_results.get('total_amount', 0),
        expense_types=EXPENSE_TYPES,
        selected_types=selected_types or [],
        date_from=date_from,
        date_to=date_to,
        person=person,
        users=_get_users()
    )
