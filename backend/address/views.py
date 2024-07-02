from address.models import User
from my_exceptions import DataNotExist
from profession.models import Profession
from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from shop.models import Shop
from user.authentication import SafeJWTAuthentication

from .constants import *
from .constants import INVALID_KEY, INVALID_VALUE
from .models import Address
from .my_logger import logger
from .serializers import AddressSerializer


class AddressViewSets(ModelViewSet):
    """
    A UserViewSets that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions for that respect address object.
    If you want changes in that default methods we can override it is possible.
    Also, this class manage the all crud requests from end address.
    """

    queryset = Address.objects.filter(is_deleted=False)
    serializer_class = AddressSerializer
    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        """
        This method overrides the default create method in ViewSet
        Added some fields like Created by this who crates this object
        :param request: post request for create address
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the address with status code
                 else return error message with status code
        """
        try:
            type = request.data[MODULE]
            if type == HOME_ADDRESS:
                request.data[MODULE] = 1
                created_by = User.objects.get(
                    is_deleted=False, id=request.data[MODULE_FIELD_ID]
                )
                request.data[CREATED_BY] = created_by.id
                request.data[UPDATED_BY] = created_by.id
            elif type == WORK_ADDRESS:
                request.data[MODULE] = 2
                created_by = Profession.objects.get(
                    is_deleted=False, id=request.data[MODULE_FIELD_ID]
                )
                request.data[CREATED_BY] = created_by.address.id
                request.data[UPDATED_BY] = created_by.address.id
            elif type == SHOP_ADDRESS:
                created_by = Shop.objects.get(
                    is_deleted=False, id=request.data[MODULE_FIELD_ID]
                )
                request.data[CREATED_BY] = created_by.address.id
                request.data[UPDATED_BY] = created_by.address.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(CREATED_SUCCESS, status.HTTP_201_CREATED)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def retrieve(self, request, *args, **kwargs):
        """
        This method overrides the default list method in viewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for list the address
        :return: if request was success returns response object of the address with status code
                 else return error message with status code
        """
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def list(self, request, *args, **kwargs):
        """
        This method overrides the default list method in viewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for list the address
        :return: if request was success returns response object of the address with status code
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
            raise DataNotExist(ADDRESS_NOT_FOUND)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def update(self, request, *args, **kwargs):
        """
        This method overrides the default create method in ViewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for create address
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the address with status code
                 else return error message with status code
        """
        try:
            updated_by = request.headers.get(USER_ID)
            instance = self.get_object()
            address_type = request.data[MODULE]
            if address_type == HOME_ADDRESS:
                request.data[MODULE] = 1
                try:
                    User.objects.get(is_deleted=False, id=request.data[MODULE_FIELD_ID])
                except Exception as e:
                    raise DataNotExist(e.__str__())
            elif address_type == WORK_ADDRESS:
                request.data[MODULE] = 2
                try:
                    Profession.objects.get(
                        is_deleted=False, id=request.data[MODULE_FIELD_ID]
                    )
                except Exception as e:
                    raise DataNotExist(e.__str__())
            elif address_type == SHOP_ADDRESS:
                request.data[MODULE] = 3
                try:
                    Shop.objects.get(is_deleted=False, id=request.data[MODULE_FIELD_ID])
                except Exception as e:
                    raise DataNotExist(e.__str__())
            try:
                instance.updated_by = User.objects.get(is_deleted=False, id=updated_by)
            except Exception as e:
                raise DataNotExist(e.__str__())
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(UPDATED_SUCCESS, status.HTTP_200_OK)
            return Response(serializer.data)
        except Exception as e:
            raise DataNotExist(e.__str__())


@api_view(
    [
        "DELETE",
    ]
)
@authentication_classes(
    [
        SafeJWTAuthentication,
    ]
)
@permission_classes(
    [
        IsAuthenticated,
    ]
)
def delete_address(request, pk):
    """
    here we perform soft delete of the object the
    state of the object is changed to in active
    :param request: delete request
    :param pk: id for delete
    :return: success message response if id present in the table
             else return error message with status code
    """
    try:
        address = Address.objects.get(pk=pk)
        if not address.is_deleted:
            address.is_deleted = True
            Address.save(address)
            logger.info(DELETED_SUCCESS)
            return Response({DETAIL: DELETED_SUCCESS})

        else:
            logger.error(ADDRESS_NOT_FOUND)
            return Response(
                {DETAIL: ADDRESS_NOT_FOUND}, status=status.HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        raise DataNotExist(e.__str__())
