from django.urls import reverse
from datetime import timezone
import datetime
import re
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from .forms import DonHangForm, LoginForm, SigninForm
from core.models import (
    ChiTietDonHang,
    DonDatHang,
    Menu,
    DanhMucSanPham,
    DanhMucThuongHieu,
    SanPham,
    ChiTietSanPham,
    Cart,
    Account,
    LoaiSanPham,
    ThuongHieuSanPham,
    Roles,
)
from datetime import date
from django.views.decorators.cache import never_cache
from decimal import Decimal
from django.db.models import Q


@never_cache
def home(request):
    menus = Menu.objects.all()
    danh_mucs = DanhMucThuongHieu.objects.all()
    danh_muc_san_phams = DanhMucSanPham.objects.all()
    data = {
        "menus": menus,
        "danh_mucs": danh_mucs,
        "danh_muc_san_phams": danh_muc_san_phams,
    }
    return render(request, "pages/home.html", data)


def cart(request):
    menus = Menu.objects.all()
    danh_mucs = DanhMucThuongHieu.objects.all()
    danh_muc_san_phams = DanhMucSanPham.objects.all()
    user_id = request.session.get("user_id")
    total_price = Decimal("0")
    product_list = []

    if user_id:
        if request.method == "POST":
            # Xóa toàn bộ sản phẩm khỏi giỏ hàng
            request.session["cart"] = {}
            return redirect("cart")

        cart_items = Cart.objects.filter(NguoiDung_id=user_id)

        for cart_item in cart_items:
            product = get_object_or_404(SanPham, MaSP=cart_item.SanPham_id)
            item_quantity = cart_item.SoLuong

            product_info = {
                "id": product.MaSP,
                "name": product.TenSP,
                "price": float(product.GiaBan),
                "price_sale": float(product.GiaGiam),
                "quantity": item_quantity,
                "image": product.HinhAnh.url,
            }
            product_list.append(product_info)

            if product.GiaGiam != 0:
                total_price += Decimal(product.GiaGiam) * item_quantity
            else:
                total_price += Decimal(product.GiaBan) * item_quantity

    request.session["total_price"] = float(total_price)

    data = {
        "menus": menus,
        "danh_mucs": danh_mucs,
        "danh_muc_san_phams": danh_muc_san_phams,
        "product_list": product_list,
        "total_price": total_price,
    }
    return render(request, "pages/cart.html", data)


def product(request, MaSP):
    menus = Menu.objects.all()
    danh_mucs = DanhMucThuongHieu.objects.all()
    danh_muc_san_phams = DanhMucSanPham.objects.all()
    product = SanPham.objects.get(MaSP=MaSP)
    product_details = ChiTietSanPham.objects.filter(MaSP=product.MaSP)
    thuonghieu = []
    for detail in product_details:
        tenthuonghieu = detail.MaThuongHieu.TenThuongHieu
        thuonghieu.append(tenthuonghieu)
    data = {
        "menus": menus,
        "danh_mucs": danh_mucs,
        "danh_muc_san_phams": danh_muc_san_phams,
        "product": product,
        "product_details": product_details,
        "thuonghieu": thuonghieu,
    }
    return render(request, "pages/product.html", data)


def add_to_cart(request, MaSP):
    user_id = request.session.get("user_id")
    if user_id:
        if request.method == "POST":
            id = MaSP
            num = request.POST.get("num")
            proDetails = get_object_or_404(SanPham, MaSP=id)
            cart_item, created = Cart.objects.get_or_create(
                NguoiDung_id=user_id, SanPham_id=id
            )
            cart_item.SoLuong += int(num)
            cart_item.save()
            cart = request.session.get("cart", {})
            if id in cart.keys():
                itemCart = {
                    "id": proDetails.MaSP,
                    "name": proDetails.TenSP,
                    "price": float(proDetails.GiaBan),
                    "price-sale": float(proDetails.GiaGiam),
                    "num": int(cart[id]["num"]) + 1,
                }
            else:
                itemCart = {
                    "id": proDetails.MaSP,
                    "name": proDetails.TenSP,
                    "price": float(proDetails.GiaBan),
                    "price-sale": float(proDetails.GiaGiam),
                    "num": num,
                }
            cart[id] = itemCart
            request.session["cart"] = cart

            return redirect("product", MaSP=id)
        else:
            return JsonResponse({"status": "error"})
    else:
        return redirect("login")


def add_to_cart_and_redirect(request, MaSP):
    user_id = request.session.get("user_id")
    if user_id:
        if request.method == "POST":
            id = MaSP
            num = request.POST.get("num")
            proDetails = get_object_or_404(SanPham, MaSP=id)
            cart_item, created = Cart.objects.get_or_create(
                NguoiDung_id=user_id, SanPham_id=id
            )
            cart_item.SoLuong += int(num)
            cart_item.save()
            cart = request.session.get("cart", {})
            if id in cart.keys():
                itemCart = {
                    "id": proDetails.MaSP,
                    "name": proDetails.TenSP,
                    "price": float(proDetails.GiaBan),
                    "price-sale": float(proDetails.GiaGiam),
                    "num": int(cart[id]["num"]) + 1,
                }
            else:
                itemCart = {
                    "id": proDetails.MaSP,
                    "name": proDetails.TenSP,
                    "price": float(proDetails.GiaBan),
                    "price-sale": float(proDetails.GiaGiam),
                    "num": num,
                }
            cart[id] = itemCart
            request.session["cart"] = cart

            return redirect("cart")
        else:
            return JsonResponse({"status": "error"})
    else:
        return redirect("login")


def remove_from_cart(request, MaSP):
    user_id = request.session.get("user_id")
    if user_id:
        if request.method == "POST":
            cart_item = Cart.objects.filter(
                NguoiDung_id=user_id, SanPham_id=MaSP
            ).first()
            if cart_item:
                cart_item.delete()
                return JsonResponse({"status": "success"})
            else:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Sản phẩm không tồn tại trong giỏ hàng.",
                    }
                )
        else:
            return JsonResponse({"status": "error", "message": "Yêu cầu không hợp lệ."})
    else:
        return redirect("login")


def dat_hang(request):
    user_id = request.session.get("user_id")
    if user_id:
        if request.method == "POST":
            form = DonHangForm(request.POST)
            if form.is_valid():
                don_hang = form.save(commit=False)
                account = get_object_or_404(Account, IDAC=user_id)
                don_hang.IDAC = account
                don_hang.TongTien = request.session.get("total_price", 0)
                don_hang.save()
                cart = request.session.get("cart", {})

                for product_id, item in cart.items():
                    product = get_object_or_404(SanPham, MaSP=product_id)
                    chi_tiet_don_hang = ChiTietDonHang(
                        MaDon=don_hang,
                        MaSP=product,
                        SL=item["num"],
                        Total=Decimal(item["num"]) * Decimal(product.GiaGiam)
                        if product.GiaGiam != 0
                        else Decimal(item["num"]) * Decimal(product.GiaBan),
                        GiaBan=product.GiaBan,
                        GiaGiam=product.GiaGiam,
                    )
                    chi_tiet_don_hang.save()

                    cart_item = Cart.objects.filter(
                        NguoiDung_id=user_id, SanPham_id=product_id
                    ).first()
                    if cart_item:
                        cart_item.delete()

                request.session["cart"] = {}
                return redirect("cart")
        else:
            form = DonHangForm()
    else:
        return redirect("login")

    return render(request, "pages/cart.html", {"form": form})


def login(request):
    form = LoginForm()
    account_name = None
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["Username"]
            password = form.cleaned_data["Pass"]
            accounts = Account.objects.filter(Username=username)
            if accounts.exists():
                for account in accounts:
                    if account.Pass == password:
                        request.session["user_id"] = account.IDAC
                        request.session["user_role"] = account.RoleID.RoleID
                        account_name = account.NameAc
                        return redirect("home")
                form.add_error("Pass", "Mật khẩu không đúng")
            else:
                form.add_error("Username", "Tài khoản không tồn tại")
    else:
        form = LoginForm()
    return render(
        request, "pages/login.html", {"form": form, "account_name": account_name}
    )


def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect("home")


def is_valid_email(email):
    # Biểu thức chính quy để kiểm tra định dạng email
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)


def signin(request):
    if request.method == "POST":
        form = SigninForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["Email"]
            username = form.cleaned_data["Username"]
            phone = form.cleaned_data["Phone"]
            if not is_valid_email(email):
                form.add_error("Email", "Email không hợp lệ.")
            elif Account.objects.filter(Email=email).exists():
                form.add_error("Email", "Email đã được sử dụng.")
            elif Account.objects.filter(Username=username).exists():
                form.add_error("Username", "Username đã được sử dụng.")
            elif Account.objects.filter(Phone=phone).exists():
                form.add_error("Phone", "Số điện thoại đã được sử dụng.")
            else:
                account = form.save(commit=False)
                role = Roles.objects.get(RoleID=2)
                account.RoleID = role
                account.save()
                return redirect("login")
    else:
        form = SigninForm()
    return render(request, "pages/signin.html", {"form": form})


def order(request):
    menus = Menu.objects.all()
    danh_mucs = DanhMucThuongHieu.objects.all()
    danh_muc_san_phams = DanhMucSanPham.objects.all()
    sdt = request.POST.get("SDT")
    dia_chi = request.POST.get("DiaChi")
    total_price = Decimal("0")
    product_list = []
    user_id = request.session.get("user_id")
    orders = DonDatHang.objects.filter(IDAC_id=user_id)
    for order in orders:
        order_details = ChiTietDonHang.objects.filter(MaDon=order.MaDon)
        for order_detail in order_details:
            product = order_detail.MaSP.TenSP
            product_list.append(product)
    data = {
        "menus": menus,
        "danh_mucs": danh_mucs,
        "danh_muc_san_phams": danh_muc_san_phams,
        "sdt": sdt,
        "dia_chi": dia_chi,
        "product_list": product_list,
        "total_price": total_price,
        "orders": orders,
        "order_details": order_details,
    }
    return render(request, "pages/order.html", data)


def brand_products(request, MaThuongHieu):
    menus = Menu.objects.all()
    danh_mucs = DanhMucThuongHieu.objects.all()
    danh_muc_san_phams = DanhMucSanPham.objects.all()
    thuong_hieu = ThuongHieuSanPham.objects.filter(pk=MaThuongHieu).first()
    if thuong_hieu:
        chiTiet_SP = ChiTietSanPham.objects.filter(MaThuongHieu=thuong_hieu)
        sp_id = chiTiet_SP.values_list("MaSP_id", flat=True)
        san_pham = SanPham.objects.filter(MaSP__in=sp_id)
    else:
        chiTiet_SP = []
        san_pham = []
    context = {
        "menus": menus,
        "danh_mucs": danh_mucs,
        "danh_muc_san_phams": danh_muc_san_phams,
        "san_pham": san_pham,
        "thuong_hieu": thuong_hieu,
        "chiTiet_SP": chiTiet_SP,
    }
    return render(request, "pages/brand_products.html", context)


def search_result(request):
    menus = Menu.objects.all()
    danh_mucs = DanhMucThuongHieu.objects.all()
    danh_muc_san_phams = DanhMucSanPham.objects.all()
    query = request.GET.get("query")
    if query is not None:
        san_pham = SanPham.objects.filter(Q(TenSP__icontains=query))
    else:
        san_pham = []
    context = {
        "menus": menus,
        "danh_mucs": danh_mucs,
        "danh_muc_san_phams": danh_muc_san_phams,
        "query": query,
        "san_pham": san_pham,
    }
    return render(request, "pages/search_result.html", context)


def cancel_order(request, MaDon):
    if request.method == "POST":
        order = get_object_or_404(DonDatHang, MaDon=MaDon)
        if order.TransactStatusID_id == 1:
            order.Deleted = 1
            order.TransactStatusID_id = 4
            order.save()
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False})
    return redirect("order")


def get_order_details(request, MaDon):
    order_details = {}
    don_hang = get_object_or_404(DonDatHang, MaDon=MaDon)
    chi_tiet_don_hang = ChiTietDonHang.objects.filter(MaDon=don_hang)
    order_details["MaDon"] = don_hang.MaDon
    order_details["ChiTietDonHang"] = []
    for chi_tiet in chi_tiet_don_hang:
        order_details["ChiTietDonHang"].append(
            {
                "MaCTDH": chi_tiet.MaCTDH,
                "MaSP": chi_tiet.MaSP.TenSP,
                "SL": chi_tiet.SL,
                "Total": chi_tiet.Total,
                "GiaBan": chi_tiet.GiaBan,
                "GiaGiam": chi_tiet.GiaGiam,
            }
        )
    return JsonResponse(order_details)
