# Author: Yehang Liu, Last Modified Date: 2016-02-17

import subprocess as sp
import os


class PythonCallMatlab(object):
    def __init__(self):
        self.status = False

    def _generate_command(self):
        path = os.getcwd()
        path_ai_flag = True # if through AI run, the path_ai_flag should set TRUE
        if not path_ai_flag:
            path = os.path.dirname(path)
            path = os.path.dirname(path)
        # command_mat_path = '"/usr/local/MATLAB/MATLAB_Production_Server/R2014b/bin/matlab"'
        print path
        command_mat_path = '"/home/filon/matlab/bin/matlab"'
        command_skip = " -nodisplay -nosplash -nodesktop -r "
        command_run_mat_program = '"run(' + "'" + path + "/library/vision/facedirection/facedirection_server()" + "');" + '"'
        command_input = "exec " + command_mat_path + command_skip + command_run_mat_program
        return command_input

    def run_connect(self):
        command = self._generate_command()
        if command is None:
            self.status = False
        else:
            sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)

if __name__ == '__main__':
    pcm = PythonCallMatlab()
    pcm.run_connect()