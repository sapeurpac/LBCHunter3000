# analyser.py
import re

def clean_text(text):
    """Nettoie le texte pour uniformiser les recherches."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[\n\r\t,;/|]', ' ', text)
    text = text.replace("gb", "go").replace("tb", "to")
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_specs(titre, description):
    full_text = clean_text(str(titre) + " " + str(description))
    
    specs = {
        "cpu": "Non spécifié",
        "gpu": "Non spécifié",
        "gpu_vram": None,
        "ram": 0,
        "ram_type": None,
        "ssd": 0,
        "hdd": 0,
        "etat": "Non spécifié"
    }

    # --- 1. CPU ---
    cpu_intel = re.search(r'(?:intel\s?)?(?:core\s?)?(i[3579][\s-]?\d{3,5}[a-z]*)', full_text)
    cpu_amd = re.search(r'(?:amd\s?)?(ryzen\s?[3579]\s?-?\s?\d{4}[a-z]*)', full_text)
    
    if cpu_intel:
        specs['cpu'] = "Intel Core " + cpu_intel.group(1).replace(" ", "")
    elif cpu_amd:
        specs['cpu'] = "AMD " + cpu_amd.group(1).replace(" ", "-")

    # --- 2. GPU & VRAM ---
    gpu_patterns = [
        r'(rtx\s?\d{3,4}\s?(?:ti|super|xt)?)',
        r'(gtx\s?\d{3,4}\s?(?:ti|super)?)',
        r'(rx\s?\d{3,4}\s?(?:xt)?)',
        r'(arc\s?a\d{3})'
    ]
    
    for pattern in gpu_patterns:
        match = re.search(pattern, full_text)
        if match:
            specs['gpu'] = match.group(1).upper().replace(" ", "")
            # VRAM
            start = max(0, match.start() - 15)
            end = min(len(full_text), match.end() + 15)
            snippet = full_text[start:end]
            vram_match = re.search(r'(\d{1,2})\s?go', snippet)
            if vram_match:
                specs['gpu_vram'] = f"{vram_match.group(1)} Go"
            break
            
    if specs['gpu'] == "Non spécifié" and any(x in full_text for x in ["intel uhd", "iris", "graphics"]):
        specs['gpu'] = "iGPU (Intégré)"

    # --- 3. RAM ---
    ram_matches = re.findall(r'(\d{1,3})\s?go\s?(?:de\s?)?(?:ram|ddr|mémoire|memoire)', full_text)
    for r in ram_matches:
        val = int(r)
        if val in [4, 8, 12, 16, 24, 32, 48, 64, 128]: 
            if val > specs['ram']:
                specs['ram'] = val

    if "ddr5" in full_text: specs['ram_type'] = "DDR5"
    elif "ddr4" in full_text: specs['ram_type'] = "DDR4"
    elif "ddr3" in full_text: specs['ram_type'] = "DDR3"

    # --- 4. STOCKAGE (SSD/HDD) ---
    def parse_storage_size(val, unit):
        val = int(val)
        if "to" in unit: return val * 1024
        return val

    # SSD
    ssd_match = re.search(r'(\d{3,4})\s?(go)|(\d{1,2})\s?(to)\s?(?:ssd|nvme|m\.2)', full_text)
    if ssd_match:
        if ssd_match.group(1): specs['ssd'] = parse_storage_size(ssd_match.group(1), "go")
        else: specs['ssd'] = parse_storage_size(ssd_match.group(3), "to")
    
    # HDD
    hdd_match = re.search(r'(\d{3,4})\s?(go)|(\d{1,2})\s?(to)\s?(?:hdd|disque dur|sata)', full_text)
    if hdd_match:
        if hdd_match.group(1): specs['hdd'] = parse_storage_size(hdd_match.group(1), "go")
        else: specs['hdd'] = parse_storage_size(hdd_match.group(3), "to")

    # Fallback générique -> SSD par défaut
    if specs['ssd'] == 0 and specs['hdd'] == 0:
        generic_storage = re.search(r'(\d{3,4})\s?(go)|(\d{1,2})\s?(to)', full_text)
        if generic_storage:
             val = 0
             if generic_storage.group(1): val = int(generic_storage.group(1))
             else: val = int(generic_storage.group(3)) * 1024
             # On assume SSD sauf si très petit (<120) ou très gros sans contexte
             specs['ssd'] = val

    # --- 5. ETAT ---
    if re.search(r'(neuf|scell.|blister|jamais ouvert)', full_text): specs['etat'] = "Neuf/Scellé"
    elif re.search(r'(tr.s bon .tat|comme neuf|nickel|impeccable)', full_text): specs['etat'] = "Très bon état"
    elif re.search(r'(bon .tat|fonctionne parfaitement)', full_text): specs['etat'] = "Bon état"
    elif re.search(r'(hs|panne|pour pi.ces|probl.me)', full_text): specs['etat'] = "HS/Pour pièces"

    return specs