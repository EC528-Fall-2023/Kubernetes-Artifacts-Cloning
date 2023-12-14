import csv
import time
import subprocess
import psutil
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway
from prometheus_client.exposition import basic_auth_handler

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

                    # Get memory usage of the subprocess
                    subprocess_memory_info = process_obj.memory_info()
                    memory_usage_list.append(subprocess_memory_info.rss)
                else:
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    finally:
        # Wait for the subprocess to finish and collect its exit status
        try:
            psutil.Process(process.pid).wait()
        except (psutil.NoSuchProcess, psutil.ZombieProcess):
            pass

        # Record the end time
        end_time = time.time()

        # Calculate the elapsed time
        elapsed_time = end_time - start_time

        # Print performance information
        print(f'Total Elapsed Time: {elapsed_time:.2f}s')

    return cpu_percent_list, memory_usage_list

def write_to_csv(cpu_percent_list, memory_usage_list, csv_filename="performance_data.csv"):
    with open(csv_filename, mode='w', newline='') as csv_file:
        fieldnames = ['Timestamp', 'CPU Usage (%)', 'RAM Usage (MB)']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for timestamp, (cpu_percent, memory_usage) in enumerate(zip(cpu_percent_list, memory_usage_list)):
            writer.writerow({
                'Timestamp': timestamp,
                'CPU Usage (%)': cpu_percent,
                'RAM Usage (MB)': memory_usage / (1024 * 1024)
            })

def send_to_prometheus(cpu_percent_list, memory_usage_list, job_name, pushgateway_url="localhost:9091"):
    registry = CollectorRegistry()
    cpu_gauge = Gauge('subprocess_cpu_usage', 'CPU Usage of Subprocess', ['job'])
    memory_gauge = Gauge('subprocess_memory_usage', 'Memory Usage of Subprocess (MB)', ['job'])

    for timestamp, (cpu_percent, memory_usage) in enumerate(zip(cpu_percent_list, memory_usage_list)):
        cpu_gauge.labels(job=job_name).set(cpu_percent)
        memory_gauge.labels(job=job_name).set(memory_usage / (1024 * 1024))

        # Push metrics to Prometheus Pushgateway
        push_to_gateway(pushgateway_url, job=job_name, registry=registry, handler=basic_auth_handler('username', 'password'))

if __name__ == "__main__":
    bash_script_path = "simpleTest.sh"
    job_name = "subprocess_performance_test"

    cpu_percent_list, memory_usage_list = run_bash_script(bash_script_path)

    # Write data to CSV
    write_to_csv(cpu_percent_list, memory_usage_list)

    # Send data to Prometheus
    send_to_prometheus(cpu_percent_list, memory_usage_list, job_name)
