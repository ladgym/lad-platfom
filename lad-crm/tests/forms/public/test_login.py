from lad_crm.forms.public.login import LoginForm


# FIXME need to identify the root of problem
# RuntimeError: Working outside of request context.
class TestLoginForm:
    def test_login_form_validate_success(self, test_app):
        form = LoginForm()
        assert form
