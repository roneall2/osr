import mysql.connector

# Setting up a cursor:
mycursor = None
mydb = None

last_user = 0
last_item = 0
last_receipt = 0
last_store = 0

def initialize():
    global mycursor, mydb, last_item, last_store, last_receipt
    # initialize tables
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="", 
        database='OSRdb'
    )
    mycursor = mydb.cursor()
    
    mycursor.execute("DROP TABLE IF EXISTS Item")
    mycursor.execute("DROP TABLE IF EXISTS Receipt")
    mycursor.execute("DROP TABLE IF EXISTS Store")
    mycursor.execute("DROP TABLE IF EXISTS User")
    mycursor.execute("CREATE TABLE User (UserID INT, budget REAL, name VARCHAR(255), password VARCHAR(255), PRIMARY KEY (UserID))")
    mycursor.execute("CREATE TABLE Store(StoreID INT, name VARCHAR(255), location VARCHAR(255), category VARCHAR(255), PRIMARY KEY (StoreID))")
    mycursor.execute("CREATE TABLE Receipt(PurchaseID INT, UserID INT, StoreID INT, subtotal float, total float, PRIMARY KEY (PurchaseID), FOREIGN KEY (UserID) REFERENCES User (UserID) ON DELETE CASCADE, FOREIGN KEY (StoreID) REFERENCES Store (StoreID) ON DELETE CASCADE)")
    mycursor.execute("CREATE TABLE Item(ItemID INT, PurchaseID INT, brand VARCHAR(255), name VARCHAR(255), price float, PRIMARY KEY (ItemID), FOREIGN KEY (PurchaseID) REFERENCES Receipt (PurchaseID) ON DELETE CASCADE)")
    

    # initialize demo user
    sql = "INSERT INTO User(UserID, budget, name, password) VALUES (%s, %s, %s, %s)"
    val = (0, 10000, "John Smith", "password")
    mycursor.execute(sql, val)

    # initialize demo store
    sql = "INSERT INTO Store (StoreID, name, location, category) VALUES (%s, %s, %s, %s)"
    val = (0, "Best Buy", "Champaign", "electronics")
    mycursor.execute(sql, val)

    # initialize demo store 2
    sql = "INSERT INTO Store (StoreID, name, location, category) VALUES (%s, %s, %s, %s)"
    val = (1, "Walmart", "Urbana", "electronics")
    mycursor.execute(sql, val)

    # initialize demo receipt
    sql = "INSERT INTO Receipt(PurchaseID, UserID, StoreID, subtotal, total) VALUES (%s, %s, %s, %s, %s)"
    val = (0, 0, 0, 2300.00, 2530.00)
    mycursor.execute(sql, val)

     # initialize demo receipt2
    sql = "INSERT INTO Receipt(PurchaseID, UserID, StoreID, subtotal, total) VALUES (%s, %s, %s, %s, %s)"
    val = (1, 0, 1, 1800.00, 1980.00)
    mycursor.execute(sql, val)

    # initialize demo items
    sql = "INSERT INTO Item(ItemID, PurchaseID, brand, name, price) VALUES (%s, %s, %s, %s, %s)"
    val = [
        (0, 0, "Apple", "AirPods", 200.00),
        (1, 0, "Nintendo", "Switch", 300.00),
        (2, 0, "Apple", "iPhone", 1800.00),
        (3, 1, "Apple", "iPhone", 1800.00)
    ]
    mycursor.executemany(sql, val)
    last_item += 3
    last_receipt += 1
    last_store += 1

    mydb.commit()

# returns number of items in a receipt
def items_per_receipt(user_id):
    global mycursor
    mycursor.execute("SELECT Receipt.PurchaseID, count(Item.ItemID) FROM Receipt LEFT OUTER JOIN Item ON Item.PurchaseID = Receipt.PurchaseID WHERE Receipt.UserID = %s GROUP BY Receipt.PurchaseID", (user_id,))
    return mycursor.fetchall()

# how many items from each brand have you bought from a store
def brand_per_store():
    global mycursor
    mycursor.execute("SELECT Item.brand, Store.name, count(Item.ItemID) FROM Item NATURAL JOIN Receipt JOIN Store ON Receipt.StoreID=Store.StoreID GROUP BY Store.name, Item.Brand")
    return mycursor.fetchall()

# returns all items that you purchased
def get_items(user_id):
    global mycursor
    mycursor.execute("SELECT * FROM Receipt JOIN Item ON Item.PurchaseID = Receipt.PurchaseID WHERE Receipt.UserID = %s", (user_id,))
    return mycursor.fetchall()

# returns items matching name
def find_items(user_id, item_name):
    global mycursor
    mycursor.execute("SELECT * FROM Receipt LEFT OUTER JOIN Item ON Item.PurchaseID = Receipt.PurchaseID WHERE Receipt.UserID = %s AND Item.name = %s", (user_id, item_name))
    return mycursor.fetchall()
    
# adds a receipt to the database
# store_id should be the return value of check_store
def add_receipt(user_id, store_id, subtotal, total):
    global mydb, mycursor, last_receipt
    sql = "INSERT INTO Receipt(PurchaseID, UserID, StoreID, subtotal, total) VALUES (%s, %s, %s, %s, %s)"
    last_receipt += 1
    val = (last_receipt, user_id, store_id, subtotal, total)
    mycursor.execute(sql, val)
    mydb.commit()

# delete a receipt from the database
def delete_receipt(purchase_id):
    global mydb, mycursor
    sql = "DELETE FROM Receipt WHERE PurchaseID = %s"
    val = (purchase_id,)
    mycursor.execute(sql, val)
    mydb.commit()

# returns store_id
def check_store(name, location, category):
    global mydb, mycursor, last_store
    mycursor.execute("SELECT StoreID FROM Store WHERE Store.name = %s AND Store.location = %s", (name, location))
    result = mycursor.fetchone()
    store_id = 0
    if result:
        return store_id
    else:
        last_store += 1
        store_id = last_store
    sql = "INSERT INTO Store (StoreID, name, location, category) VALUES (%s, %s, %s, %s)"
    val = (store_id, name, location, category)
    mycursor.execute(sql, val)
    mydb.commit()
    return store_id

# delete a store
def delete_store(store_id):
    global mydb, mycursor
    sql = "DELETE FROM Store WHERE StoreID = %s"
    val = (store_id,)
    mycursor.execute(sql, val)
    mydb.commit()

# adds an item to the database
def add_item(purchase_id, brand, name, price):
    global mydb, mycursor, last_item
    mycursor.execute("SELECT ItemID FROM Item WHERE Item.brand = %s AND Item.name = %s", (brand, name))
    result = mycursor.fetchone()
    item_id = 0
    if result:
        item_id = result
    else:
        last_item += 1
        item_id = last_item
    sql = "INSERT INTO Item(ItemID, PurchaseID, brand, name, price) VALUES (%s, %s, %s, %s, %s)"
    val = (item_id, purchase_id, brand, name, price)
    mycursor.execute(sql, val)
    mydb.commit()

# deletes a item and all the items related to that reciept
def delete_item(item_id):
    global mycursor, mydb
    sql = "DELETE FROM Item WHERE ItemId = %s"
    val = (item_id,)
    mycursor.execute(sql, val)
    mydb.commit()
    
# updates an item in the database
def update_item(ItemID, brand, name, price):
    global mydb, mycursor
    sql = "UPDATE Item SET brand = %s, name = %s, price = %s WHERE Item.ItemID = %s"
    val = (brand, name, price, ItemID)
    mycursor.execute(sql, val)
    mydb.commit()

# add user to the database
def add_user(name, password, budget):
    global mydb, mycursor, last_user
    last_user += 1
    user_id = last_user
    sql = "INSERT INTO User(UserID, budget, name, password) VALUES (%s, %s, %s, %s)"
    val = (user_id, budget, name, password)
    mycursor.execute(sql, val)
    mydb.commit()

# deletes user from the database
def delete_user(UserID):
    global mydb, mycursor
    sql = "DELETE FROM User WHERE UserID = %s"
    val = (UserID,)
    mycursor.execute(sql, val)
    mydb.commit()

def get_all_user_info(UserID):
    global mydb, mycursor
    # if this doesn't work, swap receipt and item in the join
    sql = "SELECT * FROM (Receipt NATURAL JOIN Store) AS R LEFT OUTER JOIN Item ON R.PurchaseID = Item.PurchaseID WHERE R.UserID = %s"
    val = (UserID,)
    sql2 = "SELECT * FROM User WHERE User.UserID = %s"
    val2 = (UserID,)
    return mycursor.execute(sql, val), mycursor.execute(sql2, val2)

# def get_spend(user_id):
#     global mycursor
#     mycursor.execute("SELECT * FROM Receipt LEFT OUTER JOIN Item ON Item.PurchaseID = Receipt.PurchaseID WHERE Receipt.UserID = %s GROUP BY ", query)
#     return mycursor.fetchall()

if __name__ == "__main__":
    print('hi')
