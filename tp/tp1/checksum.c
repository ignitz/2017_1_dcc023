#include "checksum.h"

word16 checksum(byte *addr, word32 count) {
	register word32 sum = 0;

	// Main summing loop
	while(count > 1)
	{
		sum = sum + *((word16 *) addr);
		addr += 2;
		count = count - 2;
	}

	// Add left-over byte, if any
	if (count > 0)
		sum = sum + *((byte *) addr);

	// Fold 32-bit sum to 16 bits
	while (sum>>16)
		sum = (sum & 0xFFFF) + (sum >> 16);

	return(~sum);
}

//===== Main program ==========================================================
void _main(void) {
	byte        buff[1000]; // Buffer of packet bytes
	word16      check;            // 16-bit checksum value
	word32      i;                // Loop counter

	buff[0] = 0xDC;
	buff[1] = 0xC0;
	buff[2] = 0x23;
	buff[3] = 0xC2;
	buff[4] = 0xDC;
	buff[5] = 0xC0;
	buff[6] = 0x23;
	buff[7] = 0xC2;
	buff[8] = 0;
	buff[9] = 0;
	buff[10] = 0;
	buff[11] = 5;
	buff[12] = 0;
	buff[13] = 0;
	//buff[14] = 1;
	//buff[15] = 2;
	//buff[16] = 3;
	//buff[17] = 4;
	
	//printf("buff %u\n", (unsigned int)buff[14]);
	FILE* fp = fopen("testChecksum", "rb");
	int bytesRead = fread(buff+14, sizeof(unsigned char), 100, fp);
	printf("buff %c\n", buff[14]);
	printf("buff %c\n", buff[15]);
	printf("buff %c\n", buff[16]);
	printf("buff %c\n", buff[17]);

	// Compute the 16-bit checksum
	check = checksum(buff, 14+bytesRead);
	printf("checksum = %04X \n", check);

	//Verify Checksum
	buff[8] = check & 0xFFFF;	
	buff[9] = (check >> 8) & 0xFFFF;
	//printf("buff %02X\n", buff[8]);
	//printf("buff %02X\n", buff[9]);
	check = checksum(buff, 14+bytesRead);
	printf("checksum = %04X \n", check);
}
