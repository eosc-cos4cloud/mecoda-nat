![ ](docs/natusfera_banner_github_2.jpg)

Librería para extraer información recogida en la API Natusfera.

# Instalación

```bash
pip install natusfera
```

# Uso

## Obtener observaciones

Con `get_obs` se pueden extraer datos de las observaciones recogidas en la API. La función admite combinaciones de estos argumentos, que actúan como filtros, obteniendo las observaciones en orden descendente de id, con un máximo de 20.000 (limitación de la API):

| Argumento | Descripción | Ejemplo |
| --------- | ----------- | ------- |
| `query` | Palabra o frase encontrada en los datos de una observación | `query="quercus quercus"` |
| `id_project` | Número de identificación de un proyecto | `id_project=806` |
| `id_obs` | Número de identificación de una observación en concreto | `id_obs=425` |
| `user` | Nombre de usuaria que ha subido las observaciones | `user="zolople"` |
| `taxon` | Una de las taxonomías principales | `taxon="fungi"` |
| `place_id` | Número de identificación de un lugar | `place_id=1011` |
| `place_name` | Nombre de un lugar | `place_name="Barcelona"` |
| `year` | Año de las observaciones | `year=2019` |

Para el argumento `taxon` los valores posibles son:
`chromista`, `protozoa`, `animalia`, `mollusca`, `arachnida`, `insecta`, `aves`, `mammalia`, `amphibia`, `reptilia`, `actinopterygii`, `fungi`, `plantae` y `unknown`.

Ejemplo de uso:

```python
from natusfera import get_obs

observaciones = get_obs(year=2018, taxon='fungi')

```
`observaciones` es una lista de objetos [`Observation`](#observation).


## Obtener proyectos

Con `get_project` se puede obtener la información de los proyectos recogidos en la API. La función admite un solo argumento, que puede ser el número de identificación del proyecto o el nombre del proyecto. En caso de que el nombre no se corresponda exclusivamente con un proyecto, devuelve la información de la lista de proyectos que incluyen dicha palabra.

Ejemplo de uso:

```python
from natusfera import get_project

projects = get_project("urbamar")

```
`projects` es siempre una lista de objetos [`Project`](#project).


## Obtener recuento de observaciones por familia taxonómica

Con `get_count_by_taxon` podemos conocer el número de observaciones que se corresponden a cada una de las familias taxonómicas. La función no admite ningún argumento.

Ejemplo de uso:

```python
from natusfera import get_count_by_taxon

count = get_count_by_taxon()

```
`count` es un diccionario con la estructura taxonomía: número de observaciones


# Modelos

Los modelos están definidos usando objetos de [Pydantic](https://pydantic-docs.helpmanual.io/). Se hace validación de los tipos de todos los atributos y se pueden extraer los datos con el método `dict` o `json`.


## Observation

El objeto `Observation` contiene la información de cada una de las observaciones registradas en [Natusfera](https://natusfera.gbif.es/observations) y tiene los siguientes atributos:

| Atributo | Tipo | Description | Valor por defecto |
| -------- | ---- | ----------- | ----------------- |
| `id` | `int` | Número de la observación |  |
| `captive` | `Optional[bool]` | Estado de cautividad | `None` |
| `created_at` | `Optional[datetime]` | Fecha de creación | `None` |
| `updated_at` | `Optional[datetime]` | Fecha de actualización | `None` |
| `observed_on` | `Optional[date]` | Fecha de la observación | `None` |
| `description` | `Optional[str]` | Descripción de la observación | `None` |
| `iconic_taxon` | `Optional[IconicTaxon]` | Famlia taxonómíca | `None` |
| `taxon` | `Optional[Taxon]` | Objeto [`Taxon`](#taxon) con información del especimen | `None` |
| `latitude` | `Optional[float]` | Latitud | `None` |
| `longitude` | `Optional[float]` | Longitud | `None` |
| `place_id` | `Optional[int]` | Número de identificación del lugar | `None` |
| `quality_grade` | `Optional[QualityGrade]` | Grado de calidad: `basico` o `investigacion` |`None` |
| `user_id` | `Optional[int]` | Número de identificación de la usuaria | `None` |
| `user_login` | `Optional[str]` | Nombre de registro de la usuaria | `None` |
| `project_ids` | `List[int]` | Lista con el o los números de proyecto en los que se engloba la observación | `[]` |
| `photos` | `List[Photo]` | Lista de objetos [`Photo`](#photo), que incluyen información de cada fotografía de la observación | `[]` |
| `num_identification_agreements` | `Optional[int]` | Número de votos favorables a la identificación | `None` |
| `num_identification_disagreements` | `Optional[int]` | Número de votos favorables a la identificación | `None` |


## Project

El objeto `Project` contiene la información de cada uno de los proyectos registrados en [Natusfera](https://natusfera.gbif.es/observations) y tiene los siguientes atributos:

| Atributo | Tipo | Description | Valor por defecto |
| -------- | ---- | ----------- | ----------------- |
| `id` | `int` | Número de identificación del proyecto |  |
| `title` | `str` | Título del proyecto |  |
| `description` | `Optional[str]` | Descripción del proyecto | `None` |
| `created_at` | `Optional[datetime]` | Fecha de creación del proyecto | `None` |
| `updated_at` | `Optional[datetime]` | Fecha de actualización del proyecto |`None` |
| `latitude` | `Optional[float]` | Latitud |`None` |
| `longitude` | `Optional[float]` | Longitud |`None` |
| `place_id` | `Optional[int]` | Número de identificación del lugar | `None` |
| `parent_id` | `Optional[int]` | Número de identificación del proyecto en el que se engloba |`None` |
| `children_id` | `List[int]` | Números de identificación de los proyectos que tiene dentro | `[]` |
| `user_id` | `Optional[int]` | Número de identificación de la usuaria que lo crea | `None` |
| `icon_url` | `Optional[str]` | Enlace al icono del proyecto | `None` |
| `observed_taxa_count` | `Optional[int]` | Número de observaciones que incluye el proyecto | `None` |


## Taxon

El objeto `Taxon` contiene la información taxonómica de cada observación registrada y tiene los siguientes atributos.

| Atributo | Tipo | Description | Valor por defecto |
| -------- | ---- | ----------- | ----------------- |
| `iconic_taxon` | `IconicTaxon` | Familia taxonómica |  |
| `id` | `int` | Número de identificación de la especie |  |
| `name` | `str` | Nombre de la especie observada |  |


## Photo

El objeto `Photo` contiene la información de cada fotografía vinculada a una observación y tiene los siguientes atributos.

| Atributo | Tipo | Description | Valor por defecto |
| -------- | ---- | ----------- | ----------------- |
| `id` | `int` | Número de identificación de la fotografía |   |
| `large_url` | `str` | Enlace a la fotografía en formato grande |   |
| `medium_url` | `str` | Enlace a la fotografía en formato mediano |   |
| `small_url` | `str` | Enlace a la fotografía en formato pequeño |   |


# Contribuciones

Para contribuir a esta librería, sigue los siguientes pasos.

* Necesitas tener instalado Python 3.7 o superior, virtualenv y git.

* Crea un fork en github de este proyecto.

* Clona tu fork y entra en el directorio

    ```bash
    git clone git@github.com:<tu nombre de usuaria>/natusfera.git
    cd natusfera
    ```
* Configura tu virtualenv para correr los tests:
    ```bash
    virtualenv -p `which python3.7` env
    source env/bin/activate
    ```

* Instala `natusfera` y sus dependencias.
    ```bash
    pip3 install -e .
    pip3 install -r requirements-dev.txt
    ```

* Crea una nueva rama y haz tus cambios:
    ```bash
    git checkout -b mi-nueva-rama
    ```

* Corre los tests con:
    ```bash
    python -m pytest --cov-report term-missing --cov src tests
    ```

    Si necesitas pasar un test en concreto, puedes usar `pytest -k <nombre-del-test>`.

* Actualiza la documentación.

* Haz commit, push y crea tu pull request.


## Subir una nueva versión

* Cambiar a master y actualizar:
    ```bash
    git checkout master
    git pull
    ```

* Crear una nueva rama:
    ```bash
    git checkout -b <nombre-de-la-rama>
    git pull
    ```
* Hacer los cambios en el código

* Correr los tests:
    ```bash
    python -m pytest --cov-report term-missing --cov src tests
    ```

* Editar el archivo `setup.py` para subir la versión, que significa cambiar el argumento `version` en la función `setup`. La convención es 0.1.0 == major.minor.patch. `major` es introducir cambios que rompen el código existente. `minor` se refiere a cambios que agregan funcionalidad pero no rompen código existente. `patch` se refiere a cambios que arreglan errores pero no añaden funcionalidad.

* Hacer commit y push:
    ```bash
    git add .
    git commit -m "<comentario>"
    git push --set-upstream origin <nombre-de-la-rama>
    ```

* Seguir el link a github devuelto por el push y mergear.

* Actualizar master:
    ```bash
    git checkout master
    git pull
    ```

* Crear tag con la nueva versión:
    ```bash
    git tag <nueva-version>
    git push --tags
    ```

* Construir el paquete:
    ```bash
    rm dist/ build/ -r
    python setup.py -q bdist_wheel
    python setup.py -q sdist
    ```

* Subir paquete a pypi:
    ```bash
    twine upload -r pypi dist/*
    ```

¡Gracias por contribuir a este proyecto!