# blueprints/bank/routes.py
# Préfixe : /titoubank  (défini dans create_app)

from flask import render_template, redirect, request, flash, url_for
from flask_login import login_required

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


# ── Accueil ──────────────────────────────────────────────────────────────────

@bp.route('', methods=['GET'])
@bp.route('/', methods=['GET'])
@login_required
def titoubank():
    user_id = ext.session_manager.get_current_user_id()
    return render_template('bank/titoubank_home.html',
        id=user_id,
        pay=round(ext.database_handler.get_pay(user_id), 2),
        all_transfer_history=ext.database_handler.get_all_bank_transfer(user_id),
    )


# ── Retrait ──────────────────────────────────────────────────────────────────

@bp.route('/withdrawl', methods=['GET', 'POST'])
@bp.route('/withdrawl/', methods=['GET', 'POST'])
@login_required
def withdrawl():
    user_id = ext.session_manager.get_current_user_id()

    if request.method == 'GET':
        return render_template('bank/titoubank_withdrawl.html', id=user_id)

    amount = int(request.form['withdrawl'])
    success, message = process_withdrawl(user_id, amount)
    flash(message, "success" if success else "error")
    return redirect(url_for('bank.withdrawl'))


# ── Virement ─────────────────────────────────────────────────────────────────

@bp.route('/transfer', methods=['GET', 'POST'])
@bp.route('/transfer/', methods=['GET', 'POST'])
@login_required
def transfer():
    user_id = ext.session_manager.get_current_user_id()

    if request.method == 'GET':
        return render_template('bank/titoubank_transfer.html',
            id=user_id,
            all_transfer_history=ext.database_handler.get_all_bank_transfer(user_id),
        )

    amount      = int(request.form['transfer_value'])
    receiver_id = int(request.form['id_receiver'])

    success, message = process_transfer(user_id, receiver_id, amount)
    flash(message, "success" if success else "error")
    return redirect(url_for('bank.transfer'))


# ── Bourse (BTC/USD) ──────────────────────────────────────────────────────────

@bp.route('/stock_market', methods=['GET'])
@bp.route('/stock_market/', methods=['GET'])
@login_required
def titoubank_stock_market():
    user_id = ext.session_manager.get_current_user_id()

    data, error = get_stock_market_data(user_id)
    if error:
        flash(error)
        return render_template('bank/titoubank_stock_market.html', id=user_id)

    return render_template('bank/titoubank_stock_market.html', id=user_id, **data)


@bp.route('/stock_market/sell', methods=['POST'])
@bp.route('/stock_market/sell/', methods=['POST'])
@login_required
def titoubank_stock_market_sell():
    user_id      = ext.session_manager.get_current_user_id()
    stock_number = float(request.form['stock_number'])

    success, message = process_sell(user_id, stock_number)
    flash(message)
    return redirect(url_for('bank.titoubank_stock_market'))


@bp.route('/stock_market/sell_all', methods=['POST'])
@bp.route('/stock_market/sell_all/', methods=['POST'])
@login_required
def titoubank_stock_market_sell_all():
    user_id = ext.session_manager.get_current_user_id()

    success, message = process_sell_all(user_id)
    flash(message)
    return redirect(url_for('bank.titoubank_stock_market'))


@bp.route('/stock_market/buy', methods=['POST'])
@bp.route('/stock_market/buy/', methods=['POST'])
@login_required
def titoubank_stock_market_buy():
    user_id      = ext.session_manager.get_current_user_id()
    stock_number = float(request.form['stock_number'])

    success, message = process_buy(user_id, stock_number)
    flash(message)
    return redirect(url_for('bank.titoubank_stock_market'))