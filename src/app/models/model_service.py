# coding: utf-8
from secrets import token_hex

from app.lib.requests_wrapper import get_requests
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


def _get_token():
    # Cannot use lambda in Django model default
    return token_hex(16)


class CommonInfo(models.Model):
    created_at = models.DateTimeField(_("Created date"), default=timezone.now)
    updated_at = models.DateTimeField(_("Updated date"), auto_now=True)
    token = models.CharField(_("Token"), max_length=256, unique=True, default=_get_token, primary_key=True)  # NOQA
    deleted = models.BooleanField(_("Flag_deleted"), default=False)

    class Meta:
        abstract = True


class Service(CommonInfo):
    name = models.CharField(_("Service name"), max_length=256, unique=True)
    server_scheme = models.CharField(_("Server scheme"), max_length=16)
    server_host = models.CharField(_("Server host"), max_length=256)
    server_token = models.CharField(_("Server token"), max_length=256, null=True, blank=True)  # NOQA
    auth_instructions_url = models.CharField(_("Auth instructions url"), max_length=256)  # NOQA
    contact_info_url = models.CharField(_("Contact info url"), max_length=256)

    class Meta:
        db_table = "service"
        verbose_name = "service"
        verbose_name_plural = "services"

    def __str__(self):
        return "Service: {}".format(self.name)

    def create_from_form(self, cleaned_data):
        self.name = cleaned_data["service_name"]
        self.server_scheme = cleaned_data["server_scheme"]
        self.server_host = cleaned_data["server_host"]
        self.server_token = cleaned_data["server_token"]
        self.auth_instructions_url = cleaned_data["d_response"]["auth_instructions_url"]  # NOQA
        self.contact_info_url = cleaned_data["d_response"]["contact_info_url"]
        self.save()
        for res_workflow_engine in cleaned_data["d_response"]["workflow_engines"]:  # NOQA
            ins_workflow_engine = WorkflowEngine.objects.create(
                service=self,
                name=res_workflow_engine["engine_name"],
                version=res_workflow_engine["engine_version"],
            )
            for res_workflow_type in res_workflow_engine["workflow_types"]:
                ins_workflow_type, _ = WorkflowType.objects.get_or_create(
                    type=res_workflow_type["language_type"],
                    version=res_workflow_type["language_version"],
                )
                ins_workflow_type.save()
                ins_workflow_engine.workflow_types.add(ins_workflow_type)
            ins_workflow_engine.save()
        for wes_version in cleaned_data["d_response"]["supported_wes_versions"]:  # NOQA
            SupportedWesVersion.objects.create(
                service=self,
                wes_version=wes_version,
            )

        return True

    def update_from_server(self):
        d_response = get_requests(self.server_scheme,
                                  self.server_host, "/service-info",
                                  self.server_token)
        if d_response is None:
            return False
        self.auth_instructions_url = d_response["auth_instructions_url"]
        self.contact_info_url = d_response["contact_info_url"]
        res_workflow_engine_names = [workflow_engine["engine_name"] for workflow_engine in d_response["workflow_engines"]]  # NOQA
        for ins_workflow_engine in self.workflow_engines.all():
            if ins_workflow_engine.name in res_workflow_engine_names:
                res_workflow_engine = [workflow_engine for workflow_engine in d_response["workflow_engines"] if workflow_engine["engine_name"] == ins_workflow_engine.name][0]  # NOQA
                if ins_workflow_engine.version != res_workflow_engine["engine_version"]:  # NOQA
                    ins_workflow_engine.version = res_workflow_engine["engine_version"]  # NOQA
                    ins_workflow_engine.workflow_types.clear()
                    ins_workflow_engine.save()
                    for res_workflow_type in res_workflow_engine["workflow_types"]:  # NOQA
                        ins_workflow_type, _ = WorkflowType.objects.get_or_create(type=res_workflow_type["language_type"], version=res_workflow_type["language_version"])  # NOQA
                        ins_workflow_type.save()
                        ins_workflow_engine.workflow_types.add(ins_workflow_type)  # NOQA
                    ins_workflow_engine.save()
            else:
                ins_workflow_engine.delete()
        for res_workflow_engine in d_response["workflow_engines"]:
            ins_workflow_engine, created = WorkflowEngine.objects.get_or_create(service=self, name=res_workflow_engine["engine_name"], version=res_workflow_engine["engine_version"])  # NOQA
            if created is False:
                ins_workflow_engine.workflow_types.clear()
            ins_workflow_engine.save()
            for res_workflow_type in res_workflow_engine["workflow_types"]:
                ins_workflow_type, _ = WorkflowType.objects.get_or_create(
                    type=res_workflow_type["language_type"],
                    version=res_workflow_type["language_version"],
                )
                ins_workflow_type.save()
                ins_workflow_engine.workflow_types.add(ins_workflow_type)
            ins_workflow_engine.save()
        for ins_supported_wes_version in self.supported_wes_versions.all():
            if ins_supported_wes_version.wes_version not in d_response["supported_wes_versions"]:  # NOQA
                ins_supported_wes_version.delete()
        for wes_version in d_response["supported_wes_versions"]:
            supported_wes_version, _ = SupportedWesVersion.objects.get_or_create(service=self, wes_version=wes_version)  # NOQA
            supported_wes_version.save()
        self.save()

        return True

    def create_workflows_from_server(self):
        from app.models.model_workflow import Workflow
        d_response = get_requests(self.server_scheme,
                                  self.server_host, "/workflows",
                                  self.server_token)
        if d_response is None:
            return False
        for res_workflow in d_response["workflows"]:
            ins_workflow_type, _ = WorkflowType.objects.get_or_create(
                type=res_workflow["language_type"],
                version=res_workflow["language_version"],
            )
            ins_workflow_type.save()
            Workflow.objects.create(
                service=self,
                name=res_workflow["workflow_name"],
                version=res_workflow["workflow_version"],
                workflow_type=ins_workflow_type,
                location=res_workflow["workflow_location"],
                content=res_workflow["workflow_content"],
                parameters_template_location=res_workflow["workflow_parameters_template_location"],  # NOQA
                parameters_template=res_workflow["workflow_parameters_template"],  # NOQA
            )

        return True

    def update_workflows_from_server(self):
        from app.models.model_workflow import Workflow
        d_response = get_requests(self.server_scheme,
                                  self.server_host, "/workflows",
                                  self.server_token)
        if d_response is None:
            return False
        res_workflow_names = [workflow["workflow_name"]
                              for workflow in d_response["workflows"]]
        for ins_workflow in self.workflows.all():
            if ins_workflow.name in res_workflow_names:
                res_workflow = [workflow for workflow in d_response["workflows"] if workflow["workflow_name"] == ins_workflow.name][0]  # NOQA
                if ins_workflow.version != res_workflow["workflow_version"]:
                    ins_workflow_type, _ = WorkflowType.objects.get_or_create(
                        type=res_workflow["language_type"],
                        version=res_workflow["language_version"],
                    )
                    ins_workflow_type.save()
                    ins_workflow.version = res_workflow["workflow_version"]
                    ins_workflow.workflow_type = ins_workflow_type
                    ins_workflow.location = res_workflow["workflow_location"]
                    ins_workflow.content = res_workflow["workflow_content"]
                    ins_workflow.parameters_template_location = res_workflow["workflow_parameters_template_location"]  # NOQA
                    ins_workflow.parameters_template = res_workflow["workflow_parameters_template"]  # NOQA
                    ins_workflow.save()
            else:
                ins_workflow.deleted = True
                ins_workflow.save()
        for res_workflow in d_response["workflows"]:
            ins_workflow_type, _ = WorkflowType.objects.get_or_create(
                type=res_workflow["language_type"],
                version=res_workflow["language_version"],
            )
            ins_workflow_type.save()
            ins_workflow, _ = Workflow.objects.get_or_create(
                service=self,
                name=res_workflow["workflow_name"],
                version=res_workflow["workflow_version"],
                workflow_type=ins_workflow_type,
                location=res_workflow["workflow_location"],
                content=res_workflow["workflow_content"],
                parameters_template_location=res_workflow["workflow_parameters_template_location"],  # NOQA
                parameters_template=res_workflow["workflow_parameters_template"],  # NOQA
            )

        return True

    def delete_by_flag(self):
        self.deleted = True
        self.save()
        for workflow_engine in self.workflow_engines.all():
            workflow_engine.deleted = True
            workflow_engine.save()
        for supported_wes_version in self.supported_wes_versions.all():
            supported_wes_version.deleted = True
            supported_wes_version.save()
        for workflow in self.workflows.all():
            workflow.deleted = True
            workflow.save()

        return True


class WorkflowType(CommonInfo):
    type = models.CharField(_("Workflow type"), max_length=64)
    version = models.CharField(_("Workflow version"), max_length=64)

    class Meta:
        db_table = "workflow_type"
        verbose_name = "workflow_type"
        verbose_name_plural = "workflow_types"

    def __str__(self):
        return "Workflow Type: {} {}".format(self.type, self.version)


class WorkflowEngine(CommonInfo):
    service = models.ForeignKey(Service, verbose_name=_("Belong service"), on_delete=models.CASCADE, related_name="workflow_engines")  # NOQA
    name = models.CharField(_("Workflow engine name"), max_length=64)
    version = models.CharField(_("Workflow engine version"), max_length=64)
    workflow_types = models.ManyToManyField(WorkflowType, verbose_name=_("Excutable workflow types"), related_name="workflow_engines", blank=True)  # NOQA

    class Meta:
        db_table = "workflow_engine"
        verbose_name = "workflow_engine"
        verbose_name_plural = "workflow_engines"

    def __str__(self):
        return "Workflow Engine: {}".format(self.name)


class SupportedWesVersion(CommonInfo):
    service = models.ForeignKey(Service, verbose_name=_("Belong service"), on_delete=models.CASCADE, related_name="supported_wes_versions")  # NOQA
    wes_version = models.CharField(_("Wes version"), max_length=64)

    class Meta:
        db_table = "supported_wes_version"
        verbose_name = "supported_wes_version"
        verbose_name_plural = "supported_wes_versions"

    def __str__(self):
        return "Supported Wes Version: {}".format(self.wes_version)
