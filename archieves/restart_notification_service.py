import os
import signal
import subprocess
import time
import sys

def run_command(command):
    """Run a shell command and return the output"""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
        text=True
    )
    stdout, stderr = process.communicate()
    return {
        'stdout': stdout,
        'stderr': stderr,
        'exit_code': process.returncode
    }

def find_notification_process():
    """Find the PID of the running notification.py process"""
    result = run_command("ps -ef | grep 'notification.py' | grep -v grep")
    if result['exit_code'] == 0 and result['stdout'].strip():
        # Parse PID from the ps output
        parts = result['stdout'].strip().split()
        if len(parts) >= 2:
            return int(parts[1])  # PID is in the second column
    return None

def stop_notification_service():
    """Stop the running notification service if it's running"""
    pid = find_notification_process()
    if pid:
        print(f"Stopping notification service (PID: {pid})...")
        try:
            os.kill(pid, signal.SIGTERM)
            # Wait a moment to ensure it's stopped
            time.sleep(2)
            if find_notification_process() is None:
                print("Notification service stopped successfully.")
                return True
            else:
                print("Service did not stop with SIGTERM, trying SIGKILL...")
                os.kill(pid, signal.SIGKILL)
                time.sleep(1)
                if find_notification_process() is None:
                    print("Notification service stopped successfully with SIGKILL.")
                    return True
                else:
                    print("Failed to stop notification service.")
                    return False
        except Exception as e:
            print(f"Error stopping notification service: {e}")
            return False
    else:
        print("No notification service is currently running.")
        return True

def start_notification_service():
    """Start the notification service with the correct environment variables"""
    # Set up environment variables
    env = os.environ.copy()
    env.update({
        'EMAIL_ENABLED': 'true',
        'EMAIL_HOST': 'smtp.mailersend.net',
        'EMAIL_PORT': '587',
        'EMAIL_USER': 'MS_FSeNj8@trial-r6ke4n1xr63gon12.mlsender.net',
        'EMAIL_PASSWORD': 'mssp.c15zPmM.3zxk54vnek6ljy6v.175bFNr',
        'EMAIL_FROM': 'MS_FSeNj8@trial-r6ke4n1xr63gon12.mlsender.net',
        'EMAIL_FROM_NAME': 'Drone Delivery Service',
        'MAILERSEND_API_KEY': 'mlsn.6bdfb137652a12742bf620598b7374f59e91fb2f64b88e42636680365ffb92fc',
        'USE_MAILERSEND_API': 'true',
        'RABBITMQ_HOST': 'localhost'
    })
    
    # The notification.py is located at ./atomic/notification-service/notification.py
    notification_path = './atomic/notification-service/notification.py'
    if not os.path.exists(notification_path):
        print(f"Cannot find notification.py at {notification_path}. Please run this script from the project root directory.")
        return False
    
    # Change to the directory containing notification.py
    os.chdir(os.path.dirname(notification_path))
    notification_filename = os.path.basename(notification_path)
    
    # Start the service in the background
    try:
        print(f"Starting notification service with script: {notification_filename}")
        cmd = f"python {notification_filename}"
        
        # Start in a new terminal window on macOS
        if sys.platform == "darwin":  # macOS
            # First move to the right directory
            terminal_cmd = f'''osascript -e 'tell app "Terminal" to do script "cd {os.getcwd()} && export EMAIL_ENABLED=true EMAIL_HOST=smtp.mailersend.net EMAIL_PORT=587 EMAIL_USER=MS_FSeNj8@trial-r6ke4n1xr63gon12.mlsender.net EMAIL_PASSWORD=mssp.c15zPmM.3zxk54vnek6ljy6v.175bFNr EMAIL_FROM=MS_FSeNj8@trial-r6ke4n1xr63gon12.mlsender.net EMAIL_FROM_NAME=\\"Drone Delivery Service\\" MAILERSEND_API_KEY=mlsn.6bdfb137652a12742bf620598b7374f59e91fb2f64b88e42636680365ffb92fc USE_MAILERSEND_API=true RABBITMQ_HOST=localhost && python {notification_filename}"' '''
            print("Starting new terminal with command:", terminal_cmd)
            result = run_command(terminal_cmd)
            if result['exit_code'] == 0:
                print("Notification service started in a new terminal window.")
                return True
            else:
                print(f"Failed to start in Terminal: {result['stderr']}")
                # Fall back to background process
        
        # If not on macOS or terminal start failed, start as a background process
        print("Starting as background process...")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            env=env,
            text=True
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(2)
        
        if find_notification_process():
            print(f"Notification service started with PID: {find_notification_process()}")
            return True
        else:
            print("Failed to start notification service.")
            return False
            
    except Exception as e:
        print(f"Error starting notification service: {e}")
        return False

def main():
    print("==================================================")
    print("     NOTIFICATION SERVICE MANAGEMENT UTILITY      ")
    print("==================================================")
    
    # Stop the current service if running
    if not stop_notification_service():
        print("WARNING: Could not stop the current notification service.")
        response = input("Continue anyway? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Start the service with proper environment variables
    if start_notification_service():
        print("==================================================")
        print("Notification service restarted successfully with proper environment variables.")
        print("You can now run your tests and should receive emails.")
        print("==================================================")
    else:
        print("==================================================")
        print("Failed to restart notification service.")
        print("==================================================")

if __name__ == "__main__":
    main() 