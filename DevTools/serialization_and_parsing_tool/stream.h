/**
  * \file    stream.h
  * 
  * \brief   Stream is fixed length buffer for output/input. 
  *          Put and get the bytes/bits in network order 
  * \author  Worldsensing  
  *
  * \section License
  *          (C) Copyright 2014 Worldsensing, http://www.worldsensing.com
  */
#ifndef __STREAM_H__
#define __STREAM_H__

#include "ws_types.h"
#include "string.h"

/* Type definition */

typedef union {
    uint32_t int_value;
    float    float_value;
} STREAM_FLOAT_T;

/* Prototypes */

uint32_t Stream_PutBits(uint8_t *p_buf, uint16_t buf_size, uint16_t bit_offset, uint32_t v, uint8_t num_bits);
uint32_t Stream_PutBits64(uint8_t *p_buf, uint16_t buf_size, uint16_t bit_offset, uint64_t v, uint8_t num_bits);
uint64_t Stream_GetBitsUint64(uint8_t const *p_buf, WS_UNUSED uint16_t buf_size, uint16_t bit_offset, uint8_t num_bits, uint64_t *p_i);
uint16_t Stream_GetBitsUint32(uint8_t const *p_buf, WS_UNUSED uint16_t buf_size, uint16_t bit_offset, uint8_t num_bits, uint32_t *p_i);
uint16_t Stream_GetBitsInt32(uint8_t const *p_buf, WS_UNUSED uint16_t buf_size, uint16_t bit_offset, uint8_t num_bits, int32_t *p_i);
uint32_t Stream_PutBitsFromBuffer(uint8_t *p_buf_out, WS_UNUSED uint16_t buf_out_size, uint16_t bit_offset_out,
                                  const uint8_t *p_buf_in, WS_UNUSED uint16_t buf_in_size, uint16_t bit_offset_in, uint16_t num_bits);

/**
 * \brief Put a float in the buffer
 *
 * \param p_buf Pointer to buffer
 * \param v     Float to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutFloat(uint8_t *p_buf, float v) {
    STREAM_FLOAT_T v_to_process = {
        .float_value = v
    };

    p_buf[0u] = (v_to_process.int_value >> 24u) & 0xFF;
    p_buf[1u] = (v_to_process.int_value >> 16u) & 0xFF;
    p_buf[2u] = (v_to_process.int_value >> 8u) & 0xFF;
    p_buf[3u] = v_to_process.int_value & 0xFF;
    return sizeof(float);
}
/**
 * \brief Put a uint32 in the buffer
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutUint32(uint8_t *p_buf, uint32_t v) {
    p_buf[0u] = (v >> 24u) & 0xFF;
    p_buf[1u] = (v >> 16u) & 0xFF;
    p_buf[2u] = (v >> 8u) & 0xFF;
    p_buf[3u] = v & 0xFF;
    return sizeof(uint32_t);
}

/**
 * \brief Put a int32 in the buffer
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutInt32(uint8_t *p_buf, int32_t v) {
    p_buf[0u] = (v >> 24u) & 0xFF;
    p_buf[1u] = (v >> 16u) & 0xFF;
    p_buf[2u] = (v >> 8u) & 0xFF;
    p_buf[3u] = v & 0xFF;
    return sizeof(int32_t);
}

/**
 * \brief Put a uint24 in the buffer
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutUint24(uint8_t *p_buf, uint32_t v) {
    p_buf[0u] = (v >> 16u) & 0xFF;
    p_buf[1u] = (v >> 8u) & 0xFF;
    p_buf[2u] = v & 0xFF;
    return sizeof(uint32_t) - 1u;
}

/**
 * \brief Put a int24 in the buffer
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutInt24(uint8_t *p_buf, int32_t v) {
    p_buf[0u] = (v >> 16u) & 0xFF;
    p_buf[1u] = (v >> 8u) & 0xFF;
    p_buf[2u] = v & 0xFF;
    return sizeof(int32_t) - 1u;
}

/**
 * \brief Put a uint16 in the buffer
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutUint16(uint8_t *p_buf, uint16_t v) {
    p_buf[0u] = (v >> 8u) & 0xFF;
    p_buf[1u] = v & 0xFF;
    return sizeof(uint16_t);
}

/**
 * \brief Put a int16 in the buffer
 *
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutInt16(uint8_t *p_buf, int16_t v) {
    p_buf[0u] = (v >> 8u) & 0xFF;
    p_buf[1u] = v & 0xFF;
    return sizeof(int16_t);
}

/**
 * \brief Put a uint8 in the buffer
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutUint8(uint8_t *p_buf, uint8_t v) {
    p_buf[0u] = v & 0xFF;
    return sizeof(uint8_t);
}

/**
 * \brief Put a int8 in the buffer
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutInt8(uint8_t *p_buf, int8_t v) {
    p_buf[0u] = v & 0xFF;
    return sizeof(int8_t);
}


/**
 * \brief Put a float in the buffer little endian format
 *
 * \param p_buf Pointer to buffer
 * \param v     Float to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutFloatLE(uint8_t *p_buf, float v) {
    STREAM_FLOAT_T v_to_process = {
        .float_value = v
    };
    p_buf[0u] = v_to_process.int_value & 0xFF;
    p_buf[1u] = (v_to_process.int_value >> 8u) & 0xFF;
    p_buf[2u] = (v_to_process.int_value >> 16u) & 0xFF;
    p_buf[3u] = (v_to_process.int_value >> 24u) & 0xFF;
    return sizeof(float);
}
/**
 * \brief Put a uint32 in the buffer little endian format
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutUint32LE(uint8_t *p_buf, uint32_t v) {
    p_buf[0u] = v & 0xFF;
    p_buf[1u] = (v >> 8u) & 0xFF;
    p_buf[2u] = (v >> 16u) & 0xFF;
    p_buf[3u] = (v >> 24u) & 0xFF;
    return sizeof(uint32_t);
}

/**
 * \brief Put a int32 in the buffer little endian format
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutInt32LE(uint8_t *p_buf, int32_t v) {
    p_buf[0u] = v & 0xFF;
    p_buf[1u] = (v >> 8u) & 0xFF;
    p_buf[2u] = (v >> 16u) & 0xFF;
    p_buf[3u] = (v >> 24u) & 0xFF;
    return sizeof(int32_t);
}

/**
 * \brief Put a uint24 in the buffer little endian format
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutUint24LE(uint8_t *p_buf, uint32_t v) {
    p_buf[0u] = v & 0xFF;
    p_buf[1u] = (v >> 8u) & 0xFF;
    p_buf[2u] = (v >> 16u) & 0xFF;
    return sizeof(uint32_t) - 1u;
}

/**
 * \brief Put a int24 in the buffer little endian format
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutInt24LE(uint8_t *p_buf, int32_t v) {
    p_buf[0u] = v & 0xFF;
    p_buf[1u] = (v >> 8u) & 0xFF;
    p_buf[2u] = (v >> 16u) & 0xFF;
    return sizeof(int32_t) - 1u;
}

/**
 * \brief Put a uint16 in the buffer little endian format
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutUint16LE(uint8_t *p_buf, uint16_t v) {
    p_buf[0u] = v & 0xFF;
    p_buf[1u] = (v >> 8u) & 0xFF;
    return sizeof(uint16_t);
}

/**
 * \brief Put a int16 in the buffer little endian format
 *
 *
 * \param p_buf Pointer to buffer
 * \param v     Integer to put in the buffer
 *
 * \return Number of bytes written in the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutInt16LE(uint8_t *p_buf, int16_t v) {
    p_buf[0u] = v & 0xFF;
    p_buf[1u] = (v >> 8u) & 0xFF;
    return sizeof(int16_t);
}


/**
 * \brief Get a Float from the buffer
 *
 * \param p_buf Pointer to buffer
 * \param p_f   Pointer to the returned value.
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_GetFloat(const uint8_t *p_buf, float *p_f) {
    uint32_t i;

    i = (p_buf[0] << 24);
    i |= (p_buf[1] << 16);
    i |= (p_buf[2] << 8);
    i |= (p_buf[3]);
    memmove(p_f, &i, sizeof(float)); /* sic */

    return sizeof(float);
}

/**
 * \brief Get a uint32 from the buffer
 *
 * \param p_buf Pointer to buffer
 * \param p_i   Pointer to the returned value.
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_GetUint32(const uint8_t *p_buf, uint32_t *p_i) {
    *p_i = (p_buf[0] << 24);
    *p_i |= (p_buf[1] << 16);
    *p_i |= (p_buf[2] << 8);
    *p_i |= (p_buf[3]);
    return sizeof(uint32_t);
}


/**
 * \brief Get a int32 from the buffer
 *
 * \param p_buf Pointer to buffer
 * \param p_i   Pointer to the returned value.
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_GetInt32(const uint8_t *p_buf, int32_t *p_i) {
    *p_i = (p_buf[0] << 24);
    *p_i |= (p_buf[1] << 16);
    *p_i |= (p_buf[2] << 8);
    *p_i |= (p_buf[3]);
    return sizeof(uint32_t);
}

/**
 * \brief Get a uint24 from the buffer
 *
 * \param p_buf Pointer to buffer
 * \param p_i   Pointer to the returned value.
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_GetUint24(const uint8_t *p_buf, uint32_t *p_i) {
    *p_i = (p_buf[0] << 16);
    *p_i |= (p_buf[1] << 8);
    *p_i |= (p_buf[2]);
    return sizeof(uint32_t) - 1;
}

/**
 * \brief Get a int24 from the buffer
 *
 * \param p_buf Pointer to buffer
 * \param p_i   Pointer to the returned value.
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_GetInt24(const uint8_t *p_buf, int32_t *p_i) {
    *p_i = (p_buf[0] << 16);
    *p_i |= (p_buf[1] << 8);
    *p_i |= (p_buf[2]);
    return sizeof(uint32_t) - 1;
}

/**
 * \brief Get a uint16 from the buffer
 *
 * \param p_buf Pointer to buffer
 * \param p_i   Pointer to the returned value.
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_GetUint16(const uint8_t *p_buf, uint16_t *p_i) {
    *p_i = (p_buf[0] << 8);
    *p_i |= (p_buf[1]);
    return sizeof(uint16_t);
}

/**
 * \brief Get a int16 from the buffer
 *
 * \param p_buf Pointer to buffer
 * \param p_i   Pointer to the returned value.
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_GetInt16(const uint8_t *p_buf, int16_t *p_i) {
    *p_i = (p_buf[0] << 8);
    *p_i |= (p_buf[1]);
    return sizeof(uint16_t);
}

/**
 * \brief Get a uint8 from the buffer
 *
 * \param p_buf Pointer to buffer
 * \param p_i   Pointer to the returned value.
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_GetUint8(const uint8_t *p_buf, uint8_t *p_i) {
    *p_i = (p_buf[0]);
    return sizeof(uint8_t);
}

/**
 * \brief Get a int8 from the buffer
 *
 * \param p_buf Pointer to buffer
 * \param p_i   Pointer to the returned value.
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_GetInt8(const uint8_t *p_buf, int8_t *p_i) {
    *p_i = (p_buf[0]);
    return sizeof(uint8_t);
}

/**
 * \brief Put a N bytes from the buffer to stream buffer
 *
 * \param p_buf Pointer to stream buffer
 * \param p_inbuf  Pointer to input buffer
 * \param n Number of bytes  
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_PutNBytes(uint8_t *p_buf, const uint8_t *p_inbuf, uint32_t n) {
    memcpy(p_buf, p_inbuf, n);
    return n;
}

/**
 * \brief Get a N bytes from the buffer
 *
 * \param p_buf Pointer to buffer
 * \param p_outbuf  Pointer to output buffer
 * \param n Number of bytes  
 *
 * \return Number of bytes read from the buffer
 */
WS_STATIC_INLINE uint32_t Stream_GetNBytes(const uint8_t *p_buf, uint8_t *p_outbuf, uint32_t n) {
    memcpy(p_outbuf, p_buf, n);
    return n;
}

#endif
