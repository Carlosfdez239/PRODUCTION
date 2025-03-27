/**
  * \file    ws_util.h
  * 
  * \brief   Utility Functions 
  * \author  Worldsensing  
  *
  * \section License
  *          (C) Copyright 2014 Worldsensing, http://www.worldsensing.com
  */
#ifndef __WS_UTIL_H__
#define __WS_UTIL_H__

#include <string.h>

#include "ws_types.h"
#include <ws_assert.h>

#include "math.h"

#ifdef GCC_ARMCM4
#include "em_device.h"
#endif

#ifdef __WS_UTIL_C__
#define WSUTIL_EXT
#else
#define WSUTIL_EXT extern
#endif

/************************************ Defines *************************************************/
#define WSUTIL_DEFAULT_FLOAT_PRINTF_LEN 10

/************************************ Typedef *************************************************/
typedef enum {
    WSUTIL_FLOATTOINT_ERROR_NONE = 0,
    WSUTIL_FLOATTOINT_ERROR_MAX,
    WSUTIL_FLOATTOINT_ERROR_MIN,
    WSUTIL_FLOATTOINT_ERROR_NAN
} WSUTIL_FLOATTOINT_ERROR_T;


typedef struct {
    float64_t Mean;
    float64_t M2;
    float64_t Delta;
    uint16_t  N;
} WSUTIL_STDEV_WELFORD_HANDLE_T;

/********************************** Function prototypes **************************************/
void                      itoa(int32_t n, char *p_out); /* NOLINT - avoid tidy check on "standard" susbtitution function. */
uint8_t                   WSUtil_Itoa(int32_t n, char *p_out);
int32_t                   WSUtil_StrNToInt32(uint8_t *p_str, uint8_t size, uint8_t **p_endptr);
int64_t                   WSUtil_StrNToInt64(uint8_t *p_str, uint8_t size, uint8_t **p_endptr);
int32_t                   WSUtil_StrNToFixedPoint32(uint8_t *p_str, uint8_t size, uint8_t **p_endptr, uint8_t *p_decimals);
void                      WSUtil_RandInit(void);
void                      WSUtil_FloatToStr(char *, uint8_t, float);
void                      WSUtil_Reverse(char *p_str, int length);
WSUTIL_FLOATTOINT_ERROR_T WSUtil_FloatToInt32(float32_t value, int32_t max_value, int32_t min_value, int8_t decimals, int32_t *p_int_value);
WSUTIL_FLOATTOINT_ERROR_T WSUtil_FloatToUInt32(float32_t value, uint32_t max_value, uint32_t min_value, int8_t decimals, uint32_t *p_int_value);
uint32_t                  WSUtil_BigEndianArraytoUint32(uint8_t *p_received, uint8_t num_bytes);
void                      WSUtil_StDevWelfordStep(WSUTIL_STDEV_WELFORD_HANDLE_T *p_handle, float64_t value);
void                      WSUtil_StDevWelfordInit(WSUTIL_STDEV_WELFORD_HANDLE_T *p_handle);
float64_t                 WSUtil_StDevPopulationWelfordResult(WSUTIL_STDEV_WELFORD_HANDLE_T *p_handle);
float64_t                 WSUtil_StDevSampleWelfordResult(WSUTIL_STDEV_WELFORD_HANDLE_T *p_handle);

int32_t WSUtil_ChangeMagnitudeInt32(int32_t value, int8_t exponent, bool_t *p_overflowed);

/********************************** Function implementation **************************************/
/**
 * \brief Maximum of two numbers
 *
 * \param a  number 1
 * \param b  number 2
 * \return Max(a,b)
 */
#define WSUTIL_MAX(a, b) ((a) > (b) ? (a) : (b))

/**
 * \brief Minimum of two numbers
 *
 * \param a  number 1
 * \param b  number 2
 * \return Max(a,b)
 */
#define WSUTIL_MIN(a, b) ((a) < (b) ? (a) : (b))

/**
 * \brief The rounded integer value of the x floating point number 
 *
 * \param x  floating point number
 * \return integer value of x rounded to the nearest value
 */
#define WSUTIL_FLOAT_TO_INT_ROUNDED(x) ((x) >= 0 ? (int32_t)((x) + 0.5) : (int32_t)((x)-0.5))

/**
 * \brief The rounded integer value of the x floating point number 
 * 
 * \param x  floating point number
 * \return integer value of x rounded to the nearest value
 * \note   Negative values are accepted so any number from 0 to -0.5 is converted to 0. 
 *         Any number further negative gives wrong results.
 */
#define WSUTIL_FLOAT_TO_UINT_ROUNDED(x) ((x) >= 0 ? (uint32_t)((x) + 0.5) : (uint32_t)((x)-0.5))

/**
 * \brief Ceiling of a division a/b
 *
 * \param a  number 1
 * \param b  number 2
 * \return ceiling(a,b)
 */
#define WSUTIL_CEILING(a, b) (((a) + (b)-1) / (b))

/**
 * \brief Checks if a number is in a range, if it is, the same value is returned, otherwise, the closest value in the range is returned.
 *
 * \param value         original value
 * \param range_bottom  
 * \param range_top     number 2
 * \return if value in range, value
 *         otherwise, closest value (top or bottom of the range)
 */
#define WSUTIL_ROUND_TO_RANGE(value, range_bottom, range_top) ((value) < (range_bottom) ? (range_bottom) : ((value) > (range_top) ? (range_top) : (value)))

/**
 * \brief Checks if the bit bit_num is set in value 
 *
 * \param value         value in which to set for the bit
 * \param bit_num       number of the bit to check. LSb is 0, MSb depends on the type of value and can be 7, 15, 31 or 63
 * 
 * \return DEF_TRUE if the bit bit_num is set in value, DEF_FALSE otherwise
 */
#define WSUTIL_IS_BIT_SET(value, bit_num) (0 != ((value) & (1u << (bit_num))))


/**
 * \brief Calculates the maximum value of an integer of the given bit length
 *
 * \param num_bits      number of representation bits
 * 
 * \return Maximum value of an int of num_bits bits.
 */
#define WSUTIL_N_BIT_MAX_INT_VALUE(num_bits) ((int64_t)((1uLL << ((num_bits)-1uLL)) - 1uLL))

/**
 * \brief Calculates the minimum value of an integer of the given bit length
 *
 * \param num_bits      number of representation bits
 * 
 * \return Minimum value of an int of num_bits bits.
 */
#define WSUTIL_N_BIT_MIN_INT_VALUE(num_bits) (-(int64_t)(1uLL << ((num_bits)-1uLL)))

/**
 * \brief Calculates the maximum value of an unsigned integer of the given bit length
 *
 * \param num_bits      number of representation bits
 * 
 * \return Maximum value of an unsigned int of num_bits bits.
 *
 * \note 1) The standard (1 << num_bits)-1 fails on the limit case when num_bits is 64 due to an overflow. To avoid it,
 *          the calculaton is divided in the maximum for num_bits-1 an then composed with the num_bits'th bit.
 */
#define WSUTIL_N_BIT_MAX_UINT_VALUE(num_bits) (((1uLL << ((num_bits)-1uLL)) - 1uLL) | (1uLL << ((num_bits)-1uLL))) /* See Note #1 */

/**
 * \brief Generates a mask of num_bits bits
 *
 * \param num_bits      number of bits for the mask
 * 
 * \return Mask with the lower num_bits set.
 *
 * \note 1) The mask is the same as the maximum unsingend integer value representable with that number of bits, so 
 *          the macro for max uint is used.
 */
#define WSUTIL_GET_MASK(num_bits) WSUTIL_N_BIT_MAX_UINT_VALUE(num_bits)


/**
 * \brief Converts radians to degrees
 *
 * \param  angle_radians  angle in radians
 * \return angle converted to degrees
 */
#define WSUTIL_RADIANS_TO_DEGREES(angle_radians) ((angle_radians)*180.0 / M_PI)

/**
 * \brief Generates a pseudo random value in a range.
 *        Call WSUtil_RandInit before using this macro.
 *
 * \param  min lower value of the range
 * \param  max upper value of the range
 * \return Pseudo random number in the range [min..max]
 */
#define WSUTIL_RANDR(min, max) ((int32_t)rand() % ((max) - (min) + 1) + (min))

/**
 * \brief Calculates the number of elements in an array.
 *
 * \param  array array
 * \return number of elements in the array
 */
#define WSUTIL_NUM_ELEM(array) (sizeof(array) / sizeof(array[0]))


/*************** Fixed Point Operations ************************/
#define WSUTIL_MILLIS_MULTIPLIER (1000)

/**
 * \brief Returns the rounded up value in units of a unsigned value given in Milli units.
 *
 * \param  x    Value in Milli units to round.
 * \return Round(x/1000)
 */
WS_STATIC_INLINE uint32_t WSUtil_RoundMillisU(uint32_t x) {
    return (x + (WSUTIL_MILLIS_MULTIPLIER >> 1)) / WSUTIL_MILLIS_MULTIPLIER;
}

/**
 * \brief Checks if the current task has been marked as being floating point by reading the FPCA bit. See note 1
 *
 * \return  DEF_TRUE if the FPCA bit is not enabled; DEF_FALSE otherwise.
 *
 * \note List of notes:
 *      1. When the FPCA register is active and a context switch takes place, the microcontroller will also store the
 *         FPU registers. This is used to debug if a suspicious task is mistakenly marked as being floating point,
 *         thus, requiring the extended registers during a context switch (which may cause a stack overlow error if not
 *         properly managed).
 */
WS_STATIC_INLINE bool_t WSUtil_TaskUsedFloatingPoint(void) {
#ifdef GCC_ARMCM4
    CONTROL_Type ctrl_reg = { .w = __get_CONTROL() };
    return ctrl_reg.b.FPCA == 1u ? DEF_TRUE : DEF_FALSE;
#else
    return DEF_FALSE;
#endif
}

/**
 * \brief Moves a bitfield within a value to another offset, possibly changing the value width.
 *
 * The macro extracts FIELD_SIZE bits located at offset IN_OFFSET from the input value
 * and shifts them to the offset OUT_OFFSET. All other bits in the output value are set to 0.
 * The macro is intended to streamline building values containing bitfields without using C struct bitfields for portability.
 *
 * Example:
 *
 *   #define FIELD_IN_OFFSET    5
 *   #define FIELD_OUT_OFFSET   19
 *   #define FIELD_FIELD_SIZE   6
 *   #define FIELD_WIDTH        uint32_t
 *
 *   uint16_t input_value = 0xA5D9;
 *   uint32_t output_value = WSUTIL_BITFIELD_MOVE(FIELD, input_value);
 *
 *                       _IN_OFFSET = 5
 *                              v
 *                ----------------------
 *   Input value  | 1010 0101 1101 1001|
 *                --------_______-------
 *                           \
 *                            \
 *                            |  _FIELD_SIZE = 6
 *                         ___v____
 *                ---------        ------------------------
 *   Output value |0000 0001 0111 0000 0000 0000 0000 0000|     _WIDTH = uint32_t
 *                -----------------------------------------
 *                                ^
 *                      _OUT_OFFSET = 19
 *
 * Usage:
 *
 *   #define TYPE_UP    0x80
 *   #define TYPE_DOWN  0xC0
 *   uint8_t type = TYPE_DOWN;
 *   uint8_t addr = 0x50;
 *   uint8_t seqno = 0x1A;
 *
 *   typedef union {
 *     struct {
 *       uint8_t type     :2; // 2 MSB of TYPE_*
 *       uint8_t addr     :8;
 *       uint8_t seqno    :6;
 *     };
 *     uint16_t plain;
 *   } PKT_T;

 *   PKT_T pkt = (PKT_T){
 *     .type = type>>6,
 *     .addr = addr,
 *     .seqno = seqno,
 *   }
 *
 *   uint16_t output = pkt.plain;
 *
 * would be equivalent to this:
 *
 *   #define TYPE_IN_OFFSET    6
 *   #define TYPE_OUT_OFFSET   14
 *   #define TYPE_FIELD_SIZE   2
 *   #define TYPE_WIDTH        uint16_t
 *
 *   #define ADDR_IN_OFFSET    0
 *   #define ADDR_OUT_OFFSET   6
 *   #define ADDR_FIELD_SIZE   8
 *   #define ADDR_WIDTH        uint16_t
 *
 *   #define SEQNO_IN_OFFSET   0
 *   #define SEQNO_OUT_OFFSET  0
 *   #define SEQNO_FIELD_SIZE  6
 *   #define SEQNO_WIDTH       uint16_t
 *
 *  uint16_t output = WSUTIL_BITFIELD_MOVE(TYPE, type)
 *                  | WSUTIL_BITFIELD_MOVE(ADDR, addr)
 *                  | WSUTIL_BITFIELD_MOVE(SEQNO, seqno);
 *
 * \param _field    Name of the defined field. This will be prepended to each suffix listed below to get the bitfield definition.
 * \param _in_value Value containing the input bitfield
 * \return Value of width '*_VALUE_WIDTH' where the bitfield is now at the offset '*_OUT_OFFSET'. All other bits of the value are set to 0.
 *
 * The following are the definitions of suffixes needed for each bitfield definition
 *
 * *_IN_OFFSET  Initial offset of the bitfield within the input value.
 * *_OUT_OFFSET Final offset of the bitfield within the output value
 * *_FIELD_SIZE Size of the bitfield in bits
 * *_WIDTH      Type of the value containing the output bitfield (e.g. 'uint16_t')
 */
#define WSUTIL_BITFIELD_MOVE(_field, _in_value) ((((_field##_WIDTH)((_in_value) >> _field##_IN_OFFSET)) & WSUTIL_GET_MASK(_field##_FIELD_SIZE)) << _field##_OUT_OFFSET)

/**
 * \brief Conversions of endiannes from and to network endianness to local endianness
 *
 * \param a  number 1
 *
 * \return a with the endianness fixed
 */
#ifdef GCC_ARMCM4
#ifndef ARM_MATH_BIG_ENDIAN
#define WSUTIL_ENDIAN_LITTLE_TO_LOCAL_16(a) (a)
#define WSUTIL_ENDIAN_LOCAL_TO_LITTLE_16(a) (a)
#define WSUTIL_ENDIAN_NET_TO_LOCAL_16(a)    __REV16(a)
#define WSUTIL_ENDIAN_LOCAL_TO_NET_16(a)    __REV16(a)
#define WSUTIL_ENDIAN_NET_TO_LOCAL_32(a)    __REV(a)
#define WSUTIL_ENDIAN_LOCAL_TO_NET_32(a)    __REV(a)
#define WSUTIL_ENDIAN_BIG_TO_LITTLE_32(a)   __REV(a)
#else
#error Endianness not supported by the macros.
#endif
#else
#define WSUTIL_ENDIAN_LITTLE_TO_LOCAL_16(a) (a)
#define WSUTIL_ENDIAN_NET_TO_LOCAL_16(a)    ((((a) >> 8) & 0xFFu) | (((a) << 8) & 0xFF00u))
#define WSUTIL_ENDIAN_LOCAL_TO_NET_16(a)    WSUTIL_ENDIAN_NET_TO_LOCAL_16(a)
#define WSUTIL_ENDIAN_BIG_TO_LITTLE_32(a)   ((((a) >> 24) & 0xFFu) | (((a) >> 8) & 0xFF00u) | (((a) << 8) & 0xFF0000u) | (((a) << 24) & 0xFF000000u))
#define WSUTIL_ENDIAN_NET_TO_LOCAL_32(a)    ((((a) >> 24) & 0xFFu) | (((a) >> 8) & 0xFF00u) | (((a) << 8) & 0xFF0000u) | (((a) << 24) & 0xFF000000u))
#define WSUTIL_ENDIAN_LOCAL_TO_NET_32(a)    WSUTIL_ENDIAN_NET_TO_LOCAL_32(a)
#endif

/**
 * \brief Divides two unsigned integers and returns the ceiling of the division
 *
 * \param a  Dividend
 * \param b  Divisor
 * \return Result of the division
 */
WS_STATIC_INLINE uint32_t WSUtil_DivCeilU(uint32_t a, uint32_t b) {
    WS_ASSERT(0 != b);

    if (0 == a) {
        return 0;
    }
    else {
        return 1 + ((a - 1) / b);
    }
}


/**
 * \brief Divides two 64 bit unsigned integers and returns the ceiling of the division
 *
 * \param a  Dividend
 * \param b  Divisor
 * \return Result of the division
 */
WS_STATIC_INLINE uint64_t WSUtil_DivCeilU64(uint64_t a, uint64_t b) {
    WS_ASSERT(0 != b);

    if (0 == a) {
        return 0;
    }
    else {
        return 1 + ((a - 1) / b);
    }
}

/**
 * \brief Extends the sign of the lower num_bits in value. The top (32-num_bits) bits must be 0.
 *
 * \param value     Value whose sign needs to be extended. All bits at the left of the bit 
 *                  num_bits must already be 0.
 * \param num_bits  Number of significant bits in value.
 * 
 * \return value with the sign extended.
 * 
 * \note 1) Algorithm from https://graphics.stanford.edu/~seander/bithacks.html#VariableSignExtend
 */
WS_STATIC_INLINE int32_t WSUtil_SignExtension(int32_t value, uint8_t num_bits) {
    WS_ASSERT(0 != num_bits && 32 >= num_bits);

    int32_t       result;
    int32_t const mask = 1U << (num_bits - 1);

    result = (((int32_t)value) ^ mask) - mask;
    return result;
}

/**
 * \brief Casts from int32_t to int8_t by binding to a max/min value possible
 * when it exceeds the limit
 *
 * \param value value to be casted
 * 
 * \return Value casted to int8_t and binded to max/min
 */
WS_STATIC_INLINE int8_t WSUtil_Int8Bind(int32_t value) {
    if (INT8_MAX < value) {
        return INT8_MAX;
    }
    else if (INT8_MIN > value) {
        return INT8_MIN;
    }
    else {
        return value;
    }
}

/**
 * \brief Casts from uint32_t to int8_t by binding to a max value possible when
 * it exceeds the limit
 *
 * \param value value to be casted
 *
 * \return Value casted to uint8_t and binded to max
 */
WS_STATIC_INLINE uint8_t WSUtil_UInt8Bind(uint32_t value) {
    if (UINT8_MAX < value) {
        return UINT8_MAX;
    }
    else {
        return value;
    }
}

#endif
