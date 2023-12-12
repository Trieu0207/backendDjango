from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer
from .models import *


class UserSerializer(ModelSerializer):
    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(user.password)
        user.save()

        return user

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        extra_kwargs = {
            'password': {'write_only': 'true'}
        }


class BanSerializer(ModelSerializer):
    class Meta:
        model = Ban
        fields = "__all__"


class MenuSerializer(ModelSerializer):
    link_anh = SerializerMethodField()

    def get_link_anh(self, menu):
        request = self.context['request']
        link_anh = menu.link_anh.name
        if menu.link_anh:
            if link_anh.startswith("static/"):
                path = '/%s' % link_anh
            else:
                path = '/static/%s' % link_anh

            return request.build_absolute_uri(path)

    class Meta:
        model = Menu
        fields = "__all__"


class CustomDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        # Chuyển đổi thời gian thành chuỗi không kèm theo múi giờ
        if value:
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return None


class DSDatBanSerialier(ModelSerializer):
    thoi_gian_nhan_ban = CustomDateTimeField(format='%Y-%m-%d %H:%M:%S')
    thoi_gian_dat_ban = CustomDateTimeField(format='%Y-%m-%d %H:%M:%S')

    class Meta:
        model = DsDatBan
        fields = "__all__"


class KhachHangSerializer(ModelSerializer):
    class Meta:
        model = KhachHang
        fields = "__all__"


class DsOrderSerialier(ModelSerializer):
    class Meta:
        model = DsOrder
        fields = "__all__"


class HoaDonThanhToanSerializer(ModelSerializer):
    class Meta:
        model = HoaDonThanhToan
        fields = "__all__"


class ChiTietHoaDonSerializer(ModelSerializer):
    class Meta:
        model = ChiTietHoaDon
        fields = "__all__"


class GiamGiaSerializer(ModelSerializer):
    class Meta:
        model = GiamGia
        fields = "__all__"


class HoaDonCocTienSerializer(ModelSerializer):
    class Meta:
        model = HoaDonCocTien
        fields = "__all__"


class ManageSerialiser(ModelSerializer):
    class Meta:
        model = Manage
        fields = "__all__"


class ActivedSerializer(ModelSerializer):
    class Meta:
        model = list_actived
        fields = "__all__"
