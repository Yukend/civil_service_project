from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .constants import *
from .models import Profession
from .my_logger import logger
from .serializers import ProfessionResponseSerializer, ProfessionSerializer
from address.models import AddressType, Address
from address.serializers import WorkingAddressResponseSerializer
from job.models import WorkType
from my_exceptions import DataNotExist
from user.authentication import SafeJWTAuthentication
from user.permissions import IsWorker


class ProfessionViewSets(ModelViewSet):
    """
    A ProfessionViewSets that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions for that respect profession object.
    If you want changes in that default methods we can override it is possible.
    Also, this class manage the all crud requests from end profession.
    """
    queryset = Profession.objects.filter(is_deleted=False)
    serializer_class = ProfessionSerializer
    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (IsWorker,)

    def create(self, request, *args, **kwargs):
        """
        This method overrides the default create method in ViewSet
        Added some fields like Created by this who crates this object
        :param request: post request for create profession
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the profession with status code
                 else return error message with status code
        """
        try:
            created_by = User.objects.get(is_deleted=False, id=request.data[USER])
            request.data[PROFESSION] = WorkType.objects.get(name=request.data[PROFESSION]).id
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
        and we can get the profession objects here
        :param request: get request for retrieve profession
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the profession with status code
                 else return error message with status code
        """
        try:
            instance = self.get_object()
            serializer = ProfessionResponseSerializer(instance)
            logger.info(RETRIEVED_SUCCESS)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def list(self, request, *args, **kwargs):
        """
        This method overrides the default list method in viewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for list the profession
        :return: if request was success returns response object of the profession with status code
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
            raise DataNotExist(PROFESSION_NOT_EXIST)
        except Exception as e:
            raise DataNotExist(e.__str__())
        
    def update(self, request, *args, **kwargs):
        """
        This method overrides the default create method in ViewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for create profession
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the profession with status code
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            raise DataNotExist(e.__str__())


@api_view(['DELETE'])
@authentication_classes([SafeJWTAuthentication, ])
@permission_classes([IsWorker, ])
def delete_profession(request, pk):
    """
    here we perform soft delete of the object the
    state of the object is changed to in active
    :param request: delete request
    :param pk: id for delete
    :return: success message response if id present in the table
             else return error message with status code
    """
    try:
        profession = Profession.objects.get(pk=pk)
        if not profession.is_deleted:
            profession.is_deleted = True
            Profession.save(profession)
            logger.info(DELETED_SUCCESS)
            return Response({DETAIL: DELETED_SUCCESS})
        else:
            logger.error(PROFESSION_NOT_EXIST)
            return Response({DETAIL: PROFESSION_NOT_EXIST}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        raise DataNotExist(e.__str__())


class SearchProfession(APIView):
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
                
                if len(request.data) == 1 and PROFESSION in request.data:
                    profession = request.data[PROFESSION]
                    work = WorkType.objects.get(name=profession)
                    professions = work.work_type.filter(is_deleted=False, is_available=True)
                    if not professions:
                        raise DataNotExist(DATA_NOT_FOUND)
                    profession_serializer = ProfessionResponseSerializer(professions, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(profession_serializer.data, status=status.HTTP_200_OK)
                    
                elif SALARY in request.data and len(request.data) == 1:
                    salary = request.data[SALARY]
                    professions = Profession.objects.filter(is_deleted=False, expected_salary=salary, is_available=True)
                    if not professions:
                        raise DataNotExist(DATA_NOT_FOUND)
                    profession_serializer = ProfessionResponseSerializer(professions, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(profession_serializer.data, status=status.HTTP_200_OK)
                    
                elif PROFESSION and SALARY in request.data and len(request.data) == 2:
                    salary = request.data[SALARY]
                    profession = request.data[PROFESSION]
                    work = WorkType.objects.get(name=profession)
                    professions = work.work_type.filter(is_deleted=False, expected_salary__gte=salary, is_available=True)
                    if not professions:
                        raise DataNotExist(DATA_NOT_FOUND)
                    profession_serializer = ProfessionResponseSerializer(profession, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(profession_serializer.data, status=status.HTTP_200_OK)
                    
                elif CITY in request.data and len(request.data) == 1:
                    city = request.data[CITY]
                    shop = AddressType.objects.get(address_type=WORK_ADDRESS)
                    address = Address.objects.filter(is_deleted=False, module=shop.id, city=city)
                    if not address:
                        raise DataNotExist(DATA_NOT_FOUND)
                    result = []
                    for i in address:
                        result.append(Profession.objects.get(id=i.__dict__[MODULE_FIELD_ID], is_available=True))
                    profession_serializer = ProfessionResponseSerializer(result, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(profession_serializer.data, status=status.HTTP_200_OK)
                        
                elif CITY and TYPE in request.data and len(request.data) == 2:
                    city = request.data[CITY]
                    type = request.data[TYPE]
                    shop = AddressType.objects.get(address_type=WORK_ADDRESS)
                    work = WorkType.objects.get(name=type)
                    professions = work.work_type.filter(is_deleted=False, is_available=True)
                    result_list = []
                    for i in professions:
                        address = Address.objects.get(is_deleted=False, module_field_id=i.__dict__[ID],
                                                      city=city, module=shop.id)
                        if address:
                            address_serializer = WorkingAddressResponseSerializer(address)
                            profession_serializer = ProfessionResponseSerializer(i)
                            result = profession_serializer.data
                            result.__setitem__(ADDRESS, address_serializer.data)
                            result_list.append(result)
                    logger.info(RETRIEVED_SUCCESS)
                    if not result_list:
                        raise DataNotExist(DATA_NOT_FOUND)
                    return Response(result_list, status=status.HTTP_200_OK)
            else:
                queryset = Profession.objects.filter(is_deleted=False)
                if queryset:
                    page = Profession.paginate_queryset(queryset)
    
                    if page is not None:
                        serializer = ProfessionResponseSerializer(page, many=True)
                        logger.info(RETRIEVED_SUCCESS)
                        return Profession.get_paginated_response(serializer.data)
    
                    serializer = ProfessionResponseSerializer(queryset, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(serializer.data)
    
                raise DataNotExist(PROFESSION_NOT_EXIST)
        except Exception as e:
            raise DataNotExist(e.__str__())
