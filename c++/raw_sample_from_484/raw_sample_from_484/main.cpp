#include <cstdio>
#include <cstdlib>
#include <signal.h>
#include <pthread.h>
#include <string> 
#include <iostream>
#include <vector>
#include <unistd.h>
#include <fstream>

#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>
#include <netinet/in.h> 
#include<netdb.h>

#include <mutex>
#include <ctime>
#include <chrono>
#include <sys/time.h>
#include <sys/ioctl.h>

#include "serial.h"
#include <bcm2835.h>


struct pack_points_signals
{
	int64_t data;
};

struct pack_return_signals
{
	uint8_t adr;           //0
	uint8_t func_code;     //1
	uint16_t count_point;        //2,3
	
	pack_points_signals data;    //4..3076
} __attribute__((packed));


struct processed_data
{
	int32_t x;
	int32_t y;
	int32_t z;
} ready_data;






int result = 0;
//uint8_t write_buffer[] = { 0x07, 0x6E, 0x82, 0x6C };
uint8_t write_buffer[] = { 0x04, 0x6E, 0x82, 0x9C };
//uint8_t buffer[] = { 0x01, 0x03, 0x00, 0x00, 0x00, 0x01, 0x84, 0x0A };
//uint8_t buffer[] = { 0x01, 0x03, 0x02, 0x03, 0x22, 0x38, 0xAD };
uint8_t read_buffer[5000];

std::vector<processed_data> big_buffer;



//struct sockaddr_in address;
int sock = 0, valread;
struct sockaddr_in serv_addr;
const char* address = "192.168.5.131";
struct timeval timeout;



int count_recived_data = 0;
int count_read = 0;
int32_t xx = 0;
int32_t yy = 0;
int32_t zz = 0;
bool ready_to_write = false;
std::mutex g_lock;
struct timeval tv;
std::ofstream myfile;
time_t curtime;







//void* write_to_file(void* args)
//{		
//	char file_name[30];
//	char buf[30];
//
//
//	gettimeofday(&tv, NULL);
//	curtime = tv.tv_sec;
//	strftime(buf, 30, "%Y-%m-%d %T", localtime(&curtime));
//		
//	std::sprintf(file_name, "%s.csv", buf);
//
//
//	//myfile.open(file_name, std::ios_base::app); //append to file
//	myfile.open(file_name);
//
//
//	try
//	{
//		g_lock.lock();
//		
//
//		for (int i = 0; i < big_buffer.size(); i++)
//		{
//			gettimeofday(&tv, NULL);
//			curtime = tv.tv_sec;
//			strftime(buf, 30, "%Y-%m-%d %T.", localtime(&curtime));
//
//			myfile << buf << tv.tv_usec << ";" << big_buffer[i].x << ";" << big_buffer[i].y << ";" << big_buffer[i].z << std::endl;
//		}
//
//		ready_to_write = false;
//
//
//		g_lock.unlock();
//		
//
//		printf("write %d\n", big_buffer.size());
//		//printf("write %d\n");
//	}
//
//	catch (const std::exception&)
//	{
//		printf("write error\n");
//	}
//
//	myfile.close();
//
//	return 0;
//}





int main()
{
	pthread_t write_thread;

	//timeout.tv_sec = 1;
	//timeout.tv_usec = 0;

	char file_name[30];
	char buf[30];
	int fd;


	fd = openPort("/dev/serial0", B921600);


	uint64_t te = 0;


	gettimeofday(&tv, NULL);
	curtime = tv.tv_sec;
	strftime(buf, 30, "%Y-%m-%d %T", localtime(&curtime));
	std::sprintf(file_name, "%s.csv", buf);
	//myfile.open(file_name, std::ios_base::app); //append to file
	myfile.open(file_name);
	//fd_set set;
	//FD_ZERO(&set); /* clear the set */
	//FD_SET(sock, &set); /* add our file descriptor to the set */

	bcm2835_init();
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_38, BCM2835_GPIO_FSEL_OUTP);
	bcm2835_gpio_fsel(RPI_V2_GPIO_P1_40, BCM2835_GPIO_FSEL_OUTP);


	while (1)
	{

		bcm2835_gpio_write(RPI_V2_GPIO_P1_38, HIGH); //DE(Driver Enable - разрешение работы передатчика)
		bcm2835_gpio_write(RPI_V2_GPIO_P1_40, LOW); //~RE (Receiver Enable - разрешение работы приёмника) 						
		
		
		result = sendData(fd, write_buffer, sizeof(write_buffer));		
		printf("send %d \n", result);


		bcm2835_gpio_write(RPI_V2_GPIO_P1_38, LOW);
		bcm2835_gpio_write(RPI_V2_GPIO_P1_40, HIGH);
		
		
		usleep(500000);
		result = readData(fd, read_buffer, 3078, 300000);
		

		for (int i = 0; i < 4; i++)
		{
			printf("%00X ", read_buffer[i]);
		}
		

		if (result > 0)
		{


			pack_return_signals* pack = (pack_return_signals*)&read_buffer;

			int count_point = pack->count_point > 1000 ? 0 : pack->count_point;						

			pack_points_signals* point = (pack_points_signals*)&pack->data;

			while (count_point-- > 0)
			{

				xx = (int32_t)((point->data & 0x1FFFFF));
				yy = (int32_t)((point->data >> 21) & (0x1FFFFF));
				zz = (int32_t)((point->data >> 42) & (0x1FFFFF));


				xx = xx > 0xFFFFF ? xx - 0x200000 : xx;
				yy = yy > 0xFFFFF ? yy - 0x200000 : yy;
				zz = zz > 0xFFFFF ? zz - 0x200000 : zz;




				gettimeofday(&tv, NULL);
				curtime = tv.tv_sec;
				strftime(buf, 30, "%Y-%m-%d %T.", localtime(&curtime));

				myfile << buf << tv.tv_usec << ";" << xx << ";" << yy << ";" << zz << std::endl;
				//myfile << te++ << ";" << xx << ";" << yy << ";" << zz << std::endl;


				point++;
			}



		}

		//printf("%d %d %d\n", xx, yy, zz);
		//printf("result %d \n", result);

		//usleep(4000);
		
	}


	bcm2835_close();
	return 0;
}