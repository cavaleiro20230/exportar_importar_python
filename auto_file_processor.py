import os
import time
import json
import csv
import xml.dom.minidom
import xml.etree.ElementTree as ET
import shutil
import threading
import schedule
import datetime
from typing import Dict, List, Any, Callable, Union, Optional
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas as pd

class FileImportExport:
    """Classe utilitária para importação e exportação de arquivos em diferentes formatos"""
    
    @staticmethod
    def export_to_csv(data: List[List[str]], file_path: str) -> None:
        """Exporta dados para um arquivo CSV"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(data)
        print(f"Arquivo CSV exportado com sucesso: {file_path}")
    
    @staticmethod
    def import_from_csv(file_path: str) -> List[List[str]]:
        """Importa dados de um arquivo CSV"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                data.append(row)
        return data
    
    @staticmethod
    def export_to_json(data: Dict[str, Any], file_path: str) -> None:
        """Exporta dados para um arquivo JSON"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Arquivo JSON exportado com sucesso: {file_path}")
    
    @staticmethod
    def import_from_json(file_path: str) -> Dict[str, Any]:
        """Importa dados de um arquivo JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def export_to_xml(root_element: str, elements: Dict[str, str], file_path: str) -> None:
        """Exporta dados para um arquivo XML"""
        root = ET.Element(root_element)
        for key, value in elements.items():
            element = ET.SubElement(root, key)
            element.text = value
        
        tree = ET.ElementTree(root)
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        print(f"Arquivo XML exportado com sucesso: {file_path}")
    
    @staticmethod
    def import_from_xml(file_path: str) -> ET.Element:
        """Importa dados de um arquivo XML"""
        tree = ET.parse(file_path)
        return tree.getroot()
    
    @staticmethod
    def export_to_excel(sheet_name: str, headers: List[str], data: List[List[Any]], file_path: str) -> None:
        """Exporta dados para um arquivo Excel"""
        df = pd.DataFrame(data, columns=headers)
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"Arquivo Excel exportado com sucesso: {file_path}")
    
    @staticmethod
    def import_from_excel(file_path: str) -> List[List[Any]]:
        """Importa dados de um arquivo Excel"""
        df = pd.read_excel(file_path)
        return [df.columns.tolist()] + df.values.tolist()
    
    @staticmethod
    def detect_format(file_path: str) -> str:
        """Detecta o formato do arquivo com base na extensão"""
        extension = os.path.splitext(file_path)[1].lower()[1:]
        
        format_mapping = {
            'csv': 'csv',
            'json': 'json',
            'xml': 'xml',
            'xlsx': 'excel',
            'xls': 'excel',
            'pdf': 'pdf',
            'bin': 'bin',
            'pickle': 'pickle',
            'pkl': 'pickle'
        }
        
        return format_mapping.get(extension, 'unknown')


class FileEventHandler(FileSystemEventHandler):
    """Manipulador de eventos para novos arquivos"""
    
    def __init__(self, processor):
        self.processor = processor
    
    def on_created(self, event):
        if not event.is_directory:
            # Pequeno delay para garantir que o arquivo esteja completamente escrito
            time.sleep(0.5)
            print(f"Novo arquivo detectado: {event.src_path}")
            self.processor.process_file(event.src_path)


class AutoFileProcessor:
    """Sistema automatizado para processamento de arquivos"""
    
    def __init__(self, input_directory: str = "./input", 
                 output_directory: str = "./output", 
                 archive_directory: str = "./archive"):
        """Inicializa o processador com diretórios personalizados"""
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.archive_directory = archive_directory
        
        # Configurações
        self.archive_processed_files = True
        self.convert_all_to_json = False
        self.create_backups = True
        
        # Inicializa os processadores de formato
        self.format_processors = {}
        self.init_format_processors()
        
        # Cria os diretórios se não existirem
        self.create_directories()
        
        # Observador para monitoramento de diretórios
        self.observer = None
        self.running = False
    
    def create_directories(self):
        """Cria os diretórios necessários se não existirem"""
        os.makedirs(self.input_directory, exist_ok=True)
        os.makedirs(self.output_directory, exist_ok=True)
        os.makedirs(self.archive_directory, exist_ok=True)
        print("Diretórios criados/verificados com sucesso")
    
    def init_format_processors(self):
        """Inicializa os processadores para cada formato de arquivo"""
        
        # Processador para arquivos CSV
        def process_csv(file_path):
            try:
                print(f"Processando arquivo CSV: {file_path}")
                data = FileImportExport.import_from_csv(file_path)
                
                # Exemplo: Exporta para JSON se a conversão estiver ativada
                if self.convert_all_to_json:
                    json_data = self.convert_csv_to_json(data)
                    output_path = os.path.join(
                        self.output_directory, 
                        f"{os.path.splitext(os.path.basename(file_path))[0]}.json"
                    )
                    FileImportExport.export_to_json(json_data, output_path)
                    print(f"Convertido para JSON: {output_path}")
                
                # Processa os dados conforme necessário
                self.process_csv_data(data)
                
                # Arquiva o arquivo processado
                if self.archive_processed_files:
                    self.archive_file(file_path)
            except Exception as e:
                print(f"Erro ao processar arquivo CSV: {file_path}")
                print(f"Erro: {str(e)}")
        
        # Processador para arquivos JSON
        def process_json(file_path):
            try:
                print(f"Processando arquivo JSON: {file_path}")
                data = FileImportExport.import_from_json(file_path)
                
                # Processa os dados conforme necessário
                self.process_json_data(data)
                
                # Arquiva o arquivo processado
                if self.archive_processed_files:
                    self.archive_file(file_path)
            except Exception as e:
                print(f"Erro ao processar arquivo JSON: {file_path}")
                print(f"Erro: {str(e)}")
        
        # Processador para arquivos XML
        def process_xml(file_path):
            try:
                print(f"Processando arquivo XML: {file_path}")
                data = FileImportExport.import_from_xml(file_path)
                
                # Processa os dados conforme necessário
                self.process_xml_data(data)
                
                # Arquiva o arquivo processado
                if self.archive_processed_files:
                    self.archive_file(file_path)
            except Exception as e:
                print(f"Erro ao processar arquivo XML: {file_path}")
                print(f"Erro: {str(e)}")
        
        # Processador para arquivos Excel
        def process_excel(file_path):
            try:
                print(f"Processando arquivo Excel: {file_path}")
                data = FileImportExport.import_from_excel(file_path)
                
                # Exemplo: Exporta para CSV
                if self.convert_all_to_json:
                    csv_data = data  # Já está no formato adequado
                    output_path = os.path.join(
                        self.output_directory, 
                        f"{os.path.splitext(os.path.basename(file_path))[0]}.csv"
                    )
                    FileImportExport.export_to_csv(csv_data, output_path)
                    print(f"Convertido para CSV: {output_path}")
                
                # Processa os dados conforme necessário
                self.process_excel_data(data)
                
                # Arquiva o arquivo processado
                if self.archive_processed_files:
                    self.archive_file(file_path)
            except Exception as e:
                print(f"Erro ao processar arquivo Excel: {file_path}")
                print(f"Erro: {str(e)}")
        
        # Registra os processadores
        self.format_processors = {
            'csv': process_csv,
            'json': process_json,
            'xml': process_xml,
            'excel': process_excel,
        }
    
    def start_watching(self):
        """Inicia o monitoramento do diretório de entrada"""
        if self.observer is not None:
            print("Monitoramento já está ativo")
            return
        
        self.observer = Observer()
        event_handler = FileEventHandler(self)
        self.observer.schedule(event_handler, self.input_directory, recursive=False)
        self.observer.start()
        self.running = True
        
        print(f"Monitorando diretório de entrada: {self.input_directory}")
    
    def stop_watching(self):
        """Para o monitoramento do diretório"""
        if self.observer is not None:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self.running = False
            print("Monitoramento interrompido")
    
    def process_file(self, file_path: str):
        """Processa um arquivo com base em seu formato"""
        format_type = FileImportExport.detect_format(file_path)
        
        if format_type == 'unknown':
            print(f"Formato desconhecido para o arquivo: {file_path}")
            return
        
        # Cria backup se necessário
        if self.create_backups:
            self.create_backup(file_path)
        
        # Obtém o processador para o formato e executa
        processor = self.format_processors.get(format_type)
        if processor:
            processor(file_path)
        else:
            print(f"Nenhum processador definido para o formato: {format_type}")
    
    def create_backup(self, file_path: str):
        """Cria um backup do arquivo antes de processá-lo"""
        try:
            backup_dir = os.path.join(self.output_directory, "backups")
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = str(int(time.time()))
            filename = os.path.basename(file_path)
            backup_path = os.path.join(backup_dir, f"{timestamp}_{filename}")
            
            shutil.copy2(file_path, backup_path)
            print(f"Backup criado: {backup_path}")
        except Exception as e:
            print(f"Erro ao criar backup: {str(e)}")
    
    def archive_file(self, file_path: str):
        """Move um arquivo processado para o diretório de arquivamento"""
        try:
            filename = os.path.basename(file_path)
            target_path = os.path.join(self.archive_directory, filename)
            shutil.move(file_path, target_path)
            print(f"Arquivo movido para: {target_path}")
        except Exception as e:
            print(f"Erro ao arquivar arquivo: {str(e)}")
    
    def schedule_exports(self):
        """Configura exportações automáticas programadas"""
        # Exporta dados para CSV a cada hora
        schedule.every(60).minutes.do(self.scheduled_export)
        
        # Inicia uma thread para executar as tarefas agendadas
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True
        scheduler_thread.start()
        
        print("Exportações programadas configuradas")
    
    def scheduled_export(self):
        """Realiza uma exportação programada"""
        try:
            print("Executando exportação programada...")
            
            # Gera dados de exemplo (substitua por seus dados reais)
            data = self.generate_sample_data()
            
            # Exporta para CSV
            timestamp = str(int(time.time()))
            filename = f"export_{timestamp}.csv"
            output_path = os.path.join(self.output_directory, filename)
            FileImportExport.export_to_csv(data, output_path)
            
            print(f"Exportação programada concluída: {output_path}")
        except Exception as e:
            print(f"Erro na exportação programada: {str(e)}")
    
    def manual_export(self, format_type: str):
        """Realiza uma exportação manual no formato especificado"""
        try:
            print(f"Realizando exportação manual no formato: {format_type}")
            
            # Gera dados de exemplo (substitua por seus dados reais)
            csv_data = self.generate_sample_data()
            timestamp = str(int(time.time()))
            output_path = os.path.join(self.output_directory, f"manual_export_{timestamp}.{format_type}")
            
            if format_type == 'csv':
                FileImportExport.export_to_csv(csv_data, output_path)
            elif format_type == 'json':
                json_data = self.convert_csv_to_json(csv_data)
                FileImportExport.export_to_json(json_data, output_path)
            elif format_type == 'xml':
                xml_elements = {
                    'timestamp': timestamp,
                    'count': str(len(csv_data) - 1)
                }
                FileImportExport.export_to_xml('export', xml_elements, output_path)
            elif format_type == 'excel':
                headers = csv_data[0]
                data = csv_data[1:]
                FileImportExport.export_to_excel('Exportação', headers, data, output_path)
            else:
                print(f"Formato não suportado para exportação manual: {format_type}")
                return
            
            print(f"Exportação manual concluída: {output_path}")
        except Exception as e:
            print(f"Erro na exportação manual: {str(e)}")
    
    # Métodos auxiliares para processamento de dados
    
    def process_csv_data(self, data: List[List[str]]):
        """Processa dados CSV"""
        print(f"Processando {len(data)} linhas de dados CSV")
        # Implemente o processamento específico para dados CSV
    
    def process_json_data(self, data: Dict[str, Any]):
        """Processa dados JSON"""
        print(f"Processando dados JSON: {len(data)} campos")
        # Implemente o processamento específico para dados JSON
    
    def process_xml_data(self, data: ET.Element):
        """Processa dados XML"""
        print("Processando documento XML")
        # Implemente o processamento específico para dados XML
    
    def process_excel_data(self, data: List[List[Any]]):
        """Processa dados Excel"""
        print(f"Processando {len(data)} linhas de dados Excel")
        # Implemente o processamento específico para dados Excel
    
    def convert_csv_to_json(self, csv_data: List[List[str]]) -> Dict[str, Any]:
        """Converte dados CSV para formato JSON"""
        result = {}
        
        if not csv_data:
            return result
        
        headers = csv_data[0]
        rows = []
        
        for i in range(1, len(csv_data)):
            row = csv_data[i]
            row_dict = {}
            
            for j in range(min(len(headers), len(row))):
                row_dict[headers[j]] = row[j]
            
            rows.append(row_dict)
        
        result['data'] = rows
        return result
    
    def generate_sample_data(self) -> List[List[str]]:
        """Gera dados de exemplo para exportações"""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = [
            ["ID", "Nome", "Email", "Data"],
            ["1", "João Silva", "joao@exemplo.com", current_time],
            ["2", "Maria Santos", "maria@exemplo.com", current_time]
        ]
        return data
    
    def add_custom_processor(self, format_type: str, processor: Callable[[str], None]):
        """Adiciona um processador personalizado para um formato específico"""
        self.format_processors[format_type] = processor
        print(f"Processador personalizado adicionado para o formato: {format_type}")
    
    def set_convert_all_to_json(self, convert: bool):
        """Configura o processador para converter todos os arquivos para JSON"""
        self.convert_all_to_json = convert
        print(f"Conversão automática para JSON: {'ativada' if convert else 'desativada'}")
    
    def set_archive_processed_files(self, archive: bool):
        """Configura se os arquivos processados devem ser arquivados"""
        self.archive_processed_files = archive
        print(f"Arquivamento de arquivos processados: {'ativado' if archive else 'desativado'}")
    
    def set_create_backups(self, create_backups: bool):
        """Configura se devem ser criados backups antes do processamento"""
        self.create_backups = create_backups
        print(f"Criação de backups: {'ativada' if create_backups else 'desativada'}")
    
    def start_command_line_interface(self):
        """Inicia uma interface de linha de comando simples"""
        def cli_thread():
            print("\n=== Sistema de Processamento Automático de Arquivos ===")
            print("Digite 'ajuda' para ver os comandos disponíveis")
            
            while self.running:
                command = input("\nComando> ").strip()
                
                if command == "ajuda":
                    print("Comandos disponíveis:")
                    print("  iniciar - Inicia o monitoramento de diretórios")
                    print("  parar - Para o monitoramento e as tarefas programadas")
                    print("  converter json [on/off] - Ativa/desativa conversão para JSON")
                    print("  arquivar [on/off] - Ativa/desativa arquivamento de arquivos")
                    print("  backup [on/off] - Ativa/desativa criação de backups")
                    print("  processar [caminho] - Processa um arquivo específico")
                    print("  exportar [formato] - Realiza uma exportação manual")
                    print("  status - Exibe o status atual do sistema")
                    print("  sair - Encerra o programa")
                
                elif command == "iniciar":
                    self.start_watching()
                    self.schedule_exports()
                
                elif command == "parar":
                    self.stop_watching()
                
                elif command == "converter json on":
                    self.set_convert_all_to_json(True)
                
                elif command == "converter json off":
                    self.set_convert_all_to_json(False)
                
                elif command == "arquivar on":
                    self.set_archive_processed_files(True)
                
                elif command == "arquivar off":
                    self.set_archive_processed_files(False)
                
                elif command == "backup on":
                    self.set_create_backups(True)
                
                elif command == "backup off":
                    self.set_create_backups(False)
                
                elif command == "status":
                    print("Status do sistema:")
                    print(f"  Diretório de entrada: {self.input_directory}")
                    print(f"  Diretório de saída: {self.output_directory}")
                    print(f"  Diretório de arquivo: {self.archive_directory}")
                    print(f"  Conversão para JSON: {'ativada' if self.convert_all_to_json else 'desativada'}")
                    print(f"  Arquivamento: {'ativado' if self.archive_processed_files else 'desativado'}")
                    print(f"  Backups: {'ativados' if self.create_backups else 'desativados'}")
                
                elif command == "sair":
                    print("Encerrando o programa...")
                    self.running = False
                    self.stop_watching()
                    break
                
                elif command.startswith("processar "):
                    file_path = command[10:].strip()
                    print(f"Processando arquivo: {file_path}")
                    self.process_file(file_path)
                
                elif command.startswith("exportar "):
                    format_type = command[9:].strip()
                    self.manual_export(format_type)
                
                else:
                    print("Comando desconhecido. Digite 'ajuda' para ver os comandos disponíveis.")
        
        self.running = True
        thread = threading.Thread(target=cli_thread)
        thread.daemon = True
        thread.start()
        
        return thread

# Função principal para demonstração
def main():
    processor = AutoFileProcessor()
    cli_thread = processor.start_command_line_interface()
    
    try:
        # Mantém o programa em execução até que o usuário saia
        while processor.running:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário")
        processor.stop_watching()

if __name__ == "__main__":
    main()