from address.models import Address, AddressType
from my_exceptions import DataNotExist
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from user.authentication import SafeJWTAuthentication
from user.models import User
from user.permissions import IsShopOwner

from .constants import *
from .models import Shop, ShopType
from .my_logger import logger
from .serializers import ShopResponseSerializer, ShopSerializer


class ShopViewSets(ModelViewSet):
    """
    A UserViewSets that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions for that respect user object.
    If you want changes in that default methods we can override it is possible.
    Also, this class manage the all crud requests from end user.
    """

    queryset = Shop.objects.filter(is_deleted=False)
    serializer_class = ShopSerializer
    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (IsShopOwner,)

    def retrieve(self, request, *args, **kwargs):
        """
        This method overrides the default create method in ViewSet
        Added some fields like Created by this who crates this object
        :param request: post request for create user
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the user with status code
                 else return error message with status code
        """
        try:
            instance = self.get_object()
            serializer = ShopResponseSerializer(instance)
            logger.error(RETRIEVED_SUCCESS)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def create(self, request, *args, **kwargs):
        """
        This method overrides the default create method in ViewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for create user
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the user with status code
                 else return error message with status code
        """
        try:
            type = {"Electrical": 1, "Plumbing": 2, "Raw Material": 3}
            created_by = User.objects.get(is_deleted=False, id=request.data["user"])
            type_list = []
            for i in request.data["type"]:
                type_list.append(type[i])
            request.data["type"] = type_list
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=created_by, updated_by=created_by)
            logger.info(CREATED_SUCCESS, status.HTTP_201_CREATED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def list(self, request, *args, **kwargs):
        """
        This method overrides the default list method in viewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for list the shop
        :return: if request was success returns response object of the shop with status code
                 else return error message with status code
        """
        try:
            queryset = self.filter_queryset(self.get_queryset())
            if queryset:
                page = self.paginate_queryset(queryset)
                if page is not None:
                    serializer = self.get_serializer(page, many=True)
                    logger.info()
                    return self.get_paginated_response(serializer.data)

                serializer = self.get_serializer(queryset, many=True)
                logger.info(RETRIEVED_SUCCESS)
                return Response(serializer.data)
            raise DataNotExist(SHOP_NOT_EXIST)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def update(self, request, *args, **kwargs):
        """
        This method overrides the default create method in ViewSet
        Added some fields like Created by this who crates this object
        :param request: post request for create user
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the user with status code
                 else return error message with status code
        """
        try:
            updated_by = request.headers.get("User_id")
            instance = self.get_object()
            user = User.objects.get(is_deleted=False, id=updated_by)
            instance.updated_by = user
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(UPDATED_SUCCESS, status.HTTP_200_OK)
            return Response(serializer.data)
        except Exception as e:
            raise DataNotExist(e.__str__())


class DeleteShop(APIView):
    """
    Api view class for delete this object using api request from user
    """

    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (IsShopOwner,)

    @staticmethod
    def delete(request, pk):
        """
        here we perform soft delete of the object the
        state of the object is changed to in active.
        :param request: delete request
        :param pk: id for delete
        :return: success message response if id present in the table
                 else return error message with status code
        """
        try:
            shop = Shop.objects.get(pk=pk)
            if not shop.is_deleted:
                shop.is_deleted = True
                Shop.save(shop)
                logger.info(DELETED_SUCCESS)
                return Response({DETAIL: DELETED_SUCCESS})
            else:
                logger.error(SHOP_NOT_EXIST)
                return Response(
                    {DETAIL: SHOP_NOT_EXIST}, status=status.HTTP_404_NOT_FOUND
                )
        except Exception as e:
            raise DataNotExist(e.__str__())


class SearchShop(APIView):
    """
    Api view class for view shop
    """

    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (AllowAny,)

    @staticmethod
    def get(request):
        """
        view the shop using shop id
        :param request: get request
        :return: returns shop details if the shop is
        present else return .DoesNotExist exception
        """
        try:
            if request.data:
                if CITY and TYPE in request.data and len(request.data) == 2:
                    shop_type = request.data[TYPE]
                    city = request.data[CITY]
                    shop = AddressType.objects.get(address_type=SHOP_ADDRESS)
                    address = Address.objects.filter(
                        is_deleted=False, module=shop.id, city=city
                    )

                    if not address:
                        raise DataNotExist(NO_DATA)
                    result = []
                    shop_type = ShopType.objects.get(name=shop_type)
                    for i in address:
                        shop = shop_type.shops.filter(
                            id=i.__dict__[MODULE_FIELD_ID], is_deleted=False
                        )
                        if shop:
                            shop_serializer = ShopResponseSerializer(shop, many=True)
                            result.append(shop_serializer.data)
                    if not result:
                        raise DataNotExist(NO_DATA)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(result, status=status.HTTP_200_OK)

                elif NAME and CITY in request.data and len(request.data) == 2:
                    name = request.data[NAME]
                    city = request.data[CITY]
                    shop = AddressType.objects.get(address_type=SHOP_ADDRESS)
                    address = Address.objects.filter(
                        is_deleted=False, module=shop.id, city=city
                    )

                    if not address:
                        raise DataNotExist(NO_DATA)
                    result = []
                    for i in address:
                        shop = Shop.objects.filter(
                            name=name, id=i.__dict__[MODULE_FIELD_ID], is_deleted=False
                        )
                        if shop:
                            shop_serializer = ShopResponseSerializer(shop, many=True)
                            result.append(shop_serializer.data)
                    if not result:
                        raise DataNotExist(NO_DATA)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response({DATA: result}, status=status.HTTP_200_OK)

                elif NAME in request.data and len(request.data) == 2:
                    name = request.data[NAME]
                    shop = Shop.objects.filter(is_deleted=False, name=name)
                    if not shop:
                        raise DataNotExist(NO_DATA)
                    shop_serializer = ShopResponseSerializer(shop, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(shop_serializer.data, status=status.HTTP_200_OK)

                elif CITY in request.data and len(request.data) == 1:
                    city = request.data[CITY]
                    shop = AddressType.objects.get(address_type=SHOP_ADDRESS)
                    address = Address.objects.filter(
                        is_deleted=False, module=shop.id, city=city
                    )
                    if not address:
                        raise DataNotExist(NO_DATA)
                    result = []
                    for i in address:
                        result.append(Shop.objects.get(id=i.__dict__[MODULE_FIELD_ID]))
                    shop_serializer = ShopResponseSerializer(result, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(shop_serializer.data, status=status.HTTP_200_OK)
            else:
                queryset = Shop.objects.filter(is_deleted=False)
                if queryset:
                    page = Shop.paginate_queryset(queryset)

                    if page is not None:
                        serializer = ShopResponseSerializer(page, many=True)
                        logger.info(RETRIEVED_SUCCESS)
                        return Shop.get_paginated_response(serializer.data)

                    serializer = ShopResponseSerializer(queryset, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(serializer.data)

                raise DataNotExist(SHOP_NOT_EXIST)
        except Exception as e:
            raise DataNotExist(e.__str__())
