# TFT Analyzer

## Descripción
Sistema de análisis de datos sobre el juego **TeamFight Tactics**.
El objetivo es mostrar al usuario de la aplicación información
sobre su rendimiento en el juego de la manera más amigable posible,
y darle la posibilidad de compararla con los datos del Top 200 mundial
de jugadores para que pueda mejorar su juego.
Ofrecemos además integración con la plataforma de directos **Twitch.tv**
para un acceso rápido a contenido relacionado con el juego, e integración
con **Youtube** para una búsqueda rápida de guías sobre ciertos elementos
del juego.

## Casos de uso
- Búsqueda de un perfil de usuario por nombre y visualización de sus
estadísticas.
- Búsqueda del Top 200 jugadores (también con visualización de
estadísticas.
- Análisis sobre el uso de Piezas, Objetos y Sinergias para cada
usuario y el Top 200.
- Listado de directos en Twitch.tv
- Búsqueda de guías sobre Sinergias en Youtube

## Cambios respecto a la primera propuesta
- Gestión de usuarios. permitimos registro y logging de usuarios.
	Estos pueden añadir jugadores a su pestaña de favoritos para un acceso mas fácil
- Gestión de errores de las APIS
	Errores con las APIs de Twitch y de Youtube: Se muestra un mensaje de error en lugar de la información esperada.
	Errores con las APIs de Riot Games: Se obtiene la informacion de la base de datos propia. En caso de no disponer de informacion en nuestra base de datos, se muestran mensajes de error.
- Libreria python Seaborn utilizada para generar el historgrama de /tft/user/{user_name}

## Integrantes del grupo
- Alejandro Fernández Fraga (​a.fernandez3@udc.es​)
- Alejandro García Tenreiro (a.garciat@udc.es)

## Cómo ejecutar
```
docker pull tftanalyzer/tftanalyser_web:PI
sudo docker run -p 8000:8000 --network='host' tftanalyzer/tftanalyser_web:PI python3 manage.py runserver
```

## Problemas conocidos
- El filtrado por regiones no está implementado
- La gráfica de rangos de la vista detallada de usuario no está implementada(no podemos obtener la información de la api)
