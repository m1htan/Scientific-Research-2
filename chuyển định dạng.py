import pandas as pd

# Đọc file
file_path = 'E:/Bài tập Python/z_Scientific-Research-main/recommended_items.csv'
data = pd.read_csv(file_path)

# Tách cột dữ liệu thành hai phần dựa vào dấu phẩy đầu tiên
split_data = data['customer_id'].str.split(',', n=1, expand=True)

# Gán lại tên cột cho phù hợp
split_data.columns = ['customer_id', 'recommended_product_ids']

# Xử lý chuỗi 'recommended_product_ids' để loại bỏ dấu ngoặc kép
split_data['recommended_product_ids'] = split_data['recommended_product_ids'].str.replace('"', '')

# Tạo danh sách rỗng để lưu dữ liệu sau khi tách
recommended_item = []

# Duyệt qua mỗi hàng trong dữ liệu
for index, row in split_data.iterrows():
    # Tách các recommended_product_id bằng dấu phẩy
    product_ids = row['recommended_product_ids'].split(',')
    # Đối với mỗi product_id, thêm vào danh sách với customer_id tương ứng
    for product_id in product_ids:
        recommended_item.append({'customer_id': row['customer_id'], 'recommended_product_id': product_id})

# Chuyển danh sách thành DataFrame
expanded_data = pd.DataFrame(recommended_item)

new_file_path = 'E:/Bài tập Python/z_Scientific-Research-main/recommended_item.csv'
expanded_data.to_csv(new_file_path, index=True)
