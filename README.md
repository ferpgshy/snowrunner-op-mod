# SnowRunner OP Mod

Mod OP para SnowRunner que modifica **todos os veículos** do jogo base + 48 mods do mod.io.

## Como instalar

1. Baixe o **CONTEUDOS.zip** na aba [Releases](https://github.com/ferpgshy/snowrunner-op-mod/releases/latest) (v6.2 ou mais recente)
2. Extraia a pasta
3. Execute **INSTALAR.bat** como administrador
4. Precisa do [WinRAR](https://www.win-rar.com/download.html) instalado

## O que o mod faz

| Recurso | Detalhes |
|---------|----------|
| Motores | 7 motores OP (700hp a 3000hp) |
| Câmbios | 4 câmbios de 8 marchas (45, 49, 52, 56 km/h) |
| Suspensões | 13 níveis (STOCK+ até DEUS) |
| Pneus | Pneu DEUS (grip 15.0 em todos os terrenos) |
| Guincho | 100m de alcance, 20x força |
| Diferencial | Bloqueio sempre ativo |
| Snorkel | Submersível (Y=10.0) |
| AWD | Sem custo de combustível |

## Requisitos

- [WinRAR](https://www.win-rar.com/download.html) instalado
- SnowRunner via Steam
- Mods do mod.io já baixados (se quiser os mods modificados também)

## Estrutura

```
CONTEUDOS/
├── initial.pak          # Pak do jogo base modificado
├── INSTALAR.bat         # Instalador automático
├── LEIA-ME.txt          # Instruções
└── modio_patch/         # XMLs modificados para 48 mods do modio
    ├── 1096632/         # Cada pasta = um mod
    ├── 1097827/
    └── ...
```

O instalador:
1. Substitui o `initial.pak` na pasta do jogo
2. Injeta os XMLs modificados nos `.pak` dos mods do mod.io (sem apagar nada)
- **O instalador NAO faz backup.** Ele sobrescreve o `initial.pak` e altera os `.pak` dos mods no lugar. Para reverter: *Verificar integridade dos arquivos* na Steam restaura o `initial.pak`; os mods voltam ao original desinscrevendo e reinscrevendo no mod.io.
- O `INSTALAR.bat` detecta a pasta do jogo automaticamente nos drives C: a G:, nos layouts `Program Files (x86)\Steam`, `SteamLibrary` e `Steam`. Se nao achar, pede o caminho da pasta `client`
