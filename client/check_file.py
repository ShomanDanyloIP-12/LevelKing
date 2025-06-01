import numbers

# Допустимі шари
ALLOWED_LAYERS = {
    'bricks bg', 'bg palms', 'water', 'interract_info', 'finish_info',
    'sign bottom', 'sign top', 'sign left', 'sign right',
    'terrain', 'bricks fg', 'platforms', 'enemies',
    'coins', 'fg objects'
}

# Максимальні межі координат
X_LIMIT = 64000
Y_LIMIT = 32000

# Максимальна кількість об'єктів у шарі
MAX_OBJECTS_PER_LAYER = 1000
MAX_TOTAL_OBJECTS = 10000

# Допустимі типи значень для кожного шару
LAYER_VALUE_TYPES = {
    'terrain': str,
    'coins': int,
    'platforms': str,
    'enemies': int,
    'bricks fg': str,
    'bricks bg': str,
    'bg palms': int,
    'fg objects': int,
    'water': str,
    'interract_info': str,
    'finish_info': str,
    'sign bottom': str,
    'sign top': str,
    'sign left': str,
    'sign right': str
}


def validate_level_data(data: list) -> bool:
    try:
        # Перевірка основної структури
        if not isinstance(data, list) or len(data) != 2:
            return False
        layers, ser_offset = data

        if not isinstance(layers, dict) or not isinstance(ser_offset, list) or len(ser_offset) != 2:
            return False
        if not all(isinstance(n, int) for n in ser_offset):
            return False

        total_objects = 0

        for layer_name, layer_data in layers.items():
            # Назва шару — тільки з whitelist
            if layer_name not in ALLOWED_LAYERS:
                return False

            if not isinstance(layer_data, dict):
                return False

            if len(layer_data) > MAX_OBJECTS_PER_LAYER:
                return False

            expected_type = LAYER_VALUE_TYPES.get(layer_name)
            if expected_type is None:
                return False

            for coords, value in layer_data.items():
                # Ключ має бути кортежем з 2 цілих чисел
                if not (isinstance(coords, tuple) and len(coords) == 2 and all(isinstance(c, int) for c in coords)):
                    return False
                x, y = coords
                if abs(x) > X_LIMIT or abs(y) > Y_LIMIT:
                    return False

                # Значення має бути потрібного типу
                if not isinstance(value, expected_type):
                    return False

                # Захист від вбудованих класів / функцій
                if isinstance(value, str):
                    if any(bad in value.lower() for bad in ['<script>', '__class__', '__globals__', 'lambda']):
                        return False
                    if len(value) > 100:  # довгі рядки не допускаються
                        return False
                if isinstance(value, int) and abs(value) > 1_000_000:
                    return False

            total_objects += len(layer_data)

        if total_objects > MAX_TOTAL_OBJECTS:
            return False

        return True

    except Exception:
        return False

# grid = [{'bricks bg': {(1024, 576): 'bricks_bg'}, 'bg palms': {(1432, 754): 18, (1683, 831): 15, (1492, 532): 16, (1074, 970): 17, (1258, 902): 18}, 'water': {(320, 640): 'top', (384, 640): 'top', (448, 640): 'top', (320, 704): 'bottom', (384, 704): 'bottom', (448, 704): 'bottom'}, 'interract_info': {(960, 0): 'interract_info'}, 'finish_info': {(1408, 64): 'finish_info'}, 'sign bottom': {(1856, 320): 'sign_bottom'}, 'sign top': {(1856, 576): 'sign_top'}, 'sign left': {(1856, 832): 'sign_left'}, 'sign right': {(1984, 768): 'sign_right'}, 'terrain': {(0, 640): '3', (64, 640): '37', (128, 640): '37', (192, 640): '37', (256, 640): '7', (384, 320): '7', (320, 320): '37', (256, 320): '37', (192, 320): '37', (128, 320): '3'}, 'bricks fg': {(832, 448): 'bricks_fg'}, 'platforms': {(512, 512): 'platform', (576, 512): 'platform', (640, 512): 'platform'}, 'enemies': {(256, 576): 7, (320, 256): 8, (128, 256): 9, (576, 256): 10, (640, 256): 10, (768, 320): 21, (832, 320): 21, (896, 320): 21, (1088, 320): 23, (1216, 384): 24, (1216, 320): 24, (1088, 256): 22, (1024, 192): 22, (960, 192): 22, (896, 192): 22, (1408, 384): 32, (1600, 256): 32}, 'coins': {(608, 416): 4, (864, 608): 5, (672, 672): 6, (800, 736): 6, (608, 800): 33}, 'fg objects': {(22, 496): 0, (1138, 508): 1, (760, 828): 11, (979, 776): 12, (1088, 731): 13, (1264, 732): 14}}, [2, 3]]
# print(validate_level_data(grid))