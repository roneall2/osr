# Write out Mongo to aggregate from user data the following Visualizations:
# - Total amount spent
# - Amount spent per Brand
# - Amount spent per Store
# - Amount spent per Category

import pymongo
from db import get_all_user_info
from bson.code import Code
import db

myclient = None
mydb = None
local_client = 'mongodb://localhost:27017/'
db_name = 'user_data'


def get_categories(user_id):
    global myclient, mydb
    update_user(user_id)
    col = mydb[str(user_id)]
    return col.distinct('category')

def get_top_store_spend(user_id, limit):
    global myclient, mydb
    update_user(user_id)
    col = mydb[str(user_id)]
    m = col.aggregate([{'$group': {'_id': "$StoreID", 'total_spent': {'$sum': '$price'}, 'items': {'$push': {'item_name': '$item_name', 'price': '$price'}}}}, {'$sort': {'total_spent': 1}}, {'$limit': limit}])
    return [dict({'store_name': db.get_store_name(x['_id'])}, **x) for x in m]

def get_most_expensive(user_id, limit):
    global myclient, mydb
    update_user(user_id)
    col = mydb[str(user_id)]
    return col.aggregate([{'$group': {'_id': "$UserID", 'items': {'$push': {'name': '$item_name', 'price': '$price'}}}}, {'$unwind': '$items'}, {'$sort': {'name.price': 1}}, {'$limit': limit}])

def get_top_category_spend(user_id, limit):
    global myclient, mydb
    update_user(user_id)
    col = mydb[str(user_id)]
    return col.aggregate([{'$group': {'_id': "$category", 'total_spent': {'$sum': '$price'}, 'items': {'$push': {'name': '$item_name', 'price': '$price'}}}}, {'$sort': {'total_spent': 1}}, {'$limit': limit}])

# Returns combined aggregate values across all recipts by category
def get_category_spend(user_id):
    global myclient, mydb
    update_user(user_id)
    col = mydb[str(user_id)]
    return  col.aggregate([{'$match': {'UserID': user_id}}, {'$group': {'_id': "$category", 'spend': {'$addToSet': '$total'}}}, {'$unwind': '$spend'}, {'$group': {'_id': '$_id', 'total_spent': {'$sum': '$spend'}, 'avg_spend': {'$avg': '$spend'}, 'biggest_spend': {'$max': "$spend"}}}])

# Returns combined aggregate values across all recipts by brand
def get_brand_spend(user_id):
    global myclient, mydb
    update_user(user_id)
    col = mydb[str(user_id)]
    return col.aggregate([{'$group': {'_id': "$brand", 'total_spent': {'$sum': '$price'}, 'avg_spend': {'$avg': '$price'}, 'biggest_spend': {'$max': "$price"}}}])

# Returns combined aggregate values across all recipts by store 
def get_store_spend(user_id):
    global myclient, mydb
    update_user(user_id)
    col = mydb[str(user_id)]
    m =  col.aggregate([{'$match': {'UserID': user_id}}, {'$group': {'_id': "$StoreID", 'spend': {'$addToSet': '$total'}}}, {'$unwind': '$spend'}, {'$group': {'_id': '$_id', 'total_spent': {'$sum': '$spend'}, 'avg_spend': {'$avg': '$spend'}, 'biggest_spend': {'$max': "$spend"}}}])
    return [dict({'store_name': db.get_store_name(x['_id'])}, **x) for x in m]

# Returns combined aggregate values across all recipts 
def get_amount_spent(user_id):
    global myclient, mydb
    update_user(user_id)
    col = mydb[str(user_id)]
    print(user_id)
    # print([x for x in ])
    return col.aggregate([{'$match': {'UserID': user_id}}, {'$group': {'_id': "$UserID", 'spend': {'$addToSet': '$total'}}}, {'$unwind': '$spend'}, {'$group': {'_id': '$_id', 'total_spent': {'$sum': '$spend'}, 'avg_spend': {'$avg': '$spend'}, 'biggest_spend': {'$max': "$spend"}}}])

def get_user_budget(user_id):
    _, user_info = get_all_user_info(user_id)
    return user_info[0][1]

# Ensures that the most recent data is pulled from MySQL and pushed into Mongo
def update_user(user_id):
    global myclient, mydb
    col = mydb[str(user_id)]
    user_data, user_info = get_all_user_info(user_id)
    userid, budget, name, password = user_info[0]
    for record in user_data:
        storeid, purchaseid, userid, subtotal, total, name, location, category, itemid, purchaseid, brand, itemname, itemprice = record
        # print(record)
        doc = {'UserID': userid, 'budget': budget, 'name': name, 'StoreID': storeid, 'PurchaseID': purchaseid, 'subtotal': subtotal, 'total': total, 'name': name, 'location': location, 'category': category, 'ItemID': itemid, 'brand': brand, 'item_name': itemname, 'price': itemprice}
        col.update({'UserID': userid, 'PurchaseID': purchaseid, 'ItemID': itemid}, doc, upsert=True)
    

# Initializes the values for connecting to the Mongo Server
def initialize_client():
    global myclient, mydb
    myclient = pymongo.MongoClient(local_client)
    mydb = myclient[db_name]
    

