import io
import socket
import struct
import time
import picamera
from threading import Thread

def handle_client(client_socket):
    """Handles an individual client by streaming camera data."""
    connection = client_socket.makefile('wb')
    try:
        camera = picamera.PiCamera()
        camera.resolution = (640, 480)
        camera.start_preview()
        time.sleep(2)

        stream = io.BytesIO()
        for _ in camera.capture_continuous(stream, format='jpeg'):
            try:
                # Send the image length and image data
                connection.write(struct.pack('<L', stream.tell()))
                connection.flush()
                stream.seek(0)
                connection.write(stream.read())
                stream.seek(0)
                stream.truncate()
            except BrokenPipeError:
                print("Client disconnected.")
                break
    except Exception as e:
        print(f"Error with client: {e}")
    finally:
        # Only attempt to clean up if the connection is open
        try:
            connection.close()
        except Exception as e:
            print(f"Error closing connection: {e}")
        finally:
            client_socket.close()
        camera.close()



def server():
    """Sets up the server to accept connections."""
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8000))  # Listen on all interfaces, port 8000
    server_socket.listen(5)
    print("Server is running on port 8000...")
    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Client connected from {addr}")
            client_thread = Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    except KeyboardInterrupt:
        print("Shutting down server.")
    finally:
        server_socket.close()

if __name__ == '__main__':
    server()
