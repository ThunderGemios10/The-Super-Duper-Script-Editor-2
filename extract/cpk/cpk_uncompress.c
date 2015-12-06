/*
    Copyright 2009-2012 Luigi Auriemma

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA

    http://www.gnu.org/licenses/gpl-2.0.txt
*/

#include "cpk_uncompress.h"

////////////////////////////////////////////////////////////////////////////////
/// From unz.h of QuickBMS: http://aluigi.org/quickbms.htm
////////////////////////////////////////////////////////////////////////////////
#include <string.h>

// from cpk_uncompress.c of hcs: http://hcs64.com/files/utf_tab04.zip
// modified by Luigi Auriemma
// Decompress compressed segments in CRI CPK filesystems
static inline unsigned short CPK_get_next_bits(unsigned char *infile, int * const offset_p, unsigned char * const bit_pool_p, int * const bits_left_p, const int bit_count)
{
    unsigned short out_bits = 0;
    int num_bits_produced = 0;
    while (num_bits_produced < bit_count)
    {
        if (0 == *bits_left_p)
        {
            *bit_pool_p = infile[*offset_p];
            *bits_left_p = 8;
            --*offset_p;
        }

        int bits_this_round;
        if (*bits_left_p > (bit_count - num_bits_produced))
            bits_this_round = bit_count - num_bits_produced;
        else
            bits_this_round = *bits_left_p;

        out_bits <<= bits_this_round;
        out_bits |=
            (*bit_pool_p >> (*bits_left_p - bits_this_round)) &
            ((1 << bits_this_round) - 1);

        *bits_left_p -= bits_this_round;
        num_bits_produced += bits_this_round;
    }

    return out_bits;
}

#define CPK_GET_NEXT_BITS(bit_count) CPK_get_next_bits(infile, &input_offset, &bit_pool, &bits_left, bit_count)

int CPK_uncompress(unsigned char *infile, int input_size, unsigned char *output_buffer, int uncompressed_size) {
    if(uncompressed_size < 0x100) return(-1);
    uncompressed_size -= 0x100; // blah, terrible algorithm or terrible implementation

    const int input_end = input_size - 0x100 - 1;
    int input_offset = input_end;
    const int output_end = 0x100 + uncompressed_size - 1;
    unsigned char bit_pool = 0;
    int bits_left = 0;
    int bytes_output = 0;
    int     i;

    if(input_size < 0x100) return(-1);
    memcpy(output_buffer, infile + input_size - 0x100, 0x100);

    while ( bytes_output < uncompressed_size )
    {
        if(input_offset < 0) break;
        if (CPK_GET_NEXT_BITS(1))
        {
            int backreference_offset =
                output_end-bytes_output+CPK_GET_NEXT_BITS(13)+3;
            int backreference_length = 3;

            // decode variable length coding for length
            enum { vle_levels = 4 };
            int vle_lens[vle_levels] = { 2, 3, 5, 8 };
            int vle_level;
            for (vle_level = 0; vle_level < vle_levels; vle_level++)
            {
                int this_level = CPK_GET_NEXT_BITS(vle_lens[vle_level]);
                backreference_length += this_level;
                if (this_level != ((1 << vle_lens[vle_level])-1)) break;
            }
            if (vle_level == vle_levels)
            {
                int this_level;
                do
                {
                    this_level = CPK_GET_NEXT_BITS(8);
                    backreference_length += this_level;
                } while (this_level == 255);
            }

            //printf("0x%08lx backreference to 0x%lx, length 0x%lx\n", output_end-bytes_output, backreference_offset, backreference_length);
            for (i=0;i<backreference_length;i++)
            {
                output_buffer[output_end-bytes_output] = output_buffer[backreference_offset--];
                bytes_output++;
            }
        }
        else
        {
            // verbatim byte
            output_buffer[output_end-bytes_output] = CPK_GET_NEXT_BITS(8);
            //printf("0x%08lx verbatim byte\n", output_end-bytes_output);
            bytes_output++;
        }
    }

    return 0x100 + bytes_output;
}
