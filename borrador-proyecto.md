# PLAN DEL PROYECTO

1. Creación de una librería de Python para Natusfera: permite que cualquier persona pueda desarrollar scripts nuevos utilizando la API de Natusfera. De esta forma el/la usuario/a no necesita conocer la API para poder utilizarla. Esta librería podría ser adaptada a minka fácilmente. Es decir, los programas que utilicen esta librería seguirían funcionando si se abandona Natusfera para pasar a Minka.

Hay que comprobar que la API de Natusfera puede aguantar el número de peticiones que implica esta librería, y asegurarse de que no sufre sobrecargas (que existen medidas para evitar un número excesivo de peticiones, etc). A tener en cuenta que hay unas 80.000 observaciones indexadas en natusfera, por lo que la librería haría unas 400 peticiones a la API (límite de 200 resultados por petición en la API) para obtener todos los resultados.

2. Módulo propio para Orange: desarrollar un módulo específico que conecte los datos de la API con la interfaz de Orange, como origen de los datos. Este módulo utiliza la librería anterior. De esta manera, un usuario/a sólo tendría que cargar el módulo y podría empezar a explorar, analizar y visualizar los datos de Natusfera en la interfaz de Orange.

3. Crear un workflow en Orange con distintas posibilidades de visualización y análisis utilizando ese módulo como origen de los datos:
    - Histograma de uso de la aplicación / incorporación de nuevas observaciones.
    - Mapa geográfico de las observaciones en función de taxonomías (?)
    - Ver otras opciones de visualización de los datos (mapa de calor, esquema de árbol,...). Aquí me tendrías que orientar para localizar las perspectivas más interesantes. En esta parte todo sería probar y jugar con las distintas posibilidades que ofrece orange.
En la documentación se incluiría la forma de utilizar el módulo y cargar este workflow. Después cada persona puede añadir nuevas visualizaciones o probar distintas opciones a las predeterminadas. He estado mirando la documentación de Orange y me gusta. Tengo ganas de meterme para ver posibilidades.

Estos tres primeros puntos sería posible tenerlos antes de la presentación. Si da tiempo y los pasos anteriores se finalizan antes de noviembre, se podría complementar el trabajo con el siguiente paso:
4.  Uso de otras librerías de visualización: utilizar la librería de Python de Natusfera para integrarla con otras librerías de visualización geográfica (Folium/Leaflet) y demostrar otros desarrollos fuera de Orange. Por el tipo de datos recogidos, las librerías de visualización geoespacial pueden ser las más interesantes.


# DOCUMENTACION

Librería R rinat: https://docs.ropensci.org/rinat/reference/index.html

Funciones:
get_inat_obs(): Download iNaturalist data
get_inat_obs_id(): Get information on a specific observation
get_inat_obs_project(): Download observations or info from a project
get_inat_obs_user(): Download observations for a user
get_inat_taxon_stats(): Get stats on taxon counts
get_inat_user_stats(): Get stats on users
inat_map(): Plot iNaturalist observations

Github rinat: https://github.com/ropensci/rinat

API: https://natusfera.gbif.es/api

# PASOS pasosos

x Introducción al testing
x Apuntar los errores que se detectan en la API y notificarlos.
        * Error 500 en la paginación de las búsquedas
        * Fechas erróneas

Para mi semana:
- Crear la librería de Python:
    * Definir todas las funciones devolviendo los datos según los da la API.
        x Observaciones por taxonomía
        x Observaciones por lugar
            * buscador lugar(str) -> [{place_name, place_id, place_type_name}]
            * buscador obs(place_id) -> [observaciones]
    x Poner información de tipos a las funciones (como en licitaciones)
    
    * Devolver objetos datetime en lugar de las fechas en formato string.
        x Corregir las funciones incluyendo el código del notebook de convertir en datetime
        x Incluir en los tests que dan resultado con campos que puedes ser datetime las pruebas para verificarlo (ejemplo: test_get_observations_by_id_returns_observations_data())
        * Asegurarse de que todos los tests pasan.
        
    * Unificar las funciones: 1-2 funciones en lugar de 40 para cada modelo
        x Archivar código anterior + cambiar nombre a test_natusfera para que pase el pytest
        x Hacer testes para las funciones unificadas
            x modificar los test existentes para que usen las nuevas funciones
            x test para nombre de place_name que no devuelve nada
            x test de uso de la función con taxon en minúsculas
            x test de usos combinados

        x Hacer el commit



    x Revisar si get_project funciona correctamente: devuelve diccionario o lista
        * Que devuelva siempre diccionario (con búsqueda por nombre puede devolver lista de muchos diccionarios)
        * Si la lista tiene más de un elemento, devuelve mensaje de error (raise ValueError)

    x "https://natusfera.gbif.es/taxa" 13 categorías principales

    * Leer la documentación de pydantic:
    https://pydantic-docs.helpmanual.io/usage/
    https://lyz-code.github.io/blue-book/coding/python/pydantic/ 



    * Crear objetos específicos
        * Objetos de las entidades de nuestro programa: observaciones y proyectos
            * Refinar el objeto Observation:
                x Campos válidos del quality_grade: crear un enum llamado QualityGrade
                x Modificar el objeto Observation para utilizar esa clase
                x Corregir el taxon_iconic para que utilice IntEnum en lugar de Enum:
                    https://lyz-code.github.io/blue-book/coding/python/pydantic_types/#enums-and-choices
                
            x Construir objeto observations en _request()
                x Utilizar el _build_observations en todos los observations.extend
                
            * Modificar los tests
                x test_get_obs_by_id_returns_observations_data, crear un expected_result con todos los campos del objeto observation, para ver que todos los campos se construyen bien (los que no aparecen con el nombre exacto o que devuelven una lista). 
                x En el resto de tests crear un objeto con solo los campos obligatorios (campos que no tienen nada por defecto).

        - Crear objeto natusfera
            - Convertir las funciones actuales en métodos de natusfera.

    * Escribir documentación
Aquí estoy recogiendo a lo que aspiro yo al escribir documentación, pero ni yo llego
hasta allí: https://lyz-code.github.io/blue-book/documentation/ . Si te gusta la idea,
mírate las referencias.

Puedes fijarte en la documentación de paquetes que te gusta cómo está escrita y cómo te
ha ayudado. Para mi, la mejor documentación es la de [FastAPI](https://fastapi.tiangolo.com/tutorial/)

Apuntar a esto en tu primera librería no es realista. Te diría que mirases los apartados
que uso yo en varias de mis documentaciones e intentes reunirlas en un README.md.
Ejemplos:

https://lyz-code.github.io/mkdocs-newsletter/
https://lyz-code.github.io/autoimport/
https://lyz-code.github.io/pynbox/
https://lyz-code.github.io/faker-optional/
https://lyz-code.github.io/yamlfix/
https://lyz-code.github.io/pydo/

O puede que esta documentación que te he enseñado no te sirva de nada a ti, y tu puedas
escribir una documentación que sea más util a los usuarios. Coge lo que te gusta de lo
que te he enseñado y crea algo tuyo.
    * Paquetito para que se pueda instalar y subirlo a pypi.
    
    * Crear validaciones de los argumentos de entrada para evitar valores que la API no acepta.

# Documentación

* Introduction: A short description with optional pictures or screen casts, that catches the user's attention and makes them want to use it. Like the advertisement of your program.
* Get started: Lessons that allows the newcomer learn how to start using the software. Like teaching a small child how to cook.
* How-to guides: Series of steps that show how to solve a specific problem. Like a recipe in a cookery book.
* Technical reference: Searchable and organized dry description of the software's machinery. Like a reference encyclopedia article.
* Background information: Discursive explanations that makes the user understand how the software works and how has it evolved. Like an article on culinary social history.

# Orange

* Crear el módulo de Orange
    * Data Inputs:
    https://orange3.readthedocs.io/projects/orange-data-mining-library/en/latest/tutorial/data.html#data-input
    * Leerse el tutorial del widget
        * Ver cómo se definen los outputs del módulo (crear el objeto Table?)
        * Ver cómo pasar de una lista de Observaciones a objeto Table
    * Cómo queremos la interfaz del módulo:
        * número de cajitas, etc -> hacer dibujo
    * Programar esa interfaz
* De nuestro módulo de observaciones -> Table
    * Generar un csv con datos de observaciones, usando el módulo de file:
            * Sacar un csv con 20.000 observaciones para jugar con ellas
    * Empezar a jugar con los datos y crear workflows
    
