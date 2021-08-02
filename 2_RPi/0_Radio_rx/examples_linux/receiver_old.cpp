/*
 * Autor: Álvaro Martín Rodríguez
 * 
 * Trabajo Final de Master
 * 
 * Elemento: Receptor RF24 en RPi 3B
 * 
 */

//#include <time.h>
#include <fstream>
#include <iostream>
#include <unistd.h>
#include <RF24/RF24.h>

#define   LECTURA   0
#define   ESCRITURA 1

#define   hubFIFO   "/temp/hubFIFO"

using namespace std;

/******* Datos en Tx ********/

struct tx_data {
  int hum;
  int temp;
  //char * date;  
};

/*******    ******   ********/

/******* Raspberry Pi *******/

//RPi, with Spidev, GPIO 15, pin 10#
RF24 radio(15,0);

/*******    *******   *******/

// Direcciones radio para la comunicación
const uint64_t pipes[] = {0xABCDABCD71LL, 0xF0F0F0F0E1LL};

// Descriptores para la comunicación con el hub
//int pipes_descr[2] = {257, 288};


int main(int argc, char** argv){

  /******* Variables *******/
  
  // Para recibir los datos de arduino
  uint8_t data[2];
  
  // Para detener el programa
  int inactivity = 0;
  
  // Para marcar el tiempo de los datos
  //time_t rawtime;
  //struct tm * timeinfo;
  
  // Para la tubería
  // int fifo, status;
  std::fstream fs;
  
  // Para transmitir los datos al hub en python
  struct tx_data data2send;
  long totalbytes = sizeof(data2send);
  
  /*******  *******   ******/

  cout << " +++ INICIALIZANDO +++\n\n";

  // Inicializando y configurando la radio
  radio.begin();

  // Retraso entre reintentos, reintentos
  radio.setRetries(1,1);
  
  radio.setDataRate(RF24_2MBPS);
  radio.setChannel(76);
  
  // Para depuración
  radio.printDetails();
  cout << "\n+++ RECIBIENDO +++ \n";
  
  // Creamos las tuberías
  // pipe(pipes_descr);
  // fifo = open(hubFIFO, std::fstream::out);
  fs.open(hubFIFO, std::fstream::out);
  
  // Especificamos el tamaño de las transmisiones
  totalbytes = sizeof(tx_data);

  /*******    *******   *******/
  
  // Abrimos la tubería de recepción de datos
  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1, pipes[1]);
	
	radio.startListening();
	
	// Mientras se reciban datos con cierta regularidad
	while (inactivity < 10)
	{
    
    // cout << "Probando... " << inactivity << "\n";
    
    // Si hay datos para leer
    if ( radio.available() )
    {
    
      // Reset del contador de inactividad: hemos recibido
      inactivity = 0;
    
      // Lectura de los datos
      memset(&data, 0,sizeof(data));
      radio.read( &data, sizeof(data) );
      
      // Marca de tiempo
      //time(&rawtime);
      //timeinfo = localtime(&rawtime);
      
      //cout << asctime(timeinfo) << "\t-\t"; 
      
      // Convertimos los datos
      data2send.hum = (int) data[0];
      data2send.temp = (int) data[1];
      
      if ( ((int) data[0]) != 0)
      {
      
        // Humedad y temperatura
        cout << "Humedad: " << data2send.hum << "\t-\t";
        cout << "Temperatura: " << data2send.temp << "*C\n";
        
        // Los enviamos
        // write(pipes_descr[ESCRITURA], &data2send, totalbytes);
        write(fifo, &data2send, totalbytes);
      
      }
      else
      {
      
        // Evento
        if ( ((int) data[1]) == 1 )
        {
        
          cout << "EVENTO: Entrada\n";
          
          // Lo enviamos
          // write(pipes_descr[ESCRITURA], &data2send, totalbytes);
          write(fifo, &data2send, totalbytes);
          
        }
        else if ( ((int) data[1]) == 2 )
        {
        
          cout << "EVENTO: Salida\n";
          
          // Los enviamos
          // write(pipes_descr[ESCRITURA], &data2send, totalbytes);
          write(fifo, &data2send, totalbytes);
          
        }
        else
        {
          cout << "Lectura de DHT invalida...\n";
        }

      }
      
    }
    else
    {
    
      // Contador de inactividad
      inactivity++;
      // cout << inactivity << "\n";
      
    }
    
    // Inactividad en microsegundos
    usleep(250*1000);

	}

  // Cerramos las tuberias
  // close(pipes_descr[LECTURA]);
  // close(pipes_descr[ESCRITURA]);
  
  close(fifo);

  return 0;
  
}

