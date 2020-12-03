from flask import Flask, render_template, redirect, url_for, request, send_from_directory
from werkzeug.utils import secure_filename
import db as db
import mongo as mongo
import OCR as ocr
app = Flask(__name__)

current_userid = -1

@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login_page():
    global current_userid
    error = None
    db.initialize_cursor()
    mongo.initialize_client()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        result = db.get_user_id(username)
        if result == None or password != result[1]:
            error = 'Invalid Credentials. Please try again.'
        else:
            current_userid = result[0]
            return redirect(url_for('home_page'))
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        budget = request.form['budget']
        db.add_user(username, password, budget)
        return redirect(url_for('login_page'))
    return render_template('register.html')

@app.route('/home', methods=['GET', 'POST'])
def home_page():
    global current_userid
    inputdata = db.get_items(current_userid)
    print(inputdata)
    if request.method == 'POST':
        item_name = request.form['name']
        print(item_name)
        tempdata = db.find_items(current_userid, item_name)
        print(tempdata)
        return render_template('index.html', data=tempdata)
    return render_template('index.html', data=inputdata)

@app.route('/upload', methods=['GET', 'POST'])
def upload_page():
    global current_userid
    if request.method == 'POST':
        # Save file to disk and call OCR function.
        file = request.files['file']
        file.save(secure_filename(file.filename))
        name = file.filename
        ocr.image2Text(name, current_userid)
        return redirect(url_for('upload_page'))
    return render_template('upload.html')

@app.route('/budget', methods=['GET', 'POST'])
def budget_page():
    global current_userid

    print(current_userid)
    # Budget setup
    used = [x['total_spent'] for x in mongo.get_amount_spent(current_userid)][0]
    budget = mongo.get_user_budget(current_userid)
    bar = [used, budget, (used/budget) * 100]
    print("Bar:", bar)
    print([x for x in mongo.get_amount_spent(current_userid)])
    if request.method == 'POST':
        newbudget = request.form['budget']
        db.update_budget(current_userid, newbudget)
        print([x for x in mongo.get_amount_spent(current_userid)])
        return redirect(url_for('budget_page'))

    # Spending by store
    data1 = [["Store", "Total"]]
    for i in mongo.get_store_spend(current_userid):
        newList = [i['store_name'], i['total_spent']]
        data1.append(newList)

    # Spending by brand
    data2 = [["Brand", "Total"]]
    for i in mongo.get_brand_spend(current_userid):
        newList = [i['_id'], i['total_spent']]
        data2.append(newList)

    # Spending by category
    data3 = [["Category", "Total"]]
    for i in mongo.get_category_spend(current_userid):
        newList = [i['_id'], i['total_spent']]
        data3.append(newList)
    return render_template('budget.html', bar=bar, data1=data1, data2=data2, data3=data3)

@app.route('/receipt', methods=['GET', 'POST'])
def receipt_page():
    global current_userid
    if request.method == 'POST':
        receipt = request.form.to_dict(flat=False)
        storeName = receipt["name"]
        total= receipt["total"]
        subtotal = receipt["subtotal"]
        category = receipt["category"]
        storeLocation = receipt["location"]
        storeId= db.check_store(storeName[0], storeLocation[0], category[0])
        db.add_receipt(current_userid, storeId, total[0], subtotal[0])
        print(receipt)
        return redirect(url_for('receipt_page'))
    return render_template('receipt.html')

@app.route('/items', methods=['GET', 'POST'])
def items_page():
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
    global current_userid
    num_items_in_receipt = db.items_per_receipt(current_userid)
    num_items_per_brand = db.brand_per_store()
    return render_template('stats.html', receipt=num_items_in_receipt, brand=num_items_per_brand)