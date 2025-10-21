import requests
import sys

API_BASE_ROUTE = "https://graphhopper.com/api/1/route"
API_BASE_GEOCODE = "https://graphhopper.com/api/1/geocode"
API_KEY = "bddbd46e-08cf-4d90-b5cc-b30313d3f540"

# Direcciones por defecto
ORIGEN_DEFECTO = "Libertad 2244, Valparaíso, Valparaíso"
DESTINO_DEFECTO = "Álvarez 2336, Viña del Mar, Valparaíso"

def formatea_km(metros: float) -> float:
    return round(metros / 1000.0, 2)

def formatea_min(ms: float) -> float:
    return round(ms / 60000.0, 2)

def geocodificar(direccion: str):
    params = {
        "q": direccion,
        "locale": "es",
        "limit": 1,
        "key": API_KEY
    }
    try:
        r = requests.get(API_BASE_GEOCODE, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        hits = data.get("hits", [])
        if not hits:
            return None
        punto = hits[0].get("point", {})
        lat = punto.get("lat")
        lng = punto.get("lng")
        if lat is None or lng is None:
            return None
        return (lat, lng)
    except Exception as e:
        print(f"Error al geocodificar: {e}")
        return None

def rutear(origen_latlng, destino_latlng, vehicle="car"):
    params = {
        "key": API_KEY,
        "locale": "es",
        "points_encoded": "false",
        "instructions": "true",
        "vehicle": vehicle
    }
    points = [
        ("point", f"{origen_latlng[0]},{origen_latlng[1]}"),
        ("point", f"{destino_latlng[0]},{destino_latlng[1]}")
    ]
    try:
        r = requests.get(API_BASE_ROUTE, params=points + list(params.items()), timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error al obtener la ruta: {e}")
        return None

def imprimir_resumen_y_instrucciones(route_json):
    if not route_json or "paths" not in route_json or not route_json["paths"]:
        print("No se recibió una ruta válida desde el servicio.")
        return

    path = route_json["paths"][0]
    distancia_m = path.get("distance", 0.0)
    tiempo_ms = path.get("time", 0.0)
    instrucciones = path.get("instructions", [])

    distancia_km = formatea_km(distancia_m)
    tiempo_min = formatea_min(tiempo_ms)

    print("\n=== Resumen del viaje ===")
    print(f"- Distancia total: {distancia_km:.2f} km")
    print(f"- Tiempo estimado: {tiempo_min:.2f} min")

    if instrucciones:
        print("\n=== Instrucciones paso a paso (narrativa en español) ===")
        for idx, instr in enumerate(instrucciones, start=1):
            texto = instr.get("text", "Sin texto")
            instr_dist_m = instr.get("distance", 0.0)
            instr_time_ms = instr.get("time", 0.0)
            instr_km = formatea_km(instr_dist_m)
            instr_min = formatea_min(instr_time_ms)
            print(f"{idx}. {texto} ({instr_km:.2f} km, {instr_min:.2f} min)")
    else:
        print("No se recibieron instrucciones para este viaje.")

def solicitar_direccion(mensaje: str, defecto: str) -> str:
    dir_input = input(f"{mensaje} (Enter para usar '{defecto}'): ").strip()
    if dir_input.lower() in ("s", "salir"):
        print("Saliendo del programa. Hasta luego.")
        sys.exit(0)
    return dir_input if dir_input else defecto

def main():
    print("=== Planificador de rutas con GraphHopper (español) ===")
    print("Indique el viaje desde su casa hacia la sede.")
    print("Puede salir en cualquier momento escribiendo 's' o 'salir'.")

    while True:
        origen = solicitar_direccion("Ingrese su dirección de origen", ORIGEN_DEFECTO)
        destino = solicitar_direccion("Ingrese su dirección de destino", DESTINO_DEFECTO)

        print("\nGeocodificando direcciones...")
        origen_ll = geocodificar(origen)
        destino_ll = geocodificar(destino)

        if origen_ll is None:
            print("No se pudo geocodificar la dirección de origen. Verifique y vuelva a intentar.\n")
            continue
        if destino_ll is None:
            print("No se pudo geocodificar la dirección de destino. Verifique y vuelva a intentar.\n")
            continue

        print(f"Origen: {origen} -> ({origen_ll[0]:.6f}, {origen_ll[1]:.6f})")
        print(f"Destino: {destino} -> ({destino_ll[0]:.6f}, {destino_ll[1]:.6f})")

        print("\nCalculando ruta...")
        ruta = rutear(origen_ll, destino_ll, vehicle="car")
        imprimir_resumen_y_instrucciones(ruta)

        seguir = input("\n¿Desea calcular otra ruta? (enter para continuar, 's' o 'salir' para terminar): ").strip().lower()
        if seguir in ("s", "salir"):
            print("Saliendo del programa. Hasta luego.")
            break

if __name__ == "__main__":
    main()
