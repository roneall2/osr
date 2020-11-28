from flask import Flask, render_template, redirect, url_for, request
import db as db

app = Flask(__name__)

@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login_page():
    error = None
    db.initialize()
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home_page'))
    return render_template('login.html', error=error)

inputdata = []
@app.route('/home', methods=['GET', 'POST'])
def home_page():
    global inputdata
    inputdata = db.get_items(0)
    if request.method == 'POST':
        item_name = request.form['name']
        print(item_name)
        tempdata = db.find_items(0, item_name)
        return render_template('index.html', data=tempdata)
    return render_template('index.html', data=inputdata)

@app.route('/budget')
def budget_page():
    return render_template('budget.html')

receipt = {}
@app.route('/receipt', methods=['GET', 'POST'])
def receipt_page():
    global receipt
    if request.method == 'POST':
        receipt = request.form.to_dict(flat=False)
        storeName = receipt["name"]
        total= receipt["total"]
        subtotal = receipt["subtotal"]
        category = receipt["category"]
        storeLocation = receipt["location"]
        storeId= db.check_store(storeName[0], storeLocation[0], category[0])
        db.add_receipt(0, storeId, total[0], subtotal[0])
        print(receipt)
        return redirect(url_for('receipt_page'))
    return render_template('receipt.html')

item = {}
@app.route('/items', methods=['GET', 'POST'])
def items_page():
    global item
    if request.method == 'POST':
        item = request.form.to_dict(flat=False)
        purchaseId = item["purchaseid"]
        brand= item["brand"]
        name=item["name"]
        price = item["price"]
        db.add_item(purchaseId[0], brand[0], name[0], price[0])
        print(item)
        return redirect(url_for('items_page'))
    return render_template('items.html')

@app.route('/delete', methods=['GET', 'POST'])
def delete_page():
    if request.method == 'POST':
        purchaseid = request.form['purchaseid']
        db.delete_item(purchaseid)
        print(purchaseid)
        return redirect(url_for('delete_page'))
    return render_template('delete.html')

@app.route('/update', methods=['GET', 'POST'])
def update_page():
    if request.method == 'POST':
        item = request.form.to_dict(flat=False)
        itemID = item["itemid"]
        brand= item["brand"]
        name=item["name"]
        price = item["price"]
        db.update_item(itemID[0], brand[0], name[0], price[0])
        print(item)
        return redirect(url_for('update_page'))
    return render_template('update.html')

@app.route('/stats', methods=['GET', 'POST'])
def stats_page():
    num_items_in_receipt = db.items_per_receipt(0)
    num_items_per_brand = db.brand_per_store()
    return render_template('stats.html', receipt=num_items_in_receipt, brand=num_items_per_brand)