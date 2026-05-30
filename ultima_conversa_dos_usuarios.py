import re
import sys
from datetime import datetime

# Garante que o terminal suporte UTF-8 (necessário no Windows)
sys.stdout.reconfigure(encoding='utf-8')

input_file = '_chat.txt'

# Regex para detectar o início de uma mensagem no formato [dd/mm/yyyy, hh:mm:ss] Usuário: Mensagem
pattern = re.compile(r'\[(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}:\d{2})\] (.*?): (.*)')

# Dicionário para guardar a última mensagem de cada usuário
# Formato: { usuario: { 'datetime': datetime_obj, 'date': str, 'time': str, 'message': str } }
ultima_mensagem = {}

print(f"Lendo '{input_file}'...")

try:
    with open(input_file, 'r', encoding='utf-8') as f:
        current_user = None
        current_date = None
        current_time = None
        current_msg = None

        for line in f:
            line = line.strip()
            if not line:
                continue

            match = pattern.match(line)
            if match:
                # Salva a mensagem anterior antes de processar a nova
                if current_user is not None:
                    dt = datetime.strptime(f"{current_date} {current_time}", "%d/%m/%Y %H:%M:%S")
                    # Atualiza se for a mensagem mais recente do usuário
                    if current_user not in ultima_mensagem or dt >= ultima_mensagem[current_user]['datetime']:
                        ultima_mensagem[current_user] = {
                            'datetime': dt,
                            'date': current_date,
                            'time': current_time,
                            'message': current_msg
                        }

                current_date = match.group(1)
                current_time = match.group(2)
                current_user = match.group(3)
                current_msg = match.group(4)
            else:
                # Continuação de mensagem multi-linha
                if current_msg is not None:
                    current_msg += ' ' + line

        # Processa a última mensagem do arquivo
        if current_user is not None:
            dt = datetime.strptime(f"{current_date} {current_time}", "%d/%m/%Y %H:%M:%S")
            if current_user not in ultima_mensagem or dt >= ultima_mensagem[current_user]['datetime']:
                ultima_mensagem[current_user] = {
                    'datetime': dt,
                    'date': current_date,
                    'time': current_time,
                    'message': current_msg
                }

    # Ordena os usuários pela data da última mensagem (mais recente primeiro)
    usuarios_ordenados = sorted(
        ultima_mensagem.items(),
        key=lambda x: x[1]['datetime'],
        reverse=True
    )

    print(f"\n{'='*70}")
    print(f"{'ÚLTIMA MENSAGEM DE CADA USUÁRIO':^70}")
    print(f"{'='*70}")
    print(f"Total de usuários encontrados: {len(usuarios_ordenados)}\n")

    for usuario, info in usuarios_ordenados:
        print(f"[Usuario] {usuario}")
        print(f"   Data: {info['date']}  Hora: {info['time']}")
        print(f"   Msg : {info['message']}")
        print(f"   {'-'*60}")

except FileNotFoundError:
    print(f"Erro: O arquivo '{input_file}' não foi encontrado.")
    print("Certifique-se de executar o script na mesma pasta que o arquivo _chat.txt")
except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")
