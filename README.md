# Optimisation d'images WebP avec PHP

## Installation et Configuration

### Prérequis
- PHP avec l'extension **GD** activée
- Images source au format JPG dans `1012B767/images/lv1/`

### Activation de GD dans PHP
```bash
# 1. Copier le fichier de configuration
cp C:/php/php.ini-development C:/php/php.ini

# 2. Éditer php.ini et décommenter la ligne :
extension=gd

# 3. Vérifier que GD est activé
php -m | grep gd
```

## Utilisation

```bash
php optimize-to-webp.php
```

## Comment ça fonctionne

### Bibliothèque utilisée : GD (Graphics Draw)
Extension native PHP pour la manipulation d'images.

### Fonctions GD principales
- **`imagecreatefromjpeg()`** : Charge une image JPG
- **`imagecreatetruecolor()`** : Crée une image vide
- **`imagesx()`/`imagesy()`** : Dimensions de l'image
- **`imagecopyresampled()`** : Redimensionne avec antialiasing
- **`imagewebp()`** : Sauvegarde en WebP
- **`imagejpeg()`** : Sauvegarde en JPEG
- **`imagedestroy()`** : Libère la mémoire

### Processus d'optimisation

1. **Lecture des images** : Toutes les images `.jpg` du dossier source

2. **Redimensionnement intelligent** :
   - Calcul du ratio pour conserver les proportions
   - Création d'un canvas 112x112 avec fond blanc
   - Centrage de l'image redimensionnée

3. **Compression adaptative** :
   - Test WebP : qualités 95, 90, 85, 80, 75, 70, 65, 60
   - Si taille > 20KB : test JPEG qualités 50, 45, 40, 35, 30, 25, 20, 15, 10
   - Sélection du meilleur format sous 20KB

4. **Sauvegarde** : Dans le dossier `optimized-webp-php/`

### Configuration

```php
$input_dir = '1012B767/images/lv1/';     // Dossier source
$output_dir = 'optimized-webp-php/';     // Dossier de sortie
$target_width = 112;                     // Largeur cible
$target_height = 112;                    // Hauteur cible
$max_file_size = 20 * 1024;             // 20KB maximum
```

### Résultats

- **48 images traitées** → toutes < 20KB
- **Taille moyenne** : 1.81 KB par image
- **Format privilégié** : WebP (meilleure compression)
- **Fallback** : JPEG si WebP trop lourd

## Visualiseur 360° (viewer-webp-php.html)

### Logique JavaScript

Le visualiseur utilise une **classe ES6 `WebPViewer360`** qui gère l'animation 360° des images optimisées.

#### Fonctionnalités principales

1. **Détection WebP** : Teste si le navigateur supporte WebP
2. **Chargement intelligent** : Charge WebP si supporté, sinon fallback JPEG
3. **Animation fluide** : 50ms entre chaque frame (20 FPS)
4. **Modes d'animation** :
   - **Initial** : 2 tours automatiques au démarrage
   - **Hover** : Animation continue au survol
   - **Finishing** : Finit le tour en cours quand on quitte le survol

#### Architecture JavaScript

```javascript
class WebPViewer360 {
    constructor() {
        this.imageCount = 48;           // 48 images
        this.frameDelay = 50;           // 50ms entre frames
        this.imagePath = 'optimized-webp-php/';
        this.images = [];               // Tableau des éléments img
        this.currentIndex = 0;          // Image actuellement visible
        this.isAnimating = false;       // État de l'animation
        this.rotationCount = 0;         // Nombre de tours complets
    }
}
```

#### Méthodes clés

- **`detectWebPSupport()`** : Détecte WebP via image base64
- **`loadAllImages()`** : Charge toutes les images en parallèle
- **`animate()`** : Boucle d'animation avec `requestAnimationFrame`
- **`showNextFrame()`** : Affiche l'image suivante (système show/hide CSS)
- **`setupEventListeners()`** : Gère survol souris + tactile mobile

#### Performance

- **Images préchargées** : Toutes les images sont en mémoire
- **Animation optimisée** : `requestAnimationFrame` pour 60fps fluide
- **Support mobile** : Événements tactiles inclus
- **Fallback gracieux** : JPEG si WebP non supporté