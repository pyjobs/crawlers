[![Build Status](https://travis-ci.org/pyjobs/crawlers.svg?branch=master)](https://travis-ci.org/pyjobs/crawlers) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/pyjobs/crawlers/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/pyjobs/crawlers/?branch=master)

# PyJobs Crawlers

Crawlers pour le service d'agrégation d'offres d'emploi pyjobs.

## Utiliser pyjobs_crawler

Pour utiliser ``pyjobs_crawler`` dans votre projet, installez-le comme dépendence:

```
pip install git+https://github.com/pyjobs/crawlers.git@master
```

Pour crawler les annonces et les injecter dans votre système:

```
# -*- coding: utf-8 -*-
from pyjobs_crawlers.run import start_crawlers
import os
from mon_projet import MonConnecteur


if __name__ == '__main__':
    start_crawlers(connector_class=MonConnecteur)
```

Où ``MonConnecteur`` est une classe implémentant ``pyjobs_crawlers.Connector``.

## Récupérer le projet
<a name="recuperer_le_projet"></a>

### Cloner le dépôt

#### Linux

Vous aurez besoin des paquets ``python``, ``python-pip`` et de ``git``. Pour les installer sur une debian-like:

```
apt-get install python python-pip git
```

Récupérez le projet:

```
git clone https://github.com/pyjobs/crawlers.git pyjobs_crawlers
```

Pour installer les dépendances, placez vous dans le répertoire ``pyjobs_crawlers``:

```
cd pyjobs_crawlers
```

Installez les dépendences python (il est conseillé de créer un [environnement virtuel](http://apprendre-python.com/page-virtualenv-python-environnement-virtuel)):

```
pip install -r requirements.txt
```

## Ajouter une source d'annonces

Ajouter une nouvelle source d'offres d'emplois [python](https://fr.wikipedia.org/wiki/Python_%28langage%29) consiste à ajouter un fichier dans le répertoire ``spiders``. Le contenu de ce fichier est détaillé plus bas.

### Jargon

* ``Page liste de jobs``: Ce sont les pages qui liste les offres d'emplois. Elle ne contiennent généralement qu'une partie des informations concernant l'offre. Ces pages doivent contenir des lien vers la ``Page du job``.
* ``Page du job``: C'est la page qui contient la plus grande partie des informations sur l'offre d'emploi.
* ``Crawl``: Action de lire le contenu d'une page web pour en extraire des informations.
* ``Spider``: Objet ([classe](https://fr.wikipedia.org/wiki/Classe_%28informatique%29) [python](https://fr.wikipedia.org/wiki/Python_%28langage%29)) qui effectue le crawl des pages contenant les offres d'emplois.

### Méthode de récupération

Le ``Spider`` va parcourir la page de liste de jobs à la recherche d'offres d'emplois. Pour chacune des offres d'emplois trouvées le ``Spider`` récupérera la page et la parcourera également. 

Nous devrons fournir au ``Spider`` le paramètrage nécessaire (sous forme d'expression [XPATH](https://fr.wikipedia.org/wiki/XPath) ou [CSS](https://fr.wikipedia.org/wiki/Feuilles_de_style_en_cascade)) pour extraire les informations relatives aux offres d'empois.

La récupération de chaque composant d'un offre d'emploi (url, titre, etc.) peux être personalisé par un code [python](https://fr.wikipedia.org/wiki/Python_%28langage%29).

### Fichier Spider

Créez un fichier [python](https://fr.wikipedia.org/wiki/Python_%28langage%29) dans le répertoire ``spiders``, ex. ``pyjobs_crawlers/spiders/mon_site.py`` , contenant (remplacez les réferences à "mon_site"):

```
# -*- coding: utf-8 -*-
from pyjobs_crawlers.spiders import JobSpider, JobSource


class MonSiteSpider(JobSpider):

    name = 'mon_site'  # L'identifiant du spider, évitez les accents et espaces
    start_urls = ['http://www.mon-site.com/jobs']  # L'adresse d'où commencer le crawl
    label = 'Mon site'  # Le nom du site d'offre d'emplois
    url = 'http://www.mon-site.com'  # L'adresse de la page d'accueil du site d'offres d'emplois
    logo_url = 'http://www.mon-site.com/logo.png'  # L'adresse du logo du site d'offres d'emplois

    _crawl_parameters = {
        #  Paramètres à ajouter, voir ci-après
    }

# N'oubliez pas cette ligne
source = JobSource.from_job_spider(MonSiteSpider)
```

### Paramétrage

#### Introduction

Le ``Spider`` permet d'extraire les informations relative aux offres d'emplois à deux moment différents:

* Lors de sa découverte sur la ``Page liste de jobs``. Ce contexte sera exprimé par le préfixe ``from_list``.
* Lors de la lecture de la ``Page du job``. Ce contexte sera exprimé par le préfixe ``from_page``.

Nous pourrons indiquer deux type d'expressions pour extraire l'information:

* Une expression [XPATH](https://fr.wikipedia.org/wiki/XPath): Sera exprimé par le suffixe ``xpath``.
* Une expression [CSS](https://fr.wikipedia.org/wiki/Feuilles_de_style_en_cascade): Sera exprimé par le suffixe ``css``.

*NOTE*: Référez-vous à la [documentation Scrapy](http://doc.scrapy.org/en/1.0/topics/selectors.html) pour en savoir plus sur l'extraction.

*NOTE*: Il est possible de donner une liste d'expressions. Elles seront testés une à une.

Les différentes paramètres d'extraction des informations d'offres sont:

* ``title``: Titre de l'annonce, **obligatoire**.
* ``publication_datetime``: Date de publication de l'annonce.
* ``company``: Nom de la société proposant l'emploi.
* ``company_url``: Adresse du site de la société proposant l'emploi.
* ``address``: Adresse postale de la société proposant l'emploi.
* ``description``: Description de l'offre d'emploi.
* ``tags``: Texte où chercher à répérer des tags comme *CDI*, *CDD*, *STAGE* ou encore *Django*, *Flask*, etc.

*NOTE*: Il est possible de désactiver l'étape ``from_page`` si les informations de la ``Page liste de jobs`` vous suffisent avec le paramètre ``from_page_enabled`` (ex. ``'from_page_enabled': False``).

Ainsi que quelques paramètres nécéssaire au parcours des pages que nous allons voir ci-après.

Un paramètre sera alors exprimé sous la forme: prefix__paramètre__suffix. Exemple:

```
    _crawl_parameters = {
        'from_page__title__xpath': './h1[@id="parent-fieldname-title"]/text()',
        'from_page__publication_datetime__xpath': './div[@id="content-core"]/div[@id="content-core"]/div[@class="discreet"]/text()',
        'from_page__company__xpath': ('.//h4/a/text()', './/h4/text()'),
        'from_page__description__css': '#content-core',
    }
        
```

#### Personaliser la récupération

Il est possible de personnaliser la récupération de chaque données en surchargeant la fonction [python](https://fr.wikipedia.org/wiki/Python_%28langage%29) correspondante. Le nom de la fonction python étant ``_get_suffix__paramètre``, exemple:

```
    def _get_from_page__publication_datetime(self, node):
        return datetime.datetime.now()
```

#### Paramètrer le Spider

Avant de renseigner les paramètre de récupération d'informations d'offres d'emploi vous devez renseigner les paramètres permettant le parcours des pages.

*NOTE*: Ces paramètres concerne le parcours de la ``Page liste de jobs``, ils doivent donc être préfixé de ``from_list``:

* ``jobs_lists``: Éxpression pour récupérer la ou les listes d'offres d'emplois dans la ``Page liste de jobs``. Par défaut saisir "//body" en XPATH ou "body" en CSS. **obligatoire**.
* ``jobs``: Éxpression pour récupérer une annonce dans une liste d'annonces extraite par ``jobs_lists``.  **obligatoire**.
* ``url``: Épression pour récupérer l'url de la ``Page du job`` dans l'annonce estraite par ``jobs``.  **obligatoire**.
* ``next_page``: Éxpression pour récupérer l'url de la prochaine ``Page liste de jobs``.

Vous devez ensuite renseigner les paramètres d'extraction des informations d'offres (``title``, ``publication_datetime``, etc.)

#### Exemples

##### Minimaliste

Version minimaliste d'extraction d'annonce sur le site http://jobs.humancoders.com/python:

**pyjobs_crawlers/spiders/humancoders.py**

```
# -*- coding: utf-8 -*-
from pyjobs_crawlers.spiders import JobSpider, JobSource


class HumanCodersSpider(JobSpider):

    name = 'human'
    start_urls = ['http://jobs.humancoders.com/python']
    label = 'Human coders'
    url = 'http://jobs.humancoders.com/'
    logo_url = 'http://jobs.humancoders.com/assets/logo-b2ddc104507a3e9f623788cf9278ba0e.png'

    _crawl_parameters = {
        'from_page_enabled': False,
        'from_list__jobs_lists__css': 'body',
        'from_list__jobs__css': 'li.job',
        'from_list__url__css': 'div.job_title h2 a::attr(href)',
        'from_list__title__css': 'div.job_title h2 a::text'
    }

# N'oubliez pas cette ligne
source = JobSource.from_job_spider(HumanCodersSpider)
```

Le [test](#tester_votre_spider) de ce spider produit:

```
> pyjobs_crawlers/bin/test_spider pyjobs_crawlers.spiders.humancoders.HumanCodersSpider
LOG: (human) CRAWL_LIST_START
LOG: (human) CRAWL_LIST: http://jobs.humancoders.com/python
LOG: (human) CRAWL_LIST_FINISHED
TERMINATED: 8 job(s) found
DETAILS FOR http://jobs.humancoders.com/python/jobs/894-python-django-software-engineer:
{'address': None,
 'company': None,
 'company_url': None,
 'description': None,
 'initial_crawl_datetime': datetime.datetime(2016, 1, 26, 10, 13, 8, 557139),
 'publication_datetime': datetime.datetime(2016, 1, 26, 10, 13, 8, 557597),
 'source': 'human',
 'status': 'prefilled',
 'tags': [],
 'title': u'Python & Django Software Engineer',
 'url': u'http://jobs.humancoders.com/python/jobs/894-python-django-software-engineer'}
DETAILS FOR http://jobs.humancoders.com/python/jobs/645-developpeur-web-h-f:
[...]
```

##### Avancé

Version plus complète d'extraction d'annonce sur le site http://jobs.humancoders.com/python:

**pyjobs_crawlers/spiders/humancoders.py**

```
# -*- coding: utf-8 -*-
from datetime import datetime

from pyjobs_crawlers.spiders import JobSpider, JobSource


class HumanCodersSpider(JobSpider):

    name = 'human'
    start_urls = ['http://jobs.humancoders.com/python']
    label = 'Human coders'
    url = 'http://jobs.humancoders.com/'
    logo_url = 'http://jobs.humancoders.com/assets/logo-b2ddc104507a3e9f623788cf9278ba0e.png'

    _crawl_parameters = {
        'from_page_enabled': True,

        'from_list__jobs_lists__css': 'body',
        'from_list__jobs__css': 'li.job',
        'from_list__url__css': 'div.job_title h2 a::attr(href)',
        'from_list__title__css': 'div.job_title h2 a::text',
        'from_list__publication_datetime__css': 'div.date::text',
        'from_list__tags__xpath': '.',
        'from_list__company__css': 'div.company span.company_name::text',

        'from_page__container__css': 'body',
        'from_page__company_url__css': 'div.company_url a::attr(href)',
        'from_page__description__css': '#description'
    }

    def _get_from_list__publication_datetime(self, node):
        raw_date = self._extract_first(node, 'from_list__publication_datetime')
        if raw_date:  # La date est sous la forme "24 août 2015"
            raw_date_english = self._month_french_to_english(raw_date)  # On la converti en Anglais
            return datetime.strptime(raw_date_english, '%d %B %Y')  # On extrait la date de ce texte

# N'oubliez pas cette ligne
source = JobSource.from_job_spider(HumanCodersSpider)
```

#### Tester votre Spider
<a name="tester_votre_spider"></a>

Dans un terminal, placez vous dans le dossier du [projet](#recuperer_le_projet)  et exécutez la commande suivante (en remplaçant ``pyjobs_crawlers.spiders.humancoders.HumanCodersSpider``):

```
pyjobs_crawlers/bin/test_spider pyjobs_crawlers.spiders.humancoders.HumanCodersSpider
```

*NOTE*: Le paramètre se structure ainsi: pyjobs_crawlers.spiders.nom_du_fichier.NomDeLaClasse
