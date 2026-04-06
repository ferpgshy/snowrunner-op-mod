# SnowRunner OP Mod

Mod completo para SnowRunner que transforma todos os veículos (base + mods do mod.io) em máquinas OP.

## O que inclui

| Categoria | Detalhes |
|-----------|----------|
| **Motores** | 20 opções — ECO 80K até INFINITO 5M Nm |
| **Câmbios** | 5 níveis, 12 marchas (progressão geométrica), AWD grátis, sem freio motor |
| **Suspensões** | 13 níveis **ativas** (sobe/desce em tempo real), STOCK+ até DEUS |
| **Guinchos** | 5 níveis — 30m até 100m, força 3x até 20x |
| **Pneus** | DEUS por modelo — grip 15.0, indestrutíveis, 2.5x largura |
| **Trucks** | DiffLock sempre ativo, Snorkel alto (submersível), centro de massa rebaixado |
| **Rodas** | 3 escalas extras por veículo (1.3x, 1.45x, 1.6x) |

## Scripts

| Script | Função |
|--------|--------|
| `build_winrar_v6.py` | Aplica os mods no `initial.pak` (veículos do jogo base) |
| `mod_modio.py` | Aplica os mods em todos os paks do mod.io (veículos de mods baixados) |
| `build_conteudos.py` | Monta a pasta `CONTEUDOS/` pronta para compartilhar com amigos |
| `INSTALAR.bat` | Instalador automático — detecta pasta do jogo e copia tudo |

## Requisitos

- [WinRAR](https://www.win-rar.com/) instalado em `C:\Program Files\WinRAR\`
- Python 3.10+
- SnowRunner via Steam

## Como usar

### Mod base (initial.pak)

```
python build_winrar_v6.py
```

Restaura o pak original do backup, aplica todas as modificações e injeta com WinRAR.

### Mods do mod.io

```
python mod_modio.py
```

Faz backup automático dos paks originais, aplica as modificações OP usando WinRAR (preserva estrutura zip).

### Compartilhar com amigos

```
python build_conteudos.py
```

Gera a pasta `CONTEUDOS/` com:
- `initial.pak` moddado
- `.modio/` com todos os mods moddados
- `INSTALAR.bat` (instalador automático)
- `LEIA-ME.txt` (instruções)

## Caminhos importantes

| O quê | Caminho |
|-------|---------|
| Pak do jogo | `C:\Program Files (x86)\Steam\steamapps\common\SnowRunner\preload\paks\client\initial.pak` |
| Backup | `C:\Users\<user>\Documents\initial.pak - BACKUP` |
| Mods do mod.io | `C:\Users\<user>\Documents\My Games\SnowRunner\base\Mods\.modio\mods\` |
| Backup dos mods | `C:\Users\<user>\Downloads\_modio_backup\` |

## Notas

- **Feche o SnowRunner** antes de rodar qualquer script
- Se o mod.io atualizar um mod, rode `mod_modio.py` de novo para re-aplicar
- Os backups são criados automaticamente na primeira execução
- O `INSTALAR.bat` detecta a pasta do jogo em C:, D: ou E: automaticamente
