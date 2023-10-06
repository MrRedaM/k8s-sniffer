import os
import subprocess
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


interface = "cni0"
frequency = 15
pcap_source_folder = "/nfs/pcap/"
ip_address = '192.168.56.5'
port = '30200'


def send_pcap(file_path, url):
    try:
        with open(file_path, 'rb') as pcap_file:
            response = requests.post(url, files={'pcap_file': pcap_file})
            if response.status_code == 200:
                print(f"PCAP file {file_path} successfully sent.")
            else:
                print(f"Failed to send PCAP file {file_path}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending PCAP file: {str(e)}")


class PCAPFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        print("PCAP file created: " + event.src_path)
        if event.is_directory:
            return
        else:
            source_file = os.path.join(pcap_source_folder, event.src_path)
            send_pcap(source_file, f"http://{ip_address}:{port}/analyse-pcap/")

    def on_modified(self, event):
        print("PCAP file modified: " + event.src_path)
        if event.is_directory:
            return
        else:
            source_file = os.path.join(pcap_source_folder, event.src_path)
            send_pcap(source_file, f"http://{ip_address}:{port}/analyse-pcap/")


if __name__ == "__main__":
    print("Start watching " + pcap_source_folder)
    pcap_event_handler = PCAPFileHandler()
    pcap_observer = Observer()
    pcap_observer.schedule(pcap_event_handler, pcap_source_folder, recursive=False)
    pcap_observer.start()

    subprocess.run(f"tcpdump -i {interface} -w /nfs/pcap/capture-%Y-%m-%d_%H:%M:%S.pcap -G {frequency}")

    while True:
        time.sleep(1)
