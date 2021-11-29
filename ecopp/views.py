# from django.shortcuts import render
from ecopp import models, serialisers
from rest_framework import views, permissions
from rest_framework import serializers, response, parsers
from django.core import validators
from django.contrib.auth.models import User
from django.db.models import Sum
from rest_framework import pagination
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
            raise serializers.ValidationError(
                {"result": False,
                 "msg": "please enter all required fields"},
                code="validation_error",
            )
        if (validators.validate_email(email)):
            raise serializers.ValidationError(
                {"result": False, "msg": "Enter a Valid email address."},
                code="validation_error",
            )
        if(User.objects.filter(username=username).exists() or
           User.objects.filter(email=email).exists()):
            raise serializers.ValidationError(
                {"result": False,
                 "msg": "Email addresses or username must be unique."},
                code="validation_error",
            )
        if(password1 != password2):
            raise serializers.ValidationError(
                {"result": False, "msg": "renter password is wrong."},
                code="validation_error",
            )

        user = User(username=username, email=email, is_active=False)
        user.set_password(password1)
        user.is_staff = True
        user.save()
        token = Token.objects.get_or_create(user=user)[0]
        models.Wallet.objects.create(walletuser=user)
        return response.Response({
                "msg": "user created",
                "token": token.key,
                "result": True,
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
            else:
                if(userobj.is_active):
                    raise serializers.ValidationError({
                        "result": False,
                        "msg": "User already signin"},
                        code="validation_error",
                    )
                token = Token.objects.get_or_create(user=userobj)[0]
                userobj.is_active = True
                userobj.save()
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
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        name = data.get('name')
        category = data.get('category')
        price = data.get('price')
        brandname = data.get('brandname')
        description = data.get('description')

        if(not name or not category or not price or not brandname):
            raise serializers.ValidationError(
                {"result": False,
                 "msg": "some value must be provided is missing or empty"},
                code="validation_error",
            )
        if(models.Category.objects.filter(name=category).exists()):
            categ = models.Category.objects.get(name=category)
            pro = models.Product.objects.create(name=name, category=categ,
                                                price=price,
                                                brandname=brandname,
                                                description=description)
        else:
            raise serializers.ValidationError(
                {"result": False, "msg": "category is not included"},
                code="validation_error",
            )
        return response.Response({
                "id": pro.id,
                "msg": "created product",
                "result": True,
               }
            )


class ViewProducts(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        prolist = models.Product.objects.all()
        if not (prolist):
            raise serializers.ValidationError(
                {"result": False, "msg": "products are empty"},
                code="validation_error",
            )
        paginator = pagination.PageNumberPagination()
        result_page = paginator.paginate_queryset(prolist, request)
        prod = serialisers.ProductSerializer(result_page, many=True)
        return response.Response(prod.data)


class AddCategory(views.APIView):
    parser_classes = (parsers.MultiPartParser, parsers.FormParser)
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        data = request.data
        name = data.get('name')

        if(not name):
            raise serializers.ValidationError(
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
        cate = models.Category.objects.get(name=pk)
        data = models.Product.objects.filter(category=cate)
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
        pro = models.Product.objects.get(name=product)
        if(int(quantites) > pro.quantity):
            raise serializers.ValidationError(
                {"result": False, "msg": "stocks quantity is more"},
                code="validation_error",
            )
        if(models.Cart.objects.filter(owner=user, product=pro).exists()):
            cart = models.Cart.objects.get(owner=user, product=pro)
            cart.quantity = cart.quantity + int(quantites)
            cart.save()
        else:
            cart = models.Cart.objects.create(owner=user, product=pro,
                                              quantity=quantites)
        pro.quantity = pro.quantity - int(quantites)
        pro.save()
        return response.Response({
                "id":  pro.id,
                "name": user.username,
                "product": pro.name,
                "quantity": cart.quantity,
                "result": True,
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
            history = models.WalletHistory.objects.filter(wallets=wallet_obj,
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
        order_obj = models.Order.objects.filter(purchasedate__range=[from_date, to_date])
        if not order_obj:
            raise serializers.ValidationError(
                    {"result": False, "msg": "no products buyed in this name"},
                    code="validation_error",
                )
        ind_obj = order_obj.values('purchasedate').order_by('purchasedate').annotate(totalprice=Sum('price'), count=Sum('quantity'))
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
        order_obj = models.Order.objects.filter(purchasedate__range=[from_date, to_date])
        if not order_obj:
            raise serializers.ValidationError(
                    {"result": False, "msg": "no brand buyed in this date"},
                    code="validation_error",
                )

        brand_obj = order_obj.values('purchasedate', 'brand').order_by('purchasedate').annotate(totalprice=Sum('price'), count=Sum('quantity'))
        return response.Response(brand_obj)
