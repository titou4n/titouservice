# blueprints/bank/routes.py
# Préfixe : /titoubank  (défini dans create_app)

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


# ── Accueil ──────────────────────────────────────────────────────────────────

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


# ── Retrait ──────────────────────────────────────────────────────────────────

@bp.route('/withdrawl', methods=['GET', 'POST'])
@bp.route('/withdrawl/', methods=['GET', 'POST'])
@login_required
def withdrawl():

    if request.method == 'GET':
        return render_template('bank/titoubank_withdrawl.html', id=current_user.id)

    amount = int(request.form['withdrawl'])
    success, message = process_withdrawl(current_user.id, amount)
    flash(message, "success" if success else "error")
    return redirect(url_for('bank.withdrawl'))


# ── Virement ─────────────────────────────────────────────────────────────────

@bp.route('/transfer', methods=['GET', 'POST'])
@bp.route('/transfer/', methods=['GET', 'POST'])
@login_required
def transfer():
    if request.method == 'GET':
        return render_template('bank/titoubank_transfer.html',
            id=current_user.id,
            all_transfer_history=ext.db_bank_repository.get_transfers_by_account_id(current_user.id),
        )

    amount      = int(request.form['transfer_value'])
    receiver_id = int(request.form['id_receiver'])

    success, message = process_transfer(current_user.id, receiver_id, amount)
    flash(message, "success" if success else "error")
    return redirect(url_for('bank.transfer'))


# ── Bourse (BTC/USD) ──────────────────────────────────────────────────────────

@bp.route('/stock_market', methods=['GET'])
@bp.route('/stock_market/', methods=['GET'])
@login_required
def titoubank_stock_market():
    data, error = get_stock_market_data(current_user.id)
    if error:
        flash(error)
        return render_template('bank/titoubank_stock_market.html', id=current_user.id)

    return render_template('bank/titoubank_stock_market.html', id=current_user.id, **data)


@bp.route('/stock_market/sell', methods=['POST'])
@bp.route('/stock_market/sell/', methods=['POST'])
@login_required
def titoubank_stock_market_sell():
    stock_number = float(request.form['stock_number'])

    success, message = process_sell(current_user.id, stock_number)
    flash(message)
    return redirect(url_for('bank.titoubank_stock_market'))


@bp.route('/stock_market/sell_all', methods=['POST'])
@bp.route('/stock_market/sell_all/', methods=['POST'])
@login_required
def titoubank_stock_market_sell_all():
    success, message = process_sell_all(current_user.id)
    flash(message)
    return redirect(url_for('bank.titoubank_stock_market'))


@bp.route('/stock_market/buy', methods=['POST'])
@bp.route('/stock_market/buy/', methods=['POST'])
@login_required
def titoubank_stock_market_buy():
    stock_number = float(request.form['stock_number'])

    success, message = process_buy(current_user.id, stock_number)
    flash(message)
    return redirect(url_for('bank.titoubank_stock_market'))
