# PUT YOUR LINUX SERVERS' IPs
linux_servers_ip = [
    "192.168.0.1",
    # Add more IPs as needed
]

# PUT YOUR SSH USERS AND PASSWORDS
ssh_users = [
    {
        "user1": {
            "current_pass": "USER1_PASS",
            "new_pass": "USER1_NEW_PASS"
        }
    },
    {
        "user2": {
            "current_pass": "USER2_PASS",
            "new_pass": "USER2_NEW_PASS"
        }
    },
]


temp_pass = "!!_PUT_YOUR_TEMPORARY_PASSWORD_!!_dsgoetNJ$@*%*"

commands_output_init = {
    "command": {
        "status": None,
        "output": None
    }
}
