import subprocess
import time

def test_udp_transfer():
    server_proc = subprocess.Popen(["python3", "udp_server.py"])
    time.sleep(1)  # Give server time to start

    test_file = "test.txt"
    with open(test_file, "w") as f:
        f.write("Hello, UDP!")

    client_proc = subprocess.run(["python3", "udp_client.py", test_file])

    assert client_proc.returncode == 0, "Client failed to send the file"

    server_proc.terminate()