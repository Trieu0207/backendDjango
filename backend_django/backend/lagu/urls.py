from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register('testAPi', views.TestView, 'test')
router.register("ban", views.BanViewSet, 'ban')
router.register("menu", views.MenuViewSet, 'menu')
router.register('dsDatBan', views.DsDatBanViewSet,'ds_dat_ban')
router.register('thanhToan', views.HoaDonThanhToanViewSet, 'thanh_toan')
router.register('khachHang', views.KhachHangViewSet, 'khach_hang')
router.register("DsOrder", views.DsOrderViewSet, 'order')
router.register("GiamGia", views.GiamGiaViewSet, 'voucher')
router.register("chitiethoadon", views.ChiTietHoaDonViewSet, 'chitiethoadon')
router.register('user', views.UserViewSet)
router.register("xuatfile", views.ChangeFile, 'changefile')
router.register("active", views.Actived, 'actived')
router.register("manage", views.ManageViewSet, 'manage')
urlpatterns = [
    path('', include(router.urls)),
    # path('oauth2-info/', views.AuthInfo.as_view())
]