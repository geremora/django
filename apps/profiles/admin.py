from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CaspUser
from .forms import UserCreationForm


class CaspUserAdmin(UserAdmin):
    '''
    Customization of CaspUser admin
    '''
    add_form = UserCreationForm
    list_display = (
        'username', 'first_name', 'last_name', 'email',
        'is_active', 'is_staff', 'is_superuser')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ['username', 'email', 'first_name', 'last_name', 'groups__name']

    def __init__(self, *args, **kwargs):
        super(CaspUserAdmin, self).__init__(*args, **kwargs)
        self.fieldsets += (
            ('Other info', {
                'fields': ('phone',)}
             ),
        )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2',
                       'first_name', 'last_name', 'email', 'phone')}
         ),
    )

admin.site.register(CaspUser, CaspUserAdmin)
