# -*- coding: utf-8 -*-
"""Monta a pasta CONTEUDOS com tudo pronto pra compartilhar."""
import os
import shutil
import sys

WORKSPACE = r"c:\Users\ferna\Downloads\initial.pak modded"
CONTEUDOS = os.path.join(WORKSPACE, "CONTEUDOS")

GAME_PAK = r"C:\Program Files (x86)\Steam\steamapps\common\SnowRunner\preload\paks\client\initial.pak"
MODIO_SRC = r"C:\Users\ferna\Documents\My Games\SnowRunner\base\Mods\.modio\mods"

def main():
    print("=" * 60)
    print("  MONTANDO PASTA CONTEUDOS")
    print("=" * 60)

    # Limpar pasta anterior se existir
    if os.path.exists(CONTEUDOS):
        print("\n[1] Limpando pasta anterior...")
        shutil.rmtree(CONTEUDOS)
    
    os.makedirs(CONTEUDOS)

    # 1. Copiar initial.pak
    pak_dest = os.path.join(CONTEUDOS, "initial.pak")
    print(f"\n[2] Copiando initial.pak ({os.path.getsize(GAME_PAK)/1024/1024:.1f} MB)...")
    shutil.copy2(GAME_PAK, pak_dest)
    print("    OK")

    # 1b. Copiar INSTALAR.bat e LEIA-ME.txt
    for fname in ["INSTALAR.bat"]:
        src = os.path.join(WORKSPACE, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(CONTEUDOS, fname))
            print(f"    {fname} copiado")

    # 2. Copiar .modio/mods/
    modio_dest = os.path.join(CONTEUDOS, ".modio", "mods")
    os.makedirs(modio_dest, exist_ok=True)

    mod_folders = sorted(os.listdir(MODIO_SRC))
    total = len(mod_folders)
    copied_size = 0

    print(f"\n[3] Copiando {total} mods...")
    for i, mod_id in enumerate(mod_folders, 1):
        src = os.path.join(MODIO_SRC, mod_id)
        if not os.path.isdir(src):
            continue
        dst = os.path.join(modio_dest, mod_id)
        
        # Listar arquivos do mod pra mostrar progresso
        files = os.listdir(src)
        pak_names = [f for f in files if f.endswith(".pak") and f != "pc.pak"]
        pak_name = pak_names[0] if pak_names else mod_id
        
        mod_size = sum(os.path.getsize(os.path.join(src, f)) for f in files)
        sys.stdout.write(f"  [{i}/{total}] {pak_name} ({mod_size/1024/1024:.1f} MB)...")
        sys.stdout.flush()
        
        shutil.copytree(src, dst)
        copied_size += mod_size
        print(" OK")

    # 3. Criar README
    readme = os.path.join(CONTEUDOS, "LEIA-ME.txt")
    with open(readme, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("  SNOWRUNNER OP MOD - COMO INSTALAR\n")
        f.write("=" * 60 + "\n\n")
        f.write("PASSO 1 - initial.pak:\n")
        f.write("  Copie o arquivo 'initial.pak' para:\n")
        f.write("  C:\\Program Files (x86)\\Steam\\steamapps\\common\\SnowRunner\\preload\\paks\\client\\\n")
        f.write("  (substitua o que ja tem la)\n\n")
        f.write("PASSO 2 - Mods (.modio):\n")
        f.write("  Copie a PASTA '.modio' para:\n")
        f.write("  C:\\Users\\SEU_USUARIO\\Documents\\My Games\\SnowRunner\\base\\Mods\\\n")
        f.write("  (substitua/mescle com a que ja tem la)\n\n")
        f.write("  IMPORTANTE: Voce precisa estar inscrito nos mesmos mods no mod.io!\n")
        f.write("  Se nao estiver, os mods nao vao aparecer no jogo.\n\n")
        f.write("=" * 60 + "\n")
        f.write("  O QUE CADA MOD FAZ\n")
        f.write("=" * 60 + "\n\n")
        f.write("MOTORES: 20 opcoes (ECO 80K ate INFINITO 5M)\n")
        f.write("CAMBIOS: 5 opcoes, 12 marchas, AWD gratis, sem freio motor\n")
        f.write("SUSPENSOES: 13 opcoes ATIVAS (sobe/desce), de STOCK+ ate DEUS\n")
        f.write("GUINCHOS: 5 opcoes (30m ate 100m, forca 3x ate 20x)\n")
        f.write("PNEUS: DEUS em cada modelo (grip 15, indestrutivel, 2.5x largura)\n")
        f.write("TRUCKS: DiffLock sempre ativo, Snorkel alto, centro de massa baixo\n")
        f.write("RODAS: 3 escalas extras por veiculo (1.3x, 1.45x, 1.6x)\n\n")
        f.write("Divirta-se!\n")

    total_size = os.path.getsize(pak_dest) + copied_size
    print(f"\n" + "=" * 60)
    print(f"  PRONTO!")
    print(f"  Pasta: {CONTEUDOS}")
    print(f"  Tamanho total: {total_size/1024/1024:.0f} MB")
    print(f"  initial.pak: {os.path.getsize(pak_dest)/1024/1024:.1f} MB")
    print(f"  .modio: {copied_size/1024/1024:.0f} MB ({total} mods)")
    print(f"=" * 60)

if __name__ == "__main__":
    main()
