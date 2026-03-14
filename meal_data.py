import random
import re
from collections import defaultdict

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

ACOMPAÑAMIENTOS_LISTA = [
    "arroz", "pastas", "papas", "batatas", "puré",
    "ensalada", "verduras al horno", "tortillas", "legumbres"
]

# ─── Ingredientes por acompañamiento (para 5 personas) ───────────────────────
ACOMP_INGREDIENTES = {
    "arroz": [
        {"nombre": "arroz", "cantidad": "500 g", "categoria": "secos"},
        {"nombre": "aceite", "cantidad": "30 ml", "categoria": "otros"},
    ],
    "pastas": [
        {"nombre": "fideos (spaghetti o penne)", "cantidad": "500 g", "categoria": "secos"},
        {"nombre": "sal", "cantidad": "al gusto", "categoria": "otros"},
        {"nombre": "aceite de oliva", "cantidad": "30 ml", "categoria": "otros"},
    ],
    "papas": [
        {"nombre": "papa", "cantidad": "1.2 kg", "categoria": "verduras"},
        {"nombre": "aceite", "cantidad": "80 ml", "categoria": "otros"},
        {"nombre": "sal", "cantidad": "al gusto", "categoria": "otros"},
    ],
    "batatas": [
        {"nombre": "batata", "cantidad": "1.2 kg", "categoria": "verduras"},
        {"nombre": "aceite de oliva", "cantidad": "50 ml", "categoria": "otros"},
        {"nombre": "miel", "cantidad": "30 ml", "categoria": "otros"},
    ],
    "puré": [
        {"nombre": "papa", "cantidad": "1.5 kg", "categoria": "verduras"},
        {"nombre": "leche", "cantidad": "300 ml", "categoria": "lácteos"},
        {"nombre": "manteca", "cantidad": "80 g", "categoria": "lácteos"},
        {"nombre": "nuez moscada", "cantidad": "al gusto", "categoria": "otros"},
    ],
    "ensalada": [
        {"nombre": "lechuga", "cantidad": "1 planta", "categoria": "verduras"},
        {"nombre": "tomate", "cantidad": "2 unidades", "categoria": "verduras"},
        {"nombre": "aceite y vinagre", "cantidad": "al gusto", "categoria": "otros"},
    ],
    "verduras al horno": [
        {"nombre": "zapallito", "cantidad": "2 unidades", "categoria": "verduras"},
        {"nombre": "berenjena", "cantidad": "1 unidad", "categoria": "verduras"},
        {"nombre": "pimiento rojo", "cantidad": "1 unidad", "categoria": "verduras"},
        {"nombre": "aceite de oliva", "cantidad": "50 ml", "categoria": "otros"},
    ],
    "tortillas": [
        {"nombre": "tortillas de harina", "cantidad": "10 unidades", "categoria": "secos"},
        {"nombre": "lechuga", "cantidad": "1 planta", "categoria": "verduras"},
        {"nombre": "tomate", "cantidad": "2 unidades", "categoria": "verduras"},
    ],
    "legumbres": [
        {"nombre": "lentejas o garbanzos", "cantidad": "400 g", "categoria": "secos"},
        {"nombre": "aceite de oliva", "cantidad": "50 ml", "categoria": "otros"},
        {"nombre": "cebolla", "cantidad": "1 unidad", "categoria": "verduras"},
    ],
}

# ─── Base de datos de comidas por ingrediente base ───────────────────────────
MEALS_DB = {
    "carne vacuna": {
        "almuerzos": [
            {
                "id": "milanesas",
                "plato": "Milanesas",
                "acompañamientos_validos": ["puré", "papas", "ensalada", "arroz"],
                "ingredientes": [
                    {"nombre": "carne (nalga o peceto)", "cantidad": "1.2 kg", "categoria": "carnes"},
                    {"nombre": "huevos", "cantidad": "4 unidades", "categoria": "lácteos"},
                    {"nombre": "pan rallado", "cantidad": "250 g", "categoria": "secos"},
                    {"nombre": "ajo", "cantidad": "3 dientes", "categoria": "verduras"},
                    {"nombre": "perejil fresco", "cantidad": "1 atado", "categoria": "verduras"},
                    {"nombre": "aceite para fritura", "cantidad": "300 ml", "categoria": "otros"},
                ]
            },
            {
                "id": "asado",
                "plato": "Asado criollo",
                "acompañamientos_validos": ["ensalada", "papas", "verduras al horno", "batatas"],
                "ingredientes": [
                    {"nombre": "tira de asado", "cantidad": "1.5 kg", "categoria": "carnes"},
                    {"nombre": "chorizo", "cantidad": "500 g", "categoria": "carnes"},
                    {"nombre": "morcilla", "cantidad": "4 unidades", "categoria": "carnes"},
                    {"nombre": "sal gruesa", "cantidad": "50 g", "categoria": "secos"},
                    {"nombre": "chimichurri (preparado)", "cantidad": "1 frasco", "categoria": "otros"},
                ]
            },
            {
                "id": "bifes_criolla",
                "plato": "Bifes a la criolla",
                "acompañamientos_validos": ["arroz", "papas", "puré", "ensalada"],
                "ingredientes": [
                    {"nombre": "bifes de chorizo", "cantidad": "1.5 kg", "categoria": "carnes"},
                    {"nombre": "cebolla", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "tomate", "cantidad": "3 unidades", "categoria": "verduras"},
                    {"nombre": "pimiento rojo", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "aceite", "cantidad": "50 ml", "categoria": "otros"},
                ]
            },
            {
                "id": "guiso_carne",
                "plato": "Guiso de carne con verduras",
                "acompañamientos_validos": ["arroz", "pastas", "papas"],
                "ingredientes": [
                    {"nombre": "carne para guiso (paleta o rosbif)", "cantidad": "1 kg", "categoria": "carnes"},
                    {"nombre": "papa", "cantidad": "500 g", "categoria": "verduras"},
                    {"nombre": "zanahoria", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "cebolla", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "tomate triturado", "cantidad": "400 g", "categoria": "otros"},
                    {"nombre": "caldo de carne", "cantidad": "500 ml", "categoria": "otros"},
                ]
            },
            {
                "id": "albondigas",
                "plato": "Albóndigas en salsa",
                "acompañamientos_validos": ["arroz", "pastas", "puré"],
                "ingredientes": [
                    {"nombre": "carne picada común", "cantidad": "1 kg", "categoria": "carnes"},
                    {"nombre": "huevos", "cantidad": "2 unidades", "categoria": "lácteos"},
                    {"nombre": "pan rallado", "cantidad": "100 g", "categoria": "secos"},
                    {"nombre": "tomate triturado", "cantidad": "800 g", "categoria": "otros"},
                    {"nombre": "cebolla", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "ajo", "cantidad": "3 dientes", "categoria": "verduras"},
                ]
            },
            {
                "id": "carbonada",
                "plato": "Carbonada criolla",
                "acompañamientos_validos": ["arroz", "papas", "batatas"],
                "ingredientes": [
                    {"nombre": "carne para guiso", "cantidad": "1 kg", "categoria": "carnes"},
                    {"nombre": "zapallo", "cantidad": "500 g", "categoria": "verduras"},
                    {"nombre": "papa", "cantidad": "300 g", "categoria": "verduras"},
                    {"nombre": "choclo", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "durazno en almíbar", "cantidad": "1 lata", "categoria": "otros"},
                    {"nombre": "caldo de carne", "cantidad": "1 litro", "categoria": "otros"},
                ]
            },
        ],
        "cenas": [
            {
                "id": "sandwich_milanesa",
                "plato": "Sándwiches de milanesa",
                "acompañamientos_validos": ["ensalada", "papas"],
                "ingredientes": [
                    {"nombre": "pan francés o de milanesa", "cantidad": "5 unidades", "categoria": "secos"},
                    {"nombre": "lechuga", "cantidad": "1 planta", "categoria": "verduras"},
                    {"nombre": "tomate", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "mayonesa", "cantidad": "200 g", "categoria": "otros"},
                ]
            },
            {
                "id": "empanadas_carne",
                "plato": "Empanadas de carne",
                "acompañamientos_validos": ["ensalada", "verduras al horno"],
                "ingredientes": [
                    {"nombre": "tapas de empanada al horno", "cantidad": "2 paquetes", "categoria": "secos"},
                    {"nombre": "carne picada especial", "cantidad": "600 g", "categoria": "carnes"},
                    {"nombre": "cebolla de verdeo", "cantidad": "2 atados", "categoria": "verduras"},
                    {"nombre": "huevo duro", "cantidad": "3 unidades", "categoria": "lácteos"},
                    {"nombre": "aceitunas", "cantidad": "100 g", "categoria": "otros"},
                    {"nombre": "pimentón dulce", "cantidad": "1 cdta", "categoria": "otros"},
                ]
            },
            {
                "id": "carne_al_horno",
                "plato": "Carne al horno con vegetales",
                "acompañamientos_validos": ["papas", "batatas", "verduras al horno", "ensalada"],
                "ingredientes": [
                    {"nombre": "colita de cuadril", "cantidad": "1.5 kg", "categoria": "carnes"},
                    {"nombre": "zanahoria", "cantidad": "3 unidades", "categoria": "verduras"},
                    {"nombre": "cebolla", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "ajo", "cantidad": "4 dientes", "categoria": "verduras"},
                    {"nombre": "vino blanco", "cantidad": "200 ml", "categoria": "otros"},
                ]
            },
            {
                "id": "revuelto_gramajo",
                "plato": "Revuelto Gramajo",
                "acompañamientos_validos": ["ensalada", "papas"],
                "ingredientes": [
                    {"nombre": "papas fritas en bastones", "cantidad": "600 g", "categoria": "verduras"},
                    {"nombre": "jamón cocido", "cantidad": "200 g", "categoria": "carnes"},
                    {"nombre": "huevos", "cantidad": "6 unidades", "categoria": "lácteos"},
                    {"nombre": "cebolla de verdeo", "cantidad": "1 atado", "categoria": "verduras"},
                ]
            },
            {
                "id": "tortilla_carne",
                "plato": "Tortilla de papa y carne",
                "acompañamientos_validos": ["ensalada", "verduras al horno"],
                "ingredientes": [
                    {"nombre": "papa", "cantidad": "800 g", "categoria": "verduras"},
                    {"nombre": "huevos", "cantidad": "6 unidades", "categoria": "lácteos"},
                    {"nombre": "carne picada", "cantidad": "400 g", "categoria": "carnes"},
                    {"nombre": "cebolla", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "aceite", "cantidad": "100 ml", "categoria": "otros"},
                ]
            },
        ]
    },

    "pollo": {
        "almuerzos": [
            {
                "id": "pollo_al_horno",
                "plato": "Pollo al horno",
                "acompañamientos_validos": ["papas", "batatas", "verduras al horno", "arroz"],
                "ingredientes": [
                    {"nombre": "pollo entero o presas", "cantidad": "2 kg", "categoria": "carnes"},
                    {"nombre": "ajo", "cantidad": "5 dientes", "categoria": "verduras"},
                    {"nombre": "limón", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "romero fresco", "cantidad": "2 ramitas", "categoria": "otros"},
                    {"nombre": "aceite de oliva", "cantidad": "80 ml", "categoria": "otros"},
                    {"nombre": "pimentón", "cantidad": "1 cdta", "categoria": "otros"},
                ]
            },
            {
                "id": "arroz_con_pollo",
                "plato": "Arroz con pollo a la porteña",
                "acompañamientos_validos": ["ensalada", "verduras al horno"],
                "ingredientes": [
                    {"nombre": "pollo trozado", "cantidad": "1.5 kg", "categoria": "carnes"},
                    {"nombre": "arroz", "cantidad": "400 g", "categoria": "secos"},
                    {"nombre": "pimiento rojo", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "cebolla", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "tomate", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "caldo de pollo", "cantidad": "1 litro", "categoria": "otros"},
                    {"nombre": "cúrcuma", "cantidad": "1 cdta", "categoria": "otros"},
                ]
            },
            {
                "id": "supremas_napolitana",
                "plato": "Supremas a la napolitana",
                "acompañamientos_validos": ["arroz", "pastas", "puré", "papas"],
                "ingredientes": [
                    {"nombre": "supremas de pollo", "cantidad": "1.5 kg", "categoria": "carnes"},
                    {"nombre": "salsa de tomate", "cantidad": "400 g", "categoria": "otros"},
                    {"nombre": "jamón cocido", "cantidad": "200 g", "categoria": "carnes"},
                    {"nombre": "queso mozzarella", "cantidad": "300 g", "categoria": "lácteos"},
                    {"nombre": "huevos", "cantidad": "3 unidades", "categoria": "lácteos"},
                    {"nombre": "pan rallado", "cantidad": "200 g", "categoria": "secos"},
                ]
            },
            {
                "id": "pollo_disco",
                "plato": "Pollo al disco con verduras",
                "acompañamientos_validos": ["arroz", "papas", "tortillas"],
                "ingredientes": [
                    {"nombre": "pollo trozado", "cantidad": "1.5 kg", "categoria": "carnes"},
                    {"nombre": "pimiento rojo", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "cebolla", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "zapallito", "cantidad": "3 unidades", "categoria": "verduras"},
                    {"nombre": "vino blanco", "cantidad": "200 ml", "categoria": "otros"},
                    {"nombre": "caldo de pollo", "cantidad": "500 ml", "categoria": "otros"},
                ]
            },
            {
                "id": "pechugas_rellenas",
                "plato": "Pechugas rellenas al horno",
                "acompañamientos_validos": ["puré", "arroz", "ensalada", "papas"],
                "ingredientes": [
                    {"nombre": "pechugas de pollo enteras", "cantidad": "1.5 kg", "categoria": "carnes"},
                    {"nombre": "jamón cocido", "cantidad": "150 g", "categoria": "carnes"},
                    {"nombre": "queso en fetas", "cantidad": "150 g", "categoria": "lácteos"},
                    {"nombre": "pimiento rojo asado", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "crema de leche", "cantidad": "200 ml", "categoria": "lácteos"},
                ]
            },
        ],
        "cenas": [
            {
                "id": "ensalada_pollo",
                "plato": "Ensalada completa de pollo",
                "acompañamientos_validos": ["ensalada", "arroz"],
                "ingredientes": [
                    {"nombre": "lechuga", "cantidad": "1 planta", "categoria": "verduras"},
                    {"nombre": "tomate cherry", "cantidad": "300 g", "categoria": "verduras"},
                    {"nombre": "choclo en lata", "cantidad": "1 lata", "categoria": "otros"},
                    {"nombre": "mayonesa", "cantidad": "200 g", "categoria": "otros"},
                    {"nombre": "zanahoria rallada", "cantidad": "2 unidades", "categoria": "verduras"},
                ]
            },
            {
                "id": "sopa_pollo",
                "plato": "Sopa de pollo con fideos",
                "acompañamientos_validos": ["pastas", "arroz"],
                "ingredientes": [
                    {"nombre": "fideos cabellito o letras", "cantidad": "300 g", "categoria": "secos"},
                    {"nombre": "zanahoria", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "apio", "cantidad": "2 tallos", "categoria": "verduras"},
                    {"nombre": "caldo de pollo", "cantidad": "2 litros", "categoria": "otros"},
                    {"nombre": "papa", "cantidad": "2 unidades", "categoria": "verduras"},
                ]
            },
            {
                "id": "milanesas_pollo",
                "plato": "Milanesas de pollo",
                "acompañamientos_validos": ["papas", "ensalada", "puré"],
                "ingredientes": [
                    {"nombre": "huevos", "cantidad": "3 unidades", "categoria": "lácteos"},
                    {"nombre": "pan rallado", "cantidad": "200 g", "categoria": "secos"},
                    {"nombre": "ajo y perejil", "cantidad": "1 cdta", "categoria": "otros"},
                    {"nombre": "aceite para fritura", "cantidad": "300 ml", "categoria": "otros"},
                ]
            },
            {
                "id": "wraps_pollo",
                "plato": "Wraps de pollo y vegetales",
                "acompañamientos_validos": ["ensalada", "papas"],
                "ingredientes": [
                    {"nombre": "tortillas de harina grandes", "cantidad": "10 unidades", "categoria": "secos"},
                    {"nombre": "lechuga", "cantidad": "1 planta", "categoria": "verduras"},
                    {"nombre": "tomate", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "palta", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "queso rallado", "cantidad": "150 g", "categoria": "lácteos"},
                ]
            },
            {
                "id": "pollo_grillado",
                "plato": "Pollo grillado con chimichurri",
                "acompañamientos_validos": ["verduras al horno", "ensalada", "papas"],
                "ingredientes": [
                    {"nombre": "chimichurri", "cantidad": "200 g", "categoria": "otros"},
                    {"nombre": "limón", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "aceite de oliva", "cantidad": "50 ml", "categoria": "otros"},
                ]
            },
        ]
    },

    "pescado": {
        "almuerzos": [
            {
                "id": "merluza_al_horno",
                "plato": "Merluza al horno con papas",
                "acompañamientos_validos": ["papas", "verduras al horno", "ensalada"],
                "ingredientes": [
                    {"nombre": "filetes de merluza", "cantidad": "1.5 kg", "categoria": "carnes"},
                    {"nombre": "limón", "cantidad": "3 unidades", "categoria": "verduras"},
                    {"nombre": "ajo", "cantidad": "4 dientes", "categoria": "verduras"},
                    {"nombre": "perejil fresco", "cantidad": "1 atado", "categoria": "verduras"},
                    {"nombre": "aceite de oliva", "cantidad": "80 ml", "categoria": "otros"},
                    {"nombre": "sal y pimienta", "cantidad": "al gusto", "categoria": "otros"},
                ]
            },
            {
                "id": "cazuela_mariscos",
                "plato": "Cazuela de mariscos",
                "acompañamientos_validos": ["arroz", "pastas", "papas"],
                "ingredientes": [
                    {"nombre": "mejillones", "cantidad": "1 kg", "categoria": "carnes"},
                    {"nombre": "camarones", "cantidad": "500 g", "categoria": "carnes"},
                    {"nombre": "calamar", "cantidad": "400 g", "categoria": "carnes"},
                    {"nombre": "cebolla", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "tomate triturado", "cantidad": "400 g", "categoria": "otros"},
                    {"nombre": "pimiento rojo", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "vino blanco", "cantidad": "200 ml", "categoria": "otros"},
                ]
            },
            {
                "id": "filet_rebozado",
                "plato": "Filet de merluza rebozado",
                "acompañamientos_validos": ["puré", "papas", "ensalada", "arroz"],
                "ingredientes": [
                    {"nombre": "filetes de merluza", "cantidad": "1.5 kg", "categoria": "carnes"},
                    {"nombre": "huevos", "cantidad": "3 unidades", "categoria": "lácteos"},
                    {"nombre": "pan rallado", "cantidad": "200 g", "categoria": "secos"},
                    {"nombre": "harina", "cantidad": "100 g", "categoria": "secos"},
                    {"nombre": "aceite para fritura", "cantidad": "500 ml", "categoria": "otros"},
                    {"nombre": "limón", "cantidad": "3 unidades", "categoria": "verduras"},
                ]
            },
            {
                "id": "salmon_limon",
                "plato": "Salmón al horno con limón",
                "acompañamientos_validos": ["arroz", "ensalada", "verduras al horno", "papas"],
                "ingredientes": [
                    {"nombre": "salmón en filetes", "cantidad": "1.5 kg", "categoria": "carnes"},
                    {"nombre": "limón", "cantidad": "3 unidades", "categoria": "verduras"},
                    {"nombre": "eneldo seco", "cantidad": "2 cdtas", "categoria": "otros"},
                    {"nombre": "manteca", "cantidad": "50 g", "categoria": "lácteos"},
                    {"nombre": "ajo", "cantidad": "3 dientes", "categoria": "verduras"},
                    {"nombre": "alcaparras", "cantidad": "50 g", "categoria": "otros"},
                ]
            },
        ],
        "cenas": [
            {
                "id": "tortilla_atun",
                "plato": "Tortilla de atún",
                "acompañamientos_validos": ["ensalada", "papas"],
                "ingredientes": [
                    {"nombre": "atún en lata (al natural)", "cantidad": "4 latas", "categoria": "carnes"},
                    {"nombre": "huevos", "cantidad": "6 unidades", "categoria": "lácteos"},
                    {"nombre": "cebolla", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "pimiento rojo", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "aceite", "cantidad": "80 ml", "categoria": "otros"},
                ]
            },
            {
                "id": "fideos_atun",
                "plato": "Fideos con atún y tomate",
                "acompañamientos_validos": ["pastas", "arroz"],
                "ingredientes": [
                    {"nombre": "fideos (spaghetti o linguine)", "cantidad": "500 g", "categoria": "secos"},
                    {"nombre": "atún en lata", "cantidad": "3 latas", "categoria": "carnes"},
                    {"nombre": "tomate triturado", "cantidad": "400 g", "categoria": "otros"},
                    {"nombre": "ajo", "cantidad": "3 dientes", "categoria": "verduras"},
                    {"nombre": "aceitunas negras", "cantidad": "100 g", "categoria": "otros"},
                ]
            },
            {
                "id": "ensalada_nicoise",
                "plato": "Ensalada niçoise",
                "acompañamientos_validos": ["ensalada", "papas"],
                "ingredientes": [
                    {"nombre": "atún en lata", "cantidad": "3 latas", "categoria": "carnes"},
                    {"nombre": "lechuga", "cantidad": "1 planta", "categoria": "verduras"},
                    {"nombre": "tomate", "cantidad": "3 unidades", "categoria": "verduras"},
                    {"nombre": "aceitunas negras", "cantidad": "100 g", "categoria": "otros"},
                    {"nombre": "huevos duros", "cantidad": "4 unidades", "categoria": "lácteos"},
                    {"nombre": "chauchas cocidas", "cantidad": "200 g", "categoria": "verduras"},
                ]
            },
            {
                "id": "croquetas_pescado",
                "plato": "Croquetas de pescado",
                "acompañamientos_validos": ["puré", "ensalada", "papas"],
                "ingredientes": [
                    {"nombre": "pan rallado (rebozado)", "cantidad": "200 g", "categoria": "secos"},
                    {"nombre": "harina", "cantidad": "100 g", "categoria": "secos"},
                    {"nombre": "huevos", "cantidad": "3 unidades", "categoria": "lácteos"},
                    {"nombre": "aceite para fritura", "cantidad": "400 ml", "categoria": "otros"},
                    {"nombre": "perejil", "cantidad": "1 atado", "categoria": "verduras"},
                ]
            },
        ]
    },

    "legumbres": {
        "almuerzos": [
            {
                "id": "lentejas_estofadas",
                "plato": "Lentejas estofadas",
                "acompañamientos_validos": ["arroz", "papas", "verduras al horno"],
                "ingredientes": [
                    {"nombre": "lentejas", "cantidad": "600 g", "categoria": "secos"},
                    {"nombre": "chorizo colorado", "cantidad": "300 g", "categoria": "carnes"},
                    {"nombre": "panceta ahumada", "cantidad": "200 g", "categoria": "carnes"},
                    {"nombre": "zanahoria", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "cebolla", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "tomate triturado", "cantidad": "400 g", "categoria": "otros"},
                    {"nombre": "pimentón ahumado", "cantidad": "1 cdta", "categoria": "otros"},
                ]
            },
            {
                "id": "porotos_chorizo",
                "plato": "Porotos con chorizo y verduras",
                "acompañamientos_validos": ["arroz", "papas", "verduras al horno"],
                "ingredientes": [
                    {"nombre": "porotos pallares", "cantidad": "500 g", "categoria": "secos"},
                    {"nombre": "chorizo colorado", "cantidad": "400 g", "categoria": "carnes"},
                    {"nombre": "papa", "cantidad": "300 g", "categoria": "verduras"},
                    {"nombre": "zapallo", "cantidad": "400 g", "categoria": "verduras"},
                    {"nombre": "cebolla", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "caldo de verdura", "cantidad": "1 litro", "categoria": "otros"},
                ]
            },
            {
                "id": "garbanzos_al_horno",
                "plato": "Garbanzos al horno con vegetales",
                "acompañamientos_validos": ["arroz", "ensalada", "verduras al horno"],
                "ingredientes": [
                    {"nombre": "garbanzos cocidos", "cantidad": "800 g", "categoria": "secos"},
                    {"nombre": "zapallito", "cantidad": "3 unidades", "categoria": "verduras"},
                    {"nombre": "pimiento rojo", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "cebolla morada", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "tomate cherry", "cantidad": "300 g", "categoria": "verduras"},
                    {"nombre": "aceite de oliva", "cantidad": "80 ml", "categoria": "otros"},
                    {"nombre": "comino", "cantidad": "1 cdta", "categoria": "otros"},
                ]
            },
            {
                "id": "sopa_arvejas",
                "plato": "Sopa de arvejas",
                "acompañamientos_validos": ["pastas", "arroz", "papas"],
                "ingredientes": [
                    {"nombre": "arvejas secas", "cantidad": "500 g", "categoria": "secos"},
                    {"nombre": "panceta", "cantidad": "200 g", "categoria": "carnes"},
                    {"nombre": "zanahoria", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "apio", "cantidad": "2 tallos", "categoria": "verduras"},
                    {"nombre": "caldo de verdura", "cantidad": "1.5 litros", "categoria": "otros"},
                    {"nombre": "papa", "cantidad": "2 unidades", "categoria": "verduras"},
                ]
            },
        ],
        "cenas": [
            {
                "id": "sopa_lentejas",
                "plato": "Sopa de lentejas con vegetales",
                "acompañamientos_validos": ["arroz", "pastas"],
                "ingredientes": [
                    {"nombre": "zanahoria", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "papa", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "caldo de verdura", "cantidad": "1.5 litros", "categoria": "otros"},
                    {"nombre": "tomate", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "comino", "cantidad": "1 cdta", "categoria": "otros"},
                ]
            },
            {
                "id": "hummus_verduras",
                "plato": "Hummus con pan pita y vegetales",
                "acompañamientos_validos": ["ensalada", "verduras al horno"],
                "ingredientes": [
                    {"nombre": "pan pita o árabe", "cantidad": "10 unidades", "categoria": "secos"},
                    {"nombre": "tahine (pasta de sésamo)", "cantidad": "100 g", "categoria": "otros"},
                    {"nombre": "limón", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "zanahoria (bastones)", "cantidad": "3 unidades", "categoria": "verduras"},
                    {"nombre": "pepino", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "aceite de oliva", "cantidad": "50 ml", "categoria": "otros"},
                ]
            },
            {
                "id": "ensalada_garbanzos",
                "plato": "Ensalada tibia de garbanzos",
                "acompañamientos_validos": ["ensalada", "arroz"],
                "ingredientes": [
                    {"nombre": "tomate", "cantidad": "3 unidades", "categoria": "verduras"},
                    {"nombre": "pepino", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "cebolla morada", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "perejil", "cantidad": "1 atado", "categoria": "verduras"},
                    {"nombre": "aceite de oliva", "cantidad": "50 ml", "categoria": "otros"},
                ]
            },
            {
                "id": "milanesas_lentejas",
                "plato": "Milanesas de lentejas",
                "acompañamientos_validos": ["puré", "ensalada", "papas"],
                "ingredientes": [
                    {"nombre": "huevos", "cantidad": "3 unidades", "categoria": "lácteos"},
                    {"nombre": "pan rallado", "cantidad": "200 g", "categoria": "secos"},
                    {"nombre": "cebolla", "cantidad": "1 unidad", "categoria": "verduras"},
                    {"nombre": "zanahoria rallada", "cantidad": "2 unidades", "categoria": "verduras"},
                    {"nombre": "aceite para fritura", "cantidad": "200 ml", "categoria": "otros"},
                ]
            },
        ]
    }
}


# ─── Generador de plan semanal ────────────────────────────────────────────────

def generate_day(base, used_acompañamientos=None):
    """Generate a single day's meal plan for the given base ingredient."""
    if used_acompañamientos is None:
        used_acompañamientos = set()

    alm_options = MEALS_DB[base]["almuerzos"]
    cen_options = MEALS_DB[base]["cenas"]

    alm = random.choice(alm_options)
    cen = random.choice(cen_options)

    # Pick accompaniments (different from each other, try to minimize repetition)
    def pick_acomp(valid, exclude_self=None, prefer_avoid=None):
        options = [a for a in valid if a != exclude_self]
        if not options:
            options = valid
        fresh = [a for a in options if a not in (prefer_avoid or set())]
        pool = fresh if fresh else options
        return random.choice(pool)

    alm_acomp = pick_acomp(alm["acompañamientos_validos"], prefer_avoid=used_acompañamientos)
    cen_acomp = pick_acomp(cen["acompañamientos_validos"],
                           exclude_self=alm_acomp,
                           prefer_avoid=used_acompañamientos | {alm_acomp})

    # Build ingredient list (combine almuerzo + cena + accompaniments)
    ingredientes = []
    seen = set()

    def add_ings(ings):
        for ing in ings:
            key = ing["nombre"].lower()
            if key not in seen:
                seen.add(key)
                ingredientes.append(dict(ing))

    add_ings(alm["ingredientes"])
    add_ings(cen["ingredientes"])
    add_ings(ACOMP_INGREDIENTES.get(alm_acomp, []))
    add_ings(ACOMP_INGREDIENTES.get(cen_acomp, []))

    return {
        "base": base,
        "almuerzo": f"{alm['plato']} con {alm_acomp}",
        "cena": f"{cen['plato']} con {cen_acomp}",
        "almuerzo_id": alm["id"],
        "cena_id": cen["id"],
        "almuerzo_acomp": alm_acomp,
        "cena_acomp": cen_acomp,
        "ingredientes": ingredientes
    }


def generate_plan():
    """Generate a full 7-day meal plan following Argentine distribution rules."""
    bases = ["carne vacuna", "carne vacuna", "pollo", "pollo",
             "pescado", "legumbres",
             random.choice(["carne vacuna", "pollo", "pescado", "legumbres"])]
    random.shuffle(bases)

    plan = {}
    used_acompañamientos = set()
    for dia, base in zip(DIAS, bases):
        day_data = generate_day(base, used_acompañamientos)
        used_acompañamientos.add(day_data["almuerzo_acomp"])
        used_acompañamientos.add(day_data["cena_acomp"])
        plan[dia] = day_data

    return plan


def rebuild_day(base, almuerzo_id, cena_id, almuerzo_acomp, cena_acomp):
    """Rebuild a day given specific selections."""
    alm = next((m for m in MEALS_DB[base]["almuerzos"] if m["id"] == almuerzo_id), None)
    cen = next((m for m in MEALS_DB[base]["cenas"] if m["id"] == cena_id), None)
    if not alm or not cen:
        return None

    ingredientes = []
    seen = set()

    def add_ings(ings):
        for ing in ings:
            key = ing["nombre"].lower()
            if key not in seen:
                seen.add(key)
                ingredientes.append(dict(ing))

    add_ings(alm["ingredientes"])
    add_ings(cen["ingredientes"])
    add_ings(ACOMP_INGREDIENTES.get(almuerzo_acomp, []))
    add_ings(ACOMP_INGREDIENTES.get(cena_acomp, []))

    return {
        "base": base,
        "almuerzo": f"{alm['plato']} con {almuerzo_acomp}",
        "cena": f"{cen['plato']} con {cena_acomp}",
        "almuerzo_id": almuerzo_id,
        "cena_id": cena_id,
        "almuerzo_acomp": almuerzo_acomp,
        "cena_acomp": cena_acomp,
        "ingredientes": ingredientes
    }


def get_available_meals(base):
    """Return simplified meal lists for a given base ingredient."""
    if base not in MEALS_DB:
        return {}
    return {
        "almuerzos": [{"id": m["id"], "plato": m["plato"],
                       "acompañamientos": m["acompañamientos_validos"]}
                      for m in MEALS_DB[base]["almuerzos"]],
        "cenas": [{"id": m["id"], "plato": m["plato"],
                   "acompañamientos": m["acompañamientos_validos"]}
                  for m in MEALS_DB[base]["cenas"]]
    }


# ─── Generador de lista de compras ───────────────────────────────────────────

UNIT_NORMALIZE = {
    "g": "g", "gr": "g", "gramo": "g", "gramos": "g",
    "kg": "kg", "kilo": "kg", "kilos": "kg", "kilogramo": "kg", "kilogramos": "kg",
    "ml": "ml", "cc": "ml",
    "l": "l", "litro": "l", "litros": "l",
    "unidad": "unid.", "unidades": "unid.", "unid": "unid.", "un": "unid.",
    "lata": "latas", "latas": "latas",
    "atado": "atados", "atados": "atados",
    "cdta": "cdtas", "cdtas": "cdtas",
    "cda": "cdas", "cdas": "cdas",
    "diente": "dientes", "dientes": "dientes",
    "tallo": "tallos", "tallos": "tallos",
    "ramita": "ramitas", "ramitas": "ramitas",
    "frasco": "frascos", "frascos": "frascos",
    "paquete": "paquetes", "paquetes": "paquetes",
    "planta": "plantas", "plantas": "plantas",
    "sobre": "sobres", "sobres": "sobres",
}

CATEGORY_ORDER = ["carnes", "verduras", "lácteos", "secos", "otros"]


def parse_cantidad(s):
    """Parse a quantity string into (number, unit). Returns (None, s) if not parseable."""
    s = str(s).strip()
    m = re.match(r'^([\d]+(?:[.,]\d+)?)\s*(.*)$', s)
    if m:
        num = float(m.group(1).replace(",", "."))
        raw_unit = m.group(2).strip().lower()
        unit = UNIT_NORMALIZE.get(raw_unit, raw_unit)
        return num, unit
    return None, s


def convert_to_display(num, unit):
    """Convert quantities for display (g→kg if ≥1000, ml→l if ≥1000)."""
    if unit == "g" and num >= 1000:
        return f"{num / 1000:.2f}".rstrip("0").rstrip(".") + " kg"
    if unit == "ml" and num >= 1000:
        return f"{num / 1000:.2f}".rstrip("0").rstrip(".") + " l"
    if unit in ("kg", "l", "g", "ml"):
        disp = f"{num:.2f}".rstrip("0").rstrip(".")
        return f"{disp} {unit}"
    return f"{num:.0f} {unit}"


def generate_shopping_list(plan):
    """Aggregate all ingredients from the plan and return a sorted shopping list."""
    numeric = defaultdict(lambda: {"total": 0.0, "unit": "", "categoria": ""})
    non_numeric = defaultdict(lambda: {"entries": [], "categoria": ""})

    for day_data in plan.values():
        for ing in day_data.get("ingredientes", []):
            nombre = ing["nombre"].lower().strip()
            categoria = ing.get("categoria", "otros")
            num, unit = parse_cantidad(ing.get("cantidad", ""))

            if num is not None:
                key = (nombre, unit)
                numeric[key]["total"] += num
                numeric[key]["unit"] = unit
                numeric[key]["categoria"] = categoria
            else:
                non_numeric[nombre]["categoria"] = categoria
                non_numeric[nombre]["entries"].append(ing.get("cantidad", ""))

    result = []

    for (nombre, unit), data in numeric.items():
        result.append({
            "nombre": nombre.title(),
            "cantidad": convert_to_display(data["total"], unit),
            "categoria": data["categoria"]
        })

    for nombre, data in non_numeric.items():
        qty = data["entries"][0] if data["entries"] else "—"
        cnt = len(data["entries"])
        display = f"{qty} (×{cnt})" if cnt > 1 else qty
        result.append({
            "nombre": nombre.title(),
            "cantidad": display,
            "categoria": data["categoria"]
        })

    # Sort by category order then by name
    def sort_key(item):
        cat = item["categoria"]
        idx = CATEGORY_ORDER.index(cat) if cat in CATEGORY_ORDER else len(CATEGORY_ORDER)
        return (idx, item["nombre"])

    result.sort(key=sort_key)
    return result