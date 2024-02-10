from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import MaterialStock
from .my_logger import logger
from .serializers import MaterialStockSerializer, MaterialStockResponseSerializer
from .constants import *
from my_exceptions import DataNotExist
from shop.models import Shop
from shop.models import ShopType
from user.authentication import SafeJWTAuthentication
from user.models import User
from user.permissions import IsShopOwner


class MaterialStockViewSets(ModelViewSet):
    """
    A UserViewSets that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions for that respect material stack object.
    If you want changes in that default methods we can override it is possible.
    Also, this class manage the all crud requests from end material stack.
    """
    queryset = MaterialStock.objects.filter(is_deleted=False)
    serializer_class = MaterialStockSerializer
    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (IsShopOwner,)

    def create(self, request, *args, **kwargs):
        """
        This method overrides the default create method in ViewSet
        Added some fields like Created by this who crates this object
        :param request: post request for create material stack
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the material stack with status code
                 else return error message with status code
        """
        try:
            shop = Shop.objects.get(is_deleted=False, id=request.data[SHOP])
            type = {'Electrical': 1, 'Plumbing': 2, 'Raw Material': 3}
            created_by = User.objects.get(is_deleted=False, id=shop.user.id)
            request.data[TYPE] = type[request.data[TYPE]]
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(created_by=created_by, updated_by=created_by)
            logger.info(CREATED_SUCCESS)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def retrieve(self, request, *args, **kwargs):
        """
        This method overrides the default update method in viewSet,
        and we can get the material stack objects here
        :param request: get request for retrieve material stack
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the material stack with status code
                 else return error message with status code
        """
        try:
            instance = self.get_object()
            serializer = MaterialStockResponseSerializer(instance)
            logger.info(RETRIEVED_SUCCESS)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def list(self, request, *args, **kwargs):
        """
        This method overrides the default list method in viewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for list the material stack
        :return: if request was success returns response object of the material stack with status code
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
            raise DataNotExist(MATERIALS_DOES_NOT_EXIST)
        except Exception as e:
            raise DataNotExist(e.__str__())
        
    def update(self, request, *args, **kwargs):
        """
        This method overrides the default create method in ViewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for create material stack
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the material stack with status code
                 else return error message with status code
        """
        try:
            updated_by = request.headers.get(USER_ID)
            instance = self.get_object()
            instance.updated_by = User.objects.get(is_deleted=False, id=updated_by)
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(UPDATED_SUCCESS)
            return Response(serializer.data)
        except Exception as e:
            raise DataNotExist(e.__str__())
        
        
@api_view(['DELETE'])
@authentication_classes([SafeJWTAuthentication, ])
@permission_classes([IsShopOwner, ])
def delete_material_stock(request, pk):
    """
    here we perform soft delete of the object the
    state of the object is changed to in active
    :param request: delete request
    :param pk: id for delete
    :return: success message response if id present in the table
             else return error message with status code
    """
    try:
        material_stock = MaterialStock.objects.get(pk=pk)
        if not material_stock.is_deleted:
            material_stock.is_deleted = True
            MaterialStock.save(material_stock)
            logger.info(DELETED_SUCCESS)
            return Response({DETAIL: DELETED_SUCCESS})
        else:
            logger.error(DATA_NOT_FOUND)
            return Response({DETAIL: DATA_NOT_FOUND}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        raise DataNotExist(e.__str__())
    

class SearchMaterial(APIView):
    """
    Api view class for search material
    """
    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (AllowAny,)

    @staticmethod
    def get(request):
        """
        search all materials by their material_stock
        :param request: get request
        :return: list of materials else return .DoesNotExist exception
        """
        try:
            if request.data:                                                                                            
                
                material_stock = {}
                if TYPE in request.data and len(request.data) == 1:
                    shop_type = request.data[TYPE]
                    shop = ShopType.objects.filter(name=shop_type)
                    if not shop:
                        raise DataNotExist(SHOP_NOT_EXIST)
                    material_stock = MaterialStock.objects.filter(is_deleted=False, type=shop[0].__dict__[ID])
    
                elif BRAND in request.data and len(request.data) == 1:
                    brand = request.data[BRAND]
                    material_stock = MaterialStock.objects.filter(is_deleted=False, brand=brand)
    
                elif BRAND in request.data and len(request.data) == 1:
                    name = request.data[NAME]
                    material_stock = MaterialStock.objects.filter(is_deleted=False, name=name)
                    
                elif BRAND and TYPE in request.data and len(request.data) == 2:
                    shop_type = request.data[TYPE]
                    brand = request.data[BRAND]
                    shop = ShopType.objects.filter(name=shop_type)
                    if not shop:
                        raise DataNotExist(SHOP_NOT_EXIST)
                    material_stock = MaterialStock.objects.filter(is_deleted=False, type=shop[0].__dict__[ID], brand=brand)
                
                elif NAME and TYPE in request.data and len(request.data) == 2:
                    shop_type = request.data[TYPE]
                    name = request.data[NAME]
                    shop = ShopType.objects.filter(name=shop_type)
                    if not shop:
                        raise DataNotExist(SHOP_NOT_EXIST)
                    material_stock = MaterialStock.objects.filter(is_deleted=False, type=shop[0].__dict__[ID], name=name)
            
                elif NAME and BRAND in request.data and len(request.data) == 2:
                    name = request.data[NAME]
                    brand = request.data[BRAND]
                    material_stock = MaterialStock.objects.filter(name=name, brand=brand, is_deleted=False)
    
                elif NAME and BRAND and TYPE in request.data and len(request.data) == 3:
                    shop_type = request.data[TYPE]
                    brand = request.data[BRAND]
                    name = request.data[NAME]
                    shop = ShopType.objects.filter(name=shop_type)
                    if not shop:
                        raise DataNotExist(SHOP_NOT_EXIST)
                    material_stock = MaterialStock.objects.filter(is_deleted=False, type=shop[0].__dict__[ID],
                                                                  brand=brand, name=name)
                    
                if not material_stock:
                    raise DataNotExist(DATA_NOT_FOUND)
    
                page = MaterialStock.paginate_queryset(material_stock)
                if page is not None:
                    serializer = MaterialStockResponseSerializer(page, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return MaterialStock.get_paginated_response(serializer.data)
    
                serializer = MaterialStockResponseSerializer(material_stock, many=True)
                logger.info(RETRIEVED_SUCCESS)
                return Response(serializer.data, status=status.HTTP_200_OK)
    
            else:
                queryset = MaterialStock.objects.filter(is_deleted=False)
                if queryset:
                    page = MaterialStock.paginate_queryset(queryset)
    
                    if page is not None:
                        serializer = MaterialStockResponseSerializer(page, many=True)
                        logger.info(RETRIEVED_SUCCESS)
                        return MaterialStock.get_paginated_response(serializer.data)
    
                    serializer = MaterialStockResponseSerializer(queryset, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(serializer.data)
    
                raise DataNotExist(MATERIAL_STOCK_NOT_EXIST)
        except Exception as e:
            raise DataNotExist(e.__str__())
