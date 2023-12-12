import string
from datetime import datetime
import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


def generate_random_code():
    code_length = 6
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choice(characters) for _ in range(code_length))

# Create your models here.


class User(AbstractUser):
    avatar = models.ImageField(upload_to='upload/avatar')


class KhachHang(models.Model):
    so_dien_thoai = models.CharField(max_length=10, null=False, unique=True)
    ho_ten = models.CharField(max_length=100, null=False)
    dia_chi = models.CharField(max_length=255, null=False)
    rank = models.IntegerField(null=False, default=0)

class Ban(models.Model):
    so_luong = models.IntegerField(null=False)
    is_trang_thai = models.BooleanField(default=True, null=False)
    suc_chua = models.IntegerField(null=False)
    loai_ban = models.CharField(max_length=150, null=False,unique=True)
    def __str__(self):
        return self.loai_ban

class DsDatBan(models.Model):
    is_trang_thai = models.BooleanField(default=False)
    so_dien_thoai = models.CharField(max_length=10)
    thoi_gian_dat_ban = models.DateTimeField(null=False)
    thoi_gian_nhan_ban = models.DateTimeField(null=False)
    so_luong_ban = models.IntegerField(null=False)
    ten_nguoi_dat = models.CharField(max_length=255, null=False)
    khach_hang = models.ForeignKey(KhachHang, on_delete=models.SET_NULL, null=True, blank=True)
    ban = models.ForeignKey(Ban, on_delete=models.CASCADE, null=False)
    menus = models.ManyToManyField('Menu', through='DsOrder')
    ma_dat_ban = models.CharField(max_length=10, unique=False, null=True,blank=True)

@receiver(pre_save, sender=DsDatBan)
def generate_Ma_dat_ban(sender, instance, **kwargs):
    if not instance.ma_dat_ban:
        last_record = DsDatBan.objects.order_by('ma_dat_ban').last()
        if not last_record:
            instance.ma_dat_ban = 'MDB0000001'
        else:
            current_number = int(last_record.ma_dat_ban[3:]) + 1
            instance.ma_dat_ban = f'MDB{current_number:07d}'



class LoaiSanPham(models.TextChoices):
    MON_NUOC = 'mon_nuoc'
    MON_AN = 'mon_an'
    TRANG_MIEN = 'trang_mieng'
class Menu(models.Model):
    don_gia = models.FloatField(null=False, unique=True)
    link_anh = models.ImageField(upload_to='upload/menu',null=False)
    ten_san_pham = models.CharField(max_length=255,null= False)
    loai = models.CharField(
        max_length=20,
        choices=LoaiSanPham.choices,
        default=LoaiSanPham.MON_AN
    )
    is_trang_thai = models.BooleanField(default=True, null=False)
    def __str__(self):
        return self.ten_san_pham
class TrangThaiCocTien(models.TextChoices):
    Da_THANH_TOAN = 'da thanh toan'
    HUY_COC = 'huy coc'
    HOAN_COC = 'hoan coc'
class HoaDonCocTien(models.Model):
    ngay_thanh_toan = models.DateTimeField(default= timezone.now)
    ds_dat_ban = models.OneToOneField(DsDatBan, on_delete=models.CASCADE)
    tong_tien = models.FloatField(null= False)
    trang_thai = models.CharField(
        max_length=100,
        choices=TrangThaiCocTien.choices,
        default=TrangThaiCocTien.Da_THANH_TOAN
    )


class DsOrder(models.Model):
    ds_dat_ban = models.ForeignKey(DsDatBan, on_delete=models.CASCADE, null=False)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=False)
    so_luong = models.IntegerField(null=False)




class GiamGia(models.Model):
    ma_giam_gia = models.CharField(max_length=7,unique=True, null=False,default=generate_random_code, blank=True)
    ngay_bat_dau = models.DateTimeField(null=False)
    ngay_ket_thuc = models.DateTimeField(null=False)
    so_luong = models.IntegerField(null=True, blank=True)
    active = models.BooleanField(default=True, blank=True)
    ty_le_giam = models.DecimalField(max_digits=2, decimal_places=2, null=True, blank=True)
    so_tien_giam = models.FloatField(null=True,blank=True)

    def save(self, *args, **kwargs):
        if self.ty_le_giam is not None and self.so_tien_giam is not None:
            raise ValueError("Only one of field1 and field2 can have a value")
        super(GiamGia, self).save(*args, **kwargs)
    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(ty_le_giam__isnull=True) | Q(so_tien_giam__isnull=True),
                name="one_field_only",
            )
        ]

    def __str__(self):
        return self.ma_giam_gia


class HoaDonThanhToan(models.Model):
    thoi_gian_thanh_toan = models.DateTimeField(default= timezone.now)
    tong_tien = models.FloatField(null= False)
    giam_gia = models.ForeignKey(GiamGia, on_delete=models.SET_NULL, blank=True, null=True)
    khach_hang = models.ForeignKey(KhachHang, on_delete=models.SET_NULL, blank=True, null=True)
    ma_hoa_don = models.CharField(max_length=10, unique=True, null=True, blank=True)

@receiver(pre_save, sender=HoaDonThanhToan)
def generate_Ma_Hoa_Don(sender, instance, **kwargs):
    if not instance.ma_hoa_don:
        last_record = HoaDonThanhToan.objects.order_by('ma_hoa_don').last()
        if not last_record:
            instance.ma_hoa_don = 'MHD0000001'
        else:
            current_number = int(last_record.ma_hoa_don[3:]) + 1
            instance.ma_hoa_don = f'MHD{current_number:07d}'

class ChiTietHoaDon(models.Model):
    hoa_don = models.ForeignKey(HoaDonThanhToan, on_delete=models.CASCADE, null=False)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, null=False)
    so_luong = models.IntegerField(null=False)


class Rule(models.Model):
    name = models.CharField(max_length=255, null= False)
    value = models.IntegerField(null=False, default=0)
    unit = models.CharField(max_length=100, null=False)
    describe = models.CharField(max_length=255)


    def __str__(self):
        return self.name

class Manage(models.Model):
    name = models.CharField(max_length=255, null= False, unique=True)
    value = models.IntegerField(null=False, default=0)
    unit = models.CharField(max_length=100, null=False)
    describe = models.CharField(max_length=255)


    def __str__(self):
        return self.name



class Status(models.TextChoices):
    Success = 'success'
    Cancel = 'cancel'
    Failed = 'failed'
    Not_allow = 'not_allow'

class list_actived(models.Model):
    time = models.DateTimeField(null= False)
    actived = models.CharField(max_length=255, null= False)
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.Failed
    )


    def __str__(self):
        return self.actived