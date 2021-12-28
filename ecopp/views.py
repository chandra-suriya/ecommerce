# from django.shortcuts import render
from ecopp import models, serialisers, controllers
from rest_framework import views, permissions
from rest_framework import serializers, response, parsers
from django.core import validators
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.db.models import Sum, Q
from rest_framework import pagination, status
from rest_framework.authtoken.models import Token
# Create your views here.


class RegisterUser(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get("email")
        password1 = data.get("password1")
        password2 = data.get("password2")
        if(not username or not email or
           not password1 or not password2):
            return response.Response({
                "result": False,
                "msg": "username or password is missing"
            }, status=status.HTTP_400_BAD_REQUEST)
        if (validators.validate_email(email)):
            return response.Response({
                "result": False,
                "msg": "No email id is there"
            }, status=status.HTTP_400_BAD_REQUEST)
        if(User.objects.filter(Q(username=username) | Q(email=email))
           .exists()):
            return response.Response({
                "result": False,
                "msg": "user name or email already exsists"
            }, status=status.HTTP_400_BAD_REQUEST)
        if(password1 != password2):
            return response.Response({
                "result": False,
                "msg": "password is not equal "
            }, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(username=username,
                                        email=email,
                                        password=password1)
        token = Token.objects.get_or_create(user=user)[0]
        models.Wallet.objects.create(walletuser=user)
        return response.Response({
                "msg": "user created",
                "token": token.key,
                "result": True,
                "username": user.username,
               }
            )

class RegisterAdmin(views.APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get("email")
        password1 = data.get("password1")
        password2 = data.get("password2")
        if(not username or not email or
           not password1 or not password2):
            return response.Response({
                "result": False,
                "msg": "username or password is missing"
            }, status=status.HTTP_400_BAD_REQUEST)
        if (validators.validate_email(email)):
            return response.Response({
                "result": False,
                "msg": "No email id is there"
            }, status=status.HTTP_400_BAD_REQUEST)
        if(User.objects.filter(Q(username=username) | Q(email=email))
           .exists()):
            return response.Response({
                "result": False,
                "msg": "user name or email already exsists"
            }, status=status.HTTP_400_BAD_REQUEST)
        if(password1 != password2):
            return response.Response({
                "result": False,
                "msg": "password is not equal "
            }, status=status.HTTP_400_BAD_REQUEST)
        user = User(username=username, email=email, password=password1)
        user.is_superuser=True
        token = Token.objects.get_or_create(user=user)[0]
        models.Wallet.objects.create(walletuser=user)
        return response.Response({
                "msg": "user created",
                "token": token.key,
                "result": True,
                "username": user.username,
               }
            )


class Signin(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise serializers.ValidationError({
                "result": False,
                "msg": "username or password missing or empty"},
             code="validation_error",
            )
        if not(User.objects.filter(username=username).exists()):
            raise serializers.ValidationError({
                "result": False,
                "msg": "Account not exist for this username"},
                code="validation_error",
            )
        else:
            userobj = User.objects.get(username=username)
            is_pass = userobj.check_password(password)
            if not is_pass:
                raise serializers.ValidationError({
                    "result": False,
                    "msg": "Invalid password"},
                    code="validation_error",
                )
            token = Token.objects.get_or_create(user=userobj)[0]
            user = authenticate(username=username, password=password)
            login(request, user)
            wallet = models.Wallet.objects.get(walletuser=userobj)
        return response.Response({
                "token": token.key,
                "msg": "Sucess",
                "username": userobj.username,
                "wallet": wallet.walletcount,
                "result": True,
               }
            )


class AddProducts(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        data = request.data
        name = data.get('name')
        category_id = data.get('category')
        price = data.get('price')
        brandname = data.get('brandname')
        description = data.get('description')
        quantity = data.get('quantity')

        if(not name or not category_id or not price or not brandname):
            return response.Response({
                "result": False,
                "msg": "something is missing"
            }, status=status.HTTP_400_BAD_REQUEST)
        product = controllers.ProductControllers()
        pro_id = product.addproducts(name=name, category_id=category_id,
                                     price=price, brandname=brandname,
                                     description=description,
                                     quantity=quantity)
        return response.Response({
                "id": pro_id,
                "msg": "created product",
                "result": True,
               }
            )


class ViewProducts(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        product = controllers.ProductControllers()
        prolist = product.addproducts()
        paginator = pagination.PageNumberPagination()
        result_page = paginator.paginate_queryset(prolist, request)
        prod = serialisers.ProductSerializer(result_page, many=True)
        return response.Response(prod.data)


class AddCategory(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        data = request.data
        name = data.get('name')

        if(not name):
            return response.Response(
                {"result": False, "msg": "name is not included"},
                code="validation_error",
            )
        cat = models.Category.objects.create(name=name)
        return response.Response({
                "id": cat.id,
                "name": cat.name,
                "msg": "created categories",
                "result": True,
               }

        )


class listproductBasedCategory(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        product = controllers.ProductControllers()
        data = product.list_pro_category(pk=pk)
        paginator = pagination.PageNumberPagination()
        result_page = paginator.paginate_queryset(data, request)
        prod = serialisers.ProductSerializer(result_page, many=True)
        return response.Response(prod.data)


class ProductDetail(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def get(self, request, pk):
        if(models.Product.objects.filter(id=pk).exists()):
            objects = models.Product.objects.get(id=pk)
        else:
            raise serializers.ValidationError(
                {"result": False, "msg": "invalid id"},
                code="validation_error",
            )
        return response.Response({
                "id": objects.id,
                "name": objects.name,
                "price": objects.price,
                "brandname": objects.brandname,
                "description": objects.description,
                "result": True,
               }

        )


class AdduserWallet(views.APIView):

    def post(self, request):
        data = request.data
        user = request.user
        amount = data.get('amount')
        u = models.Wallet.objects.get(walletuser=user)
        u.walletcount = u.walletcount+int(amount)
        u.save()
        models.WalletHistory.objects.create(wallets=u, amount=amount)
        return response.Response({
                "id":  user.id,
                "name": user.username,
                "Wallets": u.walletcount,
                "result": True,
               }

        )


class AddToCart(views.APIView):

    def post(self, request):
        user = request.user
        data = request.data
        product = data.get('product')
        quantites = data.get('quantites')
        carts = controllers.CartControllers()
        cart_details = carts.add_cart(user=user, product=product,
                                      quantites=quantites)
        return response.Response({
                "data": cart_details,
                "msg": "Cart created successfully"
               }

        )


class ViewCart(views.APIView):

    def get(self, request):
        user = request.user
        cartval = models.Cart.objects.filter(owner=user)
        if not (cartval):
            raise serializers.ValidationError(
                {"result": False, "msg": "cart is empty"},
                code="validation_error",
            )
        total = 0
        for products in cartval:
            amount = products.product.price * products.quantity
            total = total + amount
        paginator = pagination.PageNumberPagination()
        result_page = paginator.paginate_queryset(cartval, request)
        carts = serialisers.CartSerializer(result_page, many=True)
        return response.Response({
                "values": carts.data,
                "total amount": total
            }
        )


class BuyCart(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)

    def get(self, request):
        user = request.user
        cartval = models.Cart.objects.filter(owner=user)
        if not (cartval):
            raise serializers.ValidationError(
                {"result": False, "msg": "cart is empty"},
                code="validation_error",
            )
        else:
            for obj in cartval:
                models.Order.objects.create(owner=user,
                                            product=obj.product,
                                            price=obj.product.price,
                                            quantity=obj.quantity,
                                            brand=obj.product.brandname
                                            )
            cartval.delete()
        return response.Response({
                "msg": "sucessfully purchased",
                "Sucess": True
            }
        )


class OrderHistory(views.APIView):

    def get(self, request):
        user = request.user
        cartval = models.Order.objects.filter(owner=user)
        if not (cartval):
            raise serializers.ValidationError(
                {"result": False, "msg": "No orders were purchased"},
                code="validation_error",
            )
        paginator = pagination.PageNumberPagination()
        result_page = paginator.paginate_queryset(cartval, request)
        carts = serialisers.OrderSerializer(result_page, many=True)
        return response.Response({
                "values": carts.data,
            }
        )


class Wallethistory(views.APIView):

    def post(self, request):
        user = request.user
        data = request.data
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        wallet_obj = models.Wallet.objects.get(walletuser=user)
        if not wallet_obj:
            raise serializers.ValidationError(
                {"result": False, "msg": "No wallets are there"},
                code="validation_error",
            )
        else:
            history = models.WalletHistory.objects.filter(
                wallets=wallet_obj,
                transactiondate__range=[from_date, to_date])
            if not history:
                raise serializers.ValidationError(
                    {"result": False, "msg": "No hisrtory are found with in"},
                    code="validation_error",
                )
            paginator = pagination.PageNumberPagination()
            result_page = paginator.paginate_queryset(history, request)
            wallet_hist = serialisers.WalletSerializer(result_page, many=True)
            return response.Response(wallet_hist.data)


class DateOrderSalesHistory(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        user = request.user
        data = request.data
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        if not(user.is_superuser):
            raise serializers.ValidationError(
                    {"result": False, "msg": "invalid login"},
                    code="validation_error",
                )
        order_obj = models.Order.objects.filter(
            purchasedate__range=[from_date, to_date])
        if not order_obj:
            raise serializers.ValidationError(
                    {"result": False, "msg": "no products buyed in this name"},
                    code="validation_error",
                )
        ind_obj = order_obj.values('purchasedate').order_by(
            'purchasedate').annotate(totalprice=Sum(
                'price'), count=Sum('quantity'))
        print(ind_obj)
        return response.Response({
                "values": ind_obj,
            }
        )


class SaleReportCategory(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        user = request.user
        data = request.data
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        if not(user.is_superuser):
            raise serializers.ValidationError(
                    {"result": False, "msg": "invalid login"},
                    code="validation_error",
                )
        order_obj = models.Order.objects.filter(
            purchasedate__range=[from_date, to_date])
        if not order_obj:
            raise serializers.ValidationError(
                    {"result": False, "msg": "no brand buyed in this date"},
                    code="validation_error",
                )

        brand_obj = order_obj.values('purchasedate', 'brand').order_by(
            'purchasedate').annotate(
                totalprice=Sum('price'), count=Sum('quantity'))
        return response.Response(brand_obj)
