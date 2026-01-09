"""
Authentication Routes
---------------------
Login/logout functionality with simple password protection.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required

from ..models.user import User


bp = Blueprint('auth', __name__)


# Whitelist of allowed redirect endpoints after login
ALLOWED_REDIRECT_ENDPOINTS = {
    'dashboard.index',
    'food.index',
    'utilities.index', 
    'fixed.index',
    'stuff.index',
    'other.index',
    'log.index',
}


def get_safe_redirect() -> str:
    """
    Get a safe redirect URL from the 'next' parameter.
    Uses endpoint whitelist to prevent open redirect attacks.
    Returns the dashboard URL if the requested endpoint is not allowed.
    """
    next_endpoint = request.args.get('next_endpoint')
    if next_endpoint and next_endpoint in ALLOWED_REDIRECT_ENDPOINTS:
        return url_for(next_endpoint)
    return url_for('dashboard.index')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle login page and authentication."""
    if request.method == 'POST':
        password = request.form.get('password', '')
        user = User.authenticate(password)
        
        if user:
            login_user(user, remember=True)
            # Use safe redirect with endpoint whitelist
            return redirect(get_safe_redirect())
        
        flash('Incorrect password. Please try again.', 'error')
    
    return render_template('auth/login.html')


@bp.route('/logout')
@login_required
def logout():
    """Handle logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
