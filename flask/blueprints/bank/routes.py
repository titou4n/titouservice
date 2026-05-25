# blueprints/bank/routes.py

import logging
from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user

from blueprints.bank import bp
from blueprints.bank.services import (
    process_withdrawl,
    process_transfer,
    get_stock_market_data,
    process_sell,
    process_sell_all,
    process_buy,
)
import extensions as ext

logger = logging.getLogger(__name__)


# Validation helpers
def validate_amount(amount_str, min_amount=0, max_amount=1_000_000_000):
    """Valide et retourne le montant ou lève une exception"""
    try:
        amount = int(amount_str)
        if amount < min_amount:
            raise ValueError(f"Amount must be at least {min_amount}")
        if amount > max_amount:
            raise ValueError(f"Amount must not exceed {max_amount}")
        return amount
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError("Amount must be a valid number")
        raise e


def validate_receiver_exists(receiver_id):
    """Vérifie que le destinataire existe"""
    try:
        receiver = ext.db_account_repository.get_by_id(receiver_id)
        if not receiver:
            raise ValueError(f"User {receiver_id} does not exist")
        return receiver_id
    except Exception as e:
        raise ValueError(f"Invalid receiver: {str(e)}")


@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
@login_required
def titoubank():
    pay_db = ext.db_account_repository.get_pay_by_id(current_user.id)
    if pay_db is None:
        pay_db = 0.0

    return render_template('bank/titoubank_home.html',
        id=current_user.id,
        pay=round(pay_db, 2),
        all_transfer_history=ext.db_bank_repository.get_transfers_by_account_id(current_user.id),
    )


@bp.route('/withdrawl', methods=['GET', 'POST'])
@bp.route('/withdrawl/', methods=['GET', 'POST'])
@login_required
def withdrawl():
    if request.method == 'GET':
        return render_template('bank/titoubank_withdrawl.html', id=current_user.id)

    try:
        amount_str = request.form.get('withdrawl', '').strip()
        if not amount_str:
            flash('Amount is required.', 'error')
            return redirect(url_for('bank.withdrawl'))

        amount = validate_amount(amount_str)
        success, message = process_withdrawl(current_user.id, amount)
        flash(message, "success" if success else "error")
        return redirect(url_for('bank.withdrawl'))
    except ValueError as e:
        flash(f'Invalid amount: {str(e)}', 'error')
        logger.warning("Invalid withdrawal amount for user %s: %s", current_user.id, str(e))
        return redirect(url_for('bank.withdrawl'))
    except Exception as e:
        flash('An error occurred. Please try again.', 'error')
        logger.error("Error processing withdrawal for user %s: %s", current_user.id, str(e))
        return redirect(url_for('bank.withdrawl'))


@bp.route('/transfer', methods=['GET', 'POST'])
@bp.route('/transfer/', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'GET':
        return render_template('bank/titoubank_transfer.html',
            id=current_user.id,
            all_transfer_history=ext.db_bank_repository.get_transfers_by_account_id(current_user.id),
        )

    try:
        amount_str = request.form.get('transfer_value', '').strip()
        receiver_str = request.form.get('id_receiver', '').strip()

        if not amount_str or not receiver_str:
            flash('All fields are required.', 'error')
            return redirect(url_for('bank.transfer'))

        # Valider le montant
        amount = validate_amount(amount_str)

        # Valider le destinataire
        receiver_id = validate_receiver_exists(int(receiver_str))

        # Vérifier que l'utilisateur ne se transfère pas à lui-même
        if receiver_id == current_user.id:
            flash('You cannot transfer to yourself.', 'error')
            logger.warning("User %s attempted self-transfer", current_user.id)
            return redirect(url_for('bank.transfer'))

        success, message = process_transfer(current_user.id, receiver_id, amount)
        flash(message, "success" if success else "error")
        return redirect(url_for('bank.transfer'))
    except ValueError as e:
        flash(f'Invalid input: {str(e)}', 'error')
        logger.warning("Invalid transfer data for user %s: %s", current_user.id, str(e))
        return redirect(url_for('bank.transfer'))
    except Exception as e:
        flash('An error occurred. Please try again.', 'error')
        logger.error("Error processing transfer for user %s: %s", current_user.id, str(e))
        return redirect(url_for('bank.transfer'))


@bp.route('/stock_market', methods=['GET'])
@bp.route('/stock_market/', methods=['GET'])
@login_required
def titoubank_stock_market():
    try:
        data, error = get_stock_market_data(current_user.id)
        if error:
            flash(error, 'error')
            return render_template('bank/titoubank_stock_market.html', id=current_user.id)

        return render_template('bank/titoubank_stock_market.html', id=current_user.id, **data)
    except Exception as e:
        flash('An error occurred loading stock market data.', 'error')
        logger.error("Error loading stock market data: %s", str(e))
        return render_template('bank/titoubank_stock_market.html', id=current_user.id)


@bp.route('/stock_market/sell', methods=['POST'])
@bp.route('/stock_market/sell/', methods=['POST'])
@login_required
def titoubank_stock_market_sell():
    try:
        stock_str = request.form.get('stock_number', '').strip()
        if not stock_str:
            flash('Stock number is required.', 'error')
            return redirect(url_for('bank.titoubank_stock_market'))

        stock_number = float(stock_str)
        success, message = process_sell(current_user.id, stock_number)
        flash(message, "success" if success else "error")
        return redirect(url_for('bank.titoubank_stock_market'))
    except ValueError:
        flash('Invalid stock number format.', 'error')
        logger.warning("Invalid stock sell amount")
        return redirect(url_for('bank.titoubank_stock_market'))
    except Exception as e:
        flash('An error occurred. Please try again.', 'error')
        logger.error("Error selling stocks: %s", str(e))
        return redirect(url_for('bank.titoubank_stock_market'))


@bp.route('/stock_market/sell_all', methods=['POST'])
@bp.route('/stock_market/sell_all/', methods=['POST'])
@login_required
def titoubank_stock_market_sell_all():
    try:
        success, message = process_sell_all(current_user.id)
        flash(message, "success" if success else "error")
        return redirect(url_for('bank.titoubank_stock_market'))
    except Exception as e:
        flash('An error occurred. Please try again.', 'error')
        logger.error("Error selling all stocks: %s", str(e))
        return redirect(url_for('bank.titoubank_stock_market'))


@bp.route('/stock_market/buy', methods=['POST'])
@bp.route('/stock_market/buy/', methods=['POST'])
@login_required
def titoubank_stock_market_buy():
    try:
        stock_str = request.form.get('stock_number', '').strip()
        if not stock_str:
            flash('Stock number is required.', 'error')
            return redirect(url_for('bank.titoubank_stock_market'))

        stock_number = float(stock_str)
        success, message = process_buy(current_user.id, stock_number)
        flash(message, "success" if success else "error")
        return redirect(url_for('bank.titoubank_stock_market'))
    except ValueError:
        flash('Invalid stock number format.', 'error')
        logger.warning("Invalid stock buy amount")
        return redirect(url_for('bank.titoubank_stock_market'))
    except Exception as e:
        flash('An error occurred. Please try again.', 'error')
        logger.error("Error buying stocks: %s", str(e))
        return redirect(url_for('bank.titoubank_stock_market'))

