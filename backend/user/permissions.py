from rest_framework import permissions


class IsCreationOrIsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "create" or "retrieve" or "list":
            return True
        else:
            return False


class IsHouseOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        elif "House Owner" in [x.name for x in request.user.role.all()]:
            return True
        else:
            return False


class IsWorker(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        elif "Worker" in [x.name for x in request.user.role.all()]:
            return True
        else:
            return False


class IsShopOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        elif "ShopOwner" in [x.name for x in request.user.role.all()]:
            return True
        else:
            return False
