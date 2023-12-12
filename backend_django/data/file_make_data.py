import re
import secrets
import string
from datetime import datetime, timedelta

import mysql.connector
from faker import Faker
import random
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='02072002',
    database='lagu'
)
faker = Faker()
cursor = conn.cursor()
random_numbers = [random.randint(1000000, 9999999) for _ in range(100)]
for _ in range(20):
    random_number = random.randint(1000000, 9999999)
    random_rank = random.randint(1, 4)
    so_dien_thoai = '098' + str(random_number)
    ho_ten = faker.name()
    dia_chi = 'quan 8, Ho Chi Minh'
    rank = str(random_rank)
    cursor.execute('INSERT INTO `lagu`.`lagu_khachhang` (`so_dien_thoai`, `ho_ten`, `dia_chi`, `rank`)  VALUES (%s, %s, %s, %s)', (so_dien_thoai, ho_ten, dia_chi, rank))
# # don_gia = 15000
# # link_anh = 'https://product.hstatic.net/200000438219/product/coca_dc31da7c7a324c9bba5220c27013569f_1024x1024.jpg'
# # ten_san_pham = 'CocaCola'
# # cursor.execute(
# #     'INSERT INTO `lagu`.`lagu_menu` (`don_gia`, `link_anh`, `ten_san_pham`)  VALUES (%s, %s, %s)',
# #     (str(don_gia), link_anh, ten_san_pham))
# # Số lượng bản ghi cần tạo
# new_number = 0
# num_records = 200
# def generate_random_code():
#     code_length = 6
#     characters = string.ascii_letters + string.digits  # Ký tự cho mã, bao gồm chữ cái và chữ số
#     return ''.join(secrets.choice(characters) for _ in range(code_length))
# # Tạo 200 bản ghi GiamGia trong quá khứ
# for i in range(100):
#     # Tạo ngày bắt đầu và ngày kết thúc ngẫu nhiên trong quá khứ
#     # ma = generate_random_code()
#     random_number = random.randint(1000000, 9999999)
#     active = True
#     # ngay_bat_dau = datetime.now() - timedelta(days=random.randint(1, 300))
#     # ngay_ket_thuc = ngay_bat_dau + timedelta(days= random.randint(3, 6))
#     ngay_bat_dau = datetime.now() - timedelta(days=random.randint(1, 300))
#     so_luong = 1
#     ban_id = 3
#     khach_hang = random.randint(1, 99)
#     # new_number += i
#     so_dien_thoai = '098' + str(random_number)
#     ho_ten = faker.name()
#     # Tạo tỷ lệ giảm giá hoặc số tiền giảm giá ngẫu nhiên
#     # if random.choice([True, False]):
#     #     ty_le_giam = round(random.uniform(0.05, 0.5), 2)
#     #     so_tien_giam = None
#     # else:
#     #     so_tien_giam = random.randint(10, 1000)
#     #     ty_le_giam = None
#
#     # Thực hiện truy vấn SQL để chèn bản ghi mới vào bảng GiamGia
#     query = 'INSERT INTO `lagu`.`lagu_dsdatban` (`is_trang_thai`,`so_dien_thoai`,`thoi_gian_dat_ban`,`thoi_gian_nhan_ban`, `ten_nguoi_dat`, `so_luong_ban`, `ban_id`, `khach_hang_id`) VALUES (%s, %s,%s,%s,%s, %s, %s, %s)'
#     values = (active,so_dien_thoai, ngay_bat_dau, ngay_ket_thuc, ho_ten, so_luong, ban_id, khach_hang)
#     cursor.execute(query, values)

# for i in range(498,598):
#     ds_dat_ban_id = i
#     ngay_bat_dau = datetime.now() - timedelta(days=random.randint(1, 150))
#     tong_tien = random.randint(100000, 5000000)
#     trang_thai = 'da thanh toan'
#     # Thực hiện truy vấn SQL để chèn bản ghi mới vào bảng GiamGia
#     query = 'INSERT INTO `lagu`.`lagu_hoadoncoctien` (`ngay_thanh_toan`,`tong_tien`,`trang_thai`,`ds_dat_ban_id`) VALUES (%s, %s,%s,%s)'
#     values = (ngay_bat_dau,tong_tien, trang_thai, ds_dat_ban_id)
#     cursor.execute(query, values)
#     update_query = "UPDATE `lagu`.`lagu_hoadoncoctien` SET `ngay_thanh_toan` = (SELECT `thoi_gian_dat_ban` FROM `lagu`.`lagu_dsdatban` WHERE `lagu_dsdatban`.`id` = `lagu_hoadoncoctien`.`ds_dat_ban_id`)"
#     cursor.execute(update_query)

# for i in range(61,1112):
#     so_luong_mon = random.randint(4, 12)
#     for j in range(so_luong_mon):
#         ds_dat_ban_id = 1112
#         menu_id = random.randint(1, 48)
#         so_luong_order = random.randint(1, 12)
#         query = 'INSERT INTO `lagu`.`lagu_chitiethoadon` (`so_luong`,`hoa_don_id`,`menu_id`) VALUES (%s,%s,%s)'
#         values = (so_luong_order, ds_dat_ban_id, menu_id)
#         cursor.execute(query, values)

# for i in range(16,277):
#     id = i
#     tong_tien = random.randint(100000, 3000000)
#     update_query = "UPDATE `lagu`.`lagu_hoadoncoctien` SET `tong_tien` =  %s where `lagu`.`lagu_hoadoncoctien`.`id` = %s"
#     values = (tong_tien, id)
#     cursor.execute(update_query, values)
# Lấy danh sách tất cả các bản ghi
# select_query = "SELECT id FROM lagu_hoadonthanhtoan"
# cursor.execute(select_query)
# ids = cursor.fetchall()

# # Cập nhật cột Ma_dat_ban
# counter = 1
# for id in ids:
#     # Tạo giá trị mới cho Ma_dat_ban
#     new_value = f"MHD{counter:07d}"
#
#     # Cập nhật Ma_dat_ban cho bản ghi với id tương ứng
#     update_query = "UPDATE lagu_hoadonthanhtoan SET ma_hoa_don = %s WHERE id = %s"
#     values = (new_value, id[0])
#     cursor.execute(update_query, values)
#
#     # Tăng biến đếm
#     counter += 1



# for i in range(500):
#     # Tạo ngày bắt đầu và ngày kết thúc ngẫu nhiên trong quá khứ
#     # ma = generate_random_code()
#     random_number = random.randint(500000, 8000000)
#     ngay_thanh_toan = datetime.now() - timedelta(days=random.randint(1, 200))
#
#     # Thực hiện truy vấn SQL để chèn bản ghi mới vào bảng GiamGia
#     query = 'INSERT INTO `lagu`.`lagu_hoadonthanhtoan` (`thoi_gian_thanh_toan`,`tong_tien`) VALUES (%s, %s)'
#     values = (ngay_thanh_toan, random_number)
#     cursor.execute(query, values)
# # Cập nhật cột Ma_dat_ban
# # Lấy danh sách tất cả các bản ghi
# select_query = "SELECT id FROM lagu_hoadonthanhtoan"
# cursor.execute(select_query)
# ids = cursor.fetchall()
# counter = 1
# for id in ids:
#     # Tạo giá trị mới cho Ma_dat_ban
#     new_value = f"MHD{counter:07d}"
#
#     # Cập nhật Ma_dat_ban cho bản ghi với id tương ứng
#     update_query = "UPDATE lagu_hoadonthanhtoan SET ma_hoa_don = %s WHERE id = %s"
#     values = (new_value, id[0])
#     cursor.execute(update_query, values)
#
#     # Tăng biến đếm
#     counter += 1
# Lưu các thay đổi vào cơ sở dữ liệu
# conn.commit()
# cursor.close()
# conn.close()
# so_dien_thoai = "sdasdasfsd"
# bool = re.match("^[0-9]+$", so_dien_thoai)
# if not bool:
#     print("okee")
# else: print("not Okee")
result = []
for i in range(1, 13, 3):
    temp = [i, i + 2]
    result.append(temp)
print(result)