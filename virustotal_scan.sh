#!/bin/bash
# Sube un archivo a VirusTotal via API y consulta el resultado.
# Uso: ./virustotal_scan.sh <ruta_al_archivo> <API_KEY>
#
# Necesitas una API key de VirusTotal (gratis): https://www.virustotal.com/gui/join-us
# El plan gratuito permite subir archivos hasta 650MB.

ARCHIVO="$1"
VT_KEY="$2"

if [ -z "$ARCHIVO" ] || [ -z "$VT_KEY" ]; then
    echo "Uso: $0 <ruta_al_archivo> <API_KEY>"
    exit 1
fi

echo "=== 1) Subiendo $ARCHIVO a VirusTotal ... ==="
# POST /api/v3/files — sube el archivo y devuelve un analysis_id
RESPUESTA=$(curl -s --max-time 180 -X POST "https://www.virustotal.com/api/v3/files" \
    -H "x-apikey: $VT_KEY" \
    -F "file=@$ARCHIVO")

# Extraer el analysis id (con python por robustez)
ANALYSIS_ID=$(echo "$RESPUESTA" | py -3.14 -c "import sys,json; d=json.load(sys.stdin); print(d.get('data',{}).get('id','ERROR'))" 2>/dev/null)
echo "analysis id: $ANALYSIS_ID"

if [ "$ANALYSIS_ID" = "ERROR" ] || [ -z "$ANALYSIS_ID" ]; then
    echo "ERROR al subir. Respuesta:"
    echo "$RESPUESTA" | head -5
    exit 1
fi

echo ""
echo "=== 2) Esperando analisis (~20s) ... ==="
sleep 20

echo "=== 3) Consultando resultado (GET /api/v3/analyses/{id}) ==="
curl -s --max-time 60 "https://www.virustotal.com/api/v3/analyses/$ANALYSIS_ID" \
    -H "x-apikey: $VT_KEY" | py -3.14 -c "
import sys, json
d = json.load(sys.stdin)
attrs = d.get('data', {}).get('attributes', {})
stats = attrs.get('stats', {})
print(f\"Detecciones: {stats.get('malicious',0)}/{stats.get('harmless',0) + stats.get('malicious',0) + stats.get('suspicious',0) + stats.get('undetected',0)}\")
print(f\"  malicious:   {stats.get('malicious',0)}\")
print(f\"  suspicious:  {stats.get('suspicious',0)}\")
print(f\"  harmless:    {stats.get('harmless',0)}\")
print(f\"  undetected:  {stats.get('undetected',0)}\")
print(f\"  timeout:     {stats.get('timeout',0)}\")
print(f\"Estado: {attrs.get('status','')}\")
"
echo ""
echo "NOTA: malicious=0 es ideal. 1-3 con nombres genericos (HackTool/PyInstaller/Inno) = falso positivo normal."
