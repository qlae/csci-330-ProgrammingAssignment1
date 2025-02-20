import socket
import hashlib  # needed to calculate the SHA256 hash of the file
import sys  # needed to get cmd line parameters
import os.path as path  # needed to get size of file in bytes


IP = '127.0.0.1'  # change to the IP address of the server
PORT = 12000  # change to a desired port number
BUFFER_SIZE = 1024  # change to a desired buffer size


def get_file_size(file_name: str) -> int:
    size = 0
    try:
        size = path.getsize(file_name)
    except FileNotFoundError as fnfe:
        print(f"Error: {fnfe}")
        sys.exit(1)
    return size


def send_file(filename: str):
    print(f"Attempting to send file: {filename}")

    # Check if the file exists
    if not path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    # get the file size in bytes
    # TODO: section 2 step 2 in README.md file
    file_size = get_file_size(filename)
    print(f"File size: {file_size} bytes")

    # convert the file size to an 8-byte byte string using big endian
    # TODO: section 2 step 3 in README.md file
    file_size_bytes = file_size.to_bytes(8, 'big')

    # create a SHA256 object to generate hash of file
    # TODO: section 2 step 4 in README.md file
    file_hash = hashlib.sha256()

    # create a UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        print("Sending file metadata to server...")
        # send the file size in the first 8-bytes followed by the bytes for the file name to server at (IP, PORT)
        # TODO: section 2 step 6 in README.md file
        client_socket.sendto(file_size_bytes + filename.encode(), (IP, PORT))

        # TODO: section 2 step 7 in README.md file
        response, _ = client_socket.recvfrom(1024)
        print(f"Server Response: {response}")

        if response != b'go ahead':
            print("Error: Server did not acknowledge.")
            sys.exit(1)

        print("Sending file data...")
        # open the file to be transferred
        with open(filename, 'rb') as file:
            # read the file in chunks and send each chunk to the server
            # TODO: section 2 step 8 a-d in README.md file
            while chunk := file.read(BUFFER_SIZE):
                client_socket.sendto(chunk, (IP, PORT))
                file_hash.update(chunk)  # Update hash with sent data

                ack, _ = client_socket.recvfrom(1024)
                if ack != b'received':
                    print("Error: Server did not acknowledge chunk.")
                    sys.exit(1)

        print("Sending file hash for verification...")
        # send the hash value so server can verify that the file was received correctly
        # TODO: section 2 step 9 in README.md file
        client_socket.sendto(file_hash.digest(), (IP, PORT))

        # TODO: section 2 step 10 in README.md file
        final_response, _ = client_socket.recvfrom(1024)
        print(f"Final Server Response: {final_response}")

        # TODO: section 2 step 11 in README.md file
        if final_response == b'success':
            print("File transfer successful!")
        else:
            print("File transfer failed.")
    except Exception as e:
        print(f"An error occurred while sending the file: {e}")
    finally:
        client_socket.close()


if __name__ == "__main__":
    # get filename from cmd line
    if len(sys.argv) < 2:
        print(f'SYNOPSIS: {sys.argv[0]} <filename>')
        sys.exit(1)
    file_name = sys.argv[1]  # filename from cmdline argument
    send_file(file_name)