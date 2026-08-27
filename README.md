# Auto Search

Auto Search é uma aplicação desktop em Python para automatizar ações repetitivas no computador, como abrir navegadores, acessar URLs, realizar buscas, clicar em posições específicas e usar pontos personalizados de clique.

## Funcionalidades

- Abrir navegador
- Acessar URLs
- Digitar texto de busca
- Executar ações repetidas
- Clicar em coordenadas personalizadas
- Escolher entre clique padrão, clique desativado e preset de canto
- Usar múltiplos cliques em posições diferentes em uma mesma execução
- Usar presets de clique para cantos e áreas frequentes
- Salvar configurações em arquivo JSON

## Estrutura do projeto

```text
.
├── app/
│   ├── __init__.py
│   ├── automation_engine.py
│   ├── config_manager.py
│   └── ui.py
├── assets/
├── autoBing.py
├── dados.json
├── README.md
└── scripts/
```

## Requisitos

- Python 3.9+
- Bibliotecas:
  - pyautogui
  - darkdetect (opcional)

Instale as dependências:

```bash
pip install pyautogui darkdetect
```

## Como executar

```bash
python autoBing.py
```

## Exemplo de ações extras

No campo de ações extras, você pode usar comandos como:

```text
url: https://example.com
pesquisar: python
esperar: 2
click: 100,200
clicks: 100,200; 500,300; 900,500
preset: canto-superior-esquerdo
default_click: off
key: enter
```

### Comportamento do clique padrão

- Padrão: executa o clique definido em X e Y
- Off: desativa o clique final padrão
- Preset: usa um ponto salvo da lista de presets

Para usar a opção visual da interface, escolha a opção na seção “Clique padrão” e, se necessário, selecione um preset em “Preset do clique padrão”.

## Observações

- A automação depende do estado da tela e do sistema operacional.
- Use com cuidado em ambientes onde o mouse e teclado são controlados automaticamente.
- Em alguns sistemas, pode ser necessário conceder permissões para automação.
- Para cancelar automação basta apeanas colocar o mouse no canto superior esquerdo até escutar o som de cancelamento do fluxo.
