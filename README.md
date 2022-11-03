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

## Come è strutturato il progetto a livello fisico e organizzativo
- L'arduino deve essere in grado di rilevare i parametri esterni tramite i trasduttori sopracitati
- L'Arduino deve essere in grado di inviare i dati ottenuti tramite bluetooth al dispositivo che funge da computer
- il computer deve essere connesso a internet per consentire l'invio dei dati sul cloud
- Lato utente sarà tutto gestito tramite un'applicazione per dispositivi mobile o installata direttamente sul pc, ma che sia in grado di connettersi a Internet
- il computer deve essere in grado di elaborare i dati e metterli a disposizione delle altre persone con lo scopo di creare delle statistiche per incentivare l'ecologia e un utilizzo ottimizzato della lavatrice
