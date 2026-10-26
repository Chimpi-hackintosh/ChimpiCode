# 🐒 ChimpiCode

**ChimpiAI Edition · v1.0.0**

Editor desktop experimental em Python com assistência de IA local via Ollama, execução de Python e compilação de programas C/C++ pelo compilador instalado no computador

O objetivo do projeto é explorar um ambiente de desenvolvimento alternativo inspirado no Xcode, com o ChimpiAI substituindo o SnoopyAI e um painel visual chamado ChimpiPhone

> Estado desta versão: o ChimpiPhone mostra saída de console dentro de uma moldura de telefone; Swift está simulado; o botão de exportação cria apenas uma estrutura básica de diretórios `.app` e não produz um aplicativo instalável ou um arquivo `.ipa`

## Recursos implementados

| Recurso | Comportamento no código atual |
| --- | --- |
| Editor | Abre arquivos de uma pasta e permite editar texto em memória |
| ChimpiAI | Envia perguntas para `http://localhost:11434/api/generate` com o modelo informado na interface |
| Python | Executa o texto do editor usando `python3` ou `python` no Windows |
| C | Compila usando `clang` ou, como alternativa, `gcc`, depois tenta executar o resultado |
| C++ | Compila usando `clang++` ou `g++`, com `-std=c++20`, depois tenta executar o resultado |
| Swift | Mostra uma mensagem, sem invocar o compilador Swift |
| ChimpiPhone | Mostra até os primeiros 3.000 caracteres da saída no painel Preview |
| Exportação | Cria `ChimpiApp.app/Contents/MacOS`, copia um arquivo-fonte Python ou C++ disponível e grava um `Info.plist` mínimo |
| Clean | Remove arquivos e pastas cujo nome começa com `chimpi_build` ou `ChimpiApp` dentro da pasta aberta |

## Requisitos

- Python 3 com suporte a Tkinter e uma sessão gráfica
- Dependências Python de `requirements.txt`: `customtkinter` e `requests`
- Ollama com um modelo instalado, para usar o ChimpiAI
- Clang/GCC para C e Clang++/G++ para C++

O compilador, o Ollama e seus modelos são instalados separadamente; o `requirements.txt` contém apenas as dependências Python

## Instalação e execução

Baixe ou clone este repositório e abra um terminal dentro da pasta do projeto

### Windows — PowerShell

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe chimpicode.py
```

### macOS / Linux

```bash
python3 -m venv venv
venv/bin/python -m pip install -r requirements.txt
venv/bin/python chimpicode.py
```

Se o Python não incluir Tkinter, instale uma distribuição de Python com Tk ou o pacote de Tkinter adequado ao seu sistema

## Configurar o ChimpiAI

Com o Ollama instalado, baixe o modelo sugerido pela interface

```bash
ollama pull qwen2.5-coder
```

Se o servidor local ainda não estiver rodando, inicie-o em outro terminal

```bash
ollama serve
```

No ChimpiCode, confira o nome do modelo no campo superior, escreva uma pergunta e clique em **Perguntar ao ChimpiAI**

A classe `ChimpiAI` usa `llama3.1` como valor inicial interno, mas a interface preenche `qwen2.5-coder` e envia o modelo do campo quando você faz uma pergunta

Quando a resposta contém um bloco entre três crases, o primeiro bloco pode substituir o texto atual do editor

## Usar o editor

1. Clique em **Abrir Pasta** e escolha uma pasta de projeto dedicada
2. Clique em um arquivo da lista ou em **Novo Arquivo**
3. Edite o texto na aba **Code**
4. Clique em **Build & Run** e acompanhe a saída no console e na aba **Preview**
5. Use **Clean** apenas quando quiser remover os arquivos gerados que usam os prefixos descritos na tabela

O botão **Novo Arquivo** inicializa o editor em memória; não abre uma janela para salvar com nome próprio

**Build & Run** grava o texto em `chimpi_build.py`, `chimpi_build.c`, `chimpi_build.cpp` ou `chimpi_build.swift`, dentro da pasta escolhida

## Limitações desta versão

- A extensão é escolhida por heurística: `iostream` seleciona C++, `#include` seleciona C, `import SwiftUI` ou `UIKit` selecionam Swift, e os demais textos são tratados como Python
- Os arquivos `.cc`, `.cxx`, `.h`, `.hpp`, `.m`, `.mm` e `.plist` podem aparecer na lista, mas isso não significa que tenham fluxo de compilação próprio
- Python tem limite de execução de 10 segundos; os executáveis C/C++ têm limite de 5 segundos; a etapa de compilação C/C++ não define timeout
- O console pode mostrar `Build OK` mesmo quando a saída anterior contém erro; consulte a saída completa
- O código atualiza alguns widgets a partir de threads de trabalho; a interface ainda precisa de validação de estabilidade
- O comando Python é procurado pelo nome no sistema, não pelo caminho do interpretador que abriu a interface
- A seleção de iPhone/iPad altera o texto do preview; não inicializa um simulador iOS
- Swift não é compilado nem executado, inclusive no macOS
- A exportação não compila, não define permissão de execução, não assina e não empacota um aplicativo funcional
- Não há geração de `.ipa`, assinatura iOS, provisioning ou instalação em iPhone nesta versão
- O fluxo C/C++ ainda precisa ser validado no Windows, inclusive a criação e execução de arquivos `.exe`

## Estrutura

```text
ChimpiCode/
├── chimpicode.py
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

`chimpicode.py` preserva integralmente o conteúdo do arquivo original `ChimpiCode.py` enviado pelo autor; apenas o nome foi padronizado para a estrutura do repositório

## Validação antes da publicação

- Sintaxe Python verificada sem executar o aplicativo
- Conteúdo de `chimpicode.py` comparado byte a byte com o original enviado
- Interface gráfica, integração Ollama, compilação de projetos e exportação ainda não foram testadas neste ambiente

## Licença

MIT — Copyright (c) 2026 ChimpiCode

Consulte [LICENSE](LICENSE)
