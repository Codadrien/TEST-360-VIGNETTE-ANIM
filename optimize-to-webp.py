#!/usr/bin/env python3
"""
Script pour optimiser les images en WebP 150x150 avec compression maximale
Objectif : 10KB par image
"""

import os
import glob
from PIL import Image

def optimize_images_to_webp():
    # Configuration
    input_dir = '1012B767/images/lv1/'
    output_dir = 'optimized-webp/'
    target_size = (112, 112)
    max_file_size = 20 * 1024  # 20KB en bytes (plus de qualité)

    # Créer le dossier de sortie
    os.makedirs(output_dir, exist_ok=True)

    # Obtenir toutes les images JPG
    image_files = sorted(glob.glob(os.path.join(input_dir, '*.jpg')))

    if not image_files:
        print(f"Aucune image trouvée dans {input_dir}")
        return

    print(f"Optimisation de {len(image_files)} images en WebP 112x112...")
    print("Objectif : < 20KB par image (qualite maximale)\n")

    total_size = 0
    results = []

    for i, file in enumerate(image_files):
        try:
            # Ouvrir l'image
            img = Image.open(file)

            # Convertir en RGB si nécessaire
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Redimensionner avec haute qualité
            img.thumbnail(target_size, Image.Resampling.LANCZOS)

            # Créer une nouvelle image avec fond blanc
            new_img = Image.new('RGB', target_size, (255, 255, 255))
            x = (target_size[0] - img.width) // 2
            y = (target_size[1] - img.height) // 2
            new_img.paste(img, (x, y))

            # Nom du fichier de sortie
            base_name = os.path.basename(file)
            output_file_webp = os.path.join(output_dir, base_name.replace('.jpg', '.webp'))
            output_file_jpg = os.path.join(output_dir, base_name)

            # Essayer différentes qualités pour atteindre 10KB
            best_quality = 0
            best_size = float('inf')
            best_format = None

            # Test WebP avec qualité élevée (on a de la marge)
            for quality in [95, 90, 85, 80, 75, 70]:
                new_img.save(output_file_webp, 'WEBP', quality=quality, method=6)
                file_size = os.path.getsize(output_file_webp)

                if file_size <= max_file_size:
                    best_quality = quality
                    best_size = file_size
                    best_format = 'WEBP'
                    break
                elif file_size < best_size:
                    best_quality = quality
                    best_size = file_size
                    best_format = 'WEBP'

            # Si WebP est encore trop gros, essayer JPEG très compressé
            if best_size > max_file_size:
                for quality in range(50, 5, -5):
                    new_img.save(output_file_jpg, 'JPEG', quality=quality, optimize=True)
                    file_size = os.path.getsize(output_file_jpg)

                    if file_size <= max_file_size:
                        best_quality = quality
                        best_size = file_size
                        best_format = 'JPEG'
                        # Supprimer le WebP si on utilise JPEG
                        if os.path.exists(output_file_webp):
                            os.remove(output_file_webp)
                        break

            # Si on utilise WebP, supprimer le JPEG temporaire
            if best_format == 'WEBP' and os.path.exists(output_file_jpg):
                os.remove(output_file_jpg)

            # Enregistrer les résultats
            results.append({
                'file': base_name,
                'format': best_format,
                'size': best_size,
                'quality': best_quality
            })

            total_size += best_size

            # Afficher la progression
            print(f"  [{i+1}/{len(image_files)}] {base_name} -> {best_format} "
                  f"({best_size/1024:.1f}KB, Q={best_quality})")

        except Exception as e:
            print(f"Erreur avec {file}: {e}")

    # Statistiques finales
    print(f"\n{'='*50}")
    print(f"RÉSUMÉ DE L'OPTIMISATION")
    print(f"{'='*50}")
    print(f"Images traitées : {len(results)}")
    print(f"Taille totale : {total_size/1024:.2f} KB ({total_size/1024/1024:.2f} MB)")
    print(f"Taille moyenne : {(total_size/len(results)/1024):.2f} KB par image")

    # Compter les formats
    webp_count = sum(1 for r in results if r['format'] == 'WEBP')
    jpeg_count = sum(1 for r in results if r['format'] == 'JPEG')
    print(f"Format WebP : {webp_count} images")
    print(f"Format JPEG : {jpeg_count} images")

    # Images dépassant 20KB
    over_20kb = [r for r in results if r['size'] > max_file_size]
    if over_20kb:
        print(f"\nATTENTION: {len(over_20kb)} images dépassent 20KB :")
        for r in over_20kb:
            print(f"  - {r['file']}: {r['size']/1024:.1f}KB")
    else:
        print(f"\nOK: Toutes les images font moins de 20KB !")

    return results

if __name__ == "__main__":
    optimize_images_to_webp()