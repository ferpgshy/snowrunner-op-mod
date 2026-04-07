# -*- coding: utf-8 -*-
"""
SnowRunner OP Mod v6
Fixes + new features:
1. Gearbox: ReverseGear AngVel corrigido (1.5 como original) - fix do bug de nao andar pra frente
2. Pneus corrente supremos: 1 pneu corrente OP por arquivo (grip absurdo em tudo)
3. DiffLockType="Always" em todos os trucks (bloq diferencial sempre ativo)
4. Snorkel OP: Y muito alto em todos os trucks (atravessa agua profunda)
5. AWDConsumptionModifier="0.0" nos cambios OP (AWD sem custo)
"""
import zipfile
import os
import re
import sys
import shutil
import subprocess
from collections import defaultdict

BACKUP_PAK = r"C:\Users\ferna\Documents\initial.pak - BACKUP"
GAME_PAK   = r"C:\Program Files (x86)\Steam\steamapps\common\SnowRunner\preload\paks\client\initial.pak"
WINRAR     = r"C:\Program Files\WinRAR\WinRAR.exe"
TEMP_DIR   = r"c:\Users\ferna\Downloads\_op_mod_temp"

LEVELS = [
    ("op1", "FURIOSO"),
    ("op2", "DEVASTADOR"),
    ("op3", "APOCALIPSE"),
    ("op4", "TITA"),
    ("op5", "DEUS"),
]

# 20 motores com personalidades diferentes
ENGINE_STATS = [
    {"id": "i6t",       "Torque": "500000",    "Fuel": "1.0", "Damage": "60000", "Resp": "0.18",
     "Tag": "I6T",      "Name": "I6 Diesel Turbo 700hp",       "Desc": "6 cilindros em linha, turbo diesel. 700 cavalos. Duravel e economico."},
    {"id": "i6bt",      "Torque": "600000",    "Fuel": "1.2", "Damage": "65000", "Resp": "0.20",
     "Tag": "I6BT",     "Name": "I6 Diesel Biturbo 800hp",     "Desc": "6 cilindros em linha, biturbo diesel. 800 cavalos. Resposta rapida."},
    {"id": "v8t",       "Torque": "700000",    "Fuel": "1.5", "Damage": "70000", "Resp": "0.22",
     "Tag": "V8T",      "Name": "V8 Diesel Turbo 900hp",       "Desc": "V8 turbo diesel. 900 cavalos. Torque alto, construcao solida."},
    {"id": "v8bt",      "Torque": "800000",    "Fuel": "1.0", "Damage": "75000", "Resp": "0.20",
     "Tag": "V8BT",     "Name": "V8 Diesel Biturbo 1000hp",    "Desc": "V8 biturbo diesel. 1000 cavalos. Potencia bruta, baixo consumo."},
    {"id": "v12t",      "Torque": "1200000",   "Fuel": "0.8", "Damage": "85000", "Resp": "0.18",
     "Tag": "V12T",     "Name": "V12 Diesel Turbo 1500hp",     "Desc": "V12 turbo diesel. 1500 cavalos. Forca extrema, consumo controlado."},
    {"id": "v16t",      "Torque": "1600000",   "Fuel": "0.5", "Damage": "90000", "Resp": "0.15",
     "Tag": "V16T",     "Name": "V16 Diesel Turbo 2000hp",     "Desc": "V16 turbo diesel. 2000 cavalos. Industrial, quase indestrutivel."},
    {"id": "v20bt",     "Torque": "2500000",   "Fuel": "0.3", "Damage": "99999", "Resp": "0.12",
     "Tag": "V20BT",    "Name": "V20 Diesel Biturbo 3000hp",   "Desc": "V20 biturbo diesel. 3000 cavalos. O mais potente. Indestrutivel."},
]
GB_STATS = [
    {"id": "8a", "Gears": 8, "MaxVel": 25, "Damage": "99999", "Tag": "8A",
     "Name": "8 Marchas 45km/h", "Desc": "~45 km/h. Forca bruta para lama, neve e carga pesada."},
    {"id": "8b", "Gears": 8, "MaxVel": 27, "Damage": "99999", "Tag": "8B",
     "Name": "8 Marchas 49km/h", "Desc": "~49 km/h. Equilibrado para trilha e estrada."},
    {"id": "8c", "Gears": 8, "MaxVel": 29, "Damage": "99999", "Tag": "8C",
     "Name": "8 Marchas 52km/h", "Desc": "~52 km/h. Rapido em estrada e terreno misto."},
    {"id": "8d", "Gears": 8, "MaxVel": 31, "Damage": "99999", "Tag": "8D",
     "Name": "8 Marchas 56km/h", "Desc": "~56 km/h. Velocidade maxima, feito pra estrada."},
]
SUSP_STATS = [
    {"H": "0.06", "S": "0.06", "D": "0.28", "Damage": "5000",  "Tag": "STOCK_PLUS",  "Name": "Suspensao STOCK+",         "Desc": "Lift: 1.5pol. Para rodas originais (33-51pol). Firme e estavel."},
    {"H": "0.09", "S": "0.06", "D": "0.32", "Damage": "8000",  "Tag": "BAIXA_1",     "Name": "Suspensao BAIXA 1",        "Desc": "Lift: 2.5pol. Para rodas de 35-56pol (1.05x-1.1x). Pouco acima do stock."},
    {"H": "0.12", "S": "0.07", "D": "0.36", "Damage": "12000", "Tag": "BAIXA_2",     "Name": "Suspensao BAIXA 2",        "Desc": "Lift: 3pol. Para rodas de 40-61pol (1.15x-1.2x). Boa estabilidade."},
    {"H": "0.15", "S": "0.07", "D": "0.40", "Damage": "16000", "Tag": "MEDIA_1",     "Name": "Suspensao MEDIA 1",        "Desc": "Lift: 4pol. Para rodas de 45-69pol (1.25x-1.35x). Equilibrada."},
    {"H": "0.19", "S": "0.08", "D": "0.44", "Damage": "22000", "Tag": "MEDIA_2",     "Name": "Suspensao MEDIA 2",        "Desc": "Lift: 5pol. Para rodas de 50-77pol (1.4x-1.5x). Boa folga."},
    {"H": "0.23", "S": "0.09", "D": "0.48", "Damage": "30000", "Tag": "ALTA_1",      "Name": "Suspensao ALTA 1",         "Desc": "Lift: 6pol. Para rodas de 56-82pol (1.5x-1.6x)."},
    {"H": "0.28", "S": "0.10", "D": "0.52", "Damage": "38000", "Tag": "ALTA_2",      "Name": "Suspensao ALTA 2",         "Desc": "Lift: 7pol. Para rodas de 60-90pol (1.6x-1.8x). Bastante altura."},
    {"H": "0.33", "S": "0.10", "D": "0.56", "Damage": "48000", "Tag": "LIFTED_1",    "Name": "Suspensao LIFTED 1",       "Desc": "Lift: 8pol. Para rodas de 66-102pol (1.8x-2.0x). Lifted truck."},
    {"H": "0.39", "S": "0.11", "D": "0.60", "Damage": "58000", "Tag": "LIFTED_2",    "Name": "Suspensao LIFTED 2",       "Desc": "Lift: 10pol. Para rodas de 80-120pol (2.0x-2.25x). Monster truck."},
    {"H": "0.46", "S": "0.12", "D": "0.64", "Damage": "68000", "Tag": "MONSTER_1",   "Name": "Suspensao MONSTER 1",      "Desc": "Lift: 12pol. Para rodas de 100-130pol (2.25x-2.5x). Passa por cima de tudo."},
    {"H": "0.54", "S": "0.13", "D": "0.68", "Damage": "80000", "Tag": "MONSTER_2",   "Name": "Suspensao MONSTER 2",      "Desc": "Lift: 14pol. Para rodas de 110-153pol (2.5x-3.0x). Extremo."},
    {"H": "0.65", "S": "0.13", "D": "0.72", "Damage": "92000", "Tag": "EXTREMA",     "Name": "Suspensao EXTREMA",        "Desc": "Lift: 16pol. Para rodas de 130-153pol (2.75x-3.0x). Altura absurda."},
    {"H": "0.80", "S": "0.14", "D": "0.78", "Damage": "99999", "Tag": "DEUS",        "Name": "Suspensao DEUS",           "Desc": "Lift: 20pol. QUALQUER roda cabe. Indestrutivel. Sem limites."},
]
WINCH_STATS = [
    {"Len": "100", "Str": "20.0"},
]

# ============================================================
# SMART FILE SELECTION
# ============================================================
def select_op_files(truck_refs):
    result = {}
    for category, refs in truck_refs.items():
        file_to_trucks = defaultdict(set)
        truck_to_files = {}
        for truck, files in refs:
            truck_to_files[truck] = files
            for f in files:
                file_to_trucks[f].add(truck)

        op_files = set()
        covered_trucks = set()

        for truck, files in sorted(refs, key=lambda x: len(x[1])):
            if len(files) == 1:
                op_files.add(files[0])
                covered_trucks.add(truck)

        for truck, files in refs:
            if truck not in covered_trucks:
                for f in files:
                    if f in op_files:
                        covered_trucks.add(truck)
                        break

        for truck, files in sorted(refs, key=lambda x: len(x[1])):
            if truck in covered_trucks:
                continue
            already = [f for f in files if f in op_files]
            if already:
                covered_trucks.add(truck)
                continue
            best = files[0]
            op_files.add(best)
            covered_trucks.add(truck)

        dupes = []
        for truck, files in refs:
            count = sum(1 for f in files if f in op_files)
            if count > 1:
                dupes.append(truck)

        result[category] = op_files
        print(f"    {category}: {len(op_files)} files, {len(dupes)} trucks com duplicata")
    return result

def select_wheel_files_all(truck_wheel_refs, existing_wheel_files):
    """Seleciona TODOS os arquivos de roda referenciados por trucks que existem no pak.
    Nomes OP ja sao unicos por arquivo (file_tag), entao nao ha problema de duplicata."""
    all_files = set()
    for truck, files in truck_wheel_refs:
        for f in files:
            if f in existing_wheel_files:
                all_files.add(f)
    covered = sum(1 for _, files in truck_wheel_refs if any(f in all_files for f in files))
    total = len(truck_wheel_refs)
    print(f"    wheels (todos): {len(all_files)} files, {covered}/{total} trucks cobertos")
    return all_files

# ============================================================
# MOD FUNCTIONS
# ============================================================
def mod_engine(content, filename):
    # Reduzir freio motor (MaxDeltaAngVel controla quao rapido o motor desacelera)
    # Valor baixo = desacelera rapido ao soltar gas. Valor alto = mantem rotacao como carro real.
    content = re.sub(r'MaxDeltaAngVel="[^"]+"', 'MaxDeltaAngVel="0.001"', content)

    if "</EngineVariants>" not in content:
        return content
    tmpl = re.search(r'_template="(\w+)"', content)
    template = tmpl.group(1) if tmpl else "Engine"
    entries = []
    for stats in ENGINE_STATS:
        entries.append(
            '\t<Engine\r\n'
            '\t\t_template="' + template + '"\r\n'
            '\t\tCriticalDamageThreshold="0.99"\r\n'
            '\t\tDamageCapacity="' + stats['Damage'] + '"\r\n'
            '\t\tDamagedConsumptionModifier="1.0"\r\n'
            '\t\tEngineResponsiveness="' + stats['Resp'] + '"\r\n'
            '\t\tFuelConsumption="' + stats['Fuel'] + '"\r\n'
            '\t\tName="op_engine_' + stats['id'] + '"\r\n'
            '\t\tTorque="' + stats['Torque'] + '"\r\n'
            '\t\tDamagedMinTorqueMultiplier="1.0"\r\n'
            '\t\tDamagedMaxTorqueMultiplier="1.0"\r\n'
            '\t>\r\n'
            '\t\t<GameData\r\n'
            '\t\t\tPrice="100"\r\n'
            '\t\t\tUnlockByExploration="false"\r\n'
            '\t\t\tUnlockByRank="1"\r\n'
            '\t\t>\r\n'
            '\t\t\t<UiDesc\r\n'
            '\t\t\t\tUiDesc="UI_ENGINE_' + stats['Tag'] + '_DESC"\r\n'
            '\t\t\t\tUiIcon30x30=""\r\n'
            '\t\t\t\tUiIcon40x40=""\r\n'
            '\t\t\t\tUiName="UI_ENGINE_' + stats['Tag'] + '_NAME"\r\n'
            '\t\t\t/>\r\n'
            '\t\t</GameData>\r\n'
            '\t</Engine>')
    insert = "\r\n" + "\r\n".join(entries) + "\r\n"
    return content.replace("</EngineVariants>", insert + "</EngineVariants>")

def mod_gearbox(content, filename):
    if "</GearboxVariants>" not in content:
        return content
    entries = []
    for stats in GB_STATS:
        mv = stats["MaxVel"]
        dmg = stats["Damage"]
        gc = stats["Gears"]
        gid = stats["id"]
        tag = stats["Tag"]
        gears = []
        gear_speeds = [round(1.41 * (mv / 1.41) ** (g / (gc - 1)), 2) for g in range(gc)]
        for i, spd in enumerate(gear_speeds):
            fm = round(1.8 - (1.0 / max(gc - 1, 1)) * i, 2)
            fm = max(fm, 0.7)
            gears.append('\t\t<Gear AngVel="' + str(spd) + '" FuelModifier="' + str(fm) + '" />')
        rv = 1.5
        hv = round(gear_speeds[-2] + (gear_speeds[-1] - gear_speeds[-2]) * 0.5, 1)
        gears_str = "\r\n".join(gears)
        entry = (
            '\t<Gearbox\r\n'
            '\t\tAWDConsumptionModifier="0.0"\r\n'
            '\t\tCriticalDamageThreshold="0.99"\r\n'
            '\t\tDamageCapacity="' + dmg + '"\r\n'
            '\t\tDamagedConsumptionModifier="1.0"\r\n'
            '\t\tFuelConsumption="1.0"\r\n'
            '\t\tIdleFuelModifier="0.1"\r\n'
            '\t\tName="op_gearbox_' + gid + '"\r\n'
            '\t\tMinBreakFreq="0.0"\r\n'
            '\t\tMaxBreakFreq="0.0"\r\n'
            '\t>\r\n'
            '\t\t<ReverseGear AngVel="' + str(rv) + '" FuelModifier="1.1" />\r\n'
            '\t\t<HighGear AngVel="' + str(hv) + '" FuelModifier="1.0" />\r\n'
            + gears_str + '\r\n'
            '\t\t<GameData\r\n'
            '\t\t\tPrice="100"\r\n'
            '\t\t\tUnlockByExploration="false"\r\n'
            '\t\t\tUnlockByRank="1"\r\n'
            '\t\t>\r\n'
            '\t\t\t<GearboxParams\r\n'
            '\t\t\t\tIsHighGearExists="true"\r\n'
            '\t\t\t\tIsLowerGearExists="true"\r\n'
            '\t\t\t\tIsLowerPlusGearExists="false"\r\n'
            '\t\t\t\tIsLowerMinusGearExists="false"\r\n'
            '\t\t\t/>\r\n'
            '\t\t\t<UiDesc\r\n'
            '\t\t\t\tUiDesc="UI_GEARBOX_' + tag + '_DESC"\r\n'
            '\t\t\t\tUiIcon30x30=""\r\n'
            '\t\t\t\tUiIcon40x40=""\r\n'
            '\t\t\t\tUiName="UI_GEARBOX_' + tag + '_NAME"\r\n'
            '\t\t\t/>\r\n'
            '\t\t</GameData>\r\n'
            '\t</Gearbox>')
        entries.append(entry)
    insert = "\r\n" + "\r\n".join(entries) + "\r\n"
    return content.replace("</GearboxVariants>", insert + "</GearboxVariants>")

def mod_winch(content, filename):
    if "</WinchVariants>" not in content:
        return content
    stats = WINCH_STATS[0]
    entry = (
        '\t<Winch\r\n'
        '\t\tName="op_winch_deus"\r\n'
        '\t\tLength="' + stats['Len'] + '"\r\n'
        '\t\tStrengthMult="' + stats['Str'] + '"\r\n'
        '\t\tIsEngineIgnitionRequired="false"\r\n'
        '\t>\r\n'
        '\t\t<GameData\r\n'
        '\t\t\tPrice="100"\r\n'
        '\t\t\tUnlockByExploration="false"\r\n'
        '\t\t\tUnlockByRank="1"\r\n'
        '\t\t>\r\n'
        '\t\t\t<WinchParams\r\n'
        '\t\t\t/>\r\n'
        '\t\t\t<UiDesc\r\n'
        '\t\t\t\tUiDesc="UI_WINCH_DEUS_DESC"\r\n'
        '\t\t\t\tUiIcon30x30=""\r\n'
        '\t\t\t\tUiIcon40x40=""\r\n'
        '\t\t\t\tUiName="UI_WINCH_DEUS_NAME"\r\n'
        '\t\t\t/>\r\n'
        '\t\t</GameData>\r\n'
        '\t</Winch>')
    insert = "\r\n" + entry + "\r\n"
    return content.replace("</WinchVariants>", insert + "</WinchVariants>")

def mod_suspension(content, filename):
    if "</SuspensionSetVariants>" not in content:
        return content
    base = os.path.splitext(filename)[0]
    entries = []
    for i, stats in enumerate(SUSP_STATS):
        h = stats["H"]
        op_id = "op" + str(i + 1)
        tag = stats["Tag"]
        entries.append(
            '\t<SuspensionSet\r\n'
            '\t\t_template="Active"\r\n'
            '\t\tCriticalDamageThreshold="0.99"\r\n'
            '\t\tDamageCapacity="' + stats['Damage'] + '"\r\n'
            '\t\tBrokenWheelDamageMultiplier="0.01"\r\n'
            '\t\tDeviationDelta=".002"\r\n'
            '\t\tName="' + base + '_' + op_id + '"\r\n'
            '\t>\r\n'
            '\t\t<Suspension Height="' + h + '" Strength="' + stats['S'] + '" Damping="' + stats['D'] + '" WheelType="front" BrokenSuspensionMax="0.0" SuspensionMin="-' + h + '" SuspensionMax="0.3" DeviationMax="0.15" />\r\n'
            '\t\t<Suspension Height="' + h + '" Strength="' + stats['S'] + '" Damping="' + stats['D'] + '" WheelType="rear" BrokenSuspensionMax="0.0" SuspensionMin="-' + h + '" SuspensionMax="0.3" DeviationMax="0.15" />\r\n'
            '\t\t<GameData\r\n'
            '\t\t\tPrice="100"\r\n'
            '\t\t\tUnlockByExploration="false"\r\n'
            '\t\t\tUnlockByRank="1"\r\n'
            '\t\t>\r\n'
            '\t\t\t<UiDesc\r\n'
            '\t\t\t\tUiDesc="UI_SUSP_' + tag + '_DESC"\r\n'
            '\t\t\t\tUiIcon30x30=""\r\n'
            '\t\t\t\tUiIcon40x40=""\r\n'
            '\t\t\t\tUiName="UI_SUSP_' + tag + '_NAME"\r\n'
            '\t\t\t/>\r\n'
            '\t\t</GameData>\r\n'
            '\t</SuspensionSet>')
    insert = "\r\n" + "\r\n".join(entries) + "\r\n"
    return content.replace("</SuspensionSetVariants>", insert + "</SuspensionSetVariants>")

def mod_wheels(content, filename):
    if "</TruckTires>" not in content:
        return content

    # ID unico por arquivo (ex: "wheels_heavy_double1.xml" -> "hd1")
    file_id = filename.replace("wheels_", "").replace("wheel_", "").replace(".xml", "")
    # Abreviar: pegar iniciais de cada parte separada por _
    parts = file_id.split("_")
    if len(parts) >= 2:
        file_tag = "".join(p[0] for p in parts if p) + parts[-1][1:] if len(parts[-1]) > 1 else "".join(p[0] for p in parts if p)
    else:
        file_tag = file_id[:8]

    # Aumentar Width em 80% (rodas bem mais grossas)
    def widen(match):
        attr = match.group(1)  # "Width" ou "WidthRear"
        val = float(match.group(2))
        new_val = round(val * 2.5, 3)
        return attr + '="' + str(new_val) + '"'
    content = re.sub(r'(Width(?:Rear)?)\s*=\s*"([0-9.]+)"', widen, content)

    # Pneus indestrutíveis
    content = re.sub(r'(<TruckWheels[^>]*?)DamageCapacity="[^"]+"', r'\1DamageCapacity="999999"', content)

    # Encontrar TODOS os TruckTire existentes (cada modelo visual diferente)
    tire_pattern = re.compile(
        r'<TruckTire\s+([^>]*?)>\s*'
        r'(.*?)'
        r'</TruckTire>',
        re.DOTALL
    )
    existing_tires = tire_pattern.findall(content)
    if not existing_tires:
        return content

    # Coletar pneus unicos por Mesh (cada mesh = um visual diferente)
    seen_meshes = {}
    for attrs_str, inner in existing_tires:
        mesh_m = re.search(r'Mesh="([^"]+)"', attrs_str)
        tmpl_m = re.search(r'_template="([^"]+)"', attrs_str)
        name_m = re.search(r'Name="([^"]+)"', attrs_str)
        # Capturar o _template do WheelFriction interno (define categoria: Chains, Mudtires, etc)
        wf_tmpl_m = re.search(r'<WheelFriction[^>]*_template="([^"]+)"', inner)
        if mesh_m and name_m:
            mesh = mesh_m.group(1)
            if mesh not in seen_meshes:
                seen_meshes[mesh] = {
                    "template": tmpl_m.group(1) if tmpl_m else "Offroad",
                    "name": name_m.group(1),
                    "wf_template": wf_tmpl_m.group(1) if wf_tmpl_m else None,
                }

    entries = []
    # Para cada modelo visual, criar 1 versao OP (a melhor - DEUS 12.0)
    for mesh, info in seen_meshes.items():
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', info["name"])
        op_name = "op_" + file_tag + "_" + safe_name + "_god"
        # Preservar _template do WheelFriction para manter a categoria (Chains, Mudtires, etc)
        wf_tmpl_attr = ' _template="' + info["wf_template"] + '"' if info["wf_template"] else ''
        entries.append(
            '\t\t<TruckTire _template="' + info["template"] + '" Mesh="' + mesh + '" Name="' + op_name + '">\r\n'
            '\t\t\t<WheelFriction' + wf_tmpl_attr + ' BodyFriction="15.0" BodyFrictionAsphalt="15.0" SubstanceFriction="15.0" IsIgnoreIce="true" />\r\n'
            '\t\t\t<GameData\r\n'
            '\t\t\t\tPrice="100"\r\n'
            '\t\t\t\tUnlockByExploration="false"\r\n'
            '\t\t\t\tUnlockByRank="1"\r\n'
            '\t\t\t>\r\n'
            '\t\t\t\t<UiDesc UiDesc="UI_TIRE_DEUS_DESC" UiName="UI_TIRE_DEUS_NAME" />\r\n'
            '\t\t\t</GameData>\r\n'
            '\t\t</TruckTire>')

    insert = "\r\n" + "\r\n".join(entries) + "\r\n\t"
    return content.replace("</TruckTires>", insert + "</TruckTires>")

def mod_truck(content, filename):
    """Modifica TruckData de cada truck:
    - DiffLockType="Always" (bloq diferencial sempre ativo)
    - Snorkel Origin Y = 10.0 (submersivel)
    - Rodas em 8 escalas (PLUS 1.1x ate DEUS 3.0x)
    """
    changed = False

    # DiffLockType -> Always
    m = re.search(r'DiffLockType="(\w+)"', content)
    if m and m.group(1) != "Always":
        content = content.replace('DiffLockType="' + m.group(1) + '"', 'DiffLockType="Always"')
        changed = True

    # Snorkel Origin Y -> 10.0 (muito alto = passa em agua profunda)
    def raise_snorkel(match):
        nonlocal changed
        full = match.group(0)
        origin_m = re.search(r'Origin="\(([^;]+);\s*([^;]+);\s*([^)]+)\)"', full)
        if origin_m:
            x = origin_m.group(1).strip()
            z = origin_m.group(3).strip()
            new_origin = 'Origin="(' + x + '; 10.0; ' + z + ')"'
            old_origin = 'Origin="(' + origin_m.group(1) + '; ' + origin_m.group(2).strip() + '; ' + origin_m.group(3) + ')"'
            if old_origin in full:
                new_full = full.replace(old_origin, new_origin)
                changed = True
                return new_full
        return full

    content = re.sub(r'<Snorkel[^/>]+/>', raise_snorkel, content)

    # Adicionar escalas maiores para cada roda existente (4 tamanhos)
    existing_cw = re.findall(r'<CompatibleWheels[^/]*/>', content)
    if existing_cw:
        scale_mults = [1.3, 1.45, 1.6]
        existing_combos = set()
        for cw in existing_cw:
            sm = re.search(r'Scale="([^"]+)"', cw)
            tm = re.search(r'Type="([^"]+)"', cw)
            if sm and tm:
                existing_combos.add((sm.group(1), tm.group(1)))

        new_entries = []
        seen_combos = set()
        for cw in existing_cw:
            scale_m = re.search(r'Scale="([^"]+)"', cw)
            type_m = re.search(r'Type="([^"]+)"', cw)
            if not scale_m or not type_m:
                continue
            orig_scale = float(scale_m.group(1))
            wtype = type_m.group(1)
            offsetz_m = re.search(r'OffsetZ="([^"]+)"', cw)
            rearoffz_m = re.search(r'RearOffsetZ="([^"]+)"', cw)

            for mult in scale_mults:
                new_scale = round(orig_scale * mult, 3)
                new_scale_str = str(new_scale)
                combo = (new_scale_str, wtype)
                if combo in existing_combos or combo in seen_combos:
                    continue
                seen_combos.add(combo)
                attrs = 'Scale="' + new_scale_str + '" Type="' + wtype + '"'
                if offsetz_m:
                    attrs = 'OffsetZ="' + offsetz_m.group(1) + '" ' + attrs
                if rearoffz_m:
                    attrs = 'RearOffsetZ="' + rearoffz_m.group(1) + '" ' + attrs
                new_entries.append('\t\t<CompatibleWheels ' + attrs + ' />')

        if new_entries:
            last_cw = existing_cw[-1]
            insert_text = last_cw + "\r\n" + "\r\n".join(new_entries)
            content = content.replace(last_cw, insert_text, 1)
            changed = True

    return content, changed

def get_op_strings():
    strs = []
    # Motores (gerado do ENGINE_STATS)
    for stats in ENGINE_STATS:
        tag = stats["Tag"]
        strs.append('UI_ENGINE_' + tag + '_NAME\t\t\t\t"' + stats["Name"] + '"')
        strs.append('UI_ENGINE_' + tag + '_DESC\t\t\t\t"' + stats["Desc"] + '"')

    # Suspensoes (gerado do SUSP_STATS)
    for stats in SUSP_STATS:
        tag = stats["Tag"]
        strs.append('UI_SUSP_' + tag + '_NAME\t\t\t\t"' + stats["Name"] + '"')
        strs.append('UI_SUSP_' + tag + '_DESC\t\t\t\t"' + stats["Desc"] + '"')

    # Cambios, Guinchos, Pneus (fixos)
    for prefix, items in [
        ("GEARBOX", [
            ("8A",      "8 Marchas 45km/h",           "~45 km/h. Forca bruta para lama, neve e carga pesada."),
            ("8B",      "8 Marchas 49km/h",           "~49 km/h. Equilibrado para trilha e estrada."),
            ("8C",      "8 Marchas 52km/h",           "~52 km/h. Rapido em estrada e terreno misto."),
            ("8D",      "8 Marchas 56km/h",           "~56 km/h. Velocidade maxima, feito pra estrada."),
        ]),
        ("WINCH", [
            ("DEUS",       "Guincho DEUS",            "Alcance 100m. Forca 20x. Funciona sem motor ligado. Puxa qualquer coisa."),
        ]),
        ("TIRE", [
            ("DEUS",            "Pneu DEUS",              "Grip 15.0 em tudo. OP sem perder contato com o solo."),
        ]),
    ]:
        for tag, name, desc in items:
            strs.append("UI_" + prefix + "_" + tag + '_NAME\t\t\t\t"' + name + '"')
            strs.append("UI_" + prefix + "_" + tag + '_DESC\t\t\t\t"' + desc + '"')
    return "\r\n".join(strs) + "\r\n"

# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("  SNOWRUNNER OP MOD v6")
    print("  Gearbox fix + Corrente + DiffLock + Snorkel + AWD")
    print("=" * 60)

    print("\n[1] Restaurando pak original...")
    shutil.copy2(BACKUP_PAK, GAME_PAK)
    print("    OK")

    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR)

    # PASS 0: Scan trucks
    print("\n[2] Analisando trucks...")
    truck_engine_refs = []
    truck_gb_refs = []
    truck_winch_refs = []
    truck_wheel_refs = []

    with zipfile.ZipFile(BACKUP_PAK, "r") as zf:
        for entry in zf.infolist():
            path = entry.filename
            if "/classes/trucks/" not in path or not path.endswith(".xml"):
                continue
            raw = zf.read(path)
            text = raw.decode("utf-8")
            truck_name = os.path.splitext(os.path.basename(path))[0]

            em = re.search(r'<EngineSocket[^>]*Type="([^"]+)"', text)
            if em:
                files = [f.strip() for f in em.group(1).split(",")]
                truck_engine_refs.append((truck_name, files))

            gm = re.search(r'<GearboxSocket[^>]*Type="([^"]+)"', text)
            if gm:
                files = [f.strip() for f in gm.group(1).split(",")]
                truck_gb_refs.append((truck_name, files))

            wm = re.search(r'<WinchUpgradeSocket[^>]*Type="([^"]+)"', text)
            if wm:
                files = [f.strip() for f in wm.group(1).split(",")]
                truck_winch_refs.append((truck_name, files))

            # Wheels: multiple <CompatibleWheels Type="xxx" /> tags
            wheel_files = re.findall(r'<CompatibleWheels[^>]*Type="([^"]+)"', text)
            if wheel_files:
                wf = [f.strip() for f in wheel_files]
                truck_wheel_refs.append((truck_name, wf))

    print(f"    Trucks: engines={len(truck_engine_refs)}, gearboxes={len(truck_gb_refs)}, winches={len(truck_winch_refs)}, wheels={len(truck_wheel_refs)}")

    # Escanear quais arquivos de roda REALMENTE existem no pak
    existing_wheel_files = set()
    with zipfile.ZipFile(BACKUP_PAK, "r") as zf:
        for entry in zf.infolist():
            path = entry.filename
            if "/classes/wheels/" in path and path.endswith(".xml"):
                existing_wheel_files.add(os.path.splitext(os.path.basename(path))[0])
    print(f"    Arquivos de roda no pak: {len(existing_wheel_files)}")

    # Construir dicionario de tipos de roda por categoria (so os que existem no pak)
    all_wheel_types_by_category = defaultdict(set)
    for truck_name, wfiles in truck_wheel_refs:
        for wf in wfiles:
            if wf not in existing_wheel_files:
                continue  # Ignorar tipos que nao tem arquivo no pak
            if "scout" in wf:
                all_wheel_types_by_category["scout"].add(wf)
            elif "superheavy" in wf:
                all_wheel_types_by_category["superheavy"].add(wf)
            elif "medium" in wf:
                all_wheel_types_by_category["medium"].add(wf)
            elif "heavy" in wf:
                all_wheel_types_by_category["heavy"].add(wf)
    for cat, types in sorted(all_wheel_types_by_category.items()):
        print(f"    Rodas {cat}: {len(types)} tipos")

    print("\n[3] Selecionando arquivos...")
    categories = {
        "engines": truck_engine_refs,
        "gearboxes": truck_gb_refs,
        "winches": truck_winch_refs,
    }
    selected = select_op_files(categories)
    engine_op_files = selected.get("engines", set())
    gearbox_op_files = selected.get("gearboxes", set())
    winch_op_files = selected.get("winches", set())
    wheel_op_files = select_wheel_files_all(truck_wheel_refs, existing_wheel_files)

    # PASS 1: Generate files
    print("\n[4] Gerando arquivos modificados...")
    counts = {"engines": 0, "gearboxes": 0, "suspensions": 0,
              "winches": 0, "wheels": 0, "trucks": 0, "strings": 0}

    with zipfile.ZipFile(BACKUP_PAK, "r") as zf:
        for entry in zf.infolist():
            path = entry.filename
            fname = os.path.basename(path)
            fname_noext = os.path.splitext(fname)[0]
            modified = False
            new_text = None

            # Engines
            if "/classes/engines/" in path and path.endswith(".xml"):
                if fname_noext in engine_op_files:
                    raw = zf.read(path)
                    text = raw.decode("utf-8")
                    new_text = mod_engine(text, fname)
                    if new_text != text:
                        modified = True
                        counts["engines"] += 1

            # Gearboxes
            elif "/classes/gearboxes/" in path and path.endswith(".xml"):
                if fname_noext in gearbox_op_files:
                    raw = zf.read(path)
                    text = raw.decode("utf-8")
                    new_text = mod_gearbox(text, fname)
                    if new_text != text:
                        modified = True
                        counts["gearboxes"] += 1

            # Winches
            elif "/classes/winches/" in path and path.endswith(".xml"):
                if fname_noext in winch_op_files:
                    raw = zf.read(path)
                    text = raw.decode("utf-8")
                    new_text = mod_winch(text, fname)
                    if new_text != text:
                        modified = True
                        counts["winches"] += 1

            # Suspensions
            elif "/classes/suspensions/" in path and path.endswith(".xml"):
                raw = zf.read(path)
                text = raw.decode("utf-8")
                new_text = mod_suspension(text, fname)
                if new_text != text:
                    modified = True
                    counts["suspensions"] += 1

            # Wheels - smart select (sem duplicatas)
            elif "/classes/wheels/" in path and path.endswith(".xml"):
                if fname_noext in wheel_op_files:
                    raw = zf.read(path)
                    text = raw.decode("utf-8")
                    new_text = mod_wheels(text, fname)
                    if new_text != text:
                        modified = True
                        counts["wheels"] += 1

            # Trucks (DiffLock + Snorkel + Rodas Gigantes)
            elif "/classes/trucks/" in path and path.endswith(".xml"):
                raw = zf.read(path)
                text = raw.decode("utf-8")
                new_text, changed = mod_truck(text, fname)
                if changed:
                    modified = True
                    counts["trucks"] += 1

            # Strings
            elif path.startswith("[strings]/") and path.endswith(".str"):
                raw = zf.read(path)
                if raw[:2] == b'\xff\xfe':
                    text = raw[2:].decode("utf-16-le")
                else:
                    text = raw.decode("utf-16-le")
                op_text = get_op_strings()
                if not text.endswith("\r\n"):
                    text = text.rstrip("\r\n") + "\r\n"
                text = text + op_text
                new_data = b'\xff\xfe' + text.encode("utf-16-le")
                out_path = os.path.join(TEMP_DIR, path.replace("/", os.sep))
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(new_data)
                counts["strings"] += 1
                sys.stdout.write("S")
                sys.stdout.flush()
                continue

            if modified and new_text:
                out_path = os.path.join(TEMP_DIR, path.replace("/", os.sep))
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(new_text.encode("utf-8"))
                sys.stdout.write(".")
                sys.stdout.flush()

    print()
    total = 0
    for k, v in counts.items():
        if v:
            print(f"    {k}: {v}")
            total += v
    print(f"    TOTAL: {total}")

    print("\n[5] Injetando com WinRAR...")
    cmd = [WINRAR, "a", "-afzip", "-o+", "-r", GAME_PAK, "*"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=TEMP_DIR)

    if result.returncode != 0:
        print("    ERRO! " + result.stdout[:300] + result.stderr[:300])
        return

    print("    OK!")
    new_size = os.path.getsize(GAME_PAK)
    orig_size = os.path.getsize(BACKUP_PAK)
    print(f"    Original: {orig_size:,}")
    print(f"    Modded:   {new_size:,}")

    print("\n" + "=" * 60)
    print("  v6 PRONTO!")
    print("  [FIX] Gearbox: ReverseGear=1.5, MaxBreakFreq=15 (sem bug)")
    print("  [FIX] AWDConsumptionModifier=0.0 (AWD gratis)")
    print("  [NEW] Pneu Corrente SUPREMA (grip 12.0 em tudo)")
    print("  [NEW] DiffLockType=Always em todos os trucks")
    print("  [NEW] Snorkel Y=10.0 (submersivel)")
    print("  [NEW] Todas as rodas da categoria disponiveis por veiculo")
    print("=" * 60)

if __name__ == "__main__":
    main()
