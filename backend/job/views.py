from address.models import Address
from address.serializers import UserAddressResponseSerializer
from my_exceptions import DataAlreadyExist, DataNotExist
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from user.authentication import SafeJWTAuthentication
from user.models import Role, User
from user.permissions import IsHouseOwner

from .constants import *
from .models import Job, WorkType
from .my_logger import logger
from .serializers import JobResponseSerializer, JobSerializer


class JobViewSets(ModelViewSet):
    """
    A UserViewSets that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions for that respect job object.
    If you want changes in that default methods we can override it is possible.
    Also, this class manage the all crud requests from end job.
    """

    queryset = Job.objects.filter(is_deleted=False)
    serializer_class = JobSerializer
    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (IsHouseOwner,)

    def create(self, request, *args, **kwargs):
        """
        This method overrides the default create method in ViewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for create job
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the job with status code
                 else return error message with status code
        """
        try:
            request.data[WORK_TYPE] = WorkType.objects.get(
                name=request.data[WORK_TYPE]
            ).id
            address = Address.objects.get(is_deleted=False, id=request.data[ADDRESS])
            job = Job.objects.filter(
                work_date=request.data[WORK_DATE], requestor=request.data["requestor"]
            )

            if not job:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                created_by = User.objects.get(id=address.module_field_id)
                serializer.save(created_by=created_by, updated_by=created_by)
                logger.info(CREATED_SUCCESS, status.HTTP_201_CREATED)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                raise DataAlreadyExist(JOB_ALREADY_POSTED)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def retrieve(self, request, *args, **kwargs):
        """
        This method overrides the default update method in viewSet,
        and we can get the job objects here
        :param request: get request for retrieve job
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the job with status code
                 else return error message with status code
        """
        try:
            instance = self.get_object()
            serializer = JobResponseSerializer(instance)
            address = Address.objects.get(is_deleted=False, pk=instance.address.id)
            address_serializer = UserAddressResponseSerializer(address)
            result = serializer.data
            result.__setitem__(ADDRESS, address_serializer.data)
            logger.error(RETRIEVED_SUCCESS)
            return Response(serializer.data)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def list(self, request, *args, **kwargs):
        """
        This method overrides the default list method in viewSet
        Added some fields like Updated by this who crates this object
        :param request: put request for list the job
        :return: if request was success returns response object of the job with status code
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
            raise DataNotExist(JOB_NOT_EXIST)
        except Exception as e:
            raise DataNotExist(e.__str__())

    def update(self, request, *args, **kwargs):
        """
        This method overrides the default update method in ViewSet
        Added some fields like Updated by this who update this object
        :param request: put request for update job
        :param args: positional arguments for add extra fields
        :param kwargs: key word arguments for add extra fields
        :return: if request was success returns response object of the job with status code
                 else return error message with status code
        """
        try:
            updated_by = request.headers.get(USER_ID)
            instance = self.get_object()
            request.data[WORK_TYPE] = WorkType.objects.get(
                name=request.data[WORK_TYPE]
            ).id
            instance.updated_by = User.objects.get(is_deleted=False, id=updated_by)
            serializer = self.get_serializer(instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            logger.info(UPDATED_SUCCESS, status.HTTP_200_OK)
            return Response(serializer.data)
        except Exception as e:
            raise DataNotExist(e.__str__())


class ApplyOffer(APIView):
    @staticmethod
    def post(request):
        """
        This is the method to save the workers for the job applied
        :param request: post request with job id and user id
        :return: return success message when job applied successfully.
        """
        try:
            if job_request[request.data["job_id"]]:
                job_request[request.data["job_id"]] = [request.data["user_id"]]
            else:
                job_request[request.data["job_id"]].append(request.data["user_id"])

            return Response(
                {
                    DETAIL: "Successfully Applied",
                    "status": 200,
                    "timestamp": datetime.datetime.now(),
                }
            )
        except Exception as e:
            return Response(
                {
                    DETAIL: e.__str__(),
                    "status": 400,
                    "timestamp": datetime.datetime.now(),
                }
            )


class ViewRequest(APIView):
    @staticmethod
    def get(request):
        """
        This is used to view the list of workers who applied job
        :param request: get request for view applied workers
        :return: if request was success returns response object of the job with status code
                 else return error message with status code
        """
        try:
            if job_request[request.data["job_id"]]:
                return Response({DETAIL: job_request[request.data["job_id"]]})
            else:
                return Response(
                    {
                        DETAIL: "No one applied",
                        "status": 200,
                        "timestamp": datetime.datetime.now(),
                    }
                )
        except Exception as e:
            return Response(
                {
                    DETAIL: e.__str__(),
                    "status": 400,
                    "timestamp": datetime.datetime.now(),
                }
            )


class AcceptOffer(APIView):
    @staticmethod
    def put(request, **kwargs):
        """
        This is the method to accept the request
        :param request: put request for accept job request
        :return: if request was success returns response object of the job with status code
                 else return error message with status code
        """
        try:
            updated_by = request.headers.get(USER_ID)
            instance = Job.objects.get(is_deleted=False, id=kwargs["pk"])
            instance.acceptor.append(request.data[ID])
            instance.no_of_workers = instance.number_of_workers - 1
            instance.updated_by = User.objects.get(is_deleted=False, id=updated_by)
            Job.save(instance)
            logger.info(UPDATED_SUCCESS, status.HTTP_200_OK)
            return Response({DETAIL: instance.number_of_workers})
        except Exception as e:
            raise DataNotExist(e.__str__())


class RejectOffer(APIView):
    @staticmethod
    def put(request, **kwargs):
        """
        This is the method to reject the request
        :param request: put request for reject job request
        :return: if request was success returns response object of the job with status code
                 else return error message with status code
        """
        try:
            job_request.get(request.data["job_id"]).pop(request.data[user_id])
            return Response(
                {DETAIL: "Rejected successfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            raise DataNotExist(e.__str__())


class DeleteJob(APIView):
    """
    Api view class for delete this object using api request from job
    """

    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (IsHouseOwner,)

    @staticmethod
    def delete(request, pk):
        """
        here we perform soft delete of the object the
        state of the object is changed to in active
        :param request: delete request
        :param pk: id for delete
        :return: success message response if id present in the table
                 else return error message with status code
        """
        try:
            job = Job.objects.get(pk=pk)

            if not job.is_deleted:
                job.is_deleted = True
                Job.save(job)
                logger.info(DELETED_SUCCESS)
                return Response({DETAIL: DELETED_SUCCESS})
            else:
                logger.error(JOB_NOT_EXIST)
                return Response(
                    {DETAIL: JOB_NOT_EXIST}, status=status.HTTP_400_BAD_REQUEST
                )
        except Exception as e:
            raise DataNotExist(e.__str__())


class SearchOfferedJobs(APIView):
    """
    Api view class for get jobs by working days
    """

    authentication_classes = (SafeJWTAuthentication,)
    permission_classes = (AllowAny,)

    @staticmethod
    def get(request):
        """
        we retrieve all jobs matches for the requested fields
        :param request: get request with fields
        :return: list of jobs
        """
        try:
            if request.data:
                jobs = {}
                if WORK_TYPE in request.data and len(request.data) == 1:
                    work_type = request.data[WORK_TYPE]
                    try:
                        work = WorkType.objects.get(name=work_type)
                    except Exception as e:
                        raise DataNotExist(e.__str__())
                    jobs = Job.objects.filter(is_deleted=False, work_type=work.id)

                elif DAYS in request.data and len(request.data) == 1:
                    days = request.data[DAYS]
                    jobs = Job.objects.filter(is_deleted=False, working_days__lte=days)

                elif PAY in request.data and len(request.data) == 1:
                    pay = request.data[PAY]
                    jobs = Job.objects.filter(is_deleted=False, work_pay__gte=pay)

                elif WORK_DATE in request.data and len(request.data) == 1:
                    date = request.data[WORK_DATE]
                    jobs = Job.objects.filter(is_deleted=False, work_date=date)

                elif WORK_DATE and PAY in request.data and len(request.data) == 2:
                    days = request.data[DAYS]
                    pay = request.data[PAY]
                    jobs = Job.objects.filter(
                        is_deleted=False, working_days=days, work_pay=pay
                    )

                elif WORK_TYPE and WORK_DATE in request.data and len(request.data) == 2:
                    date = request.data[WORK_DATE]
                    pay = request.data[PAY]
                    jobs = Job.objects.filter(
                        is_deleted=False, work_date=date, work_pay=pay
                    )

                elif WORK_DATE and DAYS in request.data and len(request.data) == 2:
                    date = request.data[WORK_DATE]
                    days = request.data[DAYS]
                    jobs = Job.objects.filter(
                        is_deleted=False, work_date=date, working_days=days
                    )

                elif (
                    DAYS
                    and WORK_DATE
                    and PAY in request.data
                    and len(request.data) == 3
                ):
                    date = request.data[WORK_DATE]
                    pay = request.data[PAY]
                    days = request.data[DAYS]
                    jobs = Job.objects.filter(
                        is_deleted=False,
                        work_date=date,
                        working_days=days,
                        work_pay=pay,
                    )

                if not jobs:
                    raise DataNotExist(DATA_NOT_FOUND)

                page = Job.paginate_queryset(jobs)
                if page is not None:
                    serializer = JobSerializer(page, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Job.get_paginated_response(serializer.data)

                serializer = JobSerializer(jobs, many=True)
                logger.info(RETRIEVED_SUCCESS)
                return Response(serializer.data, status=status.HTTP_200_OK)

            else:
                queryset = Job.objects.filter(is_deleted=False)
                if queryset:
                    page = self.paginate_queryset(queryset)

                    if page is not None:
                        serializer = Job.get_serializer(page, many=True)
                        logger.info()
                        return Job.get_paginated_response(serializer.data)

                    serializer = Job.get_serializer(queryset, many=True)
                    logger.info(RETRIEVED_SUCCESS)
                    return Response(serializer.data)

                raise DataNotExist(JOB_NOT_EXIST)
        except Exception as e:
            raise DataNotExist(e.__str__())
