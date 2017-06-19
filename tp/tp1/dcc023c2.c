#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h> 
#include <sys/socket.h>
#include <netinet/in.h>
#include <netdb.h> 

#include <sys/errno.h>  /* para errno, perror */
#include <time.h>

#include "checksum.h"

#define RECV_BUFFER_SZ 65550 //2^16 = 65536 + 14 header
#define SND_BUFFER_SZ 1000

typedef unsigned short int word16;  // 16-bit word is a short int
struct FrameBackup {
	unsigned char frame[SND_BUFFER_SZ+14];
	int frameSize;
	int sockfd;
};

struct FrameBackup frameBackup; 
int timeout;

void error(const char *msg) {
	perror(msg);
	exit(1);
}

int buildFrame(const word16 frameId, const word16 plSize, const char payload[], const int isLastFrame, unsigned char frame[]) {
	frame[0] = 0xDC;  	frame[1] = 0xC0;
	frame[2] = 0x23;	frame[3] = 0xC2;
	frame[4] = 0xDC;	frame[5] = 0xC0;
	frame[6] = 0x23;	frame[7] = 0xC2;
	frame[8] = 0; 		frame[9] = 0; //checksum

	int isDataFrame = (plSize > 0) || isLastFrame == 1;
	int length, flags;

	if (isDataFrame) {
		length = plSize;
		flags = (isLastFrame == 0) ? 0 : 0b01000000;
		memcpy(frame+14, payload, plSize);
	}
	else {
		length = 0;
		flags = 0b10000000;
	}

	//length (big endian - network byte order)
	frame[10] = (length >> 8) & 0xFFFF;
	frame[11] = length & 0xFFFF;

	frame[12] = frameId;
	frame[13] = flags;

	int frameTotalSize = length + 14;

	//loads the checksum (WARNING: little endian)
	word16 check = checksum(frame, frameTotalSize);
	frame[8] = check & 0xFFFF;
	frame[9] = (check >> 8) & 0xFFFF;

	//sanity check
	if (checksum(frame, frameTotalSize) != 0) {
		error("ERROR wrong checksum while building packet");
	}
	return frameTotalSize;
}

/* retVal:
 * 1 OK
 * 0 timeout
 * -1 error while reading from socket
 */
int recvFrame(const int sockfd, unsigned char frame[]) {
	unsigned char b;
	int bytesRead, foundSync = 0;
	do {
		bytesRead = read(sockfd, &b, 1);

		if (bytesRead > 0 && b == 0xDC) {
			bytesRead = read(sockfd, &b, 1);
			if (bytesRead < 1 || b != 0xC0) continue;
			bytesRead = read(sockfd, &b, 1);
			if (bytesRead < 1 || b != 0x23) continue;
			bytesRead = read(sockfd, &b, 1);
			if (bytesRead < 1 || b != 0xC2) continue;
			
			bytesRead = read(sockfd, &b, 1);
			if (bytesRead < 1 || b != 0xDC) continue;
			bytesRead = read(sockfd, &b, 1);
			if (bytesRead < 1 || b != 0xC0) continue;
			bytesRead = read(sockfd, &b, 1);
			if (bytesRead < 1 || b != 0x23) continue;
			bytesRead = read(sockfd, &b, 1);
			if (bytesRead < 1 || b != 0xC2) continue;
			break;
		}
	} while (bytesRead > 0);

	if (bytesRead > 0) bytesRead = read(sockfd, frame+8, 6);

	if (bytesRead < 0 && (errno == EAGAIN || errno == EWOULDBLOCK)) {
		//socket timeout
		errno = 0;
		return 0;
	} else if (bytesRead <= 0) {
		printf("Warning: socket return < 0 and it was not a timeout. It may be due end of connection\n");
		return -1;
	}

	frame[0] = 0xDC;	frame[1] = 0xC0;
	frame[2] = 0x23;	frame[3] = 0xC2;
	frame[4] = 0xDC;	frame[5] = 0xC0;
	frame[6] = 0x23;	frame[7] = 0xC2;

	word16 length = (frame[10] << 8) + frame[11];
	int flagAck = (frame[13] >> 7) == 1;
	
	if (flagAck == 0 && length > 0) {
		bytesRead = read(sockfd, frame+14, length);
		if (bytesRead < 0) {
			return 0;
		}
	}
	return 1;	
}

int validateFrame(unsigned char frame[]) {
	word16 length = (frame[10] << 8) + frame[11];
	word16 check = checksum(frame, 14+length);

	if (check != 0) {
		printf("Wrong CHECKSUM. The packet will be discarted.\n");
		return 0;
	}
	return 1;	
}

/* ret:
 * 	1 ack
 * 	0 data */
int isAckFrame(unsigned char frame[]) {
	word16 flags = frame[13];
	return (flags >> 7) == 1;
}

int isLastFrame(unsigned char frame[]) {
	word16 flags = frame[13];
	return (flags >> 6) == 1;
}

word16 getFrameId(unsigned char frame[]) {
	word16 id = frame[12];

	if (id != 0 && id != 1) {
		printf("YOU ARE DOING SOMETHING VERY WRONG!! frame id is neither 0 nor 1.\n");
		exit(-1);
	}
	return id;
}

word16 getPayload(unsigned char frame[], unsigned char payload[]) {
	word16 length = (frame[10] << 8) + frame[11];
	memcpy(payload, frame+14, length);
	return length;
}

int rejectCnt = 0;
int sendFrame(const int sockfd, const unsigned char frame[], const int frameSize, int isData) {
	if (isData) {
		frameBackup.sockfd = sockfd;
		frameBackup.frameSize = frameSize;
		memcpy(frameBackup.frame, frame, frameSize);
	}		

	int n;
#ifdef ENABLE_ERRORS
	rejectCnt++;
	if (rejectCnt % 7 == 0) { //lose frame
		n = frameSize;
		printf("jogando frame fora. id: %d\n", frame[12]);
	}
	else if (rejectCnt % 11 == 0) { //corrupt sync
		unsigned char corruptedFrame[SND_BUFFER_SZ+14];
		memcpy(corruptedFrame, frame, frameSize);
		corruptedFrame[3] = 0xAA;
		n = write(sockfd, corruptedFrame, frameSize);
		printf("corrompendo sync do frame. id: %d\n", frame[12]);
	}
	else if (rejectCnt % 13 == 0) { //corrupt length
		unsigned char corruptedFrame[SND_BUFFER_SZ+14];
		memcpy(corruptedFrame, frame, frameSize);
		corruptedFrame[11] = 0xAA;
		n = write(sockfd, corruptedFrame, frameSize);
		printf("corrompendo length do frame. id: %d\n", frame[12]);
	}
	else {
		n = write(sockfd, frame, frameSize);
	}
#else
	n = write(sockfd, frame, frameSize);
#endif

	if (n < 0) error("ERROR writing to socket");
	return n;	
}

void sendAck(const int sockfd, const word16 frameId) {
	unsigned char frame[14];
	int frameSize = buildFrame(frameId, 0, NULL, 0, frame);

	if (frameSize != 14) { 
		printf("Erro: ACK size = %d, should be 14. Closing program.\n", frameSize);
		exit(-1);
	}
	sendFrame(sockfd, frame, frameSize, 0);
}

void sendData (int sockfd, FILE *fp, const word16 frameId, int *hasDataToSend) {
	unsigned char sndBuffer[SND_BUFFER_SZ], frame[SND_BUFFER_SZ+14];
	int bytesRead = fread(sndBuffer, 1, SND_BUFFER_SZ, fp);
	if (bytesRead > 0) {
		int frameSize = buildFrame(frameId, bytesRead, sndBuffer, 0, frame);
		sendFrame(sockfd, frame, frameSize, 1);
		printf("Enviei!\n");
	}
	else {
		int frameSize = buildFrame(frameId, 0, NULL, 1, frame);
		sendFrame(sockfd, frame, frameSize, 1);
		*hasDataToSend = 0;
		printf("Terminei de enviar...\n");
	}
}

void settimer (int enable) {
	timeout = (enable == 0) ? 0 : time(0) + 1;
}

int hasTimedout () {
	time_t now = time(0);
	return (timeout != 0 && now > timeout);
}

void timeoutHandler () {
	printf ("Timed out! Sending frame again...\n");
	sendFrame(frameBackup.sockfd, frameBackup.frame, frameBackup.frameSize, 1);
	settimer(1);
}

int main(int argc, char *argv[]) {
	/******************************* Leitura dos parâmetros *********************************/
	if (argc < 5) {
		fprintf(stderr,"ERROR, wrong number of arguments\n");
		fprintf(stderr,"USAGE: ./dcc022c2 [-s <PORT>| -c <IPPAS>:<PORT>] <INPUT> <OUTPUT>\n");
		exit(1);
	}
	int isServer = argv[1][1] == 's';
	int portno;	char host[20];

	if (isServer == 1) {
		portno = atoi(argv[2]);
	} else {
		char * pch = strtok(argv[2], ":");
		strcpy(host, pch);
		pch = strtok(NULL, ":");
		portno = atoi(pch);
	}

	FILE* infp = fopen(argv[3], "rb");
	FILE* outfp = fopen(argv[4], "wb");
	if (outfp == NULL || infp == NULL) error("ERROR file not found");
	/***************************************************************************************/

	
	/************************** Configuração do socket e abertura ****************************/
	int serverSockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (serverSockfd < 0) 
		error("ERROR opening socket");

	struct sockaddr_in serv_addr;
	bzero((char *) &serv_addr, sizeof(serv_addr));
	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port = htons(portno);
	int clientSockfd;

	if (isServer == 1) {
		struct sockaddr_in cli_addr;
		serv_addr.sin_addr.s_addr = INADDR_ANY;
		if (bind(serverSockfd, (struct sockaddr *) &serv_addr, sizeof(serv_addr)) < 0) 
			error("ERROR on binding");
		listen(serverSockfd, 1);
		socklen_t clilen = sizeof(cli_addr);

		clientSockfd = accept(serverSockfd, (struct sockaddr *) &cli_addr, &clilen);
		if (clientSockfd < 0) 
			error("ERROR on accept");
	} else {	
		struct hostent *server = gethostbyname(host);
		if (server == NULL) {
			error("ERROR, no such host");
		}
		bcopy((char *)server->h_addr, (char *)&serv_addr.sin_addr.s_addr, server->h_length);
		if (connect(serverSockfd,(struct sockaddr *) &serv_addr,sizeof(serv_addr)) < 0) 
			error("ERROR connecting");
	}
	/***************************************************************************************/



	/*************************** Ciclo de recebimento e envio  *****************************/
	int sockfd = (isServer == 1) ? clientSockfd : serverSockfd;
	struct timeval tv;
	tv.tv_sec = 1; tv.tv_usec = 0;
	setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO,(struct timeval *)&tv, sizeof(struct timeval));
	settimer(0);

	unsigned char payload[RECV_BUFFER_SZ], frame[RECV_BUFFER_SZ];
	word16 lastSentFrameId = 1, lastAckedId = 1;
	int hasDataToReceive = 1, hasDataToSend = 1;

	lastSentFrameId = (lastSentFrameId + 1) % 2;
	sendData(sockfd, infp, lastSentFrameId, &hasDataToSend);
	settimer(1);

	while (hasDataToReceive || hasDataToSend) {
		//It must check timeout because if data packets are being received,
		//socket timeout will not be trigged.
		if (hasTimedout()) {
			printf("Timeout! (by time check)\n");
			timeoutHandler();
			continue;
		}
		
		int n = recvFrame(sockfd, frame);
		if (n == 0) {
			printf("Timeout! (socket timeout)\n");
			timeoutHandler();
			continue;
		} else if (n == -1) {
			break;
		}
		
		if (validateFrame(frame) == 0) {
			continue;
		}

		word16 frameId = getFrameId(frame);

		if (isAckFrame(frame) == 1) { //ack
			settimer(0);

			if (hasDataToSend == 1) {	
				lastSentFrameId = (lastSentFrameId + 1) % 2;
				sendData(sockfd, infp, lastSentFrameId, &hasDataToSend);
				settimer(1);
			}
			else{
				//disable socket timeout
				tv.tv_sec = 0; tv.tv_usec = 0;
				setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO,(struct timeval *)&tv, sizeof(struct timeval));	
				printf("Último frame enviado confirmado.\n");
			}
		}
		else { //data
			word16 payloadSize = getPayload(frame, payload);
			if (frameId != lastAckedId && payloadSize > 0) {
				fwrite(payload, 1, payloadSize, outfp);
				lastAckedId = frameId;
				printf("Recebi.\n");
			}
			sendAck(sockfd, frameId);

			if (isLastFrame(frame) == 1) {
				hasDataToReceive = 0;
				printf("Terminei de receber...\n");
			}
		}
	}
	/***************************************************************************************/

	printf("Terminei tudo. É hora de dar tchau!\n");
	fclose(infp);
	fclose(outfp);
	close(serverSockfd);
	close(clientSockfd);
}
