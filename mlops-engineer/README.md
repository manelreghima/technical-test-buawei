# Test technique MLOps

## Pré-requis

Le dossier `models` contient des modèles au format [ONNX](https://onnx.ai/).
Créez un environnement virtuel avec les dépendances dans `requirements.txt`.
Le code fourni dans `inference-server` permet de faire des inférences avec les modèles ONNX fournis.
Vous pouvez installer `inference-server` comme un module python via
```python
pip install .
```

Pour l'exécuter, il suffit d'appeler
```python
MODELS_DIR=${MODELS_DIR} python -m inference-server

set MODELS_DIR=C:/Users/Manel/Desktop/buawei/mlops-engineer/models && python -m inference_server

```
où `MODELS_DIR` est une variable d'environnement indiquant le chemin du dossier contenant les modèles. Il est aussi possible d'utiliser un fichier `.env`. 

Les modèles sont des [CNN](https://fr.wikipedia.org/wiki/R%C3%A9seau_neuronal_convolutif), leurs entrées sont des images et leurs sorties correspondent à des classes.  

Le serveur est composé de 4 endpoints :
- `GET /api/v1/list`, liste tous les modèles disponibles
- `POST /api/v1/load?name=${MODEL_NAME}`, charge en mémoire le modèle du fichier `${MODEL_DIR}/${MODEL_NAME}`
- `POST /api/v1/run/${MODEL_NAME}`, exécute une inférence avec le modèle `${MODEL_NAME}`
- `POST /api/v1/unload?name=${MODEL_NAME}`, supprime le modèle de la mémoire

Le modèle d'entrée du endpoint `/api/v1/run/${MODEL_NAME}` est un JSON contenant une entrée `"image"` ayant pour valeur une image encodée en [base64](https://fr.wikipedia.org/wiki/Base64). Attention, il ne faut pas inclure les métadonnées liées au format (e.g. `data:image/jpeg;base64,`). Par exemple, le contenu d'une requête peut être 
```json 

{"image": "iVBORw0KGgoAAAANSUhEUgAAAfwAAALICAYAAACaUUI1AAAABHNCSVQICAgIfAhkiAAAABl0RVh0U29mdHdhcmUAZ25vbW..."}
```

Pour plus d'information, notamment sur la structure de données d'entrée/sortie pour `/api/v1/run`, vous pouvez accéder au endpoint `/docs`. Cette page web fournit une documentation intéractive du serveur.

## Instructions

1. Proposez une méthodologie de test du serveur d'inférence, c'est-à-dire proposez une démarche permettant de tester le bon fonctionnement du serveur de test dans ses différents aspects (fonctionnalité, charge, etc). Implémentez au moins un de ces tests dans un framework de test (unittest, pytest, etc).

2. Ajoutez le stockage de métriques des différents modèles pour les différents endpoints. La méthode ou outils de stockage de cette information est complètement libre (p.ex. stockage dans un fichier csv, une bdd, un aggrégateur de données). Le choix des métriques est aussi libre (p.ex. temps d'exécution, utilisation de mémoire, etc). 

3. Proposez une méthodologie d'ingestion de nouveaux modèles. Il ne vous est pas demandé d'implémenter cette fonctionnalité, mais de décrire un endpoint `/api/v1/register?name=${MODEL_NAME}` qui prend en entrée un nouveau modèle ONNX comme ceux fournis, permettant par la suite de l'utiliser via `/api/v1/load`.

4. Proposez une méthodologie de test d'une nouvelle version d'un modèle. Il ne vous est pas demandé d'implémenter cette fonctionnalité, mais de décrire comment vous intégreriez la notion de versionnage de modèles (p.ex. mise à jour suite à un ré-entraînement) ainsi que la validation en production de ces nouvelles versions.

5. BONUS : Mettez en place les endpoints des points 3. et 4.

