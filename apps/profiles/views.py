from django.views.generic import DetailView, UpdateView
from django.core.urlresolvers import reverse_lazy

from braces.views import LoginRequiredMixin

from .models import CaspUser
from .forms import CaspUserUpdateForm


class ProfileDetailView(LoginRequiredMixin, DetailView):
    '''
    Displays the user profile information
    '''
    model = CaspUser

    def get_object(self, *args, **kwargs):
        # Get the currently logged in user
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    '''
    View to update basic user information
    '''
    model = CaspUser
    form_class = CaspUserUpdateForm

    def get_object(self, *args, **kwargs):
        # Get the currently logged in user
        return self.request.user

    def get_success_url(self):
        # Return the profile_detail url
        return reverse_lazy('profile_detail')
