# PyJobs Crawlers

Crawlers pour le service d'agrégation d'offres d'emploi pyjobs.

## Utiliser pyjobs_crawler

Pour utiliser ``pyjobs_crawler`` dans votre projet, installez-le comme dépendence:

```
pip install git+https://github.com/algoo/crawlers.git@master
```

Pour crawler les annonces et les injecter dans votre système:

```
# -*- coding: utf-8 -*-
from pyjobs_crawlers.run import start_crawlers
import os
from mon_projet import MonConnecteur


if __name__ == '__main__':
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'pyjobs_crawlers.settings'
    start_crawlers(connector_class=MonConnecteur)
```

Où ``MonConnecteur`` est une classe implémentant ``pyjobs_crawlers.Connector``.

## Ajouter une source d'annonces

Ajouter une nouvelle source d'offres d'emplois [python](https://fr.wikipedia.org/wiki/Python_%28langage%29) consiste à ajouter un fichier dans le répertoire ``spiders``. Le contenu de ce fichier est détaillé plus bas.

### Jargon

* ``Page liste de jobs``: Ce sont les pages qui liste les offres d'emplois. Elle ne contiennent généralement qu'une partie des informations concernant l'offre. Ces pages doivent contenir des lien vers la ``Page du job``.
* ``Page du job``: C'est la page qui contient la plus grande partie des informations sur l'offre d'emploi.
* ``Crawl``: Action de lire le contenu d'une page web pour en extraire des information.
* ``Spider``: Objet ([classe](https://fr.wikipedia.org/wiki/Classe_%28informatique%29) [python](https://fr.wikipedia.org/wiki/Python_%28langage%29)) qui effectue le crawl des pages contenant les offres d'emplois.

### Méthode de récupération

Le ``Spider`` va parcourir la page de liste de jobs à la recherche d'offres d'emplois. Pour chacune des offres d'emplois trouvé le ``Spider`` récupérera la page et la parcourera également. 

Nous devrons fournir au ``Spider`` le paramètrage nécessaire (sous forme d'expression [XPATH](https://fr.wikipedia.org/wiki/XPath) ou [CSS](https://fr.wikipedia.org/wiki/Feuilles_de_style_en_cascade)) pour extraire les informations relatives aux offres d'empois.

La récupération de chaque composant d'un offre d'emploi (url, titre, etc.) peux être personalisé par un code [python](https://fr.wikipedia.org/wiki/Python_%28langage%29).

### Fichier Spider

Créez un fichier [python](https://fr.wikipedia.org/wiki/Python_%28langage%29) dans le répertoire ``spiders``, ex. ``pyjobs_crawlers/spiders/mon_site.py`` , contenant (remplacez les réferences à "mon_site"):

```
# -*- coding: utf-8 -*-
from pyjobs_crawlers.spiders import JobSpider
from pyjobs_crawlers import JobSource


class MonSiteSpider(JobSpider):

    name = 'mon_site'  # L'identifiant du spider, évitez les accents et espaces
    start_urls = ['http://www.mon-site.com/jobs']  # L'adresse d'où commencer le crawl
    label = 'Mon site'  # Le nom du site d'offre d'emplois
    url = 'http://www.mon-site.com'  # L'adresse de la page d'accueil du site d'offres d'emplois
    logo_url = 'http://www.mon-site.com/logo.png'  # L'adresse du logo du site d'offres d'emplois

    _crawl_parameters = {
        #  Paramètres à modifier après
    }

# N'oubliez pas cette ligne
source = JobSource.from_job_spider(MonSiteSpider)
```

### Paramétrage

#### Introduction

Le ``Spider`` permet d'extraire les informations relative aux offres d'emplois à deux moment différents:

* Lors de sa découverte sur la ``Page liste de jobs``. Ce contexte sera exprimé par le préfix ``from_list``.
* Lors de la lecture de la ``Page du job``. Ce contexte sera exprimé par le préfix ``from_page``.

Nous pourrons indiquer deux type d'expressions pour extraire l'information:

* Une expression [XPATH](https://fr.wikipedia.org/wiki/XPath): Sera exprimé par le suffix ``xpath``.
* Une expression [CSS](https://fr.wikipedia.org/wiki/Feuilles_de_style_en_cascade): Sera exprimé par le suffix ``css``.

*NOTE*: Il est possible de donner une liste d'expressions. Elles seront testés une à une.

Enfin, les différentes informations paramètrables sont:

* ``title``: Titre de l'annonce, **obligatoire**.
* ``publication_datetime``: Date de publication de l'annonce.
* ``company``: Nom de la société proposant l'emploi.
* ``company_url``: Adresse du site de la société proposant l'emploi.
* ``address``: Adresse postale de la société proposant l'emploi.
* ``description``: Description de l'offre d'emploi.
* ``tags``: Texte où chercher à répérer des tags comme *CDI*, *CDD*, *STAGE* ou encore *Django*, *Flask*, etc.

Ainsi que quelques paramètres nécéssaire au parcour des pages que nous allons voir ci-après.

Un paramètre sera alorsd exprimé comme suis: prefix__paramètre__suffix. Exemple:

```
    _crawl_parameters = {
        'from_page__title__xpath': './h1[@id="parent-fieldname-title"]/text()',
        'from_page__publication_datetime__xpath': './div[@id="content-core"]/div[@id="content-core"]/div[@class="discreet"]/text()',
        'from_page__company__xpath': ('.//h4/a/text()', './/h4/text()'),
        'from_page__description__css': '#content-core',
    }
        
```

#### Personaliser la réucpération

Il est possible de personnaliser la récupération de chaque données en surchargeant la fonction [python](https://fr.wikipedia.org/wiki/Python_%28langage%29) correspondante. Le nom de la fonction python étant ``suffix_paramètre``, exemple:

```
    def _get_from_page__publication_datetime(self, node):
        return datetime.datetime.now()
```

#### Paramètrer le Spider

Avant de renseigner les paramètre de récupération d'informations d'offres d'emploi vous devez renseigner les paramètres permettant le parcour des pages.

*Ces paramètres concerne le parcour de la ``Page liste de jobs``, ils doivent donc être préfixé de ``from_list``:

* ``jobs_lists``: Éxpression pour récupérer la ou les listes d'offres d'emplois dans la ``Page liste de jobs``. Par défaut saisir "//body". **obligatoire**.
* ``jobs``: Éxpression pour récupérer une annonce dans une liste d'annonces extraite par ``jobs_lists``.  **obligatoire**.
* ``url``: Épression pour récupérer l'url de la ``Page du job`` dans l'annonce estraite par ``jobs``.  **obligatoire**.
* ``next_page``: Éxpression pour récupérer l'url de la prochaine ``Page liste de jobs``.

