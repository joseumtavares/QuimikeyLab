import serial
import json
import time
from datetime import datetime

# ============================================
# CONFIGURAÇÃO DA PORTA SERIAL
# ============================================
# Altere 'COM5' conforme a porta em que seu Arduino está conectado.
# Em Linux/Mac, use '/dev/ttyUSB0' ou '/dev/ttyACM0'

PORTA = 'COM6'
BAUDRATE = 9600
TIMEOUT = 2

# ============================================
# FUNÇÃO: Conectar ao Arduino
# ============================================
def conectar_serial():
    try:
        print(f"Conectando ao Quimikey na porta {PORTA}...")
        ser = serial.Serial(PORTA, BAUDRATE, timeout=TIMEOUT)
        time.sleep(2)  # Aguarda inicialização do Arduino
        print("✅ Conectado com sucesso!")
        return ser
    except serial.SerialException:
        print("❌ Erro: não foi possível conectar ao Quimikey.")
        return None

# ============================================
# FUNÇÃO: Enviar comando ao Arduino
# ============================================
def enviar_comando(ser, comando):
    if not ser:
        return
    ser.write((comando + '\n').encode('utf-8'))
    print(f">> Enviado: {comando}")

# ============================================
# FUNÇÃO: Ler e interpretar dados JSON vindos do Quimikey
# ============================================
def ler_dados(ser):
    if not ser:
        return
    try:
        linha = ser.readline().decode('utf-8').strip()
        if not linha:
            return
        if linha.startswith('{') and linha.endswith('}'):
            try:
                dados = json.loads(linha)
                print(f"<< Recebido JSON: {json.dumps(dados, indent=2, ensure_ascii=False)}")
                salvar_log(dados)
            except json.JSONDecodeError:
                print(f"<< [Dado bruto]: {linha}")
        else:
            print(f"<< {linha}")
    except Exception as e:
        print(f"⚠️ Erro de leitura: {e}")

# ============================================
# FUNÇÃO: Salvar log em arquivo local
# ============================================
def salvar_log(dados):
    try:
        with open("quimikey_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} | {json.dumps(dados, ensure_ascii=False)}\n")
    except Exception as e:
        print(f"Erro ao salvar log: {e}")

# ============================================
# FUNÇÃO: Menu interativo
# ============================================
def menu(ser):
    print("\n======= MENU QUIMIKEY =======")
    print("[1] Testar conexão (PING)")
    print("[2] Modo Setup")
    print("[3] Modo Normal")
    print("[4] Solicitar elemento (por número atômico)")
    print("[5] Ler respostas do Quimikey")
    print("[6] Sair")
    print("=============================\n")

    while True:
        opc = input("Escolha uma opção: ").strip()

        if opc == '1':
            enviar_comando(ser, "PING")
        elif opc == '2':
            enviar_comando(ser, "SETUP_MODE")
        elif opc == '3':
            enviar_comando(ser, "NORMAL_MODE")
        elif opc == '4':
            numero = input("Digite o número atômico do elemento: ").strip()
            enviar_comando(ser, f"ELEMENT {numero}")
        elif opc == '5':
            print("Aguardando dados do Quimikey (CTRL+C para sair)...")
            try:
                while True:
                    ler_dados(ser)
            except KeyboardInterrupt:
                print("\nInterrompido pelo usuário.")
        elif opc == '6':
            print("Encerrando comunicação...")
            break
        else:
            print("Opção inválida.")
        time.sleep(0.3)

# ============================================
# PROGRAMA PRINCIPAL
# ============================================
if __name__ == "__main__":
    ser = conectar_serial()
    if ser:
        try:
            menu(ser)
        finally:
            ser.close()
            print("🔌 Conexão encerrada.")

# //Programação: José U.M.Tavares
# //Técnico em Eletrônica
# //Projetista Eletrônico