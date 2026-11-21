from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    '''Hanya user dengan is_staff=True (admin) yang boleh mengakses.'''

    def test_func(self):
        return self.request.user.is_staff  