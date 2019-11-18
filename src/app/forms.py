# coding: utf-8
from app.lib.requests_wrapper import get_requests
from app.models import Service
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm as NativeUserCreationForm  # NOQA
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class AuthenticationFormNoPlaceholder(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = ""
        self.fields["password"].widget.attrs["placeholder"] = ""


class UserCreationForm(NativeUserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["placeholder"] = ""
        self.fields["password1"].widget.attrs["placeholder"] = ""
        self.fields["password2"].widget.attrs["placeholder"] = ""


class ServiceAdditionForm(forms.Form):
    SCHEME_CHOICES = (
        ("http", "http"),
        ("https", "https"),
    )

    service_name = forms.CharField(label=_("Service Name"), max_length=256, required=True, help_text=_("Required."))  # NOQA
    server_scheme = forms.ChoiceField(choices=SCHEME_CHOICES, required=True, initial="http")  # NOQA
    server_host = forms.CharField(label=_("Service server host"), max_length=256, required=True, help_text=_("Required. e.g. localhost:8000"))  # NOQA
    server_token = forms.CharField(label=_("Service server token"), max_length=256, required=False, help_text=_("Not Required. None is OK."))  # NOQA

    def clean(self):
        super().clean()
        d_response = get_requests(self.cleaned_data["server_scheme"],
                                  self.cleaned_data["server_host"],
                                  "/service-info",
                                  self.cleaned_data["server_token"])
        if d_response is None:
            raise forms.ValidationError("Please enter the correct URL.")
        if Service.objects.filter(name=self.cleaned_data["service_name"]).exists():  # NOQA
            raise forms.ValidationError("A form with that name already exists.")  # NOQA
        self.cleaned_data["d_response"] = d_response


class WorkflowPrepareForm(forms.Form):
    execution_engine = forms.ChoiceField(required=True)

    def __init__(self, workflow_name, input_params, excutable_engines, *args, **kwargs):  # NOQA
        """
        input_params -> list
            {
                label: str
                type: str (boolean, int, float, string)
                    - int, long, double -> int
                    - string, File, Directoru -> string
                default: str, boolean, int, float, None
                doc: str or None
            }
        """
        super().__init__(*args, **kwargs)
        self.fields["run_name"] = forms.CharField(max_length=256,
                                                  required=True,
                                                  initial="{} {}".format(workflow_name, timezone.now().strftime("%Y-%m-%d %H:%M:%S")))  # NOQA
        self.fields["execution_engine"].choices = [[engine.token, engine.name] for engine in excutable_engines]  # NOQA
        for input_param in input_params:
            if input_param["type"] == "boolean":
                self.fields[input_param["label"]] = forms.BooleanField()
            elif input_param["type"] in ["int", "long", "double"]:
                self.fields[input_param["label"]] = forms.IntegerField()
            elif input_param["type"] == "float":
                self.fields[input_param["label"]] = forms.FloatField()
            elif input_param["type"] in ["string", "File", "Directory"]:
                self.fields[input_param["label"]] = forms.CharField()
            self.fields[input_param["label"]].required = True
            if input_param["default"] is not None:
                self.fields[input_param["label"]].initial = input_param["default"]  # NOQA
            if input_param["doc"] is not None:
                self.fields[input_param["label"]].help_text = input_param["doc"]  # NOQA
        for field in self.fields.keys():
            self.fields[field].widget.attrs["placeholder"] = ""


class WorkflowParametersUploadForm(forms.Form):
    workflow_parameters = forms.FileField(
        label=_("Workflow Parameters"), required=True)
