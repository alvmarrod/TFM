#include <SPI.h>
#include <dht.h>

#include "nRF24L01.h"
#include "RF24.h"

/*
 * *** PINES ***
*/

// Sensor DHT
#define   pinDHT    4

// RF24L01
#define   pinCE     9
#define   pinCSN    10
#define   pinMOSI   11
#define   pinMISO   12
#define   pinSCK    13

// Proximidad 1 (Cerca)
#define   pinECHOnear       5
#define   pinTRIGGERnear    6

// Proximidad 2 (Lejos)
#define   pinECHOfar        2
#define   pinTRIGGERfar     3

// Tiempo de cruce en ms
#define   CROSS_TIME        1000
#define   DELAY             20

/*
 * *** VALORES ***
*/

// Contaremos para distancias menores de 200cm
#define   distanceTrigger   50

// Cada 10s se activa la lectura de temperatura (en ms)
#define   DHT_ACTIVATES     10000

// ** DETECCION **
// 1 hay una entrada
#define   Entrada     1
// 2 hay una salida
#define   Salida      2

/*
 * *** ESTADOS ***
*/
enum estados {
  idle,
  det_e,
  det_s,
  det
};

/*
 * *** VARIABLES ***
*/

// *** PROXIMIDAD 1 (Cerca) ***
long durationNear   = 0,
     cmNear         = 0;

// *** PROXIMIDAD 2 (Lejos) ***
long durationFar    = 0,
     cmFar          = 0;

// *** DETECCION  ***
int deteccion = 0;
estados estado = idle;
estados p_estado = idle;

// Tiempo de espera
long start_time = 0;
long now = 0;

// *** TEMPERATURA Y HUMEDAD ***
int temp = 0, hum = 0;

// *** CONTEO Y EVENTOS ***
long dht_last_time = 0;

// *** RF24 ***

// Configuramos el sensor en los pines 9 y 10, además del bus SPI
RF24 radio(pinCE, pinCSN);

// Tiempo que estamos esperando antes de dar por erronea la conexión
unsigned long timeoutPeriod = 150;

// Direciones de la tubería utilizada para la comunicación
const uint64_t pipes[2] = { 0xABCDABCD71LL, 0xF0F0F0F0E1LL };

// Datos enviados
// humedad, temperatura
// 0, evento entrada/salida
uint8_t RF24DATOS[2];

// *** Sensor DHT ***
dht DHT;

// ------ SETUP ------

void setup()
{

  // Serial.begin(9600);
  Serial.begin(115200);
  Serial.print(" --- SETUP --- \n");

  // Sensor NEAR
  pinMode(pinECHOnear, INPUT);
  pinMode(pinTRIGGERnear, OUTPUT);
  // Sensor FAR
  pinMode(pinECHOfar, INPUT);
  pinMode(pinTRIGGERfar, OUTPUT);
  
  IniciarRadio();
  
  Serial.print(" --- END SETUP --- \n");
  
}

// Configuramos el módulo de radio
void IniciarRadio()
{

  radio.begin();
  // Selección del canal
  radio.setChannel(76);
  //Ponemos la amplificación de potencia en nivel alto
  radio.setPALevel(RF24_PA_HIGH);

  // Tasa de transmisión a 250 KBps
  // radio.setDataRate(RF24_250KBPS);
  radio.setDataRate(RF24_2MBPS);

  // Activamos los ACK automáticos
  radio.setAutoAck(1);

  // Seleccionamos el espacio de tiempo entre varios intentos ((2+1)*250us) y el numero de reintentos (15)
  radio.setRetries(1, 1);

  // Seleccionamos la longitud del CRC
  radio.setCRCLength(RF24_CRC_16);

  // Abrimos la tubería de escritura y lectura
  radio.openWritingPipe(pipes[1]);
  radio.openReadingPipe(1, pipes[0]);

  // Imprimimos la información del módulo por el monitor serie
  //radio.printDetails();

  //Encendemos la radio
  radio.powerUp();

}

// ------ PROGRAMA ------

void loop()
{

  digitalWrite      (pinTRIGGERnear, LOW);
  delayMicroseconds (2);
  digitalWrite      (pinTRIGGERnear, HIGH);
  delayMicroseconds (5);
  digitalWrite      (pinTRIGGERnear, LOW);

  durationNear = pulseIn(pinECHOnear, HIGH);
  cmNear       = microsecondsToCentimeters(durationNear);

  digitalWrite      (pinTRIGGERfar, LOW);
  delayMicroseconds (2);
  digitalWrite      (pinTRIGGERfar, HIGH);
  delayMicroseconds (5);
  digitalWrite      (pinTRIGGERfar, LOW);

  durationFar = pulseIn(pinECHOfar, HIGH);
  cmFar       = microsecondsToCentimeters(durationFar);

/*
  Serial.print("Near: ");
  Serial.print(cmNear);
  Serial.print("cm \n");
  Serial.print("Far: ");
  Serial.print(cmFar);
  Serial.print("cm \n");
  Serial.print("Estado: ");
  Serial.print(estado);
  Serial.print("\n");
  Serial.print("P_Estado: ");
  Serial.print(p_estado);
  Serial.print("\n");
//*/

  estado = p_estado;

  if (estado == idle)
  {
    if ((cmNear != 0) && (cmNear < distanceTrigger))
    {
      p_estado = det_e;
      start_time = millis();
    }
    else if ((cmFar != 0) && (cmFar < distanceTrigger))
    {
      p_estado = det_s;
      start_time = millis();
    }
    else
    {
      p_estado = idle;
    }
  }
  else if (estado == det_e)
  {
    delay(DELAY);
    now = millis();
    if ((cmFar != 0) && (cmFar < distanceTrigger))
    {
      p_estado = det;
      deteccion = Entrada;
    }
    else if ((now - start_time) > CROSS_TIME)
    {
      // Timeout
      p_estado = idle;
    }
  }
  else if (estado == det_s)
  {
    delay(DELAY);
    now = millis();
    if ((cmNear != 0) && (cmNear < distanceTrigger))
    {
      p_estado = det;
      deteccion = Salida;
    }
    else if ((now - start_time) > CROSS_TIME)
    {
      // Timeout
      p_estado = idle;
    }
  }
  else if (estado == det)
  {
    if (deteccion == Entrada)
    {
      Serial.print("Evento: ENTRADA\t");
      notifyEvent(Entrada);
    }
    else if (deteccion == Salida)
    {
      Serial.print("Evento: SALIDA\t");
      notifyEvent(Salida);
    }
    else
    {
      Serial.print("Error\n");
    }
    p_estado = idle;
  }
  else
  {
    p_estado = idle;
  }

  // Si han pasado 10 segundos, podemos leer temperatura y humedad
  now = millis();
  if ((now - dht_last_time) > DHT_ACTIVATES)
  {

    // Establecemos este momento como la última lectura
    dht_last_time = now;

    // Leemos el sensor
    int chk = DHT.read11(pinDHT);

    if (chk == DHTLIB_OK)
    {

      hum = DHT.humidity;
      temp = DHT.temperature;

    }

    Serial.print("Humedad: ");
    Serial.print(hum);
    Serial.print(" %\t");
    Serial.print(" - Temperatura: ");
    Serial.print(temp);
    Serial.print("*C\t");

    // Enviamos los datos a la plataforma
    notifyData(temp, hum);

  }

}

/*
     La velocidad del sonido es de 340 m/s o 29 microsegundos por centimetro.
     El ping viaja de ida y vuelta, por tanto, para encontrar la distnacia al objeto
     se debe tomar la mitad de la distancia obtenida.
*/
long microsecondsToCentimeters ( long microseconds )
{
  return microseconds / 29 / 2;
}

void notifyEvent( int type )
{

  if (radio.txStandBy(timeoutPeriod))
  {

    // Si el inicio de la transferencia ha sido correcto...
    // Un valor 0 en la humedad, marca que el dato es un evento
    RF24DATOS[0] = 0;
    RF24DATOS[1] = type;

    // if (!radio.writeBlocking(&RF24DATOS, sizeof(RF24DATOS), timeoutPeriod))
    if (!radio.write(&RF24DATOS, sizeof(RF24DATOS)))
    {
      // Si el tiempo de espera se sobrepasa...
      Serial.println("- Radio: Tx ERROR (timeout)");
    }
    else
    {
      Serial.println("- Radio: Tx OK");
    }
  }
  else
  {
    // Si el inicio de la transferencia no ha sido correcto
    Serial.println("- Radio: Tx ERROR (escritura)");
  }

  //Serial.println("\n");

}

void notifyData( int temp, int hum )
{

  if (radio.txStandBy(timeoutPeriod))
  {

    // Si el inicio de la transferencia ha sido correcto...
    RF24DATOS[0] = hum;
    RF24DATOS[1] = temp;

    // if (!radio.writeBlocking(&RF24DATOS, sizeof(RF24DATOS), timeoutPeriod))
    if (!radio.write(&RF24DATOS, sizeof(RF24DATOS)))
    {
      // Si el tiempo de espera se sobrepasa...
      Serial.println("- Radio: Tx ERROR (timeout)");
    }
    else
    {
      Serial.println("- Radio: Tx OK");
    }
  }
  else
  {
    // Si el inicio de la transferencia no ha sido correcto
    Serial.println("- Radio: Tx ERROR (escritura)");
  }

  //Serial.println("\n");

}

