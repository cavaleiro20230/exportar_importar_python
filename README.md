# exportar_importar_python
# Sistema Automatizado de Importação e Exportação de Arquivos simulador local para demonstrar seu funcionamento.




Thought for 5 seconds# Sistema Automatizado de Importação e Exportação de Arquivos em Python

Vou criar uma versão em Python do sistema de processamento automático de arquivos, seguido de um simulador local para demonstrar seu funcionamento.

```python project="AutoFileProcessor" file="auto_file_processor.py"
...
```

Agora, vou criar um simulador local que demonstra o funcionamento do sistema:

```python project="FileProcessorSimulator" file="file_processor_simulator.py"
...
```

## Como Usar o Sistema

### 1. Instalação das Dependências

Antes de executar o código, você precisa instalar as bibliotecas necessárias:

```shellscript
pip install watchdog pandas openpyxl schedule
```

### 2. Executando o Sistema

Você pode usar o sistema de duas maneiras:

#### A. Diretamente como Processador de Arquivos

```python
from auto_file_processor import AutoFileProcessor

# Criar o processador com diretórios personalizados
processor = AutoFileProcessor(
    input_directory="./pasta_entrada", 
    output_directory="./pasta_saida", 
    archive_directory="./pasta_arquivo"
)

# Iniciar o monitoramento e as exportações programadas
processor.start_watching()
processor.schedule_exports()

# Iniciar a interface de linha de comando
processor.start_command_line_interface()
```

#### B. Usando o Simulador

O simulador oferece uma interface interativa para demonstrar o funcionamento do sistema:

```python
python file_processor_simulator.py
```

### 3. Funcionalidades do Simulador

O simulador permite:

- Criar arquivos de exemplo em diferentes formatos (CSV, JSON, XML, Excel)
- Observar como o sistema processa automaticamente esses arquivos
- Configurar o comportamento do processador
- Iniciar uma simulação automática que cria arquivos periodicamente


### 4. Comandos Disponíveis

Tanto o processador quanto o simulador oferecem uma interface de linha de comando com os seguintes comandos:

- `iniciar` - Inicia o monitoramento de diretórios
- `parar` - Para o monitoramento e as tarefas programadas
- `converter json [on/off]` - Ativa/desativa conversão automática para JSON
- `arquivar [on/off]` - Ativa/desativa arquivamento de arquivos processados
- `backup [on/off]` - Ativa/desativa criação de backups
- `processar [caminho]` - Processa um arquivo específico manualmente
- `exportar [formato]` - Realiza uma exportação manual (csv, json, xml, excel)
- `status` - Exibe o status atual do sistema
- `sair` - Encerra o programa


Este sistema em Python oferece as mesmas funcionalidades da versão Java, mas com a sintaxe e bibliotecas próprias do Python, além de um simulador interativo para facilitar os testes e demonstrações.
