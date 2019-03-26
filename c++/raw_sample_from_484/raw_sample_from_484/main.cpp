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
uint8_t buffer[] = { 0x07, 0x6E, 0x82, 0x6C };
uint8_t read_buffer[3078];
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

	timeout.tv_sec = 1;
	timeout.tv_usec = 0;



	if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0)
	{
		
		printf("\n Socket creation error \n");
		//return -1;
	}
	else
	{
		printf("\n Socket create %d\n", sock);
	}

	

	if (setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (char *)&timeout, sizeof(timeout)) < 0)
	{
		printf("\n setsockopt failed \n");
	}

	if (setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, (char *)&timeout, sizeof(timeout)) < 0)
	{
		printf("\n setsockopt failed \n");
	}

	//result = ioctl(sock, FIONBIO, 0); 

	
	serv_addr.sin_addr.s_addr = inet_addr(address);

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(750);


	result = connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr));
	if (result < 0)
	{
		printf("\nConnection Failed: %d\n", result);

	}


	char file_name[30];
	char buf[30];
	gettimeofday(&tv, NULL);
	curtime = tv.tv_sec;
	strftime(buf, 30, "%Y-%m-%d %T", localtime(&curtime));
	std::sprintf(file_name, "%s.csv", buf);
	//myfile.open(file_name, std::ios_base::app); //append to file
	myfile.open(file_name);
	fd_set set;
	FD_ZERO(&set); /* clear the set */
	FD_SET(sock, &set); /* add our file descriptor to the set */

	while (1)
	{

			result = send(sock, buffer, sizeof(buffer), 0);
			result = read(sock, &read_buffer, sizeof(read_buffer));
			//result = select(sock + 1, &set, NULL, NULL, &timeout);

		
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



					//ready_data.x = xx;
					//ready_data.y = yy;
					//ready_data.z = zz;

					point++;

					//printf("%d %d %d\n", xx, yy, zz);


					//g_lock.lock();
					//if (big_buffer.size() > 5000) big_buffer.erase(big_buffer.begin());
					//big_buffer.push_back(ready_data);				
					//if (count_point == 0) ready_to_write = true;



					gettimeofday(&tv, NULL);
					curtime = tv.tv_sec;
					strftime(buf, 30, "%Y-%m-%d %T.", localtime(&curtime));

					myfile << buf << tv.tv_usec << ";" << xx << ";" << yy << ";" << zz << std::endl;





					//g_lock.unlock();


					//printf("write %d\n", big_buffer.size());






				//g_lock.unlock();

				}

				//if (ready_to_write == true)
				//{
				//	pthread_create(&write_thread, NULL, write_to_file, &big_buffer);
				//}





				printf("result %d\n", result);





				//printf("%d\n", big_buffer.size());


				//usleep(10000);					
			}
	}


	
    return 0;
}