import http.client
import json

API_KEY = "XXX"

def get_last_scan_id(application_id):
    """
    Récupère l'ID du dernier scan (le plus récent) pour une application donnée.
    """
    conn = http.client.HTTPSConnection("public.escape.tech")
    headers = { 'Authorization': f"Key {API_KEY}" }
    path = f"/v2/applications/{application_id}/scans"
    
    # Envoi de la requête GET pour récupérer les scans
    conn.request("GET", path, headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    # Décodage de la réponse JSON
    response_json = json.loads(data.decode("utf-8"))
    scans = response_json.get("data", [])
    
    # Vérification s'il y a des scans
    if not scans:
        print("Aucun scan trouvé.")
        return None
    
    # Trouver le scan le plus récent selon 'createdAt'
    last_scan = max(scans, key=lambda x: x["createdAt"])
    return last_scan["id"], last_scan.get("createdAt"), last_scan.get("status", "UNKNOWN")

def get_scan_info(scan_id):
    """
    Récupère les détails des issues d'un scan donné.
    Compte et liste les issues par niveau de severity.
    """
    conn = http.client.HTTPSConnection("public.escape.tech")
    headers = { 'Authorization': f"Key {API_KEY}" }
    path = f"/v2/scans/{scan_id}/issues"
    
    # Envoi de la requête GET pour récupérer les issues
    conn.request("GET", path, headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    # Décodage des issues JSON
    issues = json.loads(data.decode("utf-8"))
    
    severity_counts = {}  # Compteur par niveau de severity
    severity_names = {}   # Noms des issues par severity
    
    # Parcours des issues pour remplir les dictionnaires
    for issue in issues:
        sev = issue.get("severity", "UNKNOWN")
        name = issue.get("name", "No name")
        
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        severity_names.setdefault(sev, []).append(name)
    
    return {
        "severity_counts": severity_counts,
        "severity_names": severity_names,
        "total_issues": len(issues)
    }

def main():
    # ID de l'application à analyser (modifie si besoin)
    application_id = "ffa839b6-1862-4f95-800f-770e9c656a56"
    
    # Récupération du dernier scan
    last_scan_data = get_last_scan_id(application_id)
    if not last_scan_data:
        return
    
    scan_id, created_at, status = last_scan_data
    
    print(f"Dernier scan ID: {scan_id}")
    print(f"Date: {created_at}")
    print(f"Status: {status}")
    
    # Récupération des infos détaillées sur ce scan
    scan_info = get_scan_info(scan_id)
    print(f"Total d'issues: {scan_info['total_issues']}")
    
    # Ordre d'affichage souhaité des niveaux de severity
    order = ["HIGH", "MEDIUM", "LOW", "INFO"]
    
    # Affichage du nombre d'issues par severity
    print("\nNombre d'issues par niveau de severity :")
    for sev in order:
        if sev in scan_info["severity_counts"]:
            print(f"- {sev}: {scan_info['severity_counts'][sev]}")
    
    # Affichage détaillé des issues par severity
    print("\nDétails des issues par severity :")
    for sev in order:
        if sev in scan_info["severity_names"]:
            names = scan_info["severity_names"][sev]
            print(f"\n=== {sev} ({len(names)}) ===")
            for i, name in enumerate(names, 1):
                print(f"{i}. {name}")

if __name__ == "__main__":
    main()
