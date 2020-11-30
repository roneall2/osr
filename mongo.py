# Write out Mongo to aggregate from user data the following Visualizations:
# - Total amount spent
# - Amount spent per Brand
# - Amount spent per Store
# - Amount spent per Category

import pymongo
from db import get_all_user_info
from bson.code import Code

myclient = None
mydb = None
local_client = 'mongodb://localhost:27017/'
db_name = 'user_data'


def get_number_categories(user_id):
    update_user(user_id)
    col = mydb[user_id]
    map = Code("function () {this.category.forEach(function(z) {emit(z, 1);});}")
    reduce = Code("function (key, values) {var total = 0;for (var i = 0; i < values.length; i++) {total += values[i];}return total;}")
    return col.map_reduce(map, reduce, "myresults")

# Returns combined aggregate values across all recipts by category
def get_category_spend(user_id):
    update_user(user_id)
    col = mydb[user_id]
    return col.aggregate({'$group': {'_id': "$category", 'total_spent': {'$sum': '$total'}, 'avg_spend': {'$avg': '$total'}, 'biggest_spend': {'$max:' "$total"}}})

# Returns combined aggregate values across all recipts by brand
def get_brand_spend(user_id):
    update_user(user_id)
    col = mydb[user_id]
    return col.aggregate({'$group': {'_id': "$brand", 'total_spent': {'$sum': '$total'}, 'avg_spend': {'$avg': '$total'}, 'biggest_spend': {'$max:' "$total"}}})

# Returns combined aggregate values across all recipts by store 
def get_store_spend(user_id):
    update_user(user_id)
    col = mydb[user_id]
    return col.aggregate({'$group': {'_id': "$StoreID", 'total_spent': {'$sum': '$total'}, 'avg_spend': {'$avg': '$total'}, 'biggest_spend': {'$max:' "$total"}}})

# Returns combined aggregate values across all recipts 
def get_amount_spent(user_id):
    update_user(user_id)
    col = mydb[user_id]
    return col.aggregate({'$group': {'_id': "$UserID", 'total_spent': {'$sum': '$total'}, 'avg_spend': {'$avg': '$total'}, 'biggest_spend': {'$max:' "$total"}}})

# Ensures that the most recent data is pulled from MySQL and pushed into Mongo
def update_user(user_id):
    col = mydb[user_id]
    user_data, user_info = get_all_user_info(user_id)
    for record in user_data:
        doc = {'UserID': user_info[0], 'budget': user_info[1], 'name': user_info[2], 'PurchaseID': record[0], 'UserID': record[1], 'StoreID': record[2], 'subtotal': record[3], 'total': record[4], 'name': record[5], 'location': record[6], 'category': record[7], 'ItemID': record[8], 'brand': record[9], 'item_name': record[10], 'price': record[11]}
        col.update(doc, doc, {'upsert':True})
    

# Initializes the values for connecting to the Mongo Server
def setup(user_id):
    myclient = pymongo.MongoClient(local_client)
    mydb = myclient[db_name]
    

