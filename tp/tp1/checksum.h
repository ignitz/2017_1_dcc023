//===================================================== file = checksum.c =====
//=  Program to compute 16-bit Internet checksum                              =
//=============================================================================
//=  Notes: 1) Based on the C-code given in RFC 1071 (Computing the Internet  =
//=            Checksum by R. Braden, D. Borman, and C. Partridge, 1988).     =
//=         2) Streamlined for 32-bit machines.  All overflows are added-in   =
//=            after the summing loop and not within the summing loop on a    =
//=            an overflow-by-overflow basis.                                 =
//=---------------------------------------------------------------------------=
//=  Build:  bcc32 checksum.c, gcc checksum.c                                 =
//=---------------------------------------------------------------------------=
//=  History:  KJC (8/25/00) - Genesis                                        =
//=============================================================================
//----- Include files ---------------------------------------------------------
#include <stdio.h>                  // Needed for printf()
#include <stdlib.h>                 // Needed for rand()

//----- Type defines ----------------------------------------------------------
typedef unsigned char      byte;    // Byte is a char
typedef unsigned short int word16;  // 16-bit word is a short int
typedef unsigned int       word32;  // 32-bit word is an int

word16 checksum(byte *addr, word32 count);
void _main(void);
