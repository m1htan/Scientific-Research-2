import csv

# Đọc dữ liệu từ file products.csv và lưu vào một dictionary
products = {}
with open('E:/Bài tập Python/test/products.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file, delimiter=';')
    for row in reader:
        products[row['ProductID']] = {
            'name': row['name'],
            'price': row['price'],
            'image': row['image'],
            'id': row['ProductID']
        }

# Đọc dữ liệu từ file recommended_items.csv và chuyển đổi định dạng
with open('E:/Bài tập Python/test/recommended_items.csv', mode='r', encoding='utf-8') as input_file:
    with open('rec2.csv', mode='w', encoding='utf-8', newline='') as output_file:
        fieldnames = ['customer_id', 'recommended_product_ids', 'id', 'name', 'price', 'image']
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()

        reader = csv.reader(input_file)
        for row in reader:
            if len(row) >= 2:  # Kiểm tra xem hàng có ít nhất 2 phần tử không
                customer_id = row[0].strip('"')
                recommended_product_ids = row[1].strip('"').split(',')

                for product_id in recommended_product_ids:
                    product = products.get(product_id.strip())
                    if product:
                        writer.writerow({
                            'customer_id': customer_id,
                            'recommended_product_ids': product_id.strip(),
                            'id': product['id'],
                            'name': product['name'],
                            'price': product['price'],
                            'image': product['image']
                        })

print("Chuyen doi du lieu thanh cong. File rec2.csv da duoc tao.")