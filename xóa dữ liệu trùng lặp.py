import csv

def remove_duplicates(input_file, output_file):
    # Tạo một set để lưu trữ các cặp (customer_id, recommended_product_ids) đã xuất hiện
    seen = set()

    with open(input_file, 'r', newline='') as infile, open(output_file, 'w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Copy header
        writer.writerow(next(reader))

        for row in reader:
            # Lấy customer_id và recommended_product_ids từ dòng hiện tại
            customer_id = row[0]
            recommended_product_ids = row[1]

            # Kiểm tra xem cặp (customer_id, recommended_product_ids) đã xuất hiện chưa
            if (customer_id, recommended_product_ids) not in seen:
                # Nếu chưa, ghi dòng vào file đầu ra và đánh dấu đã xuất hiện
                writer.writerow(row)
                seen.add((customer_id, recommended_product_ids))

if __name__ == "__main__":
    input_file = "D:/git/Scientific-Research-2/rec2.csv" # Đường dẫn tới file CSV ban đầu
    output_file = "D:/git/Scientific-Research-2/rec3.csv" # Đường dẫn tới file CSV sau khi loại bỏ các dòng trùng lặp

    remove_duplicates(input_file, output_file)
