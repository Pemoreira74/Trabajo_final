import cv2
import numpy as np
import os

def change_filament_color(image_path, new_color_hsv, lower_yellow=np.array([15, 50, 50]), upper_yellow=np.array([50, 255, 255])):
    image = cv2.imread(image_path)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    original_hsv = hsv.copy()
    original_hsv[mask == 0] = 0
    _, original_saturation, original_value = cv2.split(original_hsv)

    new_hsv = np.zeros_like(hsv)
    new_hsv[..., 0] = new_color_hsv[0]  # Tono (H)
    new_hsv[..., 1] = new_color_hsv[1]  # Saturación (S)

    # Manejo especial para blanco y negro
    if new_color_hsv == (0, 0, 255):  # Blanco
        # Mantenemos el valor original para el blanco
        new_hsv[..., 2] = original_value
    elif new_color_hsv == (0, 0, 0):  # Negro
        new_hsv[..., 2] = original_value * 0.2  # Reducimos el valor, manteniendo sombras
    else:
        # Normalizamos el valor para otros colores
        max_original_value = np.max(original_value)
        min_original_value = np.min(original_value)
        if max_original_value - min_original_value == 0:
            original_value_normalized = original_value
        else:
            original_value_normalized = (original_value - min_original_value) / (max_original_value - min_original_value) * 255
        new_hsv[..., 2] = original_value_normalized

    new_image = cv2.cvtColor(new_hsv, cv2.COLOR_HSV2BGR)
    result = np.where(mask[..., np.newaxis], new_image, image)
    return result


def batch_change_filament_color(image_folder, colors_hsv, lower_yellow=np.array([15, 50, 50]), upper_yellow=np.array([50, 255, 255])):
    """Cambia el color del filamento a varios colores y guarda las imágenes en subcarpetas."""

    modified_folder = os.path.join(image_folder, "modified")
    os.makedirs(modified_folder, exist_ok=True)

    image_files = [f for f in os.listdir(image_folder) if f.endswith((".jpg", ".png"))]

    if not image_files:
        print("No se encontraron imágenes en la carpeta.")
        return

    for color_name, new_color_hsv in colors_hsv.items():
        color_folder = os.path.join(modified_folder, color_name)
        os.makedirs(color_folder, exist_ok=True)

        for i, filename in enumerate(image_files):
            image_path = os.path.join(image_folder, filename)
            try:
                new_image = change_filament_color(image_path, new_color_hsv, lower_yellow, upper_yellow)
                new_image_path = os.path.join(color_folder, filename)
                cv2.imwrite(new_image_path, new_image)
                print(f"Imagen {i+1}/{len(image_files)} procesada ({color_name}): {filename}")
            except Exception as e:
                print(f"Error al procesar la imagen {filename} ({color_name}): {e}")

# Definimos los colores en HSV
colors_hsv = {
    "rojo": (0, 255, 255),
    "azul": (120, 255, 255),
    "verde": (60, 255, 255),
    "blanco": (0, 0, 255),
    "negro": (0, 0, 0),
}

# Ejemplo de uso (ajusta la ruta y los rangos de color amarillo si es necesario)
image_folder = "C:/Users/pemor/OneDrive/UNAB Ciencia de Datos final/Seminario Final/Programacion/Database/no_defected"  
lower_yellow = np.array([18, 61, 61]) 
upper_yellow = np.array([50, 255, 255])
batch_change_filament_color(image_folder, colors_hsv, lower_yellow, upper_yellow)


