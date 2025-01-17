import uuid

from django.forms.models import model_to_dict
from security.models import ProductRoleAssignment
from django.http import JsonResponse
from django.shortcuts import redirect, HttpResponseRedirect
from django.contrib import messages


def get_person_data(person):
    return {"first_name": person.first_name, "username": person.user.username}


def to_dict(instance):
    result = model_to_dict(instance)
    return {
        key: (
            str(result[key])
            if isinstance(result[key], uuid.UUID)
            else result[key]
        )
        for key in result.keys()
    }


def has_product_modify_permission(user, product):
    if user.is_authenticated:
        try:
            role_assignment = ProductRoleAssignment.objects.get(
                person__user=user, product=product
            )
            return role_assignment.role in [
                ProductRoleAssignment.PRODUCT_ADMIN,
                ProductRoleAssignment.PRODUCT_MANAGER,
            ]

        except ProductRoleAssignment.DoesNotExist:
            return False
    return False


def permission_error_message():
    return "You don't have enough permission to perform this action."


def modify_permission_required(view_func):
    def _wrapped_view(self, request, *args, **kwargs):
        error_message = permission_error_message()
        if self.get_context_data().get("can_modify_product", False):
            return view_func(self, request, *args, **kwargs)
        else:
            if self.is_ajax():
                return JsonResponse({"error": error_message}, status=400)
            else:
                messages.success(self.request, error_message)
                return HttpResponseRedirect(self.get_success_url())

    return _wrapped_view


def serialize_tree(node):
    """Serializer for the tree."""
    return {
        "id": node.pk,
        "node_id": uuid.uuid4(),
        "name": node.name,
        "description": node.description,
        "video_link": node.video_link,
        "video_name": node.video_name,
        "video_duration": node.video_duration,
        "has_saved": True,
        "children": [serialize_tree(child) for child in node.get_children()],
    }


def serialize_other_type_tree(node):
    """Serializer for the tree."""
    return {
        "id": node.pk,
        "name": node.name,
        "children": [
            serialize_other_type_tree(child) for child in node.get_children
        ],
    }
