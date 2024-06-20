import socket
import tkinter as tk
import threading
import matplotlib.pyplot as plt
import queue

message_queue = queue.Queue()

def ami_decode(ami_string):
    binary_string = []
    
    for bit in ami_string:
        if bit == '0':
            binary_string.append('0')
        else:
            binary_string.append('1')

    return ''.join(binary_string)

def b8zs_decode(b8zs_string):
    ami_string = []
    
    # Definir o padrão de decodificação B8ZS
    decode_pattern = {
        '000+-0-+': '00000000',
        '000-+0+-': '00000000'
    }
    
    i = 0
    while i < len(b8zs_string):
        if b8zs_string[i:i+8] in decode_pattern.keys():
            # Se encontrar um padrão de substituição B8ZS, decodificar
            for key, value in decode_pattern.items():
                if b8zs_string[i:i+8] == key:
                    ami_string.append(value)
            i += 8
        else:
            ami_string.append(b8zs_string[i])
            i += 1
    
    return ''.join(ami_string)

def decode_message(b8zs_message):
    ami_message = b8zs_decode(b8zs_message)
    bin_message = ami_decode(ami_message)

    return bin_message

def bin_to_ascii(bin_message):
    ascii_message = ''
    # Divide a string binária em segmentos de 8 bits
    for i in range(0, len(bin_message), 8):
        # Converte cada segmento binário de volta para o caractere correspondente
        ascii_message += chr(int(bin_message[i:i+8], 2))
    return ascii_message

def uncrypt_message(encripted_message, shift):
    decrypted_message = ""
    
    for char in encripted_message:
        new_code = (ord(char) - shift) % 1114112  # Unicode vai de 0 a 1114111
        decrypted_message += chr(new_code)
    
    return decrypted_message

def plot_wave(message):
    # Mapeamento dos caracteres para amplitude da onda
    amplitude_map = {
        '0': 0,
        '+': 1,
        '-': -1
    }

    # Converter a mensagem em uma lista de amplitudes
    waveform = [amplitude_map[char] for char in message]


    # Plotagem da forma de onda
    plt.figure(figsize=(10, 4))
    plt.plot(waveform, marker='o', drawstyle='steps')
    plt.title('Forma de Onda da Mensagem Recebida')
    plt.xlabel('Amostras')
    plt.ylabel('Amplitude')

    plt.yticks([-1, 0, 1])

    plt.grid(True)
    plt.tight_layout()
    plt.show()

def check_message_queue():
    while True:
        if not message_queue.empty():
            message = message_queue.get()
            plot_wave(message)

def receive_data_and_update_gui():
    global text_encoded, text_binary, text_encrypted, text_original, s, root
    client_socket, address = s.accept()
    while True:
        data = client_socket.recv(1024).decode('utf-8')

        if data:
            print('Mensagem Recebida!')
            message_queue.put(data)
            
            decoded_message = decode_message(data)
            ascii_message = bin_to_ascii(decoded_message)
            uncrypted_message = uncrypt_message(ascii_message, 3)

            text_encoded.delete('1.0', tk.END)
            text_binary.delete('1.0', tk.END)
            text_encrypted.delete('1.0', tk.END)
            text_original.delete('1.0', tk.END)

            text_encoded.insert(tk.END, data)
            text_binary.insert(tk.END, decoded_message)
            text_encrypted.insert(tk.END, ascii_message)
            text_original.insert(tk.END, uncrypted_message)

            data = ''

def main():
    global text_encoded, text_binary, text_encrypted, text_original, s

    root = tk.Tk()
    root.title("Codificação de Linha")

    # Displays para exibir as strings
    display1 = tk.Label(root, text="Mensagem Recebida Codificada em B8ZS: ")
    display1.pack()

    text_encoded = tk.Text(root, height=4)
    text_encoded.pack()

    display2 = tk.Label(root, text="Mensagem Decodificada para Binário: ")
    display2.pack()

    text_binary = tk.Text(root, height=4)
    text_binary.pack()

    display3 = tk.Label(root, text="Mensagem Criptografada em Ascii: ")
    display3.pack()

    text_encrypted = tk.Text(root, height=4)
    text_encrypted.pack()

    display4 = tk.Label(root, text="Mensagem Original: ")
    display4.pack()

    text_original = tk.Text(root, height=4)
    text_original.pack()

    # Configuração do socket para receber dados
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 5001))
    s.listen()
    print("Receiver running and waiting for connections.")

    receive_thread = threading.Thread(target=receive_data_and_update_gui)
    receive_thread.daemon = True  # Marcar a thread como daemon para que ela seja encerrada com o programa principal
    receive_thread.start()

    # Chamar o mainloop do tkinter apenas uma vez para iniciar a interface
    plot_thread = threading.Thread(target=check_message_queue)
    plot_thread.daemon = True  # Marcar a thread como daemon para que ela seja encerrada com o programa principal
    plot_thread.start()

    root.mainloop()

if __name__ == "__main__":
    main()