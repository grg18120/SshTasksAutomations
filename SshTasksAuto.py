import SshTasksAutomations.config as config
import SshTasksAutomations.utils as utils

for linux_server in config.linux_servers_ip:
    print(f"\n\nServer: {linux_server}")
    for user_dict in config.ssh_users:

        username = list(user_dict.keys())[0]
        password = user_dict.get(username).get("current_pass")

        # OPEN CONNECTION
        ssh = utils.SSH(
            linux_server, 
            username,
            password,
        )

        if ssh.ssh_connection is None:
            exit()
        
        ssh.ssh_users_year_passwd_changed_print()


        # JOB1: CHANGE PASSWORD
        # ssh.ssh_change_user_pass(user_dict.get(username).get("new_pass"))

        # JOB2: KEEP THE SAME PASSWORD AND REFRESH LAST DATE CHANGED
        # ssh.ssh_refresh_user_pass_date()

        ssh.ssh_users_year_passwd_changed_print()

        # CLOSE CONNECTION
        ssh.close_ssh_connection()