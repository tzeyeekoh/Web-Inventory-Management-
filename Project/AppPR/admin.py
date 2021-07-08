from django.contrib import admin
from .models import Approval, Inventory, Members, Requests

# Register your models here.
admin.site.register(Approval)
admin.site.register(Inventory)
admin.site.register(Members)
admin.site.register(Requests)