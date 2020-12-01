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
    mycursor = mydb.cursor(buffered=True)
    
    mycursor.execute("DROP TABLE IF EXISTS Item")
    mycursor.execute("DROP TABLE IF EXISTS Receipt")
    mycursor.execute("DROP TABLE IF EXISTS Store")
    mycursor.execute("DROP TABLE IF EXISTS User")
    mycursor.execute("CREATE TABLE User (UserID INT, budget float, name VARCHAR(255), password VARCHAR(255), PRIMARY KEY (UserID))")
    mycursor.execute("CREATE TABLE Store(StoreID INT, name VARCHAR(255), location VARCHAR(255), category VARCHAR(255), PRIMARY KEY (StoreID))")
    mycursor.execute("CREATE TABLE Receipt(PurchaseID INT, UserID INT, StoreID INT, subtotal float, total float, PRIMARY KEY (PurchaseID), FOREIGN KEY (UserID) REFERENCES User (UserID) ON DELETE CASCADE, FOREIGN KEY (StoreID) REFERENCES Store (StoreID) ON DELETE CASCADE)")
    mycursor.execute("CREATE TABLE Item(ItemID INT, PurchaseID INT, brand VARCHAR(255), name VARCHAR(255), price float, PRIMARY KEY (ItemID), FOREIGN KEY (PurchaseID) REFERENCES Receipt (PurchaseID) ON DELETE CASCADE)")

    # set up triggers
    mycursor.execute("CREATE TRIGGER ReceiptTrig Before INSERT ON Receipt FOR EACH ROW BEGIN IF new.subtotal < 0 THEN SET new.subtotal = 0; END IF; IF new.total < 0 THEN SET new.total = 0; END IF; END;")
    mycursor.execute("CREATE TRIGGER StoreTrig Before INSERT ON Store FOR EACH ROW BEGIN IF new.name = \"\" THEN SET new.name = \"Unknown\"; END IF; IF new.location = \"\" THEN SET new.location = \"Unknown\"; END IF; IF new.category = \"\" THEN SET new.category = \"Unknown\"; END IF; END;")
    mycursor.execute("CREATE TRIGGER ItemTrig Before INSERT ON Item FOR EACH ROW BEGIN IF new.name = \"\" THEN SET new.name = \"Unknown\"; END IF; IF new.brand = \"\" THEN SET new.brand = \"Unknown\"; END IF; IF new.price < 0 THEN SET new.price = 0; END IF; END;")
    mycursor.execute("CREATE TRIGGER UserTrig Before INSERT ON User FOR EACH ROW BEGIN IF new.budget < 0 THEN SET new.budget = 0; END IF; END;")

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
    last_user = 0
    last_item = 0
    last_receipt = 0
    last_store = 0
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
    
# adds a receipt to the database, returns its purchase id
# store_id should be the return value of check_store
def add_receipt(user_id, store_id, subtotal, total):
    global mydb, mycursor, last_receipt
    sql = "INSERT INTO Receipt(PurchaseID, UserID, StoreID, subtotal, total) VALUES (%s, %s, %s, %s, %s)"
    last_receipt += 1
    val = (last_receipt, user_id, store_id, subtotal, total)
    mycursor.execute(sql, val)
    mydb.commit()
    return last_receipt

# delete a receipt from the database
def delete_receipt(purchase_id):
    global mydb, mycursor
    sql = "DELETE FROM Receipt WHERE PurchaseID = %s"
    val = (purchase_id,)
    mycursor.execute(sql, val)
    mydb.commit()

# returns store_id
# checks if a store exists and returns its store id; if it doesn't exist, instead adds it to the database
def check_store(name, location, category):
    global mydb, mycursor, last_store
    mycursor.execute("SELECT StoreID FROM Store WHERE Store.name = %s AND Store.location = %s", (name, location))
    result = mycursor.fetchone()
    if result:
        return result[0]
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

# adds an item to the database, returns its item id
def add_item(purchase_id, brand, name, price):
    global mydb, mycursor, last_item
    # if name == '':
    #     name = 'null'
    # if price == '':
    #     price = 'null'
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
    return item_id

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
    global mydb, mycursorc
    # if this doesn't work, swap receipt and item in the join
    sql = "SELECT * FROM Receipt NATURAL JOIN Store LEFT OUTER JOIN Item ON Receipt.PurchaseID = Item.PurchaseID WHERE Receipt.UserID = %s"
    val = (UserID,)
    sql2 = "SELECT * FROM User WHERE User.UserID = %s"
    val2 = (UserID,)
    mycursor.execute(sql, val)
    returned = [mycursor.fetchall()]
    mycursor.execute(sql2, val2)
    returned.append(mycursor.fetchall())
    return returned

def get_store_name(StoreID):
    sql = "SELECT name FROM Store WHERE Store.StoreID = %s"
    mycursor.execute(sql, (StoreID,))
    return mycursor.fetchone()[0]

if __name__ == "__main__":
    print('hi')
