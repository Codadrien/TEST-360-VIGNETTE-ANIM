#!/usr/bin/env php
<?php
/**
 * Script pour optimiser les images en WebP 112x112 avec compression maximale
 * Objectif : 20KB par image
 */

// Configuration
$input_dir = '1012B767/images/lv1/';
$output_dir = 'optimized-webp-php/';
$target_width = 112;
$target_height = 112;
$max_file_size = 20 * 1024; // 20KB en bytes

// Créer le dossier de sortie s'il n'existe pas
if (!is_dir($output_dir)) {
    mkdir($output_dir, 0755, true);
}

// Fonction pour redimensionner et centrer l'image
function resizeImage($source_image, $target_width, $target_height) {
    $source_width = imagesx($source_image);
    $source_height = imagesy($source_image);

    // Calculer le ratio pour conserver les proportions
    $ratio_w = $target_width / $source_width;
    $ratio_h = $target_height / $source_height;
    $ratio = min($ratio_w, $ratio_h);

    // Nouvelles dimensions
    $new_width = round($source_width * $ratio);
    $new_height = round($source_height * $ratio);

    // Créer l'image de destination avec fond blanc
    $dest_image = imagecreatetruecolor($target_width, $target_height);
    $white = imagecolorallocate($dest_image, 255, 255, 255);
    imagefill($dest_image, 0, 0, $white);

    // Calculer la position pour centrer l'image
    $x = round(($target_width - $new_width) / 2);
    $y = round(($target_height - $new_height) / 2);

    // Redimensionner et copier l'image
    imagecopyresampled(
        $dest_image, $source_image,
        $x, $y, 0, 0,
        $new_width, $new_height,
        $source_width, $source_height
    );

    return $dest_image;
}

// Fonction pour sauvegarder l'image avec la bonne qualité
function saveOptimizedImage($image, $output_path, $max_file_size) {
    $base_name = basename($output_path, '.webp');
    $webp_path = dirname($output_path) . '/' . $base_name . '.webp';
    $jpg_path = dirname($output_path) . '/' . $base_name . '.jpg';

    $best_size = PHP_INT_MAX;
    $best_format = null;
    $best_quality = 0;
    $best_path = null;

    // Essayer WebP avec différentes qualités
    $webp_qualities = [95, 90, 85, 80, 75, 70, 65, 60];
    foreach ($webp_qualities as $quality) {
        // Sauvegarder en WebP
        imagewebp($image, $webp_path, $quality);
        $file_size = filesize($webp_path);

        if ($file_size <= $max_file_size) {
            $best_size = $file_size;
            $best_format = 'WEBP';
            $best_quality = $quality;
            $best_path = $webp_path;
            break;
        } elseif ($file_size < $best_size) {
            $best_size = $file_size;
            $best_format = 'WEBP';
            $best_quality = $quality;
            $best_path = $webp_path;
        }
    }

    // Si WebP est trop gros, essayer JPEG
    if ($best_size > $max_file_size) {
        for ($quality = 50; $quality >= 10; $quality -= 5) {
            imagejpeg($image, $jpg_path, $quality);
            $file_size = filesize($jpg_path);

            if ($file_size <= $max_file_size) {
                // Supprimer le WebP si on utilise JPEG
                if (file_exists($webp_path)) {
                    unlink($webp_path);
                }
                $best_size = $file_size;
                $best_format = 'JPEG';
                $best_quality = $quality;
                $best_path = $jpg_path;
                break;
            }
        }
    } else {
        // Si on utilise WebP, supprimer le JPEG temporaire s'il existe
        if (file_exists($jpg_path)) {
            unlink($jpg_path);
        }
    }

    return [
        'format' => $best_format,
        'size' => $best_size,
        'quality' => $best_quality,
        'path' => $best_path
    ];
}

// Obtenir toutes les images JPG
$image_files = glob($input_dir . '*.jpg');
sort($image_files);

if (empty($image_files)) {
    echo "Aucune image trouvée dans $input_dir\n";
    exit(1);
}

echo "Optimisation de " . count($image_files) . " images en WebP 112x112...\n";
echo "Objectif : < 20KB par image (qualité maximale)\n\n";

$total_size = 0;
$results = [];
$count = 0;

foreach ($image_files as $file) {
    $count++;
    try {
        // Charger l'image
        $source_image = imagecreatefromjpeg($file);

        if (!$source_image) {
            throw new Exception("Impossible de charger l'image");
        }

        // Redimensionner l'image
        $resized_image = resizeImage($source_image, $target_width, $target_height);

        // Nom du fichier de sortie
        $base_name = basename($file, '.jpg');
        $output_file = $output_dir . $base_name;

        // Sauvegarder avec optimisation
        $result = saveOptimizedImage($resized_image, $output_file, $max_file_size);

        // Libérer la mémoire
        imagedestroy($source_image);
        imagedestroy($resized_image);

        // Enregistrer les résultats
        $results[] = [
            'file' => basename($file),
            'format' => $result['format'],
            'size' => $result['size'],
            'quality' => $result['quality']
        ];

        $total_size += $result['size'];

        // Afficher la progression
        printf("  [%d/%d] %s -> %s (%.1fKB, Q=%d)\n",
            $count, count($image_files),
            basename($file),
            $result['format'],
            $result['size'] / 1024,
            $result['quality']
        );

    } catch (Exception $e) {
        echo "Erreur avec $file: " . $e->getMessage() . "\n";
    }
}

// Statistiques finales
echo "\n" . str_repeat('=', 50) . "\n";
echo "RÉSUMÉ DE L'OPTIMISATION\n";
echo str_repeat('=', 50) . "\n";
echo "Images traitées : " . count($results) . "\n";
printf("Taille totale : %.2f KB (%.2f MB)\n",
    $total_size / 1024,
    $total_size / 1024 / 1024
);
if (count($results) > 0) {
    printf("Taille moyenne : %.2f KB par image\n",
        ($total_size / count($results) / 1024)
    );
}

// Compter les formats
$webp_count = 0;
$jpeg_count = 0;
foreach ($results as $r) {
    if ($r['format'] == 'WEBP') $webp_count++;
    if ($r['format'] == 'JPEG') $jpeg_count++;
}
echo "Format WebP : $webp_count images\n";
echo "Format JPEG : $jpeg_count images\n";

// Images dépassant 20KB
$over_20kb = array_filter($results, function($r) use ($max_file_size) {
    return $r['size'] > $max_file_size;
});

if (!empty($over_20kb)) {
    echo "\nATTENTION: " . count($over_20kb) . " images dépassent 20KB :\n";
    foreach ($over_20kb as $r) {
        printf("  - %s: %.1fKB\n", $r['file'], $r['size'] / 1024);
    }
} else {
    echo "\nOK: Toutes les images font moins de 20KB !\n";
}

echo "\nOptimisation terminée. Les images sont dans le dossier : $output_dir\n";