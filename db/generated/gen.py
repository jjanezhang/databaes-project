import random
from werkzeug.security import generate_password_hash
import csv
from faker import Faker

num_users = 300
num_products = 4000
num_orders = 12000
max_purchases_per_order = 5
max_sellers_per_product = 4
likelihood_of_rating = 80 # out of 100

product_categories = ['Food', 'Clothing', 'Pet Supplies', 'Health & Beauty', 'Home', 'Electronics', 'Entertainment', 'Other']
image_placeholders = [
    'https://i0.wp.com/petmassage.com/wp-content/uploads/profile-pic-placeholder.png?w=512&ssl=1,3',
    'https://sweatpantsandcoffee.com/wp-content/uploads/2018/09/940x450-This-is-fine.jpg'
]

Faker.seed(0)
fake = Faker()


def get_csv_writer(f):
    return csv.writer(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)


def gen_users(num_users):
    with open('Users.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Users...', end=' ', flush=True)
        for uid in range(num_users):
            if uid % 10 == 0:
                print(f'{uid}', end=' ', flush=True)
            profile = fake.profile()
            email = profile['mail']
            plain_password = f'pass{uid}'
            password = generate_password_hash(plain_password)
            name_components = profile['name'].split(' ')
            firstname = name_components[0]
            lastname = name_components[-1]
            writer.writerow([uid, email, password, firstname, lastname, random.randint(0, 1000)])
        print(f'{num_users} generated')
    return


def gen_products(num_products):
    available_pids = []
    with open('Products.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Products...', end=' ', flush=True)
        for pid in range(num_products):
            if pid % 100 == 0:
                print(f'{pid}', end=' ', flush=True)
            name = fake.sentence(nb_words=4)[:-1]
            price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
            available = 'true'
            available_pids.append(pid)
            category = fake.random_element(elements=product_categories)
            description = fake.sentence()
            image_url = fake.random_element(elements=image_placeholders)
            created_by = fake.random_int(min=0, max=num_users - 1)
            writer.writerow([pid, name, price, category, available, description, image_url, created_by])
        print(f'{num_products} generated; {len(available_pids)} available')
    return available_pids


def gen_orders(num_orders):
    orders = []
    with open('Orders.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Orders...', end=' ', flush=True)
        for id in range(num_orders):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            uid = fake.random_int(min=0, max=num_users-1)
            time_placed = fake.date_time()
            writer.writerow([id, uid, time_placed])
            orders.append([id, uid, time_placed])
        print(f'{num_orders} generated')
    return orders

def gen_purchases(orders):
    purchases = []
    with open('Purchases.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Purchases...', end=' ', flush=True)
        for id in range(len(orders)):
            if id % 100 == 0:
                print(f'{id}', end=' ', flush=True)
            num_purchases = fake.random_int(min = 1, max=max_purchases_per_order)
            for _ in range(num_purchases):
                oid = orders[id][0]
                pid = fake.random_element(elements=available_pids)
                sid = fake.random_int(min=0, max=num_users-1)
                fulfilled = fake.random_element(['true', 'false'])
                time_fulfilled = None
                if fulfilled == 'true':
                    time_fulfilled = fake.date_time()
                quantity = fake.random_int(min=0, max=10)
                price = f'{str(fake.random_int(max=500))}.{fake.random_int(max=99):02}'
                purchase = [oid, pid, sid, fulfilled, time_fulfilled, quantity, price]
                writer.writerow(purchase)
                purchases.append(purchase)
        print(f'Purchases for {len(orders)} orders generated')
    return purchases

def gen_inventory():
    with open('Inventory.csv', 'w') as f:
        writer = get_csv_writer(f)
        print('Inventory...', end=' ', flush=True)
        for pid in available_pids:
            num_sellers = fake.random_int(min = 0, max = max_sellers_per_product)
            sellers = set()
            for _ in range(num_sellers):
                uid = fake.random_int(min=0, max=num_users-1)
                if uid in sellers:
                    continue
                sellers.add(uid)
                quantity = fake.random_int(min=0, max=1000)
                writer.writerow([uid, pid, quantity])
        print('Generated inventory')
    return

def gen_ratings(purchases, orders):
    with open('Ratings.csv', 'w') as f:
        has_rated_product = set()
        writer = get_csv_writer(f)
        print('Ratings...', end=' ', flush=True)
        for purchase in purchases:
            corresponding_order = None
            for order in orders:
                if order[0] == purchase[0]:
                    corresponding_order = order
            if corresponding_order is None:
                print("UH OH-------------")
                continue
            # Rate product
            if fake.random_int(min=0, max=100) < likelihood_of_rating:
                uid = corresponding_order[1]
                pid = purchase[1]
                ids = (uid, pid)
                if ids in has_rated_product:
                    continue
                has_rated_product.add(ids)
                rating = fake.random_int(min = 1, max = 5)
                review = fake.sentence()
                upvotes = fake.random_int(min = 0, max=num_users - 1)
                time_added = fake.date_time_between(start_date = corresponding_order[2])
                writer.writerow([uid, pid, rating, review, upvotes, time_added])
        print('Generated ratings')

def gen_sellers(purchases, orders):
    with open('Sellers.csv', 'w') as f:
        has_rated_seller = set()
        writer = get_csv_writer(f)
        print('Sellers...', end=' ', flush=True)
        for purchase in purchases:
            corresponding_order = None
            for order in orders:
                if order[0] == purchase[0]:
                    corresponding_order = order
            if corresponding_order is None:
                print("UH OH-------------")
                continue
            # Rate seller
            if fake.random_int(min = 0, max=100) < likelihood_of_rating:
                ids = (corresponding_order[1], purchase[2])
                if ids in has_rated_seller:
                    break
                has_rated_seller.add(ids)
                rating = fake.random_int(min = 1, max = 5)
                review = fake.sentence()
                upvotes = fake.random_int(min = 0, max=num_users - 1)
                time_added = fake.date_time_between(start_date = corresponding_order[2])
                writer.writerow([purchase[2], corresponding_order[1], rating, review, upvotes, time_added])
        print('Generated sellers')

gen_users(num_users)
available_pids = gen_products(num_products)
orders = gen_orders(num_orders)
purchases = gen_purchases(orders)
gen_ratings(purchases, orders)
gen_sellers(purchases, orders)
gen_inventory()
