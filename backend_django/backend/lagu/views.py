import re
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.handlers.modwsgi import check_password
from django.contrib.auth.hashers import make_password
from django.db.models import Sum, Count
import locale

from django.db.models.functions import ExtractMonth, ExtractDay, ExtractYear
from django.forms import FloatField
from django.http import HttpResponse
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import action
from rest_framework.views import APIView
from .models import *
import pandas as pd
from .serializers import BanSerializer, MenuSerializer, DSDatBanSerialier, KhachHangSerializer, DsOrderSerialier, \
    HoaDonThanhToanSerializer, GiamGiaSerializer, HoaDonCocTienSerializer, ChiTietHoaDonSerializer, UserSerializer, \
    ActivedSerializer, ManageSerialiser


# ACCEPTANCE_TIME = 5  # phút | KHOẢNG THỜI GIAN CHẤP NHẬN ĐƯỢC
# TIME_CHECK = 2
# # COUNT_BOOK = 6
# TIME_BOOK_FEW = 120  # phút | khoảng thời gian trước khi nhận bàn (few)
# TIME_BOOK_MANY = 7  # ngày | khoảng thời gian trước khi nhận bàn (many)
# ORDER_MANY = 4  # MÓN | order tối thiểu (many)
# ORDER_FEW = 2  # MÓN | order tối thiểu (few)
# COUNT_TABLE_FEW = 2  # BÀN | số bàn tối thiểu (few)
# COUNT_TABLE_MANY = 6  # BÀN | số bàn tối thiểu (many)
# LAST_TIME_RECEIVE_BOOK_MANY = 120  # phút | khoảng thời gian cho phép nhận bàn (many)
# LAST_TIME_RECEIVE_BOOK_FEW = 45  # phút | khoảng thời gian cho phép nhận bàn (few)
# CANCEL_BOOK_FEW = 60  # phút | trước khoảng thời gian cho phép hủy (few)
# CANCEL_BOOK_MANY = 1  # ngày | trước khoảng thời gian cho phép hủy (many)
# UPDATE_TIME_BOOK_MANY = 7  # ngày | khoảng thời gian tối đa cho phép thay đổi thời gian nhận bàn sớm hơn (many)
# LAST_UPDATE_TIME_BOOK_MANY = 30  # ngày | khoảng thời gian tối đa cho phép thay đổi thời gian nhận bàn trễ hơn (many)
# UPDATE_TIME_BOOK_FEW = 60  # phút | khoảng thời gian tối đa cho phép thay đổi thời gian nhận bàn sớm hơn (few)
# LAST_UPDATE_TIME_BOOK_FEW = 60  # phút | khoảng thời gian tối đa cho phép thay đổi thời gian nhận bàn trễ hơn (few)
# TIME_UPDATE_ORDER_MANY = 1  # ngày | trước khoảng thời gian cho phép thay đổi order (many)
# TIME_UPDATE_ORDER_FEW = 60  # phút | trước khoảng thời gian cho phép thay đổi order (few)
# TIME_UPDATE_COUNT_TABLE_MANY = 1  # ngày | trước khoảng thời gian cho phép thay đổi số lượng bàn (many)
# TIME_UPDATE_COUNT_TABLE_FEW = 45  # phút | trước khoảng thời gian cho phép thay đổi số lượng bàn (few)
# PERCENT_TOTAL_BILL = 40  # Phần trăm | khoảng thanh toán đặt cọc
def take_manage(name):
    role = Manage.objects.get(name=name)
    return int(role.value)


ACCEPTANCE_TIME = take_manage("ACCEPTANCE_TIME")  # phút | KHOẢNG THỜI GIAN CHẤP NHẬN ĐƯỢC
# TIME_CHECK = take_manage("TIME_CHECK")
# COUNT_BOOK = 6
# TIME_BOOK_FEW = take_manage("TIME_BOOK_FEW")  # phút | khoảng thời gian trước khi nhận bàn (few)
# TIME_BOOK_MANY = take_manage("TIME_BOOK_MANY")  # ngày | khoảng thời gian trước khi nhận bàn (many)
# ORDER_MANY = take_manage("ORDER_MANY")  # MÓN | order tối thiểu (many)
# ORDER_FEW = take_manage("ORDER_FEW")  # MÓN | order tối thiểu (few)
# COUNT_TABLE_FEW = take_manage("COUNT_TABLE_FEW")  # BÀN | số bàn tối thiểu (few)
# COUNT_TABLE_MANY = take_manage("COUNT_TABLE_MANY")  # BÀN | số bàn tối thiểu (many)
# LAST_TIME_RECEIVE_BOOK_MANY = take_manage("LAST_TIME_RECEIVE_BOOK_MANY")  # phút | khoảng thời gian cho phép nhận bàn (many)
# LAST_TIME_RECEIVE_BOOK_FEW = take_manage("LAST_TIME_RECEIVE_BOOK_FEW")  # phút | khoảng thời gian cho phép nhận bàn (few)
# CANCEL_BOOK_FEW = take_manage("CANCEL_BOOK_FEW")  # phút | trước khoảng thời gian cho phép hủy (few)
# CANCEL_BOOK_MANY = take_manage("CANCEL_BOOK_MANY")  # ngày | trước khoảng thời gian cho phép hủy (many)
# UPDATE_TIME_BOOK_MANY = take_manage("UPDATE_TIME_BOOK_MANY")  # ngày | khoảng thời gian tối đa cho phép thay đổi thời gian nhận bàn sớm hơn (many)
# LAST_UPDATE_TIME_BOOK_MANY = take_manage("LAST_UPDATE_TIME_BOOK_MANY")  # ngày | khoảng thời gian tối đa cho phép thay đổi thời gian nhận bàn trễ hơn (many)
# UPDATE_TIME_BOOK_FEW = take_manage("UPDATE_TIME_BOOK_FEW")  # phút | khoảng thời gian tối đa cho phép thay đổi thời gian nhận bàn sớm hơn (few)
# LAST_UPDATE_TIME_BOOK_FEW = take_manage("LAST_UPDATE_TIME_BOOK_FEW")  # phút | khoảng thời gian tối đa cho phép thay đổi thời gian nhận bàn trễ hơn (few)
# TIME_UPDATE_ORDER_MANY = take_manage("TIME_UPDATE_ORDER_MANY")  # ngày | trước khoảng thời gian cho phép thay đổi order (many)
# TIME_UPDATE_ORDER_FEW = take_manage("TIME_UPDATE_ORDER_FEW")  # phút | trước khoảng thời gian cho phép thay đổi order (few)
# TIME_UPDATE_COUNT_TABLE_MANY = take_manage("TIME_UPDATE_COUNT_TABLE_MANY")  # ngày | trước khoảng thời gian cho phép thay đổi số lượng bàn (many)
# TIME_UPDATE_COUNT_TABLE_FEW = take_manage("TIME_UPDATE_COUNT_TABLE_FEW")  # phút | trước khoảng thời gian cho phép thay đổi số lượng bàn (few)
# PERCENT_TOTAL_BILL = take_manage("PERCENT_TOTAL_BILL")  # Phần trăm | khoảng thanh toán đặt cọc


# Create your views here.

def add_actived(actived, status):
    time = datetime.now().replace(tzinfo=None)
    new_actived = list_actived(time=time, actived=actived, status=status)
    new_actived.save()


class TestView(viewsets.ViewSet, generics.ListAPIView):
    def test(self, request):
        return Response('hello world!!')


class UserViewSet(viewsets.ViewSet,
                  generics.CreateAPIView,
                  generics.RetrieveAPIView):
    queryset = User.objects.filter(is_active=True)
    serializer_class = UserSerializer
    parser_classes = [MultiPartParser]

    # def get_permissions(self):
    #     if self.action == 'retrieve':
    #         return [permissions.IsAuthenticated]
    #     return  [permissions.AllowAny()]
    @action(methods=['post'], detail=False, url_path="login")
    def login(self, request, pk=None):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            user = User.objects.get(username=username)
            if user.check_password(password):
                return Response(dict(isLogin='true'), status.HTTP_200_OK)
            else:
                raise Exception('not have user')
        except Exception as e:
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)


class BanViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Ban.objects.all()
    serializer_class = BanSerializer

    @action(methods=['get'], detail=False, url_path="get-ds-ban")
    def get_ds_ban(self, request):
        try:
            ban = Ban.objects.all()
            data = BanSerializer(ban, many=True).data
            return Response(data, status.HTTP_200_OK)
        except Exception as e:
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path="test")
    def test_manage(self, request, pk=None):
        role = take_manage("TIME_CHECK")
        return Response(dict(role=role), status.HTTP_200_OK)

    @action(methods=['put'], detail=True, url_path="change-active")
    def change_active(self, request, pk):
        try:
            ban = Ban.objects.get(id=pk)
            if ban.is_trang_thai:
                ban.is_trang_thai = False
                ban.save()
            else:
                ban.is_trang_thai = True
                ban.save()
            actived = f"CHANGE_ACTIVE_BAN BAN_ID = {str(ban.id)}"
            add_actived(actived, Status.Success)
            return Response(dict(message="update success"), status.HTTP_200_OK)
        except Exception as e:
            actived = f"CHANGE_ACTIVE_BAN"
            add_actived(actived, Status.Failed)
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path="create-table")
    def create_table(self, request, pk=None):
        try:
            so_luong = request.data.get('so_luong')
            suc_chua = request.data.get('suc_chua')
            loai_ban = request.data.get('loai_ban')
            ban = Ban.objects.filter(loai_ban=loai_ban)
            if not ban:
                new_ban = Ban(so_luong=so_luong, suc_chua=suc_chua, loai_ban=loai_ban)
                new_ban.save()
                actived = f"CREATE_BAN"
                add_actived(actived, Status.Success)
                return Response(dict(message="create success"), status.HTTP_200_OK)
            else:
                actived = f"CREATE_BAN"
                add_actived(actived, Status.Not_allow)
                raise Exception("Loại bàn đã tồn tại")
        except Exception as e:
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, url_path="update-info")
    def update_info(self, request, pk):
        try:
            ban = Ban.objects.get(id=pk)
            if request.data.get('so_luong'):
                ban.so_luong = request.data.get('so_luong')
            if request.data.get('suc_chua'):
                ban.suc_chua = request.data.get('suc_chua')
            if request.data.get('loai_ban'):
                loai_ban = request.data.get('loai_ban')
                check = Ban.objects.filter(loai_ban=loai_ban)
                if not check:
                    ban.loai_ban = loai_ban
            ban.save()
            actived = f"UPDATE_INFO_BAN BAN_ID={str(ban.id)}"
            add_actived(actived, Status.Success)
            return Response(dict(message="update success"), status.HTTP_200_OK)
        except Exception as e:
            actived = f"UPDATE_INFO_BAN"
            add_actived(actived, Status.Failed)
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)


class MenuViewSet(viewsets.ModelViewSet, generics.ListAPIView):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    parser_classes = [MultiPartParser, ]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        actived = f"DELETE_MENU"
        add_actived(actived, Status.Success)
        return Response({"message": "Delete successful"}, status=204)

    @action(methods=['get'], detail=False, url_path="get-active-menu")
    def active_menu(self, request):
        menus = Menu.objects.filter(is_trang_thai=True).all()
        serializer_data = MenuSerializer(menus, many=True).data
        return Response(serializer_data, status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path="create-menu")
    def create_menu(self, request, pk=None):
        try:
            ten = request.data.get('ten_san_pham')
            don_gia = request.data.get('don_gia')
            don_gia_str = don_gia.replace('"', '')
            don_gia = float(don_gia_str)
            loai = request.data.get('loai')
            anh = request.FILES['link_anh']
            mon = Menu(ten_san_pham=ten, don_gia=don_gia, loai=loai, link_anh=anh)
            mon.save()
            actived = f"CREATE_MENU"
            add_actived(actived, Status.Success)
            return Response("Message: Create success", status.HTTP_200_OK)
        except Exception as e:
            actived = f"CREATE_MENU"
            add_actived(actived, Status.Failed)
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=True, url_path="up-hinh")
    def up(self, request, pk):
        try:
            mon = Menu.objects.get(id=pk)
            uploaded_file = request.FILES['link_anh']
            mon.link_anh = uploaded_file
            if uploaded_file is None:
                raise Exception('file null')
            mon.save()
            actived = f"UPDATE_MENU MENU_ID={mon.id}"
            add_actived(actived, Status.Success)
            return Response("Message: Upload success", status.HTTP_200_OK)
        except Exception as e:
            actived = f"UPDATE_MENU"
            add_actived(actived, Status.Failed)
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path="update-trang-thai")
    def update_trang_thai(self, request, pk=None):
        try:
            id = request.data.get('id')
            mon = Menu.objects.get(id=id)
            if mon:
                if mon.is_trang_thai:
                    mon.is_trang_thai = False
                    mon.save()
                else:
                    mon.is_trang_thai = True
                    mon.save()
                actived = f"CHANGE_ACTIVE_MENU MENU_ID={mon.id}"
                add_actived(actived, Status.Success)
                return Response("Message: update success", status.HTTP_200_OK)
        except Exception as e:
            actived = f"CHANGE_ACTIVE_MENU"
            add_actived(actived, Status.Failed)
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, url_path="update-menu")
    def update_menu(self, request, pk):
        try:
            mon = Menu.objects.get(id=pk)
            if mon:
                if request.data.get('ten_san_pham'):
                    ten = request.data.get('ten_san_pham')
                    mon.ten_san_pham = ten
                    mon.save()
                if request.data.get('don_gia'):
                    don_gia = request.data.get('don_gia')
                    don_gia_str = don_gia.replace('"', '')
                    don_gia = float(don_gia_str)
                    mon.don_gia = don_gia
                    mon.save()
                if request.FILES.get('link_anh'):
                    link_anh = request.FILES['link_anh']
                    mon.link_anh = link_anh
                if request.data.get('loai'):
                    loai = request.data.get('loai')
                    mon.loai = loai
                    mon.save()
                if request.data.get('is_trang_thai'):
                    trang_thai = request.data.get('is_trang_thai')
                    if trang_thai == 'true':
                        mon.is_trang_thai = True
                        mon.save()
                    else:
                        mon.is_trang_thai = False
                        mon.save()
                mon.save()
                actived = f"UPDATE_MENU MENU_ID={mon.id}"
                add_actived(actived, Status.Success)
                return Response("Message: update success", status.HTTP_200_OK)
            else:
                actived = f"UPDATE_MENU"
                add_actived(actived, Status.Failed)
                raise Exception('khong tim duoc mon')

        except Exception as e:
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)


class KhachHangViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Menu.objects.all()
    serializer_class = KhachHangSerializer

    @action(methods=['get'], detail=False, url_path="check-khach-hang")
    def get_khach_hang_by_sdt(self, request, pk=None):
        try:
            sdt = request.data.get('so_dien_thoai')
            khach_hang = KhachHang.objects.get(so_dien_thoai=sdt)
            if khach_hang:
                json_khach_hang = KhachHangSerializer(khach_hang).data
                return Response(json_khach_hang, status.HTTP_200_OK)
        except Exception as e:
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path="create-khach-hang")
    def create_info(self, request, pk=None):
        try:
            so_dien_thoai = request.data.get('sdt')
            if not re.match("^[0-9]+$", so_dien_thoai) or len(so_dien_thoai) != 10:
                raise Exception('số điện thoại không hợp lệ')
            ho_ten = request.data.get('ho_ten')
            dia_chi = request.data.get('dia_chi')
            new_khach_hang = KhachHang(so_dien_thoai=so_dien_thoai, ho_ten=ho_ten, dia_chi=dia_chi)
            new_khach_hang.save()
            actived = f"CREATE_KHACHHANG"
            add_actived(actived, Status.Success)
            return Response(dict(message="create success"), status.HTTP_200_OK)
        except Exception as e:
            actived = f"CREATE_KHACHHANG"
            add_actived(actived, Status.Failed)
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path="khach-hang-info")
    def get_info(self, request, pk=None):
        try:
            key = request.data.get('key')
            query = Q()
            query |= Q(id__icontains=key)
            query |= Q(so_dien_thoai__icontains=key)
            query |= Q(ho_ten__icontains=key)
            query |= Q(dia_chi__icontains=key)
            result = KhachHang.objects.filter(query)
            data_result = KhachHangSerializer(result, many=True).data
            if not data_result:
                raise Exception("không tìm được dữ liệu khách hàng")
            data = KhachHangSerializer(data_result, many=True).data
            return Response(data, status.HTTP_200_OK)
        except Exception as e:
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, url_path='update-info')
    def update_info(self, request, pk):
        try:
            khach_hang = KhachHang.objects.get(id=pk)
            if not khach_hang:
                raise Exception('khách hàng không tồn tại')
            if request.data.get('so_dien_thoai'):
                so_dien_thoai = request.data.get('so_dien_thoai')
                if not re.match("^[0-9]+$", so_dien_thoai) or len(so_dien_thoai) != 10:
                    raise Exception('số điện thoại không hợp lệ')
                khach_hang.so_dien_thoai = so_dien_thoai
            if request.data.get('ho_ten'):
                khach_hang.ho_ten = request.data.get('ho_ten')
            if request.data.get('dia_chi'):
                khach_hang.dia_chi = request.data.get('dia_chi')
            if request.data.get('rank'):
                khach_hang.rank = request.data.get('rank')
            khach_hang.save()
            actived = f"UPDATE_KHACHHANG KHACHHANG={str(khach_hang.id)}"
            add_actived(actived, Status.Success)
            return Response(dict(message="update success"), status.HTTP_200_OK)
        except Exception as e:
            actived = f"UPDATE_KHACHHANG"
            add_actived(actived, Status.Failed)
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['delete'], detail=True, url_path='delete-info')
    def delete_info(self, request, pk):
        try:
            khach_hang = KhachHang.objects.get(id=pk)
            sdt = khach_hang.so_dien_thoai
            if not khach_hang:
                raise Exception('khách hàng không tồn tại')
            khach_hang.delete()
            actived = f"DELETE_KHACHHANG SDT={sdt}"
            add_actived(actived, Status.Success)
            return Response(dict(message="delete success"), status.HTTP_200_OK)
        except Exception as e:
            actived = f"DELETE_KHACHHANG"
            add_actived(actived, Status.Failed)
            return Response("Message: " + str(e), status.HTTP_400_BAD_REQUEST)


class DsDatBanViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = DsDatBan.objects.all()
    serializer_class = DSDatBanSerialier

    def Check_data(data):
        processed_result = {}
        for item in data:
            ban_id = item['ban_id']
            total_so_luong = item['total_so_luong']
            loai = Ban.objects.get(id=ban_id).loai_ban
            ban_so_luong = Ban.objects.get(id=ban_id).so_luong
            processed_so_luong = ban_so_luong - total_so_luong
            processed_result[ban_id] = ban_id
            processed_result = {'loai': loai, 'total_so_luong': processed_so_luong}
        return processed_result

    @action(methods=['get'], detail=True, url_path="get-by-id")
    def get_by_id(self, request, pk):
        try:
            ban = DsDatBan.objects.get(id=pk)
            serialier_data = DSDatBanSerialier(ban).data
            return Response(serialier_data, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message:" + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path="get-ds-dat-ban")
    def get_ds_dat_ban(self, request, pk=None):
        try:
            so_dien_thoai = request.data.get('so_dien_thoai')
            ngay_dat_ban = request.data.get('ngay_dat_ban')
            data = DsDatBan.objects.filter(
                Q(so_dien_thoai=so_dien_thoai) & Q(thoi_gian_dat_ban__date=ngay_dat_ban)).all()
            json_res = DSDatBanSerialier(data, many=True).data
            return Response(json_res, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='check-ds-dat-ban-today')
    def ds_dat_ban_today(self, request, pk=None):
        try:
            check_time = datetime.now().date()
            ds_ban = DsDatBan.objects.filter(thoi_gian_nhan_ban__date=check_time).order_by('thoi_gian_nhan_ban')
            serialier_data = DSDatBanSerialier(ds_ban, many=True).data
            return Response(serialier_data, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message:" + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='check-today')
    def Check_today(self, request, pk=None):
        TIME_CHECK = take_manage("TIME_CHECK")
        date = datetime.now()
        if date:
            result = []
            time_star = date - timedelta(hours=TIME_CHECK)
            time_end = date
            ban = Ban.objects.filter(is_trang_thai=True).all()
            if not ban:
                return Response({"message": "khong con ban trong"}, status.HTTP_200_OK)
            for item in ban:
                item_date_data = DsDatBan.objects.filter(Q(ban_id=item.id) &
                                                         Q(thoi_gian_nhan_ban__range=(time_star, time_end)) &
                                                         Q(is_trang_thai=False)).all()
                temp = item_date_data.values('ban_id').annotate(total_so_luong=Sum('so_luong_ban'))
                checked = DsDatBanViewSet.Check_data(temp)
                if checked:
                    if checked['total_so_luong'] > 0:
                        result.append(checked)
                else:
                    result.append({'loai': item.loai_ban, 'total_so_luong': item.so_luong})
            return Response(result, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='ngay-nhan')
    def Check_day(self, request, pk=None):
        try:
            TIME_CHECK = take_manage("TIME_CHECK")
            ngay_nhan_ban = request.data.get('ngay')
            date = datetime.strptime(ngay_nhan_ban, "%Y-%m-%d %H:%M:%S")

            if ngay_nhan_ban:
                result = []
                time_star = date - timedelta(hours=TIME_CHECK)
                time_end = date
                ban = Ban.objects.filter(is_trang_thai=True).all()
                if not ban:
                    return Response({"message": "khong con ban trong"}, status.HTTP_200_OK)
                for item in ban:
                    item_date_data = DsDatBan.objects.filter(Q(ban_id=item.id) &
                                                             Q(thoi_gian_nhan_ban__range=(time_star, time_end)) &
                                                             Q(is_trang_thai=False)).all()

                    temp = item_date_data.values('ban_id').annotate(total_so_luong=Sum('so_luong_ban'))

                    checked = DsDatBanViewSet.Check_data(temp)
                    if checked:
                        if checked['total_so_luong'] > 0:
                            result.append(checked)
                    else:
                        result.append({'loai': item.loai_ban, 'total_so_luong': item.so_luong})
                return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message:" + str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='them-dat-ban')
    def create_dat_ban(self, request, pk=None):
        try:
            PERCENT_TOTAL_BILL = take_manage("PERCENT_TOTAL_BILL")
            COUNT_TABLE_MANY = take_manage("COUNT_TABLE_MANY")
            COUNT_TABLE_FEW = take_manage("COUNT_TABLE_FEW")
            ORDER_FEW = take_manage("ORDER_FEW")
            ORDER_MANY = take_manage("ORDER_MANY")
            TIME_BOOK_FEW = take_manage("TIME_BOOK_FEW")
            TIME_BOOK_MANY = take_manage("TIME_BOOK_MANY")
            form_data = request.data
            so_dien_thoai = form_data.get('so_dien_thoai')
            ten = form_data.get('ten_nguoi_dat')
            ngay_dat_ban = datetime.now()
            ngay_nhan_ban = form_data.get('ngay_nhan_ban')
            loai_ban = form_data.get('loai_ban')
            so_luong = int(form_data.get('so_luong'))
            mon_an_data = form_data.get('mon_an', [])
            id_ban = Ban.objects.get(loai_ban=loai_ban).id
            ban_active = Ban.objects.get(loai_ban=loai_ban).is_trang_thai
            if not ban_active:
                raise Exception("bàn ngưng hoạt động")
            id_khach_hang = None
            time_allow = None
            if form_data.get('khach_hang'):
                khach_hang = form_data.get('khach_hang')
                id_khach_hang = KhachHang.objects.get(so_dien_thoai=khach_hang).id
            # set start_time để kiểm tra điều kiện
            if so_luong >= COUNT_TABLE_MANY:
                time_allow = ngay_dat_ban + timedelta(days=TIME_BOOK_MANY)
            elif 0 < so_luong < COUNT_TABLE_MANY:
                time_allow = ngay_dat_ban + timedelta(minutes=TIME_BOOK_FEW)
            else:
                raise Exception("Lỗi số lượng bàn")

            # kiểu tra ngày nhận bàn và số lượng bàn
            end_time = ngay_nhan_ban = datetime.strptime(ngay_nhan_ban, "%Y-%m-%d %H:%M:%S")
            if so_luong >= COUNT_TABLE_MANY and time_allow > ngay_nhan_ban:
                raise Exception("Nhận bàn tối thiểu sau {} ngày".format(TIME_BOOK_MANY))
            elif 0 < so_luong < COUNT_TABLE_MANY and time_allow > ngay_nhan_ban:
                raise Exception("Nhận bàn tối thiểu sau {} phút".format(TIME_BOOK_FEW))

            # kiểm tra số lượng order món ăn
            if so_luong >= COUNT_TABLE_MANY and len(mon_an_data) < ORDER_MANY:
                raise Exception("Chưa order đủ số lượng món")
            elif COUNT_TABLE_FEW < so_luong < COUNT_TABLE_MANY and len(mon_an_data) < ORDER_FEW:
                raise Exception("Chưa order đủ số lượng món")
            # add id khách hàng nếu có
            if id_khach_hang:
                new_ds_dat_ban = DsDatBan(so_dien_thoai=so_dien_thoai,
                                          thoi_gian_nhan_ban=ngay_nhan_ban,
                                          thoi_gian_dat_ban=ngay_dat_ban,
                                          so_luong_ban=so_luong,
                                          khach_hang_id=id_khach_hang,
                                          ten_nguoi_dat=ten,
                                          ban_id=id_ban)
            else:
                new_ds_dat_ban = DsDatBan(so_dien_thoai=so_dien_thoai,
                                          thoi_gian_nhan_ban=ngay_nhan_ban,
                                          thoi_gian_dat_ban=ngay_dat_ban,
                                          so_luong_ban=so_luong,
                                          ten_nguoi_dat=ten,
                                          ban_id=id_ban)
            try:
                new_ds_dat_ban.save()
                tong_tien = 0
                dat_ban_id = DsDatBan.objects.get(thoi_gian_dat_ban=ngay_dat_ban).id
                if mon_an_data:
                    for item in mon_an_data:
                        mon = Menu.objects.get(id=item["id"])
                        mon_an_id = mon.id
                        tong_tien += mon.don_gia
                        so_luong = item["so_luong"]
                        new_order = DsOrder(ds_dat_ban_id=dat_ban_id, menu_id=mon_an_id, so_luong=so_luong)
                        new_order.save()
                tong_tien = (tong_tien * PERCENT_TOTAL_BILL) / 100
                hoa_don = HoaDonCocTien(ngay_thanh_toan=ngay_dat_ban, tong_tien=tong_tien, ds_dat_ban_id=dat_ban_id)
                hoa_don.save()
                # serializer_data = HoaDonCocTienSerializer(HoaDonCocTien.objects.get(ngay_thanh_toan=ngay_dat_ban)).data
                return Response({"message": " Created"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"message": "1 = " + str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": "2 = " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, url_path='nhan-ban')
    def nhan_ban(self, request, pk, *args):
        try:
            LAST_TIME_RECEIVE_BOOK_FEW = take_manage("LAST_TIME_RECEIVE_BOOK_FEW")
            LAST_TIME_RECEIVE_BOOK_MANY = take_manage("LAST_TIME_RECEIVE_BOOK_MANY")
            COUNT_TABLE_MANY = take_manage("COUNT_TABLE_MANY")
            ban = DsDatBan.objects.get(id=pk)
            time_request = datetime.now().replace(tzinfo=None)
            time_accept = ban.thoi_gian_nhan_ban.replace(tzinfo=None)
            min_time_accept = None
            max_time_accept = None
            if ban.so_luong_ban >= COUNT_TABLE_MANY:
                min_time_accept = time_accept - timedelta(minutes=LAST_TIME_RECEIVE_BOOK_MANY)
                max_time_accept = time_accept + timedelta(minutes=LAST_TIME_RECEIVE_BOOK_MANY)
            elif 0 < ban.so_luong_ban <= COUNT_TABLE_MANY:
                min_time_accept = time_accept - timedelta(minutes=LAST_TIME_RECEIVE_BOOK_FEW)
                max_time_accept = time_accept + timedelta(minutes=LAST_TIME_RECEIVE_BOOK_FEW)
            if min_time_accept and max_time_accept and min_time_accept <= time_request <= max_time_accept:
                if not ban.is_trang_thai:
                    ban.is_trang_thai = True
                ban.save()
                json_result = DSDatBanSerialier(ban).data
                return Response(json_result, status.HTTP_200_OK)
            else:
                err = f"Không thể nhận bàn sớm hơn {min_time_accept}, trễ hơn {max_time_accept}"
                raise Exception(err)
        except Exception as e:
            return Response("message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, url_path='update-time-nhan-ban')
    def update_time_accept(self, request, pk):
        try:
            LAST_UPDATE_TIME_BOOK_FEW = take_manage("LAST_UPDATE_TIME_BOOK_FEW")
            UPDATE_TIME_BOOK_FEW = take_manage("UPDATE_TIME_BOOK_FEW")
            LAST_UPDATE_TIME_BOOK_MANY = take_manage("LAST_UPDATE_TIME_BOOK_MANY")
            UPDATE_TIME_BOOK_MANY = take_manage("UPDATE_TIME_BOOK_MANY")
            COUNT_TABLE_MANY = take_manage("COUNT_TABLE_MANY")
            time_request = datetime.strptime(request.data.get('time_update'), "%Y-%m-%d %H:%M:%S")
            time_update = datetime.now().replace(tzinfo=None)
            max_time_allow = None
            min_time_allow = None
            ban = DsDatBan.objects.get(id=pk)
            check = False
            thoi_gian_nhan_ban = ban.thoi_gian_nhan_ban.replace(tzinfo=None)
            if ban.so_luong_ban >= COUNT_TABLE_MANY:
                max_time_allow = thoi_gian_nhan_ban + timedelta(days=LAST_UPDATE_TIME_BOOK_MANY)
                min_time_allow = thoi_gian_nhan_ban - timedelta(days=UPDATE_TIME_BOOK_MANY)
                if time_update <= thoi_gian_nhan_ban - timedelta(days=UPDATE_TIME_BOOK_MANY):
                    check = True
            elif 0 < ban.so_luong_ban <= COUNT_TABLE_MANY:
                max_time_allow = thoi_gian_nhan_ban + timedelta(minutes=LAST_UPDATE_TIME_BOOK_FEW)
                min_time_allow = thoi_gian_nhan_ban - timedelta(minutes=UPDATE_TIME_BOOK_FEW)
                if time_update <= thoi_gian_nhan_ban - timedelta(minutes=UPDATE_TIME_BOOK_FEW):
                    check = True
                # raise Exception(f"dữ liệu so_luong_ban: {ban.so_luong_ban}, time_update = {time_update}")
            # if max_time_allow is None and min_time_allow is None:
            #     raise Exception("dữ liệu None")
            if not check:
                raise Exception("quá thời gian cho phép cập nhật")
            if check and min_time_allow <= time_request <= max_time_allow:
                ban.thoi_gian_nhan_ban = time_request
                ban.save()
                actived = f"UPDATE_thoi_gian_nhan_ban DSDATBAN_ID={str(ban.id)}"
                add_actived(actived, Status.Success)
                return Response({"message": "update success"}, status.HTTP_200_OK)
            else:
                err = f"Không thể nhận bàn sớm hơn {min_time_allow}, trễ hơn {max_time_allow}"
                raise Exception(err)
        except Exception as e:
            actived = f"UPDATE_thoi_gian_nhan_ban"
            add_actived(actived, Status.Failed)
            return Response("message: " + str(e), status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, url_path='update-ten')
    def update_ten(self, request, pk):
        try:
            ten = request.data.get('ten')
            real_time = datetime.now().replace(tzinfo=None)
            ban = DsDatBan.objects.get(id=pk)
            time = ban.thoi_gian_nhan_ban.replace(tzinfo=None)
            if real_time > time:
                return Response({"message": "đổi tên thất bại"}, status.HTTP_400_BAD_REQUEST)
            if ban:
                ban.ten_nguoi_dat = ten
                ban.save()
                actived = f"UPDATE_ten_nguoi_dat DSDATBAN_ID={str(ban.id)}"
                add_actived(actived, Status.Success)
                return Response({"message": "update successfull"}, status.HTTP_200_OK)
        except Exception as e:
            actived = f"UPDATE_TEN_NGUOI_DAT_BAN"
            add_actived(actived, Status.Failed)
            return Response({"message:" + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, url_path='update-sdt')
    def update_sdt(self, request, pk):
        try:
            sdt = request.data.get('sdt')
            real_time = datetime.now().replace(tzinfo=None)
            if len(sdt) != 10:
                raise Exception("Số điện thoại không hợp lệ")
            ban = DsDatBan.objects.get(id=pk)
            time = ban.thoi_gian_nhan_ban.replace(tzinfo=None)
            if real_time > time:
                return Response({"message": "đổi số điện thoại thất bại"}, status.HTTP_400_BAD_REQUEST)
            if ban:
                ban.so_dien_thoai = sdt
                ban.save()
                actived = f"UPDATE_so_dien_thoai DSDATBAN_ID={str(ban.id)}"
                add_actived(actived, Status.Success)
                return Response({"message": "update successfull"}, status.HTTP_200_OK)
        except Exception as e:
            actived = f"UPDATE_so_dien_thoai"
            add_actived(actived, Status.Failed)
            return Response({"message:" + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, url_path='update-so-luong-ban')
    def update_so_luong_ban(self, request, pk):
        try:
            TIME_UPDATE_COUNT_TABLE_FEW = take_manage("TIME_UPDATE_COUNT_TABLE_FEW")
            TIME_UPDATE_COUNT_TABLE_MANY = take_manage("TIME_UPDATE_COUNT_TABLE_MANY")
            COUNT_TABLE_MANY = take_manage("COUNT_TABLE_MANY")
            COUNT_TABLE_FEW = take_manage("COUNT_TABLE_FEW")
            ORDER_FEW = take_manage("ORDER_FEW")
            ORDER_MANY = take_manage("ORDER_MANY")
            new_so_luong = request.data.get('so_luong')
            ban = DsDatBan.objects.get(id=pk)
            time_update = datetime.now().replace(tzinfo=None)
            time_allow = None
            order_allow = 0
            data_request = request.data.get('order', [])
            ds_order = []
            for item in data_request:
                id = Menu.objects.get(ten_san_pham=item["mon"]).id
                ds_order.append({"id": id, "so_luong": item["so_luong"]})
            tong_tien = 0
            thoi_gian_nhan_ban = ban.thoi_gian_nhan_ban.replace(tzinfo=None)
            if 0 < ban.so_luong_ban <= COUNT_TABLE_MANY:
                time_allow = thoi_gian_nhan_ban - timedelta(minutes=TIME_UPDATE_COUNT_TABLE_FEW)
            elif ban.so_luong_ban >= COUNT_TABLE_MANY:
                time_allow = thoi_gian_nhan_ban - timedelta(days=TIME_UPDATE_COUNT_TABLE_MANY)
            if time_update <= time_allow:
                if COUNT_TABLE_FEW < new_so_luong < COUNT_TABLE_MANY:
                    order_allow = ORDER_FEW
                elif new_so_luong >= COUNT_TABLE_MANY:
                    order_allow = ORDER_MANY
                DsDatBanViewSet.update_mon(ds_order, ban, order_allow, new_so_luong, pk=None)
                ban.so_luong_ban = new_so_luong
                ban.save()
            actived = f"UPDATE_so_luong_ban DSDATBAN_ID={str(ban.id)}"
            add_actived(actived, Status.Success)
            return Response({"message": "Update success"}, status.HTTP_200_OK)
        except Exception as e:
            actived = f"UPDATE_so_luong_ban"
            add_actived(actived, Status.Failed)
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=True, url_path='load-bill-order')
    def load_bill(self, request, pk):
        try:
            hoa_don = HoaDonCocTien.objects.get(ds_dat_ban_id=pk)
            data = {"tong_tien": hoa_don.tong_tien}
            return Response(data, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, url_path='update-order')
    def update_order(self, request, pk):
        try:
            TIME_UPDATE_ORDER_FEW = take_manage("TIME_UPDATE_ORDER_FEW")
            TIME_UPDATE_ORDER_MANY = take_manage("TIME_UPDATE_ORDER_MANY")
            COUNT_TABLE_MANY = take_manage("COUNT_TABLE_MANY")
            COUNT_TABLE_FEW = take_manage("COUNT_TABLE_FEW")
            ORDER_FEW = take_manage("ORDER_FEW")
            ORDER_MANY = take_manage("ORDER_MANY")
            ban = DsDatBan.objects.get(id=pk)
            data_request = request.data.get('order', [])
            ds_order = []
            for item in data_request:
                id = Menu.objects.get(ten_san_pham=item["mon"]).id
                ds_order.append({"id": id, "so_luong": item["so_luong"]})
            order_allow = 0
            thoi_gian_nhan_ban = ban.thoi_gian_nhan_ban.replace(tzinfo=None)
            time_update = datetime.now().replace(tzinfo=None)
            if ban.so_luong_ban < COUNT_TABLE_MANY:
                time_allow = thoi_gian_nhan_ban.replace(tzinfo=None) - timedelta(minutes=TIME_UPDATE_ORDER_FEW)
            else:
                time_allow = thoi_gian_nhan_ban.replace(tzinfo=None) - timedelta(days=TIME_UPDATE_ORDER_MANY)
            if time_update <= time_allow:
                if COUNT_TABLE_FEW < ban.so_luong_ban < COUNT_TABLE_MANY:
                    order_allow = ORDER_FEW
                elif ban.so_luong_ban >= COUNT_TABLE_MANY:
                    order_allow = ORDER_MANY

                DsDatBanViewSet.update_mon(ds_order, ban, order_allow, ban.so_luong_ban)
                actived = f"UPDATE_ds_order DSDATBAN_ID={str(ban.id)}"
                add_actived(actived, Status.Success)
                return Response({"message": "Update success"}, status.HTTP_200_OK)
            else:
                raise Exception(f"cập nhật không được trễ hơn {time_allow}")
        except Exception as e:
            actived = f"UPDATE_ds_order"
            add_actived(actived, Status.Failed)
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    def update_mon(ds_order, ban, order_allow, new_so_luong, pk=None):
        COUNT_TABLE_FEW = take_manage("COUNT_TABLE_FEW")
        PERCENT_TOTAL_BILL = take_manage("PERCENT_TOTAL_BILL")
        if ds_order and len(ds_order) >= order_allow:
            try:
                data_ds_order = DsOrder.objects.filter(ds_dat_ban_id=ban.id).all()
                if data_ds_order:
                    for item in ds_order:
                        menu_id = item["id"]
                        so_luong = item["so_luong"]

                        # Kiểm tra xem order đã tồn tại trong old_ds_order hay chưa
                        order_exists = data_ds_order.filter(menu_id=menu_id).first()

                        if order_exists:
                            # Nếu order đã tồn tại, cập nhật số lượng
                            order_exists.so_luong = so_luong
                            order_exists.save()
                        else:
                            # Nếu order chưa tồn tại, tạo mới
                            mon = Menu.objects.get(id=menu_id)
                            new_order = DsOrder(ds_dat_ban_id=ban.id, menu=mon, so_luong=so_luong)
                            new_order.save()
                    # xóa đi order không có trong request
                    old_order = DsOrder.objects.filter(ds_dat_ban_id=ban.id).all()
                    new_order = old_order.exclude(menu_id__in=[item["id"] for item in ds_order])
                    new_order.delete()
                    # Tính tổng tiền
                    tong_tien = 0
                    for item in ds_order:
                        menu_id = item["id"]
                        don_gia = Menu.objects.get(id=menu_id).don_gia
                        so_luong = item["so_luong"]
                        tong_tien += (don_gia * so_luong)
                    # tong_tien = data_ds_order.aggregate(Sum('menu__so_luong'))['menu__don_gia__sum']
                    hoa_don = HoaDonCocTien.objects.get(ds_dat_ban_id=ban.id)
                    if tong_tien != 0:
                        tong_tien = (tong_tien * PERCENT_TOTAL_BILL) / 100

                    if hoa_don:
                        hoa_don = HoaDonCocTien.objects.get(ds_dat_ban_id=ban.id)
                        hoa_don.tong_tien = tong_tien
                        hoa_don.save()
                    else:
                        hoa_don = HoaDonCocTien(ngay_thanh_toan=datetime.now().replace(tzinfo=None),
                                                tong_tien=tong_tien,
                                                ds_dat_ban_id=ban.id)
                        hoa_don.save()

                elif not data_ds_order:
                    if ds_order and len(ds_order) >= order_allow:
                        tong_tien = 0
                        for item in ds_order:
                            mon = Menu.objects.get(id=item["id"])
                            mon_an_id = mon.id
                            tong_tien += mon.don_gia
                            so_luong = item["so_luong"]
                            new_order = DsOrder(ds_dat_ban_id=ban.id, menu_id=mon_an_id, so_luong=so_luong)
                            new_order.save()
                        tong_tien = (tong_tien * PERCENT_TOTAL_BILL) / 100
                        hoa_don = HoaDonCocTien.objects.get(ds_dat_ban_id=ban.id)
                        if hoa_don:
                            hoa_don = HoaDonCocTien.objects.get(ds_dat_ban_id=ban.id)
                            # hoa_don.tong_tien = tong_tien
                            hoa_don.save()
                        else:
                            hoa_don = HoaDonCocTien(ngay_thanh_toan=datetime.now().replace(tzinfo=None),
                                                    tong_tien=tong_tien,
                                                    ds_dat_ban_id=ban.id)
                            hoa_don.save()
                    elif not ds_order and order_allow > 0:
                        raise Exception("order tối thiểu trên {} món".format(order_allow))
            except Exception as e:
                raise Exception("Lỗi: " + str(e))
        elif 0 < new_so_luong <= COUNT_TABLE_FEW:
            old_order = DsOrder.objects.filter(ds_dat_ban_id=ban.id).all()
            old_order.delete()
            hoa_don = HoaDonCocTien.objects.get(ds_dat_ban_id=ban.id)
            hoa_don.tong_tien = 0
            hoa_don.save()
        elif new_so_luong > COUNT_TABLE_FEW:
            raise Exception("order tối thiểu trên {} món".format(order_allow))
        else:
            raise Exception("Lỗi số lượng bàn hoặc danh sách order")

    @action(methods=['put'], detail=True, url_path='huy-dat-ban')
    def huy_dat_ban(self, request, pk):
        try:
            CANCEL_BOOK_MANY = take_manage("CANCEL_BOOK_MANY")
            CANCEL_BOOK_FEW = take_manage("CANCEL_BOOK_FEW")
            COUNT_TABLE_MANY = take_manage("COUNT_TABLE_MANY")
            locale.setlocale(locale.LC_ALL, 'vi_VN')
            time_delete = datetime.now().replace(tzinfo=None)
            ban = DsDatBan.objects.get(id=pk)
            temp_id = ban.id
            time_allow = ban.thoi_gian_nhan_ban.replace(tzinfo=None)
            thoi_gian_nhan_ban = ban.thoi_gian_nhan_ban.replace(tzinfo=None)
            if 0 < ban.so_luong_ban <= COUNT_TABLE_MANY:
                time_allow = thoi_gian_nhan_ban - timedelta(minutes=CANCEL_BOOK_FEW)
            if ban.so_luong_ban >= COUNT_TABLE_MANY:
                time_allow = thoi_gian_nhan_ban - timedelta(days=CANCEL_BOOK_MANY)
            if time_delete <= time_allow:
                # xử lý hoàn cọc
                ban.is_trang_thai = True
                hoa_don = HoaDonCocTien.objects.get(ds_dat_ban_id=ban.id)
                hoa_don.trang_thai = TrangThaiCocTien.HOAN_COC
                hoa_don.ngay_thanh_toan = time_delete
                tong_tien = locale.currency(hoa_don.tong_tien, grouping=True)
                ban.save()
                hoa_don.save()
                actived = f"CANCEL_dat_ban DSDATBAN_ID={str(ban.id)}"
                add_actived(actived, Status.Success)
                return Response({"message": f"Hoàn lại cọc: {tong_tien}"}, status.HTTP_200_OK)
            else:
                # xử lý hủy cọc
                ban.is_trang_thai = True
                hoa_don = HoaDonCocTien.objects.get(ds_dat_ban_id=ban.id)
                hoa_don.trang_thai = TrangThaiCocTien.HUY_COC
                hoa_don.ngay_thanh_toan = time_delete
                ban.save()
                hoa_don.save()
                actived = f"CANCEL_dat_ban DSDATBAN_ID={str(ban.id)}"
                add_actived(actived, Status.Success)
                return Response({"message": f"không hoàn cọc do thời gian hoàn cọc trước {time_allow}"},
                                status.HTTP_200_OK)
        except Exception as e:
            actived = f"CANCEL_dat_ban"
            add_actived(actived, Status.Failed)
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='get-ds-dat-ban')
    def get_ds_dat_ban(self, request, pk=None):
        try:
            current_time = datetime.now().replace(tzinfo=None).date()
            key = request.data.get('key')
            if key == '':
                result = DsDatBan.objects.filter(thoi_gian_nhan_ban__date=current_time)
                data_result = DSDatBanSerialier(result, many=True).data
                return Response(data_result, status.HTTP_200_OK)
            query = Q()
            query |= Q(so_dien_thoai__icontains=key)
            query |= Q(ten_nguoi_dat__icontains=key)
            query |= Q(ma_dat_ban__icontains=key)
            query |= Q(id__icontains=key)
            result = DsDatBan.objects.filter(query)
            if not result:
                raise Exception("Không tồn tại mẫu đặt bàn")
            data_result = DSDatBanSerialier(result, many=True).data
            return Response(data_result, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='tim-dat-ban')
    def search_ds_dat_ban(self, request, pk=None):
        data = request.data.get('so_dien_thoai')
        if data:
            result = DsDatBan.objects.filter(so_dien_thoai=data).all()
            serializer = DSDatBanSerialier(result, many=True)
            json_data = serializer.data
            return Response(json_data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='ds_dat_ban_theo_ngay')
    def date_ds_dat_ban(self, request, pk=None):
        data = datetime.now().date()
        result = DsDatBan.objects.filter(thoi_gian_nhan_ban__date=data)
        serializer = DSDatBanSerialier(result, many=True)
        json_data = serializer.data
        return Response(json_data, status=status.HTTP_200_OK)

    @action(methods=['delete'], detail=True)
    def del_ds_dat_ban(self, request, pk):
        try:
            ds_dat_ban_id = pk
            temp = DsDatBan.objects.get(id=ds_dat_ban_id)
            temp.delete()
            actived = f"CANCEL_dat_ban"
            add_actived(actived, Status.Success)
            return Response({"message": "Deleted"}, status=status.HTTP_200_OK)
        except DsDatBan.DoesNotExist:
            return Response({"message": "DsDatBan not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            actived = f"DELETE_dat_ban"
            add_actived(actived, Status.Failed)
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class DsOrderViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = DsOrder.objects.all()
    serializer_class = DsOrderSerialier

    @action(methods=['get'], detail=True, url_path='get-order-by-DsDatBan')
    def get_order_by_DsDatBan(self, request, pk=None):
        data_res = []
        try:
            order = DsOrder.objects.filter(ds_dat_ban_id=pk)
            if not order:
                return Response(status=status.HTTP_200_OK)
            for item in order:
                mon = Menu.objects.get(id=item.menu_id)
                if not mon:
                    raise Exception("không tồn tại món ăn")
                data_res.append({"mon": mon.ten_san_pham, "so_luong": item.so_luong})
            return Response(data_res, status.HTTP_200_OK)

        except Exception as e:
            return Response({"message:" + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='update-order')
    def update_order(self, request, pk=None):
        try:
            PERCENT_TOTAL_BILL = take_manage("PERCENT_TOTAL_BILL")
            TIME_UPDATE_ORDER_FEW = take_manage("TIME_UPDATE_ORDER_FEW")
            TIME_UPDATE_ORDER_MANY = take_manage("TIME_UPDATE_ORDER_MANY")
            COUNT_TABLE_MANY = take_manage("COUNT_TABLE_MANY")
            tong_tien = 0
            so_dien_thoai = request.data.get('so_dien_thoai')
            order = request.data.get('ds_order', [])
            time_update = datetime.now().replace(tzinfo=None)
            ngay_dat_ban = datetime.strptime(request.data.get('ngay_dat_ban'), "%Y-%m-%d")
            ban = DsDatBan.objects.filter(
                Q(so_dien_thoai=so_dien_thoai) and Q(thoi_gian_dat_ban__date=ngay_dat_ban)).first()
            # Xác định giá trị delta_time dựa trên số lượng bàn
            if ban.so_luong_ban < COUNT_TABLE_MANY:
                delta_time = timedelta(minutes=TIME_UPDATE_ORDER_FEW)
            else:
                delta_time = timedelta(days=TIME_UPDATE_ORDER_MANY)
            time_allow = ban.thoi_gian_nhan_ban.replace(tzinfo=None) - delta_time
            if time_update <= time_allow:
                tong_tien = 0
                ds_order = DsOrder.objects.filter(ds_dat_ban_id=ban.id)
                for item in order:
                    menu_id = item["id"]
                    so_luong = item["so_luong"]

                    # Kiểm tra xem DsOrder đã tồn tại trong ds_order hay chưa
                    order_exists = ds_order.filter(menu_id=menu_id).first()

                    if order_exists:
                        # Nếu DsOrder đã tồn tại, cập nhật số lượng
                        order_exists.so_luong = so_luong
                        order_exists.save()
                    else:
                        # Nếu DsOrder chưa tồn tại, tạo mới
                        mon = Menu.objects.get(id=menu_id)
                        new_order = DsOrder(ds_dat_ban_id=ban.id, menu=mon, so_luong=so_luong)
                        new_order.save()
                # xóa đi order không có trong request
                ds_order.exclude(menu_id__in=[item["id"] for item in order]).delete()
                # Tính tổng tiền
                tong_tien = ds_order.aggregate(Sum('menu__don_gia'))['menu__don_gia__sum']
                if tong_tien != 0:
                    tong_tien = (tong_tien * PERCENT_TOTAL_BILL) / 100
                hoa_don = HoaDonCocTien.objects.get(ds_dat_ban_id=ban.id)
                hoa_don.tong_tien = tong_tien
                hoa_don.save()
                return Response("message: Updated", status=status.HTTP_200_OK)
            else:
                return Response("message: cannot update", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='thong-ke-order-today')
    def today(self, request, pk=None):
        try:
            current_time = datetime.now().replace(tzinfo=None).date()
            thong_ke = HoaDonCocTien.objects.filter(ngay_thanh_toan__date=current_time) \
                .values('trang_thai') \
                .annotate(total_tong_tien=Sum('tong_tien'), so_luong=Count('id'))
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='thong-ke-order')
    def thong_ke(self, request, pk=None):
        try:
            ngay_bat_dau = datetime.strptime(request.data.get('start_time'), "%Y-%m-%d").replace(tzinfo=None)
            if request.data.get('end_time'):
                ngay_ket_thuc = datetime.strptime(request.data.get('end_time'), "%Y-%m-%d").replace(
                    tzinfo=None)
                if ngay_ket_thuc < ngay_bat_dau:
                    raise Exception("Lỗi thời gian")
                # Lấy tất cả các hóa đơn trong khoảng thời gian đã cho
                thong_ke = HoaDonCocTien.objects.filter(ngay_thanh_toan__range=(ngay_bat_dau, ngay_ket_thuc))

                # Tạo một danh sách chứa các trạng thái
                trang_thai_choices = HoaDonCocTien.objects.values_list('trang_thai', flat=True).distinct()

                # Tạo một danh sách để lưu trữ kết quả thống kê cho mỗi trạng thái
                ket_qua_thong_ke = []

                # Duyệt qua tất cả các ngày trong khoảng thời gian đã cho
                for ngay in range((ngay_ket_thuc - ngay_bat_dau).days + 1):
                    ngay_hien_tai = ngay_bat_dau + timedelta(days=ngay)
                    thong_ke_ngay = {
                        'ngay': ngay_hien_tai.date(),
                    }
                    for trang_thai in trang_thai_choices:
                        so_luong = thong_ke.filter(ngay_thanh_toan__date=ngay_hien_tai, trang_thai=trang_thai).count()
                        thong_ke_ngay[trang_thai] = so_luong
                    ket_qua_thong_ke.append(thong_ke_ngay)
                return Response(ket_qua_thong_ke, status.HTTP_200_OK)
            else:
                thong_ke = HoaDonCocTien.objects.filter(ngay_thanh_toan__date=ngay_bat_dau) \
                    .values('trang_thai') \
                    .annotate(total_tong_tien=Sum('tong_tien'), so_luong=Count('id'))
                return Response(thong_ke, status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class HoaDonThanhToanViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = HoaDonThanhToan.objects.all()
    serializer_class = HoaDonThanhToanSerializer

    @action(methods=['post'], detail=False, url_path="thong-ke-coc-tien-theo-thoi-gian")
    def coc_tien_theo_time(self, request, pk=None):
        try:
            start_time = datetime.strptime(request.data.get('start_time'), "%Y-%m-%d").replace(tzinfo=None)
            if request.data.get('end_time'):
                end_time = datetime.strptime(request.data.get('end_time'), "%Y-%m-%d").replace(
                    tzinfo=None) + timedelta(days=1)
                if end_time < start_time:
                    raise Exception("Lỗi thời gian")
                hoa_don_theo_time = (
                    HoaDonCocTien.objects
                    .filter(ngay_thanh_toan__range=(start_time, end_time))
                    # .annotate(ngay=ExtractDay('ngay_thanh_toan'))
                    # .values('ngay')
                    .values('trang_thai')
                    .annotate(total_so_luong=Count('id'))
                    .annotate(total_tong_tien=Sum('tong_tien'))
                    # .order_by('-ngay')
                )
                return Response(hoa_don_theo_time, status.HTTP_200_OK)
            else:
                hoa_don_theo_time = (
                    HoaDonCocTien.objects
                    .filter(ngay_thanh_toan__date=start_time)
                    # .annotate(ngay=ExtractDay('ngay_thanh_toan'))
                    # .values('ngay')
                    .values('trang_thai')
                    .annotate(total_so_luong=Count('id'))
                    .annotate(total_tong_tien=Sum('tong_tien'))
                    # .order_by('-ngay')
                )
                return Response(hoa_don_theo_time, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='thong-ke-today')
    def thong_ke_today(self, request, pk=None):
        try:
            current_time = datetime.now().replace(tzinfo=None).date()
            thong_ke = HoaDonCocTien.objects.filter(ngay_thanh_toan__date=current_time) \
                .values('trang_thai') \
                .annotate(total_tong_tien=Sum('tong_tien'), so_luong=Count('id'))
            return Response(thong_ke, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='thong-ke-bill-theo-quy')
    def thong_ke_bill_quy(self, request, pk=None):
        try:
            current_time = datetime.now().replace(tzinfo=None)
            thong_ke = []
            quy = 1
            for i in range(1, 13, 3):
                item = HoaDonThanhToan.objects.filter(Q(thoi_gian_thanh_toan__month__range=(i, i + 2)) & Q(
                    thoi_gian_thanh_toan__year=current_time.year)).aggregate(total_tong_tien=Sum('tong_tien'),
                                                                             total_so_luong=Count('id'))
                item['quy'] = quy
                quy += 1
                thong_ke.append(item)
            return Response(thong_ke, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='thong-ke-bill')
    def thong_ke_bill(self, request, pk=None):
        try:
            ngay_bat_dau = datetime.strptime(request.data.get('ngay_bat_dau'), "%Y-%m-%d").replace(tzinfo=None)
            if request.data.get('ngay_ket_thuc'):
                ngay_ket_thuc = datetime.strptime(request.data.get('ngay_ket_thuc'), "%Y-%m-%d").replace(tzinfo=None)
                if ngay_ket_thuc < ngay_bat_dau:
                    raise Exception("Lỗi thời gian")
                thong_ke = HoaDonThanhToan.objects.filter(thoi_gian_thanh_toan__range=(ngay_bat_dau, ngay_ket_thuc)) \
                    .aggregate(total_tong_tien=Sum('tong_tien'), total_so_luong=Count('id'))
                return Response(thong_ke, status.HTTP_200_OK)
            else:
                thong_ke = HoaDonThanhToan.objects.filter(thoi_gian_thanh_toan__date=ngay_bat_dau) \
                    .aggregate(total_tong_tien=Sum('tong_tien'), total_so_luong=Count('id'))
                return Response(thong_ke, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='create-bill')
    def create_bill(self, request, pk=None):
        try:
            real_time = datetime.now().replace(tzinfo=None)
            tong_tien = 0
            ds_mon_an = request.data.get("ds_mon_an", [])
            if request.data.get('voucher'):
                voucher = GiamGia.objects.get(ma_giam_gia=request.data.get('voucher'))
                if not voucher:
                    raise Exception('Mã giảm giá không tồn tại')
            if request.data.get('so_dien_thoai'):
                khach_hang = KhachHang.objects.get(so_dien_thoai=request.data.get('so_dien_thoai'))
                if not khach_hang:
                    raise Exception('Số điện thoại chưa đăng kí thành viên')
            new_bill = HoaDonThanhToan(thoi_gian_thanh_toan=real_time, tong_tien=tong_tien)
            new_bill.save()
            new_bill_id = HoaDonThanhToan.objects.get(thoi_gian_thanh_toan=real_time).id
            for item in ds_mon_an:
                mon = Menu.objects.get(id=int(item["id"]))
                mon_an_id = mon.id
                so_luong = int(item["so_luong"])
                tong_tien += mon.don_gia * so_luong
                new_bill_detail = ChiTietHoaDon(so_luong=so_luong, hoa_don_id=new_bill_id, menu_id=mon_an_id)
                new_bill_detail.save()
            if request.data.get('so_dien_thoai'):
                khach_hang = KhachHang.objects.get(so_dien_thoai=request.data.get('so_dien_thoai'))
                if not khach_hang:
                    raise Exception('Số điện thoại chưa đăng kí thành viên')
                new_bill.khach_hang_id = khach_hang.id
                new_bill.save()
            if request.data.get('voucher'):
                voucher = GiamGia.objects.get(ma_giam_gia=request.data.get('voucher'))
                real_time = datetime.now().date()
                so_luong = voucher.so_luong
                if so_luong is None: so_luong = 1
                max_time_allow = voucher.ngay_bat_dau.date()
                min_time_allow = voucher.ngay_ket_thuc.date()
                if max_time_allow <= real_time <= min_time_allow and so_luong > 0:
                    if voucher.so_tien_giam:
                        tong_tien -= voucher.so_tien_giam
                    elif voucher.ty_le_giam:
                        float_value = float(voucher.ty_le_giam)
                        tong_tien -= tong_tien * float_value
                    new_bill.giam_gia_id = voucher.id
                    if voucher.so_luong is not None:
                        voucher.so_luong = so_luong - 1
                        voucher.save()
                new_bill.tong_tien = tong_tien
                new_bill.save()
            new_bill.tong_tien = tong_tien
            new_bill.save()
            serializer = HoaDonThanhToanSerializer(new_bill)
            data_serialier = serializer.data
            return Response(data_serialier, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='thong-ke-doanh-thu-today')
    def today(self, request, pk=None):
        try:
            current_time = datetime.now().replace(tzinfo=None).date()
            # thong_ke = HoaDonCocTien.objects.filter(ngay_thanh_toan__date=current_time) \
            #     .values('trang_thai') \
            #     .annotate(total_tong_tien=Sum('tong_tien'), so_luong=Count('id'))
            # return Response(thong_ke, status.HTTP_200_OK)
            thong_ke = HoaDonThanhToan.objects.filter(thoi_gian_thanh_toan__date=current_time) \
                .aggregate(total_tong_tien=Sum('tong_tien'), total_so_luong=Count('id'))
            return Response(thong_ke, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path="thong-ke-doanh-thu-theo-thoi-gian")
    def thong_ke_theo_time(self, request, pk=None):
        try:
            start_time = datetime.strptime(request.data.get('start_time'), "%Y-%m-%d").replace(tzinfo=None)
            end_time = datetime.strptime(request.data.get('end_time'), "%Y-%m-%d").replace(
                tzinfo=None) + timedelta(days=1)
            if end_time < start_time:
                raise Exception("Lỗi thời gian")
            hoa_don_theo_time = (
                HoaDonThanhToan.objects
                .filter(thoi_gian_thanh_toan__range=(start_time, end_time))
                .annotate(ngay=ExtractDay('thoi_gian_thanh_toan'))
                .annotate(thang=ExtractMonth('thoi_gian_thanh_toan'))
                .annotate(nam=ExtractYear('thoi_gian_thanh_toan'))
                .values('ngay', 'thang', 'nam')
                .annotate(total_so_luong=Count('id'))
                .annotate(total_tong_tien=Sum('tong_tien'))
                .order_by('-nam', '-thang', '-ngay')
            )
            return Response(hoa_don_theo_time, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='thong-ke-doanh-thu-theo-ngay')
    def thong_ke_theo_ngay(self, request, pk=None):
        try:
            time = datetime.now().replace(tzinfo=None).date()
            if request.data.get('time'):
                time = datetime.strptime(request.data.get('time'), '%Y-%m-%d').replace(tzinfo=None)
            thong_ke = (
                HoaDonThanhToan.objects
                .filter(thoi_gian_thanh_toan__date=time).aggregate(total_tong_tien=Sum('tong_tien'),
                                                                   total_so_luong=Count('id'))
            )
            return Response(thong_ke, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='thong-ke-doanh-thu-theo-thang')
    def thong_ke(self, request, pk=None):
        try:
            current_year = datetime.now().replace(tzinfo=None).year
            hoa_don_theo_thang = (
                HoaDonThanhToan.objects
                .filter(thoi_gian_thanh_toan__year=current_year)
                .annotate(thang=ExtractMonth('thoi_gian_thanh_toan'))
                .values('thang')
                .annotate(so_luong=Count('id'))
                .annotate(doanh_thu=Sum('tong_tien'))
                .order_by('thang')
            )
            return Response(hoa_don_theo_thang, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GiamGiaViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = GiamGia.objects.all()
    serializer_class = GiamGiaSerializer

    @action(methods=['get'], detail=False, url_path='get-current-voucher')
    def get_current_voucher(self, request, pk=None):
        try:
            current_time = datetime.now().replace(tzinfo=None)
            vouchers = GiamGia.objects.filter(
                Q(ngay_ket_thuc__date__gte=current_time.date()) & Q(ngay_ket_thuc__year=current_time.year)).order_by(
                'ngay_ket_thuc')
            vouchers = GiamGiaSerializer(vouchers, many=True).data
            return Response(vouchers, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='create-voucher')
    def create_voucher(self, request, pk=None):
        try:
            time_start = datetime.strptime(request.data.get('time_start'), "%Y-%m-%d %H:%M:%S")
            time_end = datetime.strptime(request.data.get('time_end'), "%Y-%m-%d %H:%M:%S")
            voucher_res = None
            if time_start >= time_end:
                raise Exception("thời gian không hợp lệ")
            if request.data.get('so_tien_giam'):
                tien = request.data.get('so_tien_giam')
                check_voucher = GiamGia.objects.filter(Q(ngay_bat_dau=time_start) &
                                                       Q(ngay_ket_thuc=time_end) &
                                                       Q(so_tien_giam=tien)).first()
                if check_voucher:
                    raise Exception("Voucher đã tồn tại")
                else:
                    new_voucher = GiamGia(ngay_bat_dau=time_start, ngay_ket_thuc=time_end, so_tien_giam=tien)
                if request.data.get('so_luong'):
                    new_voucher.so_luong = int(request.data.get('so_luong'))
                new_voucher.save()
                voucher_res = GiamGia.objects.filter(Q(ngay_bat_dau=time_start) &
                                                     Q(ngay_ket_thuc=time_end) &
                                                     Q(so_tien_giam=tien)).first()
            if request.data.get('ty_le_giam'):
                ty_le = int(request.data.get('ty_le_giam'))
                ty_le /= 100
                check_voucher = GiamGia.objects.filter(Q(ngay_bat_dau=time_start) &
                                                       Q(ngay_ket_thuc=time_end) &
                                                       Q(ty_le_giam=ty_le)).first()
                if check_voucher:
                    raise Exception("Voucher đã tồn tại")
                else:
                    new_voucher = GiamGia(ngay_bat_dau=time_start, ngay_ket_thuc=time_end, ty_le_giam=ty_le)
                if request.data.get('so_luong'):
                    new_voucher.so_luong = int(request.data.get('so_luong'))
                new_voucher.save()
                voucher_res = GiamGia.objects.filter(Q(ngay_bat_dau=time_start) &
                                                     Q(ngay_ket_thuc=time_end) &
                                                     Q(ty_le_giam=ty_le)).first()
            if voucher_res is not None:
                data = GiamGiaSerializer(voucher_res).data
                actived = f"CREATE_GIAMGIA"
                add_actived(actived, Status.Success)
                return Response(data, status=status.HTTP_200_OK)
            else:
                voucher_res = GiamGia.objects.filter(Q(ngay_bat_dau=time_start) &
                                                     Q(ngay_ket_thuc=time_end)).all()
                data = GiamGiaSerializer(voucher_res, many=True).data
                actived = f"CREATE_GIAMGIA"
                add_actived(actived, Status.Success)
                return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            actived = f"CREATE_GIAMGIA"
            add_actived(actived, Status.Failed)
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['put'], detail=True, url_path='change-active')
    def change_active(self, request, pk):
        try:
            voucher = GiamGia.objects.get(id=pk)
            if voucher.active:
                voucher.active = False
                voucher.save()
            else:
                voucher.active = True
                voucher.save()
            actived = f"CHANGE_ACTIVE_GIAMGIA GIAM_GIA_ID={str(voucher.id)}"
            add_actived(actived, Status.Success)
            return Response(dict(message="Update success"), status.HTTP_200_OK)

        except Exception as e:
            actived = f"CHANGE_ACTIVE_GIAMGIA"
            add_actived(actived, Status.Failed)
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='search-voucher')
    def search_voucher(self, request, pk=None):
        try:
            key = request.data.get('key')
            query = Q()
            query |= Q(ma_giam_gia__icontains=key)
            query |= Q(ty_le_giam__icontains=key)
            query |= Q(so_tien_giam__icontains=key)
            query |= Q(id__icontains=key)
            result = GiamGia.objects.filter(query).order_by('ngay_ket_thuc')
            data = GiamGiaSerializer(result, many=True).data
            return Response(data, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='check-ma-giam-gia')
    def check_code(self, request, pk=None):
        try:
            code = request.data.get('code')
            voucher = GiamGia.objects.get(ma_giam_gia=code)
            if voucher:
                real_time = datetime.now().date()
                start_date = voucher.ngay_bat_dau.date()
                end_date = voucher.ngay_ket_thuc.date()
                is_active = voucher.active
                so_luong = voucher.so_luong
                if so_luong is None: so_luong = 1
                if start_date <= real_time <= end_date and is_active is True and so_luong > 0:
                    return Response({"message: Mã giảm giá còn sử dụng được"}, status.HTTP_200_OK)
                else:
                    return Response({"message: Mã giảm giá hết hiệu lực"}, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)


class ChiTietHoaDonViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = ChiTietHoaDon.objects.all()
    serializer_class = ChiTietHoaDonSerializer

    @action(methods=['post'], detail=False, url_path='thong-ke-mon-theo-ngay')
    def thong_ke_theo_ngay(self, request, pk=None):
        try:
            time = datetime.strptime(request.data.get('time'), "%Y-%m-%d")
            thong_ke = (ChiTietHoaDon.objects.filter(hoa_don__thoi_gian_thanh_toan__date=time)
                        .values('menu__ten_san_pham', 'menu__loai')
                        .annotate(total_so_luong=Sum('so_luong')).order_by('-total_so_luong')
                        )
            for item in thong_ke:
                mon = Menu.objects.get(ten_san_pham=item['menu__ten_san_pham'])
                item['total_tong_tien'] = item['total_so_luong'] * mon.don_gia
            return Response(thong_ke, status.HTTP_200_OK)

        except Exception as e:
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path="thong-ke-mat-hang-quy")
    def mat_hang_thang(self, request, pk=None):
        try:
            current_time = datetime.now().replace(tzinfo=None)
            thong_ke = []
            quy = 1
            for i in range(1, 13, 3):
                item = HoaDonThanhToan.objects.filter(Q(thoi_gian_thanh_toan__month__range=(i, i + 2)) & Q(
                    thoi_gian_thanh_toan__year=current_time.year)).aggregate(total_tong_tien=Sum('tong_tien'),
                                                                             total_so_luong=Count('id'))
                item['quy'] = quy
                quy += 1
                thong_ke.append(item)
            return Response(thong_ke, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='thong-ke-loai-mon-an-month')
    def loai_month(self, request, pk=None):
        try:
            current_time = datetime.now().replace(tzinfo=None).year
            # Lấy tất cả các hóa đơn trong khoảng thời gian đã cho
            thong_ke = ChiTietHoaDon.objects.filter(hoa_don__thoi_gian_thanh_toan__year=current_time)

            # Tạo một danh sách chứa các loại
            loai_choices = Menu.objects.values_list('loai', flat=True).distinct()

            # Tạo một danh sách để lưu trữ kết quả thống kê cho mỗi trạng thái
            ket_qua_thong_ke = {}
            for loai in loai_choices:
                so_luong = thong_ke.filter(menu__loai=loai).count()
                ket_qua_thong_ke[loai] = so_luong

            return Response(ket_qua_thong_ke, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='thong-ke-mon-an-today')
    def today(self, request, pk=None):
        try:
            current_time = datetime.now().replace(tzinfo=None).date()
            thong_ke_mon_an = (
                ChiTietHoaDon.objects
                .filter(hoa_don__thoi_gian_thanh_toan__date=current_time)
                .values('menu__ten_san_pham', 'menu__loai')
                .annotate(tong_so_luong=Sum('so_luong')).order_by('-tong_so_luong')
            )
            for item in thong_ke_mon_an:
                mon = Menu.objects.get(ten_san_pham=item['menu__ten_san_pham'])
                item['tong_tien'] = item['tong_so_luong'] * mon.don_gia

            return Response(thong_ke_mon_an, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='thong-ke-mon-an-theo-thang')
    def thong_ke_theo_thang(self, request, pk=None):
        try:
            thang = request.data.get('thang')
            current_year = datetime.now().replace(tzinfo=None).year
            thong_ke_mon_an = (
                ChiTietHoaDon.objects
                .filter(hoa_don__thoi_gian_thanh_toan__year=current_year,
                        hoa_don__thoi_gian_thanh_toan__month=thang)
                .values('menu__ten_san_pham')
                .annotate(tong_so_luong=Sum('so_luong'))
            )
            # Tính toán tổng doanh thu bên ngoài truy vấn
            for item in thong_ke_mon_an:
                menu = Menu.objects.get(ten_san_pham=item['menu__ten_san_pham'])
                doanh_thu = menu.don_gia * item['tong_so_luong']
                item['doanh_thu'] = doanh_thu
            return Response(thong_ke_mon_an, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, url_path='thong-ke-mon-an-theo-thoi-gian')
    def thong_ke_mon_an_time(self, request, pk=None):
        try:
            start_time = datetime.strptime(request.data.get('start_time'), "%Y-%m-%d").replace(tzinfo=None)
            end_time = datetime.strptime(request.data.get('end_time'), "%Y-%m-%d").replace(
                tzinfo=None) + timedelta(days=1)
            if end_time < start_time:
                raise Exception("Lỗi thời gian")

            thong_ke_mon_an = (
                ChiTietHoaDon.objects
                .filter(hoa_don__thoi_gian_thanh_toan__range=(start_time, end_time))
                .values('menu__ten_san_pham', 'menu__loai')
                .annotate(tong_so_luong=Sum('so_luong'))
                .order_by('tong_so_luong')
            )
            # Tính toán tổng doanh thu bên ngoài truy vấn
            for item in thong_ke_mon_an:
                menu = Menu.objects.get(ten_san_pham=item['menu__ten_san_pham'])
                doanh_thu = menu.don_gia * item['tong_so_luong']
                item['doanh_thu'] = doanh_thu
            return Response(thong_ke_mon_an, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['get'], detail=False, url_path='thong-ke-mon-an-theo-nam')
    def thong_ke_theo_nam(self, request, pk=None):
        try:
            current_year = datetime.now().replace(tzinfo=None).year
            thong_ke_mon_an = (
                ChiTietHoaDon.objects
                .filter(hoa_don__thoi_gian_thanh_toan__year=current_year)
                .values('menu__ten_san_pham')
                .annotate(tong_so_luong=Sum('so_luong'))
            )
            # Tính toán tổng doanh thu bên ngoài truy vấn
            for item in thong_ke_mon_an:
                menu = Menu.objects.get(ten_san_pham=item['menu__ten_san_pham'])
                doanh_thu = menu.don_gia * item['tong_so_luong']
                item['doanh_thu'] = doanh_thu
            thong_ke_mon_an = sorted(thong_ke_mon_an, key=lambda x: x['tong_so_luong'], reverse=True)
            return Response(thong_ke_mon_an, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ChangeFile(viewsets.ViewSet, generics.ListAPIView):
    @action(methods=['post'], detail=False, url_path='json-to-excel')
    def json_to_excel(self, request, pk=None):
        try:
            data = request.data.get('data')
            df = pd.DataFrame(data)
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename="data.xlsx"'
            df.to_excel(response, index=False, engine='openpyxl')
            return response
        except Exception as e:
            return Response({"message: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Actived(viewsets.ViewSet, generics.ListAPIView):
    queryset = list_actived.objects.all()
    serializer_class = ActivedSerializer

    @action(methods=['get'], detail=False, url_path='get-today-active')
    def today_active(self, request, pk=None):
        today = datetime.now().replace(tzinfo=None).date()
        list_active = list_actived.objects.filter(time__date=today).all().order_by("time")
        len_list = len(list_active)
        list_active = ActivedSerializer(list_active, many=True)
        stt = list(range(1, len_list + 1))
        for i in range(len_list):
            list_active.data[i]['stt'] = stt[i]
        return Response(list_active.data, status.HTTP_200_OK)

    @action(methods=['post'], detail=False, url_path='get-active')
    def active(self, request, pk=None):
        try:
            date = request.data.get('date')
            date = datetime.strptime(date, "%Y-%m-%d")
            list_active = list_actived.objects.filter(time__date=date).all().order_by("time")
            len_list = len(list_active)
            list_active = ActivedSerializer(list_active, many=True)
            stt = list(range(1, len_list + 1))
            for i in range(len_list):
                list_active.data[i]['stt'] = stt[i]
            return Response(list_active.data, status.HTTP_200_OK)
        except Exception as e:
            return Response({"message: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ManageViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Manage.objects.all()
    serializer_class = ManageSerialiser

    @action(methods=['put'], detail=True, url_path='update-role')
    def update_role(self, request, pk):
        try:
            role = Manage.objects.get(id=pk)
            value = request.data.get('value')
            if int(value) < 0:
                raise Exception('error value')
            old_value = role.value
            role.value = value
            role.save()
            actived = f"UPDATE {role.name} CHANGE VALUE={old_value} TO VALUE={role.value}"
            add_actived(actived, Status.Success)
            return Response(dict(message="Update success"), status.HTTP_200_OK)
        except Exception as e:
            role = Manage.objects.get(id=pk)
            actived = f"UPDATE_ROLE {role.name}"
            add_actived(actived, Status.Failed)
            return Response({"message: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class AuthInfo(APIView):
#     def get(self, request):
#         return Response(settings.OAUTH2_INFO, status=status.HTTP_200_OK)
