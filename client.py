import io
import socket
import struct
from PIL import Image
import matplotlib.pyplot as plt
import signal
import sys

def client():
    """Connects to the server and displays the live video stream."""
    server_ip = '141.225.165.144'  # Replace with the server's IP address
    client_socket = socket.socket()
    client_socket.connect((server_ip, 8000))
    connection = client_socket.makefile('rb')

    # Flag to indicate whether to keep running
    running = True

    def signal_handler(sig, frame):
        nonlocal running
        print("\nGracefully exiting...")
        running = False
        plt.close('all')  # Close the Matplotlib window

    # Handler for Matplotlib window close event
    def on_close(event):
        nonlocal running
        print("Matplotlib window closed. Exiting...")
        running = False

    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    try:
        plt.ion()  # Interactive mode for live updates
        fig, ax = plt.subplots()
        fig.canvas.mpl_connect('close_event', on_close)  # Connect close event
        img_display = None

        while running:  # Loop until running is False
            if not plt.fignum_exists(fig.number):  # Exit if the window is closed
                break
            try:
                # Read the length of the image as a 32-bit unsigned int
                image_len_data = connection.read(struct.calcsize('<L'))
                if not image_len_data:
                    break

                image_len = struct.unpack('<L', image_len_data)[0]
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

                plt.tight_layout(pad=0)
                plt.pause(0.01)
                plt.draw()
            except (struct.error, OSError) as e:
                print(f"Stream error: {e}")
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        connection.close()
        client_socket.close()
        plt.close('all')  # Ensure the Matplotlib window is closed
        print("Connection closed.")

if __name__ == '__main__':
    client()
