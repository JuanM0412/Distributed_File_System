import json

def generate_large_json(file_name, num_lines):
    with open(file_name, 'w') as f:
        f.write('[')  # Abrir la lista JSON
        for i in range(num_lines):
            # Crear un objeto JSON simple
            data = {
                "id": i + 1,
                "name": f"Item {i + 1}",
                "value": i * 10,
                "status": "active" if i % 2 == 0 else "inactive"
            }

            # Escribir cada línea en el archivo
            json.dump(data, f)
            
            # Agregar una coma si no es la última línea
            if i < num_lines - 1:
                f.write(',')
        
        f.write(']')  # Cerrar la lista JSON

if __name__ == "__main__":
    file_name = "large_data.json"
    num_lines = 10_000_000  # 100 millones de líneas
    generate_large_json(file_name, num_lines)

