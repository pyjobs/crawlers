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
    start_crawlers(connector=MonConnecteur)
```

Où ``MonConnecteur`` est une classe implémentant ``pyjobs_crawlers.Connector``.
