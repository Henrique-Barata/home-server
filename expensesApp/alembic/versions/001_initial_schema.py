"""Initial schema with all tables

Revision ID: 001_initial
Revises: None
Create Date: 2024-01-01

This is the baseline migration that establishes the complete schema.
It captures the current state of the database including all tables.

If you're starting with a fresh database, run: alembic upgrade head
If you have an existing database, run: alembic stamp 001_initial
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all tables for the expense tracker application."""
    
    # Food expenses table
    op.create_table(
        'food_expenses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('paid_by', sa.Text(), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('individual_only', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_food_date', 'food_expenses', ['expense_date'])
    op.create_index('idx_food_paid_by', 'food_expenses', ['paid_by'])
    
    # Utility expenses table
    op.create_table(
        'utility_expenses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('paid_by', sa.Text(), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('utility_type', sa.Text(), nullable=False),
        sa.Column('individual_only', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_utility_date', 'utility_expenses', ['expense_date'])
    op.create_index('idx_utility_type', 'utility_expenses', ['utility_type'])
    
    # Stuff expenses table
    op.create_table(
        'stuff_expenses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('paid_by', sa.Text(), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('stuff_type', sa.Text(), nullable=False),
        sa.Column('individual_only', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_stuff_date', 'stuff_expenses', ['expense_date'])
    op.create_index('idx_stuff_type', 'stuff_expenses', ['stuff_type'])
    
    # Other expenses table
    op.create_table(
        'other_expenses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('paid_by', sa.Text(), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('individual_only', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_other_date', 'other_expenses', ['expense_date'])
    
    # Fixed expenses table
    op.create_table(
        'fixed_expenses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('expense_type', sa.Text(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('paid_by', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_fixed_type', 'fixed_expenses', ['expense_type', 'effective_date'])
    
    # Fixed expense types table
    op.create_table(
        'fixed_expense_types',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text(), nullable=False, unique=True)
    )
    
    # Fixed expense payments table
    op.create_table(
        'fixed_expense_payments',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('fixed_expense_id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('is_paid', sa.Integer(), server_default='0'),
        sa.Column('paid_by', sa.Text()),
        sa.Column('paid_date', sa.Date()),
        sa.UniqueConstraint('fixed_expense_id', 'year', 'month')
    )
    
    # Stuff types table
    op.create_table(
        'stuff_types',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text(), nullable=False, unique=True)
    )
    
    # Settlements table
    op.create_table(
        'settlements',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('payer', sa.Text(), nullable=False),
        sa.Column('receiver', sa.Text(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('settlement_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_settlement_date', 'settlements', ['settlement_date'])
    
    # Expense logs table
    op.create_table(
        'expense_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('action', sa.Text(), nullable=False),
        sa.Column('expense_type', sa.Text(), nullable=False),
        sa.Column('expense_id', sa.Integer()),
        sa.Column('paid_by', sa.Text()),
        sa.Column('amount', sa.Float()),
        sa.Column('expense_date', sa.Date()),
        sa.Column('description', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_log_date', 'expense_logs', ['created_at'])
    op.create_index('idx_log_type', 'expense_logs', ['expense_type'])
    
    # Reimbursements table
    op.create_table(
        'reimbursements',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('reimbursed_to', sa.Text(), nullable=False),
        sa.Column('original_expense_type', sa.Text()),
        sa.Column('original_expense_id', sa.Integer()),
        sa.Column('reimbursement_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_reimbursement_date', 'reimbursements', ['reimbursement_date'])
    op.create_index('idx_reimbursement_person', 'reimbursements', ['reimbursed_to'])
    
    # Travels table
    op.create_table(
        'travels',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    op.create_index('idx_travel_date', 'travels', ['start_date'])
    
    # Travel expenses table
    op.create_table(
        'travel_expenses',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('travel_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False, server_default='0'),
        sa.Column('paid_by', sa.Text(), nullable=False),
        sa.Column('category', sa.Text(), nullable=False),
        sa.Column('expense_date', sa.Date(), nullable=False),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['travel_id'], ['travels.id'], ondelete='CASCADE')
    )
    op.create_index('idx_travel_expense_travel', 'travel_expenses', ['travel_id'])
    op.create_index('idx_travel_expense_category', 'travel_expenses', ['travel_id', 'category'])
    op.create_index('idx_travel_expense_date', 'travel_expenses', ['expense_date'])
    
    # Budgets table
    op.create_table(
        'budgets',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('category', sa.Text(), nullable=False),
        sa.Column('monthly_limit', sa.Float(), nullable=False, server_default='0'),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('month', sa.Integer(), nullable=False),
        sa.Column('notes', sa.Text()),
        sa.UniqueConstraint('category', 'year', 'month')
    )
    op.create_index('idx_budget_month', 'budgets', ['year', 'month'])
    op.create_index('idx_budget_category', 'budgets', ['category', 'year', 'month'])


def downgrade() -> None:
    """Drop all tables."""
    # Drop in reverse order of creation (respecting foreign keys)
    op.drop_table('budgets')
    op.drop_table('travel_expenses')
    op.drop_table('travels')
    op.drop_table('reimbursements')
    op.drop_table('expense_logs')
    op.drop_table('settlements')
    op.drop_table('stuff_types')
    op.drop_table('fixed_expense_payments')
    op.drop_table('fixed_expense_types')
    op.drop_table('fixed_expenses')
    op.drop_table('other_expenses')
    op.drop_table('stuff_expenses')
    op.drop_table('utility_expenses')
    op.drop_table('food_expenses')
