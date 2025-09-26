#!/usr/bin/env python3
"""
Script Python pour créer un GIF animé à partir d'images 360°
Utilise Pillow (PIL) pour la création du GIF
"""

import os
from PIL import Image
import glob

def create_360_gif():
    # Configuration
    input_dir = '1012B767/images/lv1/'
    output_file = 'product-360.gif'
    target_size = (150, 150)
    duration = 50  # millisecondes entre frames pour fluidité
    skip_frames = 0  # utiliser TOUTES les images
    quality = 85

    # Obtenir toutes les images JPG
    image_files = sorted(glob.glob(os.path.join(input_dir, '*.jpg')))

    if not image_files:
        print(f"Aucune image trouvée dans {input_dir}")
        return

    # Sélectionner les images
    if skip_frames > 0:
        selected_files = image_files[::skip_frames + 1]
    else:
        selected_files = image_files  # Utiliser toutes les images

    print(f"Traitement de {len(selected_files)} images sur {len(image_files)}...")

    # Charger et redimensionner les images
    images = []
    for i, file in enumerate(selected_files):
        try:
            img = Image.open(file)
            # Convertir en RGB si nécessaire
            if img.mode != 'RGB':
                img = img.convert('RGB')
            # Redimensionner
            img.thumbnail(target_size, Image.Resampling.LANCZOS)
            # Créer une nouvelle image avec fond blanc
            new_img = Image.new('RGB', target_size, (255, 255, 255))
            # Centrer l'image redimensionnée
            x = (target_size[0] - img.width) // 2
            y = (target_size[1] - img.height) // 2
            new_img.paste(img, (x, y))
            images.append(new_img)
            print(f"  Image {i+1}/{len(selected_files)} traitée")
        except Exception as e:
            print(f"Erreur avec {file}: {e}")

    if not images:
        print("Aucune image n'a pu être chargée")
        return

    # Créer le GIF animé
    print(f"\nCréation du GIF...")
    images[0].save(
        output_file,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,
        optimize=True,
        quality=quality
    )

    # Afficher les informations
    file_size = os.path.getsize(output_file)
    print(f"\nGIF cree avec succes !")
    print(f"  Fichier : {output_file}")
    print(f"  Taille : {file_size / 1024:.2f} KB")
    print(f"  Dimensions : {target_size[0]}x{target_size[1]} px")
    print(f"  Images utilisées : {len(images)} sur {len(image_files)}")

if __name__ == "__main__":
    # Vérifier si Pillow est installé
    try:
        from PIL import Image
        create_360_gif()
    except ImportError:
        print("Pillow n'est pas installé. Installation en cours...")
        import subprocess
        subprocess.run(["pip", "install", "Pillow"], check=True)
        print("\nPillow installé. Relancez le script.")