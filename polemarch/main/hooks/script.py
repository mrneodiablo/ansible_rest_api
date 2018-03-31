import os
import json
import shlex
import threading
import traceback
import logging
import subprocess
from .base import BaseHook
from ..utils import tmp_file_context


logger = logging.getLogger("polemarch")


class Backend(BaseHook):


    def _exec_command_python27(self, script, when):

        def target():
            logger.error(str(script) + str(when))
            try:
                self.process = subprocess.Popen(shlex.split("bash " + script), stdout=subprocess.PIPE,
                                                  stderr=subprocess.STDOUT, shell=True, cwd="/tmp/")
                stdout_data, stderr_data = self.process.communicate()

                if stderr_data:
                    self.__cmd_err = stderr_data
                if stdout_data:
                    self.__cmd_data = stdout_data


            except subprocess.CalledProcessError as err:
                self.__cmd_data = None
                self.__cmd_err = err.message

        thread_run = threading.Thread(target=target)
        thread_run.start()
        thread_run.join(10)
        if thread_run.is_alive():
            self.process.terminate()
            thread_run.join()
            self.__cmd_data = None
            self.__cmd_err = "excute command timeout over 10s"

        return (self.__cmd_data, self.__cmd_err)

    def _execute(self, script, when, file):
        try:
            return subprocess.check_output(
                [script, when, file.name], cwd="/tmp/"
            )
        except BaseException as err:
            logger.info(traceback.format_exc())
            return str(err)

    def setup(self, **kwargs):
        super(Backend, self).setup(**kwargs)
        self.conf['HOOKS_DIR'] = self.get_settings('HOOKS_DIR', '/tmp/')

    def validate(self):
        errors = super(Backend, self).validate()
        for rep in self.hook_object.reps:
            if '../' in rep or rep not in os.listdir(self.conf['HOOKS_DIR']):
                errors["recipients"] = "Recipients must be in hooks dir."
        return errors

    def send(self, message, when):
        super(Backend, self).send(message, when)

        # with tmp_file_context() as file:
        #     file.write(json.dumps(message))
        #     return "\n".join([
        #         self._execute(r, when, file)
        #         for r in self.conf['recipients'] if r
        #     ])

        return self._exec_command_python27("abcd.sh", when, message)