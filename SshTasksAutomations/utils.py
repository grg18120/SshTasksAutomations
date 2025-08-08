import SshTasksAutomations.config as config
import logging
import paramiko
from scp import SCPClient
from time import sleep
import copy
import time
import re


def output_command(data, command):
    return [x["output"] for x in data if (x["command"] == command)].pop()

def sed_command_replace_file_line(file = None, prev_file_line_str = None, new_file_line_str = None):
    return f"sed -i '/^{prev_file_line_str}/c\\{new_file_line_str}' \"{file}\""


class SSH:
    def __init__(self, ssh_machine, ssh_username, ssh_password = "-"):
        self.ssh_machine = ssh_machine
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.ssh_connection = SSH.open_ssh_connection(self)
        
    def open_ssh_connection(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(hostname=self.ssh_machine, username=self.ssh_username, password=self.ssh_password, timeout=10)
            return client
        except paramiko.AuthenticationException:
            logging.error("Authentication failed, please verify your credentials")
            return None
        except paramiko.SSHException as sshException:
            logging.error(f"Could not establish SSH connection: {sshException}")
            return None
        except Exception as e:
            logging.error(f"Exception in connecting to SSH: {e}")
            return None
        
    def close_ssh_connection(self):
        self.ssh_connection.close()

    def ssh_sudo_command(self, command="ls", jobid="None"):
 
        if self.ssh_connection is None:
            logging.error(f"Job[{jobid}]: SSH connection failed.")
            return False, ["SSH connection failed"]

        command = "sudo -S -p '' %s" % command
        logging.info(f"Job[{jobid}]: Executing: {command}")
        try:
            stdin, stdout, stderr = self.ssh_connection.exec_command(command=command)
            stdin.write(self.ssh_password + "\n")
            stdin.flush()
            stdoutput = stdout.readlines()
            stderroutput = stderr.readlines()

            for output in stdoutput:
                logging.info(f"Job[{jobid}]: {output.strip()}")
            
            logging.debug(f"Job[{jobid}]:stdout: {stdoutput}")
            logging.debug(f"Job[{jobid}]:stderror: {stderroutput}")
            status = stdout.channel.recv_exit_status()
            logging.info(f"Job[{jobid}]:Command status: {status}")
            
            if status == 0:
                logging.info(f"Job[{jobid}]: Command executed successfully.")
                return True, stdoutput
            else:
                logging.error(f"Job[{jobid}]: Command failed.")
                for output in stderroutput:
                    logging.error(f"Job[{jobid}]: {output.strip()}")
                return False, stderroutput
        except Exception as e:
            logging.error(f"Job[{jobid}]: Exception during command execution: {e}")
            return False, [str(e)]

    def ssh_sudo_commands_list(self, commands=["pwd", "ls", "whoami", "hostname"]):
        commands_results = []
        if self.ssh_connection is not  None:
            for command in commands:
                time.sleep(0.5)
                command_result = copy.deepcopy(config.commands_output_init)
                command_result["command"] = command
                command_result["status"], command_result["output"] = self.ssh_sudo_command(
                    command=command
                )
                commands_results.append(command_result)
        return commands_results
    
    def ssh_scp_transfer_dir(self, transf_dir, remote_path):
        # SCPCLient takes a paramiko transport as an argument
        scp = SCPClient(self.ssh_connection.get_transport())
        scp.put(transf_dir, recursive=True, remote_path=remote_path)
        scp.close()

    def ssh_change_user_pass(self, new_password):

        # Open an interactive shell session
        shell = self.ssh_connection.invoke_shell()

        # Start the passwd command to change the current user's password
        shell.send('passwd\n')

        # Wait for the prompt to enter the current (old) password
        time.sleep(0.5)
        shell.send(f'{self.ssh_password}\n')

        # Wait for the prompt to enter the new password
        time.sleep(1)
        shell.send(f'{new_password}\n')

        # Wait for the prompt to confirm the new password
        time.sleep(1)
        shell.send(f'{new_password}\n')

        # Wait for a moment for the command to complete
        time.sleep(1)
        self.ssh_password = new_password

    def ssh_refresh_user_pass_date(self):
        keep_password = self.ssh_password
        self.ssh_change_user_pass(new_password = config.temp_pass)
        self.ssh_change_user_pass(new_password = keep_password)

    def ssh_users_year_passwd_changed_print(self):
        commandList = [
            "cat /etc/passwd | grep /bin/bash",
        ]
        retrieve_data = self.ssh_sudo_commands_list(commandList)
        users_line = output_command(retrieve_data, "cat /etc/passwd | grep /bin/bash")
        users = [ul.split(":")[0] for ul in users_line]
        print(users)

        commandList = [
            f"chage -l {user} | grep Last" for user in users
        ]
        retrieve_data = self.ssh_sudo_commands_list(commandList)
        last_pass_chng = [output_command(retrieve_data, c)[0] for c in commandList]
        last_pass_chng_year = [re.search(r"20\d\d",x).group() for x in last_pass_chng]
        print(last_pass_chng_year)







