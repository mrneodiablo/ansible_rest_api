# -*- coding: utf-8 -*-
# pylint: disable=broad-except,no-member,redefined-outer-name
import logging

from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.parsing.dataloader import DataLoader
from ansible.playbook import Play
from django.utils import timezone
import json
from polemarch.main.ansibleutils import AnsibleInventoryManager, AnsibleVariableManager, AnsibleResultsCallback, AnsibleOption
from ...wapp import app
from ..utils import task, BaseTask
from .exceptions import TaskError
from ..models.utils import AnsibleModule, AnsiblePlaybook, DummyHistory
from ..models.hooks import Hook
from polemarch.api.base import Response as APIResponse


logger = logging.getLogger("polemarch")



@task(app, ignore_result=True, default_retry_delay=1,
      max_retries=5, bind=True)
class RepoTask(BaseTask):
    accepted_oprations = ["clone", "sync"]

    class RepoTaskError(TaskError):
        pass

    class UnknownRepoOperation(RepoTaskError):
        _default_message = "Unknown operation {}."

    def __init__(self, app, project, operation="sync", *args, **kwargs):
        super(self.__class__, self).__init__(app, *args, **kwargs)
        self.project, self.operation = project, operation
        if self.operation not in self.accepted_oprations:
            raise self.task_class.UnknownRepoOperation(self.operation)

    def run(self):
        try:
            result = getattr(self.project, self.operation)()
            logger.info(result)
        except Exception as error:
            self.app.retry(exc=error)


@task(app, ignore_result=True, bind=True)
class ScheduledTask(BaseTask):
    def __init__(self, app, job_id, *args, **kwargs):
        super(self.__class__, self).__init__(app, *args, **kwargs)
        self.job_id = job_id

    def run(self):
        from ..models import PeriodicTask
        try:
            task = PeriodicTask.objects.get(id=self.job_id)
        except PeriodicTask.DoesNotExist:
            return
        task.execute()


class _ExecuteAnsible(BaseTask):
    ansible_class = None

    def run(self):
        # pylint: disable=not-callable
        ansible_object = self.ansible_class(*self.args, **self.kwargs)
        ansible_object.run()


@task(app, ignore_result=True, bind=True)
class ExecuteAnsiblePlaybook(_ExecuteAnsible):
    ansible_class = AnsiblePlaybook


@task(app, ignore_result=True, bind=True)
class ExecuteAnsibleModule(_ExecuteAnsible):
    ansible_class = AnsibleModule


## ddoongvt thêm action ansible script
@task(app, ignore_result=True, bind=True)
class ExecuteAnsibleScript(_ExecuteAnsible):
    """
    Thực chất sẽ gọi ansible playbook với 2 module là
    - copy file
    - commanf file
    """
    ansible_class = AnsiblePlaybook


@task(app, ignore_result=True, bind=True)
class SendHook(BaseTask):
    def __init__(self, app, when, message, *args, **kwargs):
        super(self.__class__, self).__init__(app, *args, **kwargs)
        self.when = when
        self.message = message

    def run(self):
        Hook.objects.execute(self.when, self.message)


# dongvt thêm ansible excute in worker
@task(app, ignore_result=True, bind=True)
class ExecuteAnsibleModuleAPI(BaseTask):
    """
           kwargs = {
            "data": {"list-hosts": "", "module": "shell", "group": "groupapi", "args": "ifconfig"},
            "inventory": Inventory,
            "history": history,
            "project": project
        }
    """
    status_codes = {
        4: "OFFLINE",
        -9: "INTERRUPTED",
        "other": "ERROR"
    }

    def __init__(self, app, **kwargs):
        super(self.__class__, self).__init__(app, **kwargs)
        self.inventory = kwargs["inventory"]
        self.data = kwargs["data"]
        self.history = kwargs["history"] if kwargs["history"] else DummyHistory()
        self.project = kwargs["project"]

    def executor(self):
        # data là dang dict
        loader = DataLoader()

        # load inventory
        inventories = AnsibleInventoryManager(loader=loader, sources=[self.inventory])

        # load variable manager
        variable_manager = AnsibleVariableManager(loader=loader, inventory=inventories)

        # result callback về
        results_callback = AnsibleResultsCallback()

        options = AnsibleOption()
        # load ansible option
        # pase option from data
        # [inventory, module, group, args]
        for k_option, v_option in self.data.iteritems():
            if k_option not in ["inventory", "module", "group", "args"]:
                # add option
                try:
                    if k_option == "listhosts":
                        data_out_put = inventories.get_groups_dict()[self.data["group"]]
                        return APIResponse(data_out_put, 201)
                    else:
                        options.__setattr__(k_option, True)
                except:
                    pass



        play_source = dict(
            name="Ansible Play Module " + self.data["module"] + " " + self.data["args"],
            hosts=str(self.data["group"]),
            gather_facts='no',
            tasks=[
                dict(action=dict(module=self.data["module"], args=self.data["args"])),
            ]
        )


        play = Play().load(play_source, variable_manager=variable_manager, loader=loader)


        # actually run it
        tqm = None
        try:
            tqm = TaskQueueManager(
                inventory=inventories,
                variable_manager=variable_manager,
                loader=loader,
                options=options,
                passwords=None,
                stdout_callback=results_callback,  # Use our custom callback instead of the ``default`` callback plugin
            )
            tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup ()

        return results_callback.return_data

    def prepare(self):
        self.target = self.data["group"]
        self.history.status = "RUN"
        self.history.revision = self.project.revision
        self.history.save()

    def execute(self):
        try:
            self.prepare()
            self.history.status = "OK"
            output = self.executor()
            self.history.raw_stdout = json.dumps(output)
        except Exception as exception:
            self.error_handler(exception)
        finally:
            inventory_object = getattr(self, "inventory_object", None)
            inventory_object and inventory_object.close()
            self.history.stop_time = timezone.now()
            self.history.save()

    def run(self):
        return self.execute()

    def error_handler(self, exception):
        default_status = self.status_codes["other"]
        self.history.raw_stdout = self.history.raw_stdout + str(exception)
        self.history.status = default_status