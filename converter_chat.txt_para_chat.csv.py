import re
import csv

input_file = '_chat.txt'
output_file = '_chat.csv'

# Regex para detectar o início de uma mensagem no formato [dd/mm/yyyy, hh:mm:ss] Usuário: Mensagem
# E capturar os grupos separadamente
pattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.*?): (.*)')

data = []
current_msg = None

print(f"Lendo '{input_file}' e convertendo para CSV...")

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            match = pattern.match(line)
            if match:
                # Se já tínhamos uma mensagem sendo construída, salva ela antes de começar a próxima
                if current_msg:
                    data.append(current_msg)
                
                current_msg = {
                    'Date': match.group(1),
                    'Time': match.group(2),
                    'User': match.group(3),
                    'Message': match.group(4)
                }
            else:
                # Se a linha não começa com o padrão de timestamp, ela é uma continuação da mensagem anterior (multi-line)
                if current_msg:
                    current_msg['Message'] += " " + line

        # Adiciona a última mensagem do loop
        if current_msg:
            data.append(current_msg)

    # Escrevendo os dados no arquivo CSV
    # encoding='utf-8-sig' é bom para que o Excel abra corretamente em Português
    with open(output_file, 'w', encoding='utf-8-sig', newline='') as csvfile:
        fieldnames = ['Date', 'Time', 'User', 'Message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)

    print(f"\nSucesso! O arquivo foi convertido.")
    print(f"Arquivo salvo como: {output_file}")
    print(f"Total de mensagens processadas: {len(data)}")

except FileNotFoundError:
    print(f"Erro: O arquivo '{input_file}' nao foi encontrado.")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
