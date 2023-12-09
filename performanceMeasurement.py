import subprocess
import psutil
import time

def run_bash_script(script_path):
    # Record the start time
    start_time = time.time()

    # Start the Bash script as a subprocess
    process = subprocess.Popen(['bash', script_path])

    cpu_percent_list = []
    memory_usage_list = []

    try:
        while process.poll() is None:  # While the subprocess is still running
            try:
                # Get CPU usage of the subprocess
                process_obj = psutil.Process(process.pid)
                if process_obj.is_running():
                    subprocess_cpu_percent = process_obj.cpu_percent(interval=1)
                    cpu_percent_list.append(subprocess_cpu_percent)
                    # Print CPU usage
                    print(f'CPU Usage: {subprocess_cpu_percent}%')

                    # Get memory usage of the subprocess
                    subprocess_memory_info = process_obj.memory_info()
                    memory_usage_list.append(subprocess_memory_info.rss)
                    # Print RAM usage
                    print(f'RAM Usage: {subprocess_memory_info.rss / (1024 * 1024):.2f} MB')
                else:
                    print('Process is no longer running. Exiting loop.')
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                print('Process not found or access denied during resource check. Continuing...')
                continue

    finally:
        # Wait for the subprocess to finish and collect its exit status
        try:
            psutil.Process(process.pid).wait()
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            print('Process not found or ZombieProcess encountered during wait. Continuing...')

        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        # Calculate the average CPU usage
        if cpu_percent_list:
            average_cpu_percent = sum(cpu_percent_list) / len(cpu_percent_list)
            print(f'Average CPU Usage: {average_cpu_percent:.2f}%')
        else:
            print('No CPU information collected.')

        # Calculate the average RAM usage
        if memory_usage_list:
            average_memory_usage = sum(memory_usage_list) / len(memory_usage_list)
            print(f'Average RAM Usage: {average_memory_usage / (1024 * 1024):.2f} MB')
        else:
            print('No RAM information collected.')

        print(f'Total Elapsed Time: {elapsed_time:.2f}s')

if __name__ == "__main__":
    bash_script_path = "simpleTest.sh"
    run_bash_script(bash_script_path)
