import io
import socket
import struct
from PIL import Image
import matplotlib.pyplot as plt

def client():
    """Connects to the server and displays the live video stream."""
    server_ip = '141.225.163.147'  # Replace with the server's IP address
    client_socket = socket.socket()
    client_socket.connect((server_ip, 8000))
    connection = client_socket.makefile('rb')

    try:
        plt.ion()  # Interactive mode for live updates
        fig, ax = plt.subplots()
        img_display = None

        while True:
            # Read the length of the image as a 32-bit unsigned int
            image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
            if not image_len:
                break
            # Read the image data and display it
            image_stream = io.BytesIO()
            image_stream.write(connection.read(image_len))
            image_stream.seek(0)
            image = Image.open(image_stream)

            if img_display is None:
                img_display = ax.imshow(image)
                plt.axis('off')
            else:
                img_display.set_data(image)

            plt.pause(0.01)
            plt.draw()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close()
        client_socket.close()

if __name__ == '__main__':
    client()
