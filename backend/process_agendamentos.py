from services.agendamento_service import iniciar_processamento_agendamentos
import sys

if __name__ == '__main__':
    # Obter intervalo dos argumentos ou usar padrão de 60 segundos
    intervalo = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    print(f"\nIniciando processador de agendamentos com intervalo de {intervalo} segundos...")
    iniciar_processamento_agendamentos(intervalo) 