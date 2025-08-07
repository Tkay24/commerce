from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import User, Listing, Category, Comment, Bid

class CustomUserAdmin(UserAdmin):
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'groups' in form.base_fields:
            field = form.base_fields['groups']
            field.queryset = Group.objects.all()  # 
            field.label = "User Groups"  
            field.help_text = "Select the groups this user should belong to."  
        return form

admin.site.register(User, CustomUserAdmin)
admin.site.register(Listing)

admin.site.register(Comment)
admin.site.register(Bid)




@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  
    search_fields = ('name',) 


