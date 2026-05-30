import re
from datetime import datetime
import os
import sys

def processar_chat(caminho_arquivo, data_inicio_str, arquivo_saida):
    # Reconfigura a saída padrão para suportar caracteres UTF-8 (emojis, etc) no terminal Windows
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass

    # Formato da data no WhatsApp: [DD/MM/YYYY, HH:MM:SS] ou similar
    # Regex que lida com possíveis caracteres invisíveis no início (como LRM \u200e)
    padrao = re.compile(r'^[\u200e\u200f\s]*\[(\d{2}/\d{2}/\d{4})[ ,]+(\d{2}:\d{2}:\d{2})\] (.*?): (.*)')
    
    # Data de corte especificada
    data_inicio = datetime.strptime(data_inicio_str, '%d/%m/%Y')
    hoje = datetime.now()
    
    ultima_mensagem = {}
    
    print(f"Lendo o arquivo: {caminho_arquivo}")
    print(f"Filtrando mensagens a partir de: {data_inicio_str}\n")

    with open(caminho_arquivo, 'r', encoding='utf-8') as f:
        membro_atual = None
        for linha in f:
            linha_limpa = linha.strip()
            if not linha_limpa:
                continue
            
            match = padrao.match(linha_limpa)
            if match:
                data_str, hora_str, nome, mensagem = match.groups()
                
                # Tratar nomes removendo caracteres invisíveis e o til (~)
                nome = re.sub(r'[\u200e\u200f\u202a\u202c\u202f]', '', nome)
                if nome.startswith('~'):
                    nome = nome[1:]
                nome = nome.strip()
                
                mensagem = mensagem.replace('\u200e', '').strip()
                
                try:
                    data_msg = datetime.strptime(data_str, '%d/%m/%Y')
                except ValueError:
                    continue # Se a data for inválida, pula
                
                if data_msg >= data_inicio:
                    ultima_mensagem[nome] = {
                        'data_str': data_str,
                        'data_obj': data_msg,
                        'mensagem': mensagem
                    }
                    membro_atual = nome
                else:
                    membro_atual = None # Não acompanha continuações de mensagens antes da data
            else:
                # É uma linha de continuação da mensagem anterior
                if membro_atual and membro_atual in ultima_mensagem:
                    ultima_mensagem[membro_atual]['mensagem'] += " " + linha_limpa.replace('\u200e', '').strip()
                    
    # Ordenar membros pela data da última mensagem (mais recentes primeiro)
    membros_ordenados = sorted(ultima_mensagem.items(), key=lambda x: x[1]['data_obj'], reverse=True)
    
    # Gerar arquivo de saída
    with open(arquivo_saida, 'w', encoding='utf-8') as f_out:
        for nome, info in membros_ordenados:
            data_msg_str = info['data_str']
            msg = info['mensagem']
            dias_passados = (hoje - info['data_obj']).days
            
            # Limpar quebras de linha da mensagem para garantir que fique na mesma linha
            msg_limpa = msg.replace('\n', ' ').replace('\r', '')
            
            linha_saida = f"{data_msg_str} - {nome}: {msg_limpa} ({dias_passados} dias)\n"
            f_out.write(linha_saida)
            
            # Printa no terminal
            try:
                print(linha_saida.strip())
            except UnicodeEncodeError:
                # Fallback caso o terminal não suporte o caractere mesmo com reconfigure
                linha_segura = linha_saida.encode('ascii', 'replace').decode('ascii')
                print(linha_segura.strip())
            
    print(f"\nArquivo '{arquivo_saida}' gerado com sucesso!")

if __name__ == "__main__":
    caminho_chat = '_chat.txt'
    # Data a partir da qual o script deve processar as mensagens
    data_filtro = '01/01/2026' 
    arquivo_resultado = 'ultima_msg_dos_membros.txt'
    
    # Usa o diretório do script para localizar os arquivos corretamente
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_chat_abs = os.path.join(diretorio_atual, caminho_chat)
    arquivo_resultado_abs = os.path.join(diretorio_atual, arquivo_resultado)
    
    # Executa a função principal
    if os.path.exists(caminho_chat_abs):
        processar_chat(caminho_chat_abs, data_filtro, arquivo_resultado_abs)
    else:
        print(f"Erro: Arquivo '{caminho_chat}' não encontrado em {diretorio_atual}.")
