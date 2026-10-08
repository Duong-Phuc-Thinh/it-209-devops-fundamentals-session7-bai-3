import os
import subprocess
import sys

def run_command(command, shell=False):
    try:
        result = subprocess.run(command, shell=shell, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8').strip()
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(e.stderr.decode('utf-8'))
        return None

def main():
    if os.geteuid() != 0:
        print("This script must be run as root (sudo).")
        sys.exit(1)

    print("Step 1: Creating MySQL Database and User...")
    sql_commands = """
    CREATE DATABASE IF NOT EXISTS springboot_db;
    CREATE USER IF NOT EXISTS 'spring-admin'@'localhost' IDENTIFIED BY 'SpringSecure@123';
    GRANT ALL PRIVILEGES ON springboot_db.* TO 'spring-admin'@'localhost';
    FLUSH PRIVILEGES;
    """
    try:
        subprocess.run(['mysql', '-u', 'root', '-e', sql_commands], check=True)
        print("MySQL database and user created successfully.")
    except Exception as e:
        print("Failed to run MySQL commands. Make sure MySQL is installed and running.")
        print(e)

    print("\nStep 2: Creating system user 'spring-runner'...")
    # Create system user spring-runner without login shell
    subprocess.run(['useradd', '-r', '-s', '/bin/false', 'spring-runner'], stderr=subprocess.DEVNULL)
    print("User 'spring-runner' checked/created.")

    print("\nStep 3: Preparing directory /opt/spring-app...")
    os.makedirs('/opt/spring-app', exist_ok=True)
    subprocess.run(['chown', '-R', 'spring-runner:spring-runner', '/opt/spring-app'])
    print("Directory /opt/spring-app ready with correct permissions.")

    print("\nStep 4: Writing systemd service file...")
    service_content = """[Unit]
Description=Spring Boot Application
After=network.target mysql.service

[Service]
User=spring-runner
WorkingDirectory=/opt/spring-app
ExecStart=/usr/bin/java -jar /opt/spring-app/app.jar --server.port=8082
SuccessExitStatus=143
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
"""
    with open('/etc/systemd/system/spring-app.service', 'w') as f:
        f.write(service_content)
    print("Service file written to /etc/systemd/system/spring-app.service")

    print("\nStep 5: Reloading systemd daemon...")
    run_command(['systemctl', 'daemon-reload'])
    run_command(['systemctl', 'enable', 'spring-app'])
    print("Systemd reloaded and service enabled.")

    print("\nSetup completed successfully!")
    print("Please copy your 'app.jar' to '/opt/spring-app/app.jar' and start the service with:")
    print("sudo systemctl start spring-app")

if __name__ == '__main__':
    main()