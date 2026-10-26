# 🐒 ChimpiCode 1.1.0

Editor desktop com ChimpiAI local via Ollama, execução de Python, compilação C/C++ e exportação de projetos Python para pacotes desktop nativos

## Upgrade desktop

| Sistema | Distribuição |
| --- | --- |
| Windows x64 | ChimpiCode.exe com runtime incluído, Setup EXE, instalador MSI em inglês e pt-BR, ZIP portátil |
| macOS Intel | ChimpiCode.app em ZIP que preserva permissões e links simbólicos |
| macOS Apple Silicon | ChimpiCode.app nativo arm64 em ZIP |

O aplicativo distribuído abre sem instalar Python — Ollama/modelos e as ferramentas de desenvolvimento dos seus projetos são opcionais e instalados separadamente

**Baixar builds:** abra [Actions → Desktop packages](https://github.com/Chimpi-hackintosh/ChimpiCode/actions/workflows/desktop-packages.yml), escolha uma execução concluída e baixe o artefato do seu sistema

Consulte [BUILDING.md](BUILDING.md) para compilar e instalar — a configuração do workflow não comprova que os pacotes foram compilados com sucesso; os resultados de cada execução são a referência

## O que mudou

- Exportação real de projetos Python com PyInstaller em `.app`, `.exe` e `.msi`, respeitando o sistema da compilação
- Distribuição do ChimpiCode para Windows x64 e macOS Intel/Apple Silicon
- Configurações fora da pasta de instalação, preservadas nas atualizações
- Idioma automático com base na interface do sistema, com escolha persistente de pt-BR/inglês
- Salvar, Salvar como, atalhos de teclado e aviso de alterações pendentes
- Atualização dos widgets pela fila da interface; processos e Ollama rodam em threads
- Falhas de compilação deixam de aparecer como sucesso e C/C++ usam `.exe` no Windows
- Swift de linha de comando usa `swiftc` quando instalado; SwiftUI/UIKit exigem um projeto Xcode
- A IA sugere código e aguarda a ação de inserir, preservando o texto atual
- Limpar remove apenas `.chimpicode/work`, com confirmação

## Começar

### Instalar pelo CMD sem WinGet

1. Baixe `from.cmd` em [Releases](https://github.com/Chimpi-hackintosh/ChimpiCode/releases) quando a prévia desktop estiver publicada
2. Abra o CMD na pasta desse arquivo e execute

```cmd
from my computer --install chimpicode --from github.com
```

O lançador procura o instalador Windows x64 da prévia 1.1.0 neste repositório, baixa o Setup, verifica o SHA-256 e abre a instalação normal do Windows

`from` é um comando fornecido pelo ChimpiCode — o Windows não inclui esse comando originalmente

Depois da instalação, abra um novo CMD para usá-lo em qualquer pasta — a desinstalação remove sua entrada do PATH

### Usar o editor

1. Abra uma pasta de projeto e selecione um arquivo ou crie um novo
2. Salve com a extensão correta: `.py`, `.c`, `.cpp`, `.cc`, `.cxx` ou `.swift`
3. Clique em **Compilar e executar** e consulte o console
4. Para um projeto Python, escolha `.app`, `.exe` ou `.msi`, clique em **Exportar** e escolha nome e destino

As extensões guiam a execução; a aplicação não tenta adivinhar a linguagem pelo texto

Python de desenvolvimento é necessário para executar/exportar seus projetos Python; Clang/GCC para C/C++ e Swift toolchain para Swift

Para exportar, instale PyInstaller no ambiente do projeto e selecione o interpretador no editor se necessário

```sh
python -m pip install pyinstaller
```

Exportação `.app` exige macOS; `.exe` e `.msi` exigem Windows — `.exe` é distribuído com sua pasta de dependências e `.msi` também exige WiX

Projetos com arquivos de dados e imports dinâmicos podem precisar de um spec PyInstaller próprio — esta versão exporta entradas Python simples e usa versão 1.0.0 para os instaladores de projetos exportados

## ChimpiAI

Instale Ollama e o modelo que deseja usar, por exemplo

```sh
ollama pull qwen2.5-coder
ollama serve
```

As perguntas são enviadas para `http://localhost:11434/api/generate` — o modelo não acompanha os instaladores

## Rodar a partir das fontes

Recomendado: Python 3.12 com Tkinter

```sh
python -m venv .venv
```

Windows PowerShell

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe chimpicode.py
```

macOS/Linux

```sh
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python chimpicode.py
```

## Limites atuais

O painel Prévia mostra saída do console, sem simular iOS — não há exportação `.ipa`, provisioning ou instalação em iPhone

O aplicativo usa ferramentas nativas do computador, não faz compilação cruzada e não inclui compiladores C/C++, Swift, Ollama ou modelos de IA

Os pacotes não possuem assinatura comercial ou notarização — versões anteriores de Windows/macOS só devem ser consideradas compatíveis depois de teste específico

## Verificação

```sh
python -m unittest discover -s tests -v
```

O workflow compila em Windows/macOS e verifica abertura dos bundles, instalação/atualização/desinstalação Windows e preservação das configurações — consulte os relatórios incluídos em cada artefato

Nas branches `upgrade/**`, publica uma prévia versionada em Releases somente quando os três builds nativos e suas verificações terminam com sucesso

## Licença

MIT — Copyright (c) 2026 ChimpiCode — veja [LICENSE](LICENSE)
