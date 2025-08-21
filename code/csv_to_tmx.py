import csv
import os
from xml.etree.ElementTree import Element, SubElement, ElementTree

# ---- CONFIG ----
TILESIZE = 32
MAP_WIDTH = 64   # adjust to your map width in tiles
MAP_HEIGHT = 64  # adjust to your map height in tiles

# all your CSV layers
csv_layers = {
    "floor": "mappington_floor.csv",
    "details": "mappington_details.csv",
    "entities": "mappington_entities.csv",
    "objects": "mappington_objects.csv",
    "boundary": "mappington_boundary_blocks.csv"
}

# path to your tileset image (adjust this!)
tileset_image = "graphics/tileset.png"

output_file = "recovered_map.tmx"
# ----------------


def load_csv(path):
    with open(path, newline='') as f:
        reader = csv.reader(f)
        return [[int(cell) if cell.strip() != "" and cell != "-1" else 0 for cell in row] for row in reader]


def build_tmx():
    # root map element
    map_elem = Element("map", {
        "version": "1.8",
        "tiledversion": "1.8.4",
        "orientation": "orthogonal",
        "renderorder": "right-down",
        "width": str(MAP_WIDTH),
        "height": str(MAP_HEIGHT),
        "tilewidth": str(TILESIZE),
        "tileheight": str(TILESIZE),
        "infinite": "0",
        "nextlayerid": str(len(csv_layers) + 1),
        "nextobjectid": "1"
    })

    # tileset
    tileset = SubElement(map_elem, "tileset", {
        "firstgid": "1",
        "name": "tileset",
        "tilewidth": str(TILESIZE),
        "tileheight": str(TILESIZE),
        "tilecount": "1000",   # adjust if needed
        "columns": "20"        # adjust to match your tileset layout
    })
    SubElement(tileset, "image", {
        "source": tileset_image,
        "width": "640",   # adjust to actual tileset PNG width
        "height": "640"   # adjust to actual tileset PNG height
    })

    # add each CSV as a layer
    layer_id = 1
    for name, path in csv_layers.items():
        data = load_csv(path)
        layer = SubElement(map_elem, "layer", {
            "id": str(layer_id),
            "name": name,
            "width": str(MAP_WIDTH),
            "height": str(MAP_HEIGHT)
        })
        data_elem = SubElement(layer, "data", {"encoding": "csv"})
        # flatten the 2D array into CSV text
        flat = [str(cell) for row in data for cell in row]
        data_elem.text = ",".join(flat)
        layer_id += 1

    # save
    tree = ElementTree(map_elem)
    tree.write(output_file, encoding="UTF-8", xml_declaration=True)
    print(f"✅ Saved {output_file}")


if __name__ == "__main__":
    build_tmx()
