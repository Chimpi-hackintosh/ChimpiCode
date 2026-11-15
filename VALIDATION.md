# Validação desta entrega — 26/10/2026

## Concluído neste ambiente

- 9 testes automatizados passaram
- Compilação e execução de um programa C real, com nome de arquivo contendo espaços
- Execução Python com erro e timeout retornam falha
- Idiomas pt-BR/inglês: mesmas chaves e parâmetros de tradução
- Configurações existentes preservadas ao carregar e salvar
- Geração XML MSI cobre arquivos aninhados, escapa caminhos e rejeita fontes `.py`/`.pyw` no staging
- Importação do runtime do aplicativo a partir das fontes
- Abertura da interface em uma sessão gráfica virtual Linux
- Interação com a interface: salvar arquivo, executar Python, receber o resultado pela fila e mostrar sucesso em português
- Empacotamento de verificação no Linux com PyInstaller e ausência de fontes `.py`/`.pyw` na árvore gerada

O empacotamento Linux foi um teste interno do spec e não é um dos produtos solicitados nem acompanha o ZIP

## Pendente de execução nativa

- Compilar e abrir `ChimpiCode.app` em macOS Intel e Apple Silicon
- Compilar e abrir `ChimpiCode.exe` em Windows x64
- Gerar e testar os instaladores Setup EXE/MSI, incluindo atualização e desinstalação

O workflow `Desktop packages` e o script de ciclo de instalação foram implementados para essas verificações — eles ainda não foram executados nesta entrega

Este ZIP contém o projeto atualizado e os arquivos de build, sem binários Windows/macOS pré-compilados

Integração real com Ollama e compatibilidade com outras versões dos sistemas também não foram testadas
