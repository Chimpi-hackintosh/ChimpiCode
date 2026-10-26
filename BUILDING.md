# Build desktop — ChimpiCode 1.1.0

O ChimpiCode mantém Python + CustomTkinter e inclui o runtime do Python no aplicativo distribuído

## Pela interface do GitHub

1. Abra **Actions → Desktop packages**
2. Clique em **Run workflow**, selecione a branch da atualização e confirme **Run workflow**
3. Aguarde os jobs Windows, macOS Intel e macOS Apple Silicon
4. Abra a execução e baixe os arquivos em **Artifacts**

O workflow também executa automaticamente ao enviar commits para `main` ou uma branch `upgrade/**`

Em branches `upgrade/**`, a etapa final publica os pacotes aprovados como uma prévia `v1.1.0-preview.<execução>` em Releases — o comando `from` obtém o instalador dessa prévia sem precisar de WinGet ou login no GitHub

| Artefato | Conteúdo |
| --- | --- |
| Windows-x64 | Setup EXE, MSI em inglês e pt-BR, ZIP portátil com ChimpiCode.exe, hashes e relatórios |
| macOS-Intel | ZIP preservando o bundle ChimpiCode.app para x86_64 |
| macOS-AppleSilicon | ZIP preservando o bundle ChimpiCode.app para arm64 |

O job só disponibiliza o artefato quando a compilação e as verificações da plataforma passam

## Build local

Use Python 3.12 com Tkinter e uma sessão gráfica

```sh
python -m pip install -r requirements-build.txt
python -m unittest discover -s tests -v
```

No macOS, execute com um Python da mesma arquitetura que deseja distribuir

```sh
python scripts/build.py
```

No Windows x64, instale .NET SDK 8 para a ferramenta de build MSI, WiX e NSIS

```powershell
dotnet tool install --global wix --version 4.0.6
wix extension add --global WixToolset.UI.wixext/4.0.6
choco install nsis --yes
python scripts/build.py --installers
```

O WiX está fixado em 4.0.6 para reproduzir este build e não é incluído no aplicativo final

Os pacotes aparecem em `release/` — PyInstaller precisa executar no sistema de destino

## Como instalar

**Windows**: execute `ChimpiCode-1.1.0-x64-Setup.exe` ou o MSI correspondente ao idioma desejado — os dois instalam o mesmo produto, com a mesma identidade de atualização e desinstalação

O Setup seleciona automaticamente pt-BR para a interface de sistema em português e inglês para os demais idiomas — a instalação do MSI permite escolher o atalho opcional na área de trabalho

O pacote inclui `from.cmd` e registra a pasta de instalação no PATH do sistema — abra um novo CMD após instalar

Para a primeira instalação pelo comando, baixe o `from.cmd` da prévia em Releases, abra o CMD na pasta baixada e rode

```cmd
from my computer --install chimpicode --from github.com
```

O lançador é um arquivo CMD independente, com seu código PowerShell legível dentro do próprio arquivo — o código original fica em `scripts/install-windows.ps1` e `scripts/make-launcher.py` o atualiza

Pasta padrão: `Program Files/SnoopyOS Company/ChimpiCode` — configurações editáveis ficam em LocalAppData, preservadas na atualização e desinstalação

O ZIP portátil deve ser extraído inteiro — `ChimpiCode.exe` depende da pasta `lib` e dos recursos que o acompanham

**macOS**: extraia o ZIP e mova `ChimpiCode.app` para Aplicativos — escolha Intel ou Apple Silicon conforme seu Mac

Os pacotes não têm assinatura comercial Authenticode/Developer ID nem notarização — o macOS recebe a assinatura ad hoc do PyInstaller e não há publicação na App Store

## Exportar seus próprios projetos

Salve um arquivo Python, selecione `.app`, `.exe` ou `.msi` e clique em Exportar

- `.app` exige macOS; `.exe` e `.msi` exigem Windows
- Use um ambiente de desenvolvimento Python com PyInstaller instalado e as dependências do seu projeto
- Selecione o executável desse ambiente em **Interpretador Python**, se ele não for detectado
- `.exe` gera uma pasta com o executável e suas dependências; `.msi` gera também um instalador WiX
- A exportação usa a arquitetura do Python escolhido — para MSI nesta versão, use Python x64
- Arquivos de dados, ícones e imports dinâmicos de projetos complexos exigem um spec PyInstaller próprio fora deste exportador inicial

## O que as verificações cobrem

Os testes locais validam idiomas, persistência, falhas reais de processos, timeout, compilação C quando disponível e geração dos componentes MSI

O workflow verifica a abertura do aplicativo empacotado em cada sistema, fora da pasta de fontes

No Windows, verifica instalação de um pacote de versão anterior com o mesmo payload como fixture, atualização pelo Setup EXE, alvo do atalho do menu Iniciar, abertura sem Python no PATH e desinstalação preservando configurações

Isso não equivale a validar todos os recursos do editor, Ollama ou compatibilidade com todas as versões anteriores do macOS/Windows

## Referências

- https://pyinstaller.org/en/stable/usage.html
- https://customtkinter.tomschimansky.com/documentation/packaging/
- https://docs.firegiant.com/wix/tools/wixexe/
- https://nsis.sourceforge.io/Docs/Chapter4.html
