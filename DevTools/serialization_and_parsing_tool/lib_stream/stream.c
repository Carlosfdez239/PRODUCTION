/**
  * \file    stream.c
  * 
  * \brief   Stream is fixed length buffer for output/input. 
  *          Put and get the bytes/bits in network order 
  * \author  Worldsensing  
  *
  * \section License
  *          (C) Copyright 2014 Worldsensing, http://www.worldsensing.com
  *
  * \note    Module Prefix: Stream_
  *
  */

#define __STREAM_C__

#include "stream.h"
#include "ws_assert.h"
#include "ws_util.h"


/** \addtogroup Lib_Stream
 *   @{
 */

/************************************ Defines *************************************************/

/**
 * \brief Creates a mask with the n lowest bits set to 1.
 *
 * \param n  Number of bits set in the mask.
 *
 * \return Mask with the n lowes bits set.
 */
#define STREAM_N_BITS_MASK(n) (((uint64_t)1 << (n)) - 1)

#define STREAM_LOW_64_BITS_MASK  (0x00000000FFFFFFFFuLL)
#define STREAM_HIGH_64_BITS_MASK (0xFFFFFFFF00000000uLL)

#define STREAM_PUT_BITS_FROM_BUFFER_CHUNK_SIZE_BITS (32u)

/************************************ Typedef *************************************************/

/************************************ Local Var **********************************************/

/******************************** Function prototypes ****************************************/

/***************************** Function implementation ***************************************/

/**
 * \brief Put the number of bits specified from an uint8_t array as input in the given position into an uint8_t array 
 *        as output in the given position.  
 *        
 * \param p_buf_out           Pointer to the buffer to store the data
 * \param buf_out_size        Size of the buffer pointed by p_buf_out in bytes
 * \param bit_offset_out      Bit position in the buffer from which to put the bits.
 * \param p_buf_in            Pointer to the buffer to read the data
 * \param buf_in_size         Size of the buffer pointed by p_buf_in in bytes
 * \param bit_offset_in       Bit position in the buffer from which to read the bits.
 * \param num_bits            Number of bits to copy from p_buf_in to p_buf_out
 *
 * \return Number of bits written/read in/from the buffers
 *
 */
uint32_t Stream_PutBitsFromBuffer(uint8_t *p_buf_out, WS_UNUSED uint16_t buf_out_size, uint16_t bit_offset_out,
                                  const uint8_t *p_buf_in, WS_UNUSED uint16_t buf_in_size, uint16_t bit_offset_in, uint16_t num_bits) {

    uint32_t           chunk_value;
    WS_UNUSED uint16_t last_byte_out, last_byte_in;
    uint16_t           number_of_chunks, i;
    uint8_t            remaining_bits;

    if (num_bits != 0) {
        /* Check that the input buffer has enough size to read the data */
        last_byte_in = (bit_offset_in + num_bits - 1) / 8;
        WS_ASSERT(buf_in_size > last_byte_in);

        /* Check that the output buffer has enough size to store the data */
        last_byte_out = (bit_offset_out + num_bits - 1) / 8;
        WS_ASSERT(buf_out_size > last_byte_out);

        /* Number of chunks of 32 bits to be written */
        number_of_chunks = (num_bits / STREAM_PUT_BITS_FROM_BUFFER_CHUNK_SIZE_BITS);
        /* Remaining bits (<32) */
        remaining_bits = num_bits % STREAM_PUT_BITS_FROM_BUFFER_CHUNK_SIZE_BITS;

        /* Read&Write each chunk of data */
        for (i = 0; i < number_of_chunks; i++) {
            bit_offset_in += Stream_GetBitsUint32(p_buf_in, buf_in_size, bit_offset_in, STREAM_PUT_BITS_FROM_BUFFER_CHUNK_SIZE_BITS, &chunk_value);
            bit_offset_out += Stream_PutBits(p_buf_out, buf_out_size, bit_offset_out, chunk_value, STREAM_PUT_BITS_FROM_BUFFER_CHUNK_SIZE_BITS);
        }

        /* Read&Write the remaining bits if needed */
        if (remaining_bits > 0) {
            Stream_GetBitsUint32(p_buf_in, buf_in_size, bit_offset_in, remaining_bits, &chunk_value);
            Stream_PutBits(p_buf_out, buf_out_size, bit_offset_out, chunk_value, remaining_bits);
        }
    }

    return num_bits;
}

/**
 * \brief Put the number of bits specified into an uint8_t array in the given position. This function allows to enter 
 *        values ​​of up to 64 bits, splitting the value in the high and low part.  
 *        
 * \param p_buf       Pointer to buffer
 * \param buf_size    Size of the buffer pointed by p_buf in bytes
 * \param bit_offset  Bit position in the buffer from which to put the bits.
 * \param v           Unsigned integer with the required bit size.
 * \param num_bits    Number of bits to copy from v to p_buf
 *
 * \return Number of bits written in the buffer
 *                     
 *
 */
uint32_t Stream_PutBits64(uint8_t *p_buf, WS_UNUSED uint16_t buf_size, uint16_t bit_offset, uint64_t v, uint8_t num_bits) {
    uint32_t data_high = 0x00u;
    uint32_t data_low  = 0x00u;
    uint16_t bitcount  = bit_offset;

    WS_ASSERT(64 >= num_bits);

    data_high = (uint32_t)((v & STREAM_HIGH_64_BITS_MASK) >> 32);
    data_low  = (uint32_t)(v & STREAM_LOW_64_BITS_MASK);

    if (num_bits > 32) {
        bitcount += Stream_PutBits(p_buf, buf_size, bitcount, data_high, (num_bits - 32));
        Stream_PutBits(p_buf, buf_size, bitcount, data_low, 32);
    }
    else {
        Stream_PutBits(p_buf, buf_size, bitcount, data_low, num_bits);
    }

    return num_bits;
}

/**
 * \brief Get a the specified bits of the input array and interpret them as an unsigned integer of 64 bits.
 *
 * \param p_buf       Pointer to buffer.
 * \param buf_size    Size of the input buffer in bytes.
 * \param bit_offset  First bit wanted in the array.
 * \param num_bits    Number of bits wanted.
 * \param p_i         Pointer to the returned value.
 *
 * \return Number of bits read from the buffer.
 */
uint64_t Stream_GetBitsUint64(uint8_t const *p_buf, WS_UNUSED uint16_t buf_size, uint16_t bit_offset, uint8_t num_bits, uint64_t *p_i) {
    uint32_t data_high = 0x00u;
    uint32_t data_low  = 0x00u;
    uint16_t bitcount  = bit_offset;

    WS_ASSERT(NULL != p_buf);
    WS_ASSERT(NULL != p_i);
    WS_ASSERT(64 >= num_bits);

    if (num_bits > 32) {
        bitcount += Stream_GetBitsUint32(p_buf, buf_size, bitcount, (num_bits - 32), &data_high);
        Stream_GetBitsUint32(p_buf, buf_size, bitcount, 32, &data_low);
    }
    else {
        Stream_GetBitsUint32(p_buf, buf_size, bitcount, num_bits, &data_low);
    }

    *p_i = ((uint64_t)data_high << 32) | ((uint64_t)data_low);

    return num_bits;
}

/**
 * \brief Put the number of bits specified into an uint8_t array in the given position.
 *
 * \param p_buf       Pointer to buffer
 * \param buf_size    Size of the buffer pointed by p_buf in bytes
 * \param bit_offset  Bit position in the buffer from which to put the bits.
 * \param v           Unsigned integer with the bits to put in the lower part.
 * \param num_bits    Number of bits to copy from v to p_buf
 *
 * \return Number of bits written in the buffer
 * 
 * \note 1) The algorithm to put the bits to the array of uint8_t is the following:
 *             - Copy the value that has to be put (with the proper mask) to a uint64_t and shift it to align to the 
 *               position in the byte of the last bit that has to be put. As the input is of 32 bits, using a 64 bits 
 *               var ensures that we can shift it whithout overflows. Then we loop in the bytes to substitute creating
 *               the masks and shifting the 64 bit value at every loop. Example:
 *               
 *                 Put 7 ones from the bit 4 of an array of 3:
 *                   v = 0x0000007F
 *                   p_buf = |xxxxdddd|dddxxxxx|xxxxxxxx|  -> d marks the destination of the bits, x is any value of the bit
 *               
 *                 First copy the value to a 64 bit value:
 *                      
 *                   v_64 =  |00000000|00000000|00000000|00000000|00000000|00000000|00000000|01111111|  
 *                   
 *                 Then shift the value to align it with the position of the last bit to set in p_buf:
 *                   v_64 << 5 =  |00000000|00000000|00000000|00000000|00000000|00000000|00001111|11100000|  
 *                   p_buf =                                                            |xxxxdddd|dddxxxxx|xxxxxxxx|
 *                   
 *                 Now we set the byte 1 of the p_buf:
 *                   mask = |11100000|
 *                   
 *                   Delete bits in the byte 1 in the positions marked by the mask:
 *                     p_buf =    |xxxxdddd|000xxxxx|xxxxxxxx|
 *                     
 *                   Or it with the last byte of the v_64:
 *                     p_buf =    |xxxxdddd|111xxxxx|xxxxxxxx|
 *                     
 *                   Shift 8 bits to the right the v_64;
 *                     v_64 >> 8 =  |00000000|00000000|00000000|00000000|00000000|00000000|00000000|00001111|
 *                 
 *                 Now we set the byte 0 of the p_buf:
 *                   mask = |00001111|
 *                   
 *                   Delete bits in the byte 0 in the positions marked by the mask:
 *                     p_buf =    |xxxx0000|111xxxxx|xxxxxxxx|
 *                     
 *                   Or it with the last byte of the v_64:
 *                     p_buf =    |xxxx1111|111xxxxx|xxxxxxxx|
 *                     
 *                 All the bits have been set, so no more shifts or loops needed.
 *                     
 *
 */
uint32_t Stream_PutBits(uint8_t *p_buf, WS_UNUSED uint16_t buf_size, uint16_t bit_offset, uint32_t v, uint8_t num_bits) {
    uint16_t first_byte;
    uint8_t  first_bit_offset;
    uint16_t last_byte;
    uint8_t  last_bit_offset;
    uint8_t  current_mask;
    uint64_t value_shifted;
    uint16_t i;

    WS_ASSERT(32 >= num_bits);

    if (0 != num_bits) {
        first_byte       = bit_offset / 8;
        first_bit_offset = bit_offset % 8;
        last_byte        = (bit_offset + num_bits - 1) / 8;
        last_bit_offset  = (bit_offset + num_bits - 1) % 8;


        WS_ASSERT(buf_size > last_byte);

        value_shifted = (v & STREAM_N_BITS_MASK(num_bits)) << (8u - 1u - last_bit_offset);

        /* get the left part of the last byte's mask */
        current_mask = ~(STREAM_N_BITS_MASK(8u - 1 - last_bit_offset));

        for (i = last_byte; i > first_byte; i--) { /* Skip the first byte to change, as the mask may have to be trimed from the left */
            p_buf[i] &= ~current_mask;
            p_buf[i] |= value_shifted;
            value_shifted = value_shifted >> 8u;

            current_mask = 0xFF; /* Either the next loop will use a full byte, or it will exit the loop and the mask will be trimmed from the left */
        }

        /* trim the left part for the first byte's mask */
        current_mask &= STREAM_N_BITS_MASK(8 - first_bit_offset);
        p_buf[i] &= ~current_mask;
        p_buf[i] |= value_shifted;
    }

    return num_bits;
}

/**
 * \brief Get a the specified bits of the input array and interpret them as an unsigned integer of 32 bits.
 *
 * \param p_buf       Pointer to buffer.
 * \param buf_size    Size of the input buffer in bytes.
 * \param bit_offset  First bit wanted in the array.
 * \param num_bits    Number of bits wanted.
 * \param p_i         Pointer to the returned value.
 *
 * \return Number of bits read from the buffer.
 */
uint16_t Stream_GetBitsUint32(uint8_t const *p_buf, WS_UNUSED uint16_t buf_size, uint16_t bit_offset, uint8_t num_bits, uint32_t *p_i) {
    uint16_t byte_num;
    uint8_t  first_bit;
    uint8_t  before_mask;
    uint32_t result     = 0x0u;
    uint8_t  bits_to_go = num_bits;

    WS_ASSERT(NULL != p_buf);
    WS_ASSERT(NULL != p_i);
    WS_ASSERT((sizeof(uint32_t) * 8) >= num_bits);

    byte_num = bit_offset / 8;
    WS_ASSERT(buf_size > byte_num);

    first_bit = bit_offset - byte_num * 8;

    before_mask = 0xFFu >> first_bit;

    result = p_buf[byte_num] & before_mask; /* Get all the valid bits off the first byte   */
    byte_num++;

    if (8 >= first_bit + num_bits) { /* All bits in first byte: shift result to the right */
                                     /* to discard not wanted lower bits.                 */
        result     = result >> (8 - (first_bit + num_bits));
        bits_to_go = 0;
    }
    else { /* Substract already got bits */
        bits_to_go -= 8 - first_bit;
    }

    while (bits_to_go >= 8) { /* Do full bytes */
        WS_ASSERT(buf_size > byte_num);

        result = (result << 8) | p_buf[byte_num];
        bits_to_go -= 8;
        byte_num++;
    }

    if (0 < bits_to_go) { /* If any bit remaining, get it from higher bits of */
                          /* the last byte.                                   */
        WS_ASSERT(buf_size > byte_num);
        result = (result << bits_to_go) | (p_buf[byte_num] >> (8 - bits_to_go));
    }

    *p_i = result;

    return num_bits;
}

/**
 * \brief Get a the specified bits of the input array and interpret them as an signed integer.
 *
 * \param p_buf       Pointer to buffer.
 * \param buf_size    Size of the input buffer.
 * \param bit_offset  First bit wanted in the array.
 * \param num_bits    Number of bits wanted.
 * \param p_i         Pointer to the returned value.
 *
 * \return Number of bits read from the buffer.
 */
uint16_t Stream_GetBitsInt32(uint8_t const *p_buf, WS_UNUSED uint16_t buf_size, uint16_t bit_offset, uint8_t num_bits, int32_t *p_i) {
    uint32_t unsigned_result;
    int32_t  result;
    uint32_t bits_used;
    WS_ASSERT(NULL != p_buf);
    WS_ASSERT(NULL != p_i);

    bits_used = Stream_GetBitsUint32(p_buf, buf_size, bit_offset, num_bits, &unsigned_result);

    result = WSUtil_SignExtension(unsigned_result, num_bits);

    *p_i = result;
    return bits_used;
}

/** @} (end addtogroup Lib_Stream) */
