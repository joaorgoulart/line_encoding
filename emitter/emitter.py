import socket
import tkinter as tk
import threading
import matplotlib.pyplot as plt
import queue

message_queue = queue.Queue()

# Transforma uma string binária em AMI (Alternate Mark Inversion).
def ami_encode(binary_string):

    ami_string = []
    current_polarity = '-'  # Começamos com a polaridade negativa

    for bit in binary_string:
        if bit == '0':
            ami_string.append('0')
        else:
            if current_polarity == '-':
                current_polarity = '+'
            else:
                current_polarity = '-'

            ami_string.append(current_polarity)

    return ''.join(ami_string)

# Codifica uma string AMI utilizando o algoritmo B8ZS.
def b8zs_encode(ami_string):
  
    b8zs_string = []
    previous_pulse = '0'
    
    # Definir o padrão de substituição B8ZS
    substitution_pattern = {
        '+': '000+-0-+',
        '-': '000-+0+-'
    }
    
    # Iterar sobre a string binária em blocos de 8 bits
    i = 0
    while i < len(ami_string):
        if ami_string[i:i+8] == '00000000':
            # Escolher o padrão de substituição com base no último pulso
            if previous_pulse == '+':
                b8zs_string.append(substitution_pattern['+'])
                previous_pulse = '+'  # Ultimo pulso de substituição é negativo
            else:
                b8zs_string.append(substitution_pattern['-'])
                previous_pulse = '-'  # Ultimo pulso de substituição é positivo
            i += 8
        else:
            b8zs_string.append(ami_string[i])
            i += 1
    
    return ''.join(b8zs_string)

def encode_message(bin_message):
    ami_message = ami_encode(bin_message)
    b8zs_message = b8zs_encode(ami_message)

    return b8zs_message

def encrypt_message(message, shift):
    encrypted_message = ""
    
    for char in message:
        novo_codigo = (ord(char) + shift) % 1114112  # Unicode vai de 0 a 1114111
        encrypted_message += chr(novo_codigo)
    
    return encrypted_message

def ascii_to_bin(ascii_string):
    bin_message = ''
    for char in ascii_string:
        # Converte cada caractere em seu código binário de 8 bits
        bin_message += format(ord(char), '08b')
    return bin_message

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

def send_message(s, entry):
    message = entry.get()
    encrypted_message = encrypt_message(message, 3)
    bin_message = ascii_to_bin(encrypted_message)
    encoded_message = encode_message(bin_message)
    message_queue.put(encoded_message)
    s.sendall(encoded_message.encode('utf-8'))
    print("Mensagem Enviada!")
    
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('192.168.18.5', 5001)
    s.connect(server_address)

    root = tk.Tk()
    root.title("Codificação de Linha")

    # Displays para exibir as strings
    display1 = tk.Label(root, text="Insira a Mensagem: ")
    display1.pack()

    entry = tk.Entry(root, width=50)
    entry.pack(pady=10)
 
    button = tk.Button(root, text="Enviar", command=lambda: send_message(s, entry))
    button.pack()

    plot_thread = threading.Thread(target=check_message_queue)
    plot_thread.daemon = True  # Marcar a thread como daemon para que ela seja encerrada com o programa principal
    plot_thread.start()

    # Chamar o mainloop do tkinter apenas uma vez para iniciar a interface
    root.mainloop()

if __name__ == "__main__":
    main()
