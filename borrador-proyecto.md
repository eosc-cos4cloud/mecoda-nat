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
        * Observaciones por taxonomía
        * Observaciones por lugar
            * buscador lugar(str) -> [{place_name, place_id, place_type_name}]
            * buscador obs(place_id) -> [observaciones]
    * Poner información de tipos a las funciones (como en licitaciones)
    
    * Devolver objetos datetime en lugar de las fechas en formato string.
        * Corregir las funciones incluyendo el código del notebook de convertir en datetime
        * Incluir en los tests que dan resultado con campos que puedes ser datetime las pruebas para verificarlo (ejemplo: test_get_observations_by_id_returns_observations_data())
        * Asegurarse de que todos los tests pasan.
    * Unificar las funciones: 1-2 funciones en lugar de 40 para cada modelo
    * Crear objetos específicos para observaciones, places,...
    * Paquetito para que se pueda instalar y subirlo a pypi.
    * Crear validaciones de los argumentos de entrada para evitar valores que la API no acepta.
