import os
import time
import json
import csv
import random
import threading
import shutil
from datetime import datetime
from pathlib import Path
from auto_file_processor import AutoFileProcessor, FileImportExport

class FileProcessorSimulator:
    """Simulador para demonstrar o funcionamento do processador automático de arquivos"""
    
    def __init__(self, base_dir="./simulator"):
        """Inicializa o simulador com diretórios dentro de uma pasta base"""
        self.base_dir = base_dir
        self.input_dir = os.path.join(base_dir, "input")
        self.output_dir = os.path.join(base_dir, "output")
        self.archive_dir = os.path.join(base_dir, "archive")
        
        # Limpa e cria os diretórios
        self.setup_directories()
        
        # Inicializa o processador
        self.processor = AutoFileProcessor(
            input_directory=self.input_dir,
            output_directory=self.output_dir,
            archive_directory=self.archive_dir
        )
        
        # Flag para controlar a simulação
        self.running = False
    
    def setup_directories(self):
        """Configura os diretórios para a simulação"""
        # Remove diretórios existentes se necessário
        if os.path.exists(self.base_dir):
            shutil.rmtree(self.base_dir)
        
        # Cria novos diretórios
        os.makedirs(self.input_dir)
        os.makedirs(self.output_dir)
        os.makedirs(self.archive_dir)
        print(f"Diretórios de simulação criados em: {self.base_dir}")
    
    def create_sample_csv(self, filename="dados.csv"):
        """Cria um arquivo CSV de exemplo"""
        file_path = os.path.join(self.input_dir, filename)
        data = [
            ["Nome", "Idade", "Email"],
            ["João Silva", "30", "joao@exemplo.com"],
            ["Maria Santos", "25", "maria@exemplo.com"],
            ["Pedro Oliveira", "42", "pedro@exemplo.com"]
        ]
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        
        print(f"Arquivo CSV criado: {file_path}")
        return file_path
    
    def create_sample_json(self, filename="dados.json"):
        """Cria um arquivo JSON de exemplo"""
        file_path = os.path.join(self.input_dir, filename)
        data = {
            "funcionarios": [
                {
                    "nome": "João Silva",
                    "idade": 30,
                    "email": "joao@exemplo.com",
                    "departamento": "TI"
                },
                {
                    "nome": "Maria Santos",
                    "idade": 25,
                    "email": "maria@exemplo.com",
                    "departamento": "RH"
                }
            ],
            "empresa": "Exemplo Ltda",
            "data": datetime.now().strftime("%Y-%m-%d")
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        
        print(f"Arquivo JSON criado: {file_path}")
        return file_path
    
    def create_sample_xml(self, filename="dados.xml"):
        """Cria um arquivo XML de exemplo"""
        file_path = os.path.join(self.input_dir, filename)
        
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<empresa nome="Exemplo Ltda" data="{datetime.now().strftime("%Y-%m-%d")}">
    <funcionarios>
        <funcionario id="1">
            <nome>João Silva</nome>
            <idade>30</idade>
            <email>joao@exemplo.com</email>
            <departamento>TI</departamento>
        </funcionario>
        <funcionario id="2">
            <nome>Maria Santos</nome>
            <idade>25</idade>
            <email>maria@exemplo.com</email>
            <departamento>RH</departamento>
        </funcionario>
    </funcionarios>
</empresa>
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        print(f"Arquivo XML criado: {file_path}")
        return file_path
    
    def create_sample_excel(self, filename="dados.xlsx"):
        """Cria um arquivo Excel de exemplo"""
        file_path = os.path.join(self.input_dir, filename)
        
        import pandas as pd
        
        # Cria um DataFrame de exemplo
        data = {
            'Nome': ['João Silva', 'Maria Santos', 'Pedro Oliveira'],
            'Idade': [30, 25, 42],
            'Email': ['joao@exemplo.com', 'maria@exemplo.com', 'pedro@exemplo.com'],
            'Departamento': ['TI', 'RH', 'Vendas']
        }
        
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False)
        
        print(f"Arquivo Excel criado: {file_path}")
        return file_path
    
    def start_simulation(self):
        """Inicia a simulação"""
        self.running = True
        
        # Inicia o processador
        self.processor.start_watching()
        self.processor.schedule_exports()
        
        # Inicia uma thread para criar arquivos periodicamente
        self.simulation_thread = threading.Thread(target=self.simulation_loop)
        self.simulation_thread.daemon = True
        self.simulation_thread.start()
        
        # Inicia a interface de linha de comando
        cli_thread = self.processor.start_command_line_interface()
        
        print("\n=== Simulação Iniciada ===")
        print("O sistema está monitorando a pasta de entrada e processando arquivos automaticamente.")
        print("Arquivos de exemplo serão criados a cada 20 segundos.")
        print("Use a interface de linha de comando para interagir com o sistema.")
        
        return cli_thread
    
    def simulation_loop(self):
        """Loop principal da simulação que cria arquivos periodicamente"""
        file_creators = [
            self.create_sample_csv,
            self.create_sample_json,
            self.create_sample_xml,
            self.create_sample_excel
        ]
        
        file_count = 0
        
        while self.running:
            # Espera um tempo entre a criação de arquivos
            time.sleep(20)
            
            # Escolhe aleatoriamente um tipo de arquivo para criar
            creator = random.choice(file_creators)
            
            # Cria um nome de arquivo único com contador
            file_count += 1
            timestamp = int(time.time())
            filename = f"arquivo_{file_count}_{timestamp}{self._get_extension(creator)}"
            
            # Cria o arquivo
            creator(filename)
            
            # Verifica se a simulação ainda está em execução
            if not self.running:
                break
    
    def _get_extension(self, creator_function):
        """Retorna a extensão apropriada com base na função criadora"""
        if creator_function == self.create_sample_csv:
            return ".csv"
        elif creator_function == self.create_sample_json:
            return ".json"
        elif creator_function == self.create_sample_xml:
            return ".xml"
        elif creator_function == self.create_sample_excel:
            return ".xlsx"
        return ".txt"
    
    def stop_simulation(self):
        """Para a simulação"""
        self.running = False
        self.processor.stop_watching()
        print("Simulação interrompida")
    
    def interactive_demo(self):
        """Demonstração interativa do simulador"""
        print("\n=== Demonstração Interativa do Processador de Arquivos ===")
        print("Esta demonstração mostrará como o sistema processa diferentes tipos de arquivos.")
        
        # Inicia o processador
        self.processor.start_watching()
        
        # Menu interativo
        while True:
            print("\nOpções:")
            print("1. Criar arquivo CSV")
            print("2. Criar arquivo JSON")
            print("3. Criar arquivo XML")
            print("4. Criar arquivo Excel")
            print("5. Iniciar simulação automática")
            print("6. Configurar processador")
            print("7. Sair")
            
            choice = input("\nEscolha uma opção (1-7): ")
            
            if choice == "1":
                self.create_sample_csv()
            elif choice == "2":
                self.create_sample_json()
            elif choice == "3":
                self.create_sample_xml()
            elif choice == "4":
                self.create_sample_excel()
            elif choice == "5":
                print("Iniciando simulação automática. Pressione Ctrl+C para interromper.")
                cli_thread = self.start_simulation()
                try:
                    cli_thread.join()
                except KeyboardInterrupt:
                    self.stop_simulation()
            elif choice == "6":
                self._configure_processor()
            elif choice == "7":
                self.processor.stop_watching()
                print("Demonstração encerrada.")
                break
            else:
                print("Opção inválida. Tente novamente.")
    
    def _configure_processor(self):
        """Menu para configurar o processador"""
        print("\nConfiguração do Processador:")
        print("1. Ativar/Desativar conversão para JSON")
        print("2. Ativar/Desativar arquivamento")
        print("3. Ativar/Desativar backups")
        print("4. Voltar")
        
        choice = input("\nEscolha uma opção (1-4): ")
        
        if choice == "1":
            status = input("Ativar conversão para JSON? (s/n): ").lower()
            self.processor.set_convert_all_to_json(status == 's')
        elif choice == "2":
            status = input("Ativar arquivamento? (s/n): ").lower()
            self.processor.set_archive_processed_files(status == 's')
        elif choice == "3":
            status = input("Ativar backups? (s/n): ").lower()
            self.processor.set_create_backups(status == 's')
        elif choice == "4":
            return
        else:
            print("Opção inválida.")

# Função principal
def main():
    print("=== Simulador do Sistema de Processamento Automático de Arquivos ===")
    simulator = FileProcessorSimulator()
    
    try:
        simulator.interactive_demo()
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário")
        simulator.stop_simulation()

if __name__ == "__main__":
    main()