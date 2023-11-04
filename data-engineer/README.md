# Test technique Data

L'objectif de cette première partie est d'évaluer votre capacité à traiter des données, à écrire du code de bonne qualité, et à réfléchir aux différents problèmes qui peuvent survenir dans un pipeline d'ingestion de données.

## Pré-requis
Le code fourni dans `data-provider` permet d'exécuter une application qui génère des données aléatoires au format [Pascal VOC](http://host.robots.ox.ac.uk/pascal/VOC/). Les annotations générées ne sont pas nécessairement correctes. Les annotations sont associées à des datasets, identifiés par les nombres 0 à 9.
`data-provider` peut s'exécuter en mode continu ou hors-ligne.  
Vous pouvez installer `data-provider` comme un module python via 
```python
pip install .
```

Pour exécuter `data-provider` en mode continu, il suffit d'appeler
```python
python -m data_provider serve \
    ENDPOINT \
    [--min-delay MIN_DELAY] \
    [--max-delay MAX_DELAY]
```
python -m data_provider serve "http://127.0.0.1:8000/upload" --min-delay 1000 --max-delay 1000

Un processus est alors lancé et des annotations sont générées puis envoyées via des requêtes HTTP vers `ENDPOINT`. Ces requêtes transportent une archive zip contennant un ensemble d'annotations au format XML et des fichiers JPG. Les fichiers JPG sont vides, on ne les utilisera que pour simuler des images.   
Les paramètres `--min-delay` et `--max-delay` permettent de faire varier les délais minimum et maximum entre deux requêtes. Par défaut, ces valeurs valent 1000, ce qui correspond à 1000 millisecondes.

Pour exécuter `data-provider` en mode hors-ligne, et générer un nombre fixe de nouvelles annotations, on peut appeler
```python
python -m data_provider generate N [--output-dir OUTPUT_DIR]C:/Users/Manel/Desktop/buawei/images
python -m data_provider generate 50 --output-dir ./images

```
avec `N` le nombre d'annotations à générer. Cette commande permet de générer des nouvelles annotations comme celles générées par le mode continu.  
Un argument optionnel `--output-dir` permet d'indiquer où les annotations seront stockées. Par défaut, ce paramètre vaut `/tmp/buawei` et chaque nouvelle exécution générera un dataset dans un sous-dossier avec un nom aléatoire.

Pour plus d'information sur l'exécution de `data-provider`, vous pouvez utiliser `python -m data_provider [COMMAND] --help`.

## Instructions
1. Proposez un pipeline hors-ligne d'ingestion des annotations Pascal VOC pour son stockage au format [COCO](https://cocodataset.org/#home), c'est-à-dire un script permettant de transformer les annotations Pascal VOC fournies en format COCO. 
DONE

2. Mettez en place des tests dd validation du contenu des annotations. Par exemple, au format COCO, le champ `bbox` correspond aux coordonnées d'un rectangle au format `[x, y, w, h]`, donc il faut vérifier que `w` et `h` (largeur et hauteur) sont strictement positives.
DONE

3. Finalement, mettez en place une API HTTP permettant d'ingérer les nouvelles annotations générées par `data-provider` en mode continu. Proposez une structure de système de fichiers permettant de stocker ces données. Par exemple, un dossier `images` avec toutes les images et un dossier `annotations` pour stocker toutes les annotations.
curl -X POST -F "file=@./images/fd8fc947-98cd-494e-914c-b368a3217871.zip" http://127.0.0.1:8000/upload

4. BONUS : Mettez en place quelques endpoints permettent de requêter des annotations sous certains critères. Par exemple, un endpoint `/search/3/annotations?min_width=100&max_width=1000` renverrait un sous-dataset contennant les annotations correspondant à des bounding box ayant une largeur entre 100 et 1000 pour le dataset avec id 3, ainsi que les images et catégories associées.

## Références
- Détail du format COCO: [https://www.immersivelimit.com/tutorials/create-coco-annotations-from-scratch](https://www.immersivelimit.com/tutorials/create-coco-annotations-from-scratch)
