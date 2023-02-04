# drying-rack-smart

Progetto del corso di IOT che mira alla realizzazione di uno stendino smart in grado di fornire informazioni riguardanti il tempo di asciugatura degli abiti ma non solo. Deve essere in grado anche di rielaborare i dati per fornirne altri correlati che indagano quanto è ecologica una persona. Inoltre ogni utente avrà la possibilità di effettuare il login con le proprie credenziali.

## Cosa ci serve
- Arduino (x2)
- sensore di temperatura
- sensore di umidità dell'aria
- sensore umidità del terreno
- breadboard
- led / buzzer / schermo lcd
- modulo bluetooth

## Requisiti di progetto
- L'arduino deve essere in grado di rilevare i parametri esterni tramite i trasduttori sopracitati per fornire indicazioni utili sui tempi di asciugatura degli abiti
- L'Arduino deve essere in grado di inviare i dati ottenuti tramite bluetooth al dispositivo che funge da computer
- il computer deve essere connesso a internet per consentire l'invio dei dati sul cloud
- Lato utente sarà tutto gestito tramite un'applicazione per dispositivi mobile o installata direttamente sul pc, ma che sia in grado di connettersi a Internet
- il computer deve essere in grado di elaborare i dati e metterli a disposizione delle altre persone con lo scopo di creare delle statistiche per incentivare l'ecologia e un utilizzo ottimizzato della lavatrice
- l'applicazione, grazie alla consultazione di api riguardanti il meteo, deve fornire indicazioni sulla possibilità e rischi di stendere fuori
- Effettuare il login/logout da parte degli utenti
- L'Arduino deve essere in grado di segnalare quando un abito è asciutto tramite led/notifica/buzzer
- Vedere se introdurre il controllo su stendini vicini (GPS o statico al momento della registrazione)
- Introdurre targetizzazione sugli abiti in modo da avere dati più precisi sui tempi e temperatura di asciugatorua
- Implementare documentazione tramite swagger delle API

## Arduino

Qui il [link](https://www.tinkercad.com/things/hZl0u94ahFn-drying-rack-smart/editel?sharecode=D3SCMsZ7Jgg0KzsocBVNS1I2N93rQOPSl80nIKx_3Zo) al progetto ThinkerCad con l'inserimento dei sensori che ci sono. ALcuni non sono disponibili, ma sono indicati i pin occupati.

- **DHT11**: come libreria importare DHTlib di Rob Tillaart. PIN DIGITALE 2
- **Capacitive Moisture Soil Sensor**: serve il pin analogico e quindi non ha bisogno di librerie per funzionare. AO
- **Force Sensitive Resistor**: serve il pin analogico A1
- **Rain Sensor**: serve il pin analogico A2
- **LED RGB**: serve come attuatore per capire se il ciclo di asciugatura è finito o meno. Servono il PIN 3 ROSSO, PIN 4 VERDE e PIN 5 BLU.

## Database MySQL
Il datbase su cui saranno conservati i dati degli utenti sarà gestito con DBMS mySql in una istanza locale, a cui è possibile collegarsi tramite l'utilizzo di una rete virtuale hamachi (scaricabile al [link](https://vpn.net/)).

## ThesmartStendino Bot
L'interazione con l'utente è stata implementata tramite la realizzazione di un bot telegram chiamato @ThesmartStendino in cui è possibile loggarsi, vedere statistiche e settare la posizione dello stendino. Nel lungo periodo questo bot dovrebbe trasformarsi in una vera e propria app detta StendApp.

## Flask
Per il lato server e per la realizzazione di API Rest in grado di ricevere richieste HTTP ed effettuare le query al db.
Lo script Flask si connette inoltre alla API di OpenWeather per ottenere dati meteo a date coordinate. Inoltre si occupa di calcolare statistiche sui dati conservati sul DB.
La documentazione delle API è stata implementata tramite Swagger.

TODO
- deploying Flask su AWS
