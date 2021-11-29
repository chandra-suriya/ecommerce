from django.urls import path
from ecopp import views

urlpatterns = [
    path('register/', views.RegisterUser().as_view(), name='register'),
    path('signin/', views.Signin().as_view(), name='signin'),
    path('addproduct/', views.AddProducts().as_view(), name='addproduct'),
    path('viewproduct/', views.ViewProducts().as_view(), name='viewproduct'),
    path('addcategory/', views.AddCategory().as_view(), name='addcategory'),
    path('viewcategory/<str:pk>/', views.listproductBasedCategory().as_view()),
    path('productdetail/<int:pk>/', views.ProductDetail().as_view()),
    path('addwallets/', views.AdduserWallet().as_view(), name='userwallets'),
    path('addcart/', views.AddToCart().as_view(), name='usercart'),
    path('viewcart/', views.ViewCart().as_view(), name='viewcart'),
    path('buycart/', views.BuyCart().as_view(), name='buycart'),
    path('orderhistory/', views.OrderHistory().as_view(), name='ordershistory'),
    path('wallethistory/', views.Wallethistory().as_view(), name='wallethistory'),
    path('datehistory/', views.DateOrderSalesHistory().as_view(), name='datehistory'),
    path('salereport/', views.SaleReportCategory().as_view(), name='salereport'),
]
