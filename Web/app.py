from flask import Flask, render_template, request, redirect, url_for, session, jsonify, make_response, render_template_string
import pandas as pd
from openpyxl import load_workbook
import csv
from datetime import timedelta
import secrets
import geoip2.database
import user_agents
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors
import sqlite3
import numpy as np
from sklearn.metrics import ndcg_score

secret_key = secrets.token_hex(16)

app = Flask(__name__, template_folder="Templates")
app.config['SECRET_KEY'] = secret_key
app.permanent_session_lifetime = timedelta(minutes=60)
geoip_reader = geoip2.database.Reader('Web/static/GeoLite2-Country.mmdb')
app.config['DATABASE'] = '/git/Scientific-Research/database.db'

csv_file = 'users.csv'
DB_PATH = 'Web/static/GeoLite2-City.mmdb'

product_templates  = {
    1: 'products/All-Purpose-Bike-Stand.html',
    2: 'products/AWC-Logo-Cap.html',
    3: 'products/Bike-Wash-Dissolver.html',
    4: 'products/Cable-Lock.html',
    5: 'products/Classic-Vest.html',
    6: 'products/Fender-Set-Mountain.html',
    7: 'products/Full-Finger-Gloves.html',
    8: 'products/Half-Finger-Gloves.html',
    9: 'products/Headlights-Dual-Beam.html',
    10: 'products/Headlights-Weatherproof.html',
    11: 'products/HitchRack-4Bike.html',
    12: 'products/HLMountainTire.html',
    13: 'products/HLRoadTire.html',
    14: 'products/HydrationPack-70oz.html',
    15: 'products/LLMountainTire.html',
    16: 'products/LLRoadTire.html',
    17: 'products/LongSleeveLogoJersey.html',
    18: 'products/MenBibShorts.html',
    19: 'products/MenSportsShorts.html',
    20: 'products/Minipump.html',
    21: 'products/ML_Moutain_tire.html',
    22: 'products/MLroadtire.html',
    23: 'products/Mountain_bike_socks.html',
    24: 'products/Mountain_bottle_cage.html',
    25: 'products/Mountain_pump.html',
    26: 'products/Mountain_tire_tube.html',
    27: 'products/Patch_kit_ 8_patches.html',
    28: 'products/Racing_socks.html',
    29: 'products/Road_bottle_cage.html',
    30: 'products/Road_tire_tube.html',
    31: 'products/Short-Sleeve_Classic_Jersey.html',
    32: 'products/Sport-100_Helmet.html',
    33: 'products/Taillights-Battery-Power.html',
    34: 'products/Touring_Tire.html',
    35: 'products/Touring_tire_tube.html',
    36: 'products/Touring_Panniers.html',
    37: 'products/Water_Bottle_30oz.html',
    38: 'products/Woman_Mountain_Shorts.html',
    39: 'products/Women_tight.html'
}

def load_products():
    products = []
    try:
        with open('products.csv', 'r', newline='', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                if 'price' in row:
                    row['price'] = row['price'].replace(',', '.')
                    row['price'] = '$' + row['price']
                products.append(row)
    except FileNotFoundError:
        print("File not found.")
        products = []
    return products

def load_users():
    try:
        with open(csv_file, 'r', newline='') as file:
            reader = csv.DictReader(file)
            users = [row for row in reader]
    except FileNotFoundError:
        users = []
    return users

def save_users(users):
    with open(csv_file, 'w', newline='') as file:
        fieldnames = ['Username', 'Password', 'Email', 'Full name', 'Phone number']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)

def get_product_by_id(product_id):
    products = load_products()  # Sử dụng hàm load_products để lấy danh sách sản phẩm
    for product in products:
        if product.get('id') == str(product_id):  # Giả định rằng mỗi sản phẩm có trường 'id'
            return product
    return None  # Trả về None nếu không tìm thấy sản phẩm

def save_recommended_items(customer_id, recommended_items):
    # Đường dẫn file CSV
    csv_file_path = 'recommended_items.csv'
    
    # Mở file để ghi (thêm dữ liệu) với chế độ 'a'
    with open(csv_file_path, 'a', newline='', encoding='utf-8-sig') as file:
        writer = csv.writer(file)
        # Kiểm tra xem file đã có dữ liệu chưa để viết tiêu đề cột
        if file.tell() == 0:
            writer.writerow(['customer_id', 'recommended_product_ids'])
        # Ghi thông tin khách hàng và sản phẩm đề xuất vào file
        writer.writerow([customer_id, ','.join(map(str, recommended_items))])

def get_product_recommendation(product_id):
    # Gọi hàm để lấy danh sách sản phẩm đề xuất
    products_info = get_recommended_products()
    # Duyệt qua danh sách sản phẩm để tìm sản phẩm có ID tương ứng
    for product_info in products_info:
        if product_info.get('id') == str(product_id):  # So sánh ID sản phẩm
            return product_info
    return None  # Trả về None nếu không tìm thấy sản phẩm với ID tương ứng

def get_recommended_products():
    products_info = []
    with open('E:/Bài tập Python/z_Scientific-Research-main/recommended_item.csv', 'r', newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            product_info = {
                'id': int(row['recommended_product_ids']),  # Lấy id sản phẩm và chuyển đổi sang kiểu int
                'name': row['name'],   # Lấy tên sản phẩm
                'price': row['price'],  # Lấy giá sản phẩm
                'image': row['image']   # Lấy đường dẫn hình ảnh sản phẩm
            }
            products_info.append(product_info)
    return products_info

def load_data():
    train_df = pd.read_csv('E:/Bài tập Python/z_Gợi ý sản phẩm/train.csv')
    test_df = pd.read_csv('E:/Bài tập Python/z_Gợi ý sản phẩm/test.csv')
    return train_df, test_df

train_df, test_df = load_data()

selected_df = train_df[['customer_id', 'product_id']]
train_df['Purchase'] = 1
user_item_matrix = train_df.pivot_table(index='product_id', columns='customer_id', values='Purchase', fill_value=0)

# Filter out unpurchased products
user_item_matrix = user_item_matrix[user_item_matrix.sum(axis=1) > 0]

# Calculate item-item similarity
item_similarity = cosine_similarity(user_item_matrix)
item_similarity_df = pd.DataFrame(item_similarity, index=user_item_matrix.index, columns=user_item_matrix.index)

# Train kNN model
k = 5
model_knn = NearestNeighbors(metric='cosine', algorithm='brute', n_neighbors=k)
model_knn.fit(item_similarity)

# Generate some recommendations for a specific user
def recommend_items(customer_id, user_item_matrix, similarity_df, model_knn, k=5):
    bought_items = user_item_matrix.loc[:, customer_id][user_item_matrix.loc[:, customer_id] > 0].index.tolist()
    recommended_items = []

    for item in bought_items:
        item_index = user_item_matrix.index.get_loc(item)
        distances, indices = model_knn.kneighbors(similarity_df.iloc[item_index, :].values.reshape(1, -1), n_neighbors=k + 1)
        similar_items = user_item_matrix.index[indices.flatten()].tolist()

        # Loại bỏ các sản phẩm đã mua và trùng lặp từ danh sách đề xuất
        for item in similar_items:
            if item not in bought_items and item not in recommended_items:
                recommended_items.append(item)

    return recommended_items

# Create the test set
test_set = test_df[['customer_id', 'product_id']].copy()

# Add a 'Purchase' column with a value of 1 to indicate a purchase
test_set['Purchase'] = 1

# Pivot the test set to create a user-item matrix
test_user_item_matrix = test_set.pivot_table(index='product_id', columns='customer_id', values='Purchase', fill_value=0)

# Ensure 'Purchase' is treated as binary (1 if purchased, 0 if not)
test_user_item_matrix = test_user_item_matrix.map(lambda x: 1 if x > 0 else 0)

def calculate_ndcg(customer_id, user_item_matrix, recommended_items, k, test_set=None):
    #Lấy các sản phẩm đã mua từ tập test (nếu có)
    if test_set is not None and customer_id in test_set.columns:
        test_purchased_items = test_set.loc[:, customer_id][test_set.loc[:, customer_id] > 0].index.tolist()
    else:
        print(f"Khong tim thay Customer ID {customer_id} trong cot DataFrame test_set hoặc test_set khong được cung cap.")
        return 0  # Trả về 0 nếu không có thông tin tập test

    # Tạo danh sách tổng hợp các sản phẩm từ tập test
    all_items = test_purchased_items

    # Lấy chỉ số DCG của các sản phẩm đã đề xuất
    dcg = 0
    for i in range(min(k, len(recommended_items))):
        item = recommended_items[i]
        relevance = 1 if item in test_purchased_items else 0
        rank = i + 1
        dcg += (2 ** relevance - 1) / np.log2(rank + 1)

    # Lấy chỉ số IDCG
    idcg = 0
    for i in range(min(k, len(test_purchased_items))):
        relevance = 1
        rank = i + 1
        idcg += (2 ** relevance - 1) / np.log2(rank + 1)

    #Tính chỉ số NDCG
    ndcg = dcg / idcg if idcg > 0 else 0

    return ndcg

#Test the model on the test set
target_customer_id = 30118   # Chọn customer_id cần hiển thị
show_results = False  # Biến kiểm soát việc hiển thị kết quả

for customer_id in test_df['customer_id'].unique():
   # Ensure the customer_id exists in user_item_matrix
    if customer_id in user_item_matrix.columns:
        recommended_items = recommend_items(customer_id, user_item_matrix, item_similarity_df, model_knn, k=5)
        ndcg_score = calculate_ndcg(customer_id, user_item_matrix, recommended_items, k=5, test_set=test_user_item_matrix)

        # Lưu thông tin sản phẩm đề xuất vào file CSV
        save_recommended_items(customer_id, recommended_items)

        #Kiểm tra xem customer_id hiện tại có phải là target_customer_id không
        if customer_id == target_customer_id:
            show_results = True
            print(f"Customer ID: {customer_id}")
            print("Danh sach san pham duoc de xuat:", recommended_items)
            print("Chi so NDCG:", ndcg_score)
            break  # Dừng vòng lặp nếu đã tìm thấy customer_id cần hiển thị

# Kiểm tra xem có hiển thị kết quả hay không
if not show_results:
    print(f"Khong tim thay thong tin cho customer_id: {target_customer_id}")

# Test the model on the test set
show_results = False  # Biến kiểm soát việc hiển thị kết quả
# Initialize variables to store total NDCG and count of customers
total_ndcg = 0
customer_count = 0

def get_location(ip):
    with geoip2.database.Reader(DB_PATH) as reader:
        try:
            response = reader.city(ip)
            country = response.country.name
            city = response.city.name
            return country, city
        except geoip2.errors.AddressNotFoundError:
            return "Not found", None

users = load_users()

@app.route('/')
def index():
    # Chuyển hướng trực tiếp đến trang home
    return redirect(url_for('home'))

@app.route('/home')
def home():
    products = load_products()
    username = session.get('username', 'Guest')
    return render_template('/main/home.html', products=products, username=username)

@app.route('/dashboard')
def dashboard():
    products = load_products()
    username = session.get('username')
    if not username:
        # Chuyển hướng người dùng về trang đăng nhập nếu không tìm thấy username trong session
        return redirect(url_for('login'))
    return render_template('/main/dashboard.html', products=products, username=username)

@app.route('/register', methods=['GET', 'POST'])
def register():
    global users

    if request.method == 'POST':
        email = request.form['email']
        fullname = request.form['full_name']
        phone = request.form['phone']
        username = request.form['username']
        password = request.form['password']

        if any(user['Username'] == username for user in users):
            message = "User already exists. Please choose another username."
            return render_template('/main/register.html', message=message)
        else:
            new_user = {'Email': email,'Full name': fullname, 'Phone number': phone, 'Username': username, 'Password': password}
            users.append(new_user)

            save_users(users)  # Lưu thông tin người dùng vào tệp CSV

            # Thiết lập session cho người dùng mới
            session['username'] = username

            # Chuyển hướng người dùng đến trang chủ hoặc dashboard
            return redirect(url_for('home'))  # Hoặc 'dashboard' nếu bạn muốn

    return render_template('/main/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    global users

    message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Tìm kiếm người dùng theo tên đăng nhập
        user = next((user for user in users if user['Username'] == username), None)

        if user and user['Password'] == password:
            session['username'] = username  # Lưu thông tin người dùng vào session
            return redirect(url_for('dashboard'))  # Chuyển hướng đến trang dashboard
        else:
            message = "Username or password is incorrect."
    # Xác định thông tin về người dùng
    ip_address = request.remote_addr
    country = get_country_from_ip(ip_address)
    user_agent = user_agents.parse(request.headers['User-Agent'])
    browser = user_agent.browser.family

    # Thiết lập cookie với thông tin
    response = make_response(render_template('/main/login.html', message=message))
    response.set_cookie('Location', f'Country: {country}, Browser: {browser}')
    return response

def get_country_from_ip(ip):
    try:
        response = geoip_reader.country(ip)
        return response.country.iso_code
    except geoip2.errors.AddressNotFoundError:
        return 'Unknown'

@app.route('/logout', methods=['POST'])
def logout():
    # Xóa thông tin người dùng từ phiên
    session.pop('username', None)
    # Chuyển hướng về trang đăng nhập
    return redirect(url_for('home'))

@app.route('/cart')
def cart():
    # Xử lý logic cho trang giỏ hàng
    products = load_products()
    cart_items = session.get('cart', [])
    total_amount = sum(int(item['quantity']) * float(item['price'][1:]) for item in cart_items)
    return render_template('/main/cart.html', products=products, cart_items=cart_items, total_amount=total_amount)

customer_templates= {
    30118:'/recommendations/30118.html'
}

@app.route('/recommendations/<int:customer_id>', methods=['GET', 'POST'])
def recommendations(customer_id):
    products_info = get_product_recommendation(customer_id)
    template_name = customer_templates.get(customer_id)
    if template_name:
        # Kiểm tra nếu products_info là None, thì cung cấp một danh sách rỗng
        if products_info is None:
            print('Emty')
            products_info = []
        return render_template(template_name, products_info=products_info)
    else:
        return "Customer not found!", 404

@app.route('/product/product<int:product_id>')
def product_detail(product_id):
    template_name = product_templates.get(product_id)
    if template_name:
        product = get_product_by_id(product_id)
        if product:
            return render_template(template_name, product=product)
        else:
            return "Product not found!", 404    
    else:
        return "Product not found!", 404

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    quantity = request.args.get('quantity', default=1, type=int)
    product = get_product_by_id(product_id)

    if product:
        if 'cart' not in session:
            session['cart'] = []

        # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
        found = False
        for item in session['cart']:
            if item['id'] == product_id:
                item['quantity'] += quantity  # Cập nhật số lượng nếu sản phẩm đã có
                found = True
                break

        if not found:
            # Thêm sản phẩm mới vào giỏ hàng nếu chưa có
            session['cart'].append({'id': product_id, 'name': product['name'], 'quantity': quantity, 'price': product['price']})

        session.modified = True  # Đánh dấu session đã thay đổi

        return "The product has been added to cart."
    else:
        return "Product does not exist.", 404

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    if 'cart' not in session or not session['cart']:
        return jsonify({'status': 'error', 'message': 'The shopping cart does not exist or is empty.'})

    data = request.json
    if 'product_id' not in data:
        return jsonify({'status': 'error', 'message': 'No product ID.'})

    try:
        product_id = int(data['product_id'])  # Chuyển đổi product_id sang int
    except ValueError:
        return jsonify({'status': 'error', 'message': 'The product ID is invalid.'})

    # Xóa sản phẩm khỏi giỏ hàng
    session['cart'] = [item for item in session['cart'] if item['id'] != product_id]
    session.modified = True

    return jsonify({'status': 'success', 'message': 'The product has been removed from the cart.'})

@app.route('/update_cart_quantity', methods=['POST'])
def update_cart_quantity():
    data = request.json
    product_id = data.get('product_id')
    new_quantity = data.get('quantity')

    if 'cart' not in session:
        session['cart'] = []  # Tạo giỏ hàng nếu chưa tồn tại

    # Cập nhật số lượng sản phẩm trong session
    cart_updated = False
    for item in session['cart']:
        if item['id'] == product_id:
            item['quantity'] = new_quantity
            cart_updated = True
            break

    if not cart_updated:
        session['cart'].append({'id': product_id, 'quantity': new_quantity})

    session.modified = True
    return jsonify({'status': 'success', 'message': 'The product quantity has been updated.'})

@app.route('/checkout')
def checkout():
    cart_items = session.get('cart', [])
    total_amount = sum(int(item['quantity']) * float(item['price'].replace('$', '')) for item in cart_items)
    return render_template('/main/checkout.html', cart_items=cart_items, total_amount=total_amount)

@app.route('/get_ip')
def get_ip():
    user_agent = user_agents.parse(request.headers.get('User-Agent'))           
    browser = user_agent.browser.family
    ip_address = request.remote_addr

    country, city = get_location(ip_address)
    response = make_response(f'IP address {ip_address}, Country: {country}, City: {city}, Browser: {browser}')
    response.set_cookie('Location', f'Country: {country}, Browser: {browser}')
    return response

data_file = 'order_data.csv'

def save_order(order):
    with open(data_file, 'a', newline='', encoding='utf-8') as file:
        fieldnames = ['Full name', 'Phone', 'Address', 'Payment method']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        if file.tell() == 0:  # Kiểm tra xem file có trống không
            writer.writeheader()
        writer.writerow(order)

@app.route('/process_payment', methods=['POST'])
def process_payment():
    # Lấy dữ liệu từ form
    data = request.json  # Sử dụng request.json nếu dữ liệu được gửi dưới dạng JSON
    full_name = data.get('fullName')
    phone = data.get('phone')
    address = data.get('address')
    payment_method = data.get('paymentMethod')
    # Kiểm tra xem dữ liệu có đầy đủ hay không
    if not all([full_name, phone, address, payment_method]):
        return jsonify({'status': 'error', 'message': 'Missing information'})
    # Tạo đơn hàng mới và lưu vào file CSV
    new_order = {'Full name': full_name, 'Phone': phone, 'Address': address, 'Payment method': payment_method}
    save_order(new_order)
    # Xử lý thông tin thanh toán ở đây và trả về kết quả
    return jsonify({'status': 'success', 'message': 'Order Success. Thank you for using our service.'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=999)