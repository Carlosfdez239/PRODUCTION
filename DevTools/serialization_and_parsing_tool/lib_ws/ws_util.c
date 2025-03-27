/**
 * \file    ws_util.c
 * \brief   Lib that provides utility functions
 * \author  Worldsensing  
 *
 * \section License
 *          (C) Copyright 2014 Worldsensing, http://www.worldsensing.com
 *
 * \note    Module Prefix: WSUtil_
 *
 */

#define __WS_UTIL_C__

#include "ws_types.h"
#include "ws_assert.h"
#include "ws_util.h"
#include <string.h>
#include "em_letimer.h"
#include "stdlib.h"
#include <stdio.h>

/** \addtogroup WS_Libs
 *   @{
 */

/** \addtogroup WS_UTIL
 *   @{
 */

/************************************ Defines *************************************************/

#define WSUTIL_MAX_DIGITS_IN_INT32 (10)

/************************************ Typedef *************************************************/


/************************************ Local Var **********************************************/


/******************************** Function prototypes ****************************************/

/**
 * \brief Reverse a string
 *
 * \param p_str  Pointer to string
 * \param length Length of string
 */
void WSUtil_Reverse(char *p_str, int length) {
    int  i = 0, j = length - 1;
    char tmp;
    while (i < j) {
        tmp      = p_str[i];
        p_str[i] = p_str[j];
        p_str[j] = tmp;
        i++;
        j--;
    }
}

/**
 * \brief Integer to array. Is not standard function. Got from http://www.milouchev.com/blog/2013/03/interview-questions-itoa-implementation-in-c/
 *
 * \param n      Number
 * \param p_out  Pointer to output string
 * 
 * \return  Number of chars used.
 */
uint8_t WSUtil_Itoa(int32_t n, char *p_out) {
    // if negative, need 1 char for the sign
    int sign = n < 0 ? 1 : 0;
    int i    = 0;
    if (n == 0) {
        p_out[i++] = '0';
    }
    else if (n < 0) {
        p_out[i++] = '-';
        n          = -n;
    }
    while (n > 0) {
        p_out[i++] = '0' + n % 10;
        n /= 10;
    }
    p_out[i] = '\0';
    WSUtil_Reverse(p_out + sign, i - sign);

    return i;
}

/**
 * \brief Integer to array. Is not standard function. Get from http://www.milouchev.com/blog/2013/03/interview-questions-itoa-implementation-in-c/
 *
 * \param n      Number
 * \param p_out  Pointer to output string
 */
void itoa(int32_t n, char *p_out) /* NOLINT - avoid tidy check on "standard" susbtitution function. */
{
    WSUtil_Itoa(n, p_out);
}

/**
 * \brief Converts the initial part of the string in p_str encoded in base 10 to a uint32_t.
 *        The  string  may begin a single optional '+' or '-' sign. The remainder of the string is converted to a int32_t 
 *        value in the obvious manner, stopping at the first character which is not a valid digit in.  
 *        If  p_endptr is not NULL, WSUtil_StrNToInt32() stores the address of the first invalid character in *p_endptr.  
 *        If there were no digits at all, WSUtil_StrNToInt32() stores the original value of p_str in *p_endptr (and returns 0). 
 *        In particular, if *p_str is not '\0' but **p_endptr is '\0' on return, the entire string is valid. If the entire buffer is 
 *        valid as an integer and does not end with a '\0', p_endptr will point to the first address after the buffer, 
 *        this can be checked with size == (p_endptr - p_str).
 *        
 *        If p_str contains a '+' or '-' sign with no digit afterwards, a 0 is returned with *p_endptr pointing to the 
 *        second position in the buffer.
 *
 * \param p_str:    Pointer to the buffer to convert.
 * \param size:     Size of p_str.
 * \param p_endptr: OUT: Pointer to the position in p_str where the conversion stopped.
 */
int32_t WSUtil_StrNToInt32(uint8_t *p_str, uint8_t size, uint8_t **p_endptr) {
    int32_t  res  = 0;
    int32_t  sign = 1;
    uint8_t  remaining;
    uint8_t *p_end;

    p_end = p_str;

    if (0 != size) {
        remaining = size;
        if ('-' == (*p_end)) {
            sign = -1;
            p_end++;
            remaining--;
        }
        else if ('+' == (*p_end)) {
            sign = 1;
            p_end++;
            remaining--;
        }

        while (remaining > 0 && ('0' <= (*p_end) && '9' >= (*p_end))) {
            res = res * 10 + ((*p_end) - '0');
            p_end++;
            remaining--;
        }

        res = res * sign;
    }

    if (NULL != p_endptr) {
        *p_endptr = p_end;
    }
    return res;
}

/**
 * \brief Converts the initial part of the string in p_str encoded in base 10 to a int64_t.
 *        The  string  may begin a single optional '+' or '-' sign. The remainder of the string is converted to a int64_t 
 *        value in the obvious manner, stopping at the first character which is not a valid digit in.  
 *        If  p_endptr is not NULL, WSUtil_StrNToInt64() stores the address of the first invalid character in *p_endptr.  
 *        If there were no digits at all, WSUtil_StrNToInt64() stores the original value of p_str in *p_endptr (and returns 0). 
 *        In particular, if *p_str is not '\0' but **p_endptr is '\0' on return, the entire string is valid. If the entire buffer is 
 *        valid as an integer and does not end with a '\0', p_endptr will point to the first address after the buffer, 
 *        this can be checked with size == (p_endptr - p_str).
 *        
 *        If p_str contains a '+' or '-' sign with no digit afterwards, a 0 is returned with *p_endptr pointing to the 
 *        second position in the buffer.
 *
 * \param p_str:    Pointer to the buffer to convert.
 * \param size:     Size of p_str.
 * \param p_endptr: OUT: Pointer to the position in p_str where the conversion stopped.
 */
int64_t WSUtil_StrNToInt64(uint8_t *p_str, uint8_t size, uint8_t **p_endptr) {
    int64_t  res  = 0;
    int64_t  sign = 1;
    uint8_t  remaining;
    uint8_t *p_end;

    p_end = p_str;

    if (0 != size) {
        remaining = size;
        if ('-' == (*p_end)) {
            sign = -1;
            p_end++;
            remaining--;
        }
        else if ('+' == (*p_end)) {
            sign = 1;
            p_end++;
            remaining--;
        }

        while (remaining > 0 && ('0' <= (*p_end) && '9' >= (*p_end))) {
            res = res * 10 + ((*p_end) - '0');
            p_end++;
            remaining--;
        }

        res = res * sign;
    }

    if (NULL != p_endptr) {
        *p_endptr = p_end;
    }
    return res;
}

/**
 * \brief Converts the initial part of the string in p_str encoded in base 10 to a dixed point encoded int32_t.
 *        The  string  may begin a single optional '+' or '-' sign. The remainder of the string is converted to a int32_t 
 *        value. If a dot is found during the conversion, p_decimals increases for every valid digit
 *        found after the dot. The conversion stops if there's another dot or a character which is not a valid digit.
 *        The conversion also stops if the next digit overflows the uint32_t maximum value.
 *        If  p_endptr is not NULL, WSUtil_StrNToFixedPoint32() stores the address of the first invalid character in *p_endptr.  
 *        If there were no digits at all, WSUtil_StrNToFixedPoint32() stores the original value of p_str in *p_endptr (and returns 0). 
 *        In particular, if *p_str is not '\0' but **p_endptr is '\0' on return, the entire string is valid. If the entire buffer is 
 *        valid as an integer and does not end with a '\0', p_endptr will point to the first address after the buffer, 
 *        this can be checked with size == (p_endptr - p_str).
 *        
 *        If p_str contains a '+' or '-' sign with no digit afterwards, a 0 is returned with *p_endptr pointing to the 
 *        second position in the buffer.
 *
 * \param p_str:        Pointer to the buffer to convert.
 * \param size:         Size of p_str.
 * \param p_endptr:     OUT: Pointer to the position in p_str where the conversion stopped.
 * \param p_decimals:   OUT: Pointer to the number of decimals that the float extracted has.
 */
int32_t WSUtil_StrNToFixedPoint32(uint8_t *p_str, uint8_t size, uint8_t **p_endptr, uint8_t *p_decimals) {
    int32_t  res  = 0;
    int32_t  sign = 1;
    uint8_t  remaining;
    uint8_t *p_end;
    bool_t   has_decimals = DEF_FALSE, stop_conversion = DEF_FALSE;

    p_end = p_str;

    if (0 != size) {
        remaining   = size;
        *p_decimals = 0;
        if ('-' == (*p_end)) {
            sign = -1;
            p_end++;
            remaining--;
        }
        else if ('+' == (*p_end)) {
            sign = 1;
            p_end++;
            remaining--;
        }

        while (remaining > 0 && DEF_FALSE == stop_conversion) {
            if ('0' <= (*p_end) && '9' >= (*p_end)) {
                if (sign == 1 && (res * 10 + ((*p_end) - '0')) < res) { /* Handle overflow */
                    stop_conversion = DEF_TRUE;
                }
                else if (sign == -1 && ((res * 10 + ((*p_end) - '0')) * sign) > res * sign) { /* Handle underflow */
                    stop_conversion = DEF_TRUE;
                }
                else {
                    res = res * 10 + ((*p_end) - '0');
                    p_end++;
                    remaining--;
                    if (DEF_TRUE == has_decimals) {
                        *p_decimals += 1;
                    }
                }
            }
            else if ('.' == (*p_end) && DEF_FALSE == has_decimals) {
                p_end++;
                remaining--;
                has_decimals = DEF_TRUE;
            }
            else {
                stop_conversion = DEF_TRUE;
            }
        }
        res = res * sign;
    }

    if (NULL != p_endptr) {
        *p_endptr = p_end;
    }
    return res;
}

/**
 * \brief Initializes the pseudo random number generator with a seed taken from the MCUs registers.
 */
#define WSUTIL_UNIQUE_0 (*(volatile uint32_t *)0x0FE081F0) /* Unique identifies of the gecko family, not defined elsewhere... */
#define WSUTIL_UNIQUE_1 (*(volatile uint32_t *)0x0FE081F4)
void WSUtil_RandInit(void) {
    uint32_t seed;

    seed = WSUTIL_UNIQUE_0 ^ WSUTIL_UNIQUE_1 ^ LETIMER_CounterGet(LETIMER0);

    srand(seed);
}

/**
 * \brief  Returns a string representation of the given float value
 *         The representation returned always has the sign (+/-) and has 6 decimals.
 *
 * \param  p_str   Pointer to char array. The array must be at least 10 chars long
 * \param  size    Size to hold the array including the terminating null byte
 * \param  value   Float to get the array for
 *
 */
void WSUtil_FloatToStr(char *p_str, uint8_t size, float value) {
    int32_t val_int;
    float   val_fract;
    char    val_sign = '+';

    if (0.0 > value) {
        val_sign = '-';
        value *= -1;
    }

    val_int   = value;
    val_fract = (value - val_int) * 1e6;

    snprintf(p_str, size, "%c%d.%06d", val_sign, (int)val_int, (int)val_fract);
}


/**
 * \brief  Converts a float32_t value to int32_t within the defined limits.
 *         Returns errors defined below.
 *
 * \param  value       Float to get the integer for
 * \param  max_value   Maximum input value allowed to process
 * \param  min_value   Minimum input value allowed to process
 * \param  decimals    Controls where to place the decimal places before converting to integer. Which the input value is multiplied by 10^decimals before conversion.
 *                     Negative values mean that input is divided by multiples of 10. See examples on note #1 
 * \param  p_int_value Pointer to output value.
 *
 * \return Errors in the process:
 *          - WSUTIL_FLOATTOINT_ERROR_NONE: No error. Converted value in p_int_value.
 *          - WSUTIL_FLOATTOINT_ERROR_MAX: Input value too big. Converted max_value in p_int_value.
 *          - WSUTIL_FLOATTOINT_ERROR_MIN: Input value too small. Converted min_value in p_int_value. 
 *          - WSUTIL_FLOATTOINT_ERROR_NAN: Input value is not representable as an integer. p_int_value is not modified. 
 *
 * \note 1) Examples of decimals usage:
 *          Input: 234.56
 *          With decimals = 2, multiply x 100 => output = 23456
 *          With decimals = -2, multiply x 0.01 output => 2
 *
 * \note 2) From INT32_MAX to INT32_MAX+0.4999 will be rounded to INT32_MAX by WSUTIL_FLOAT_TO_INT_ROUNDED, theoretically.
 *          But INT32_MAX+0.5 can't be represented by a float32_t. We left it to be matematically accurate and if someday it is changed to 64bits.
 */

WSUTIL_FLOATTOINT_ERROR_T WSUtil_FloatToInt32(float32_t value, int32_t max_value, int32_t min_value, int8_t decimals, int32_t *p_int_value) {
    WSUTIL_FLOATTOINT_ERROR_T ret;
    int8_t                    base = 10;
    float64_t                 value_float;
    int32_t                   value_int;

    if ((isfinite(value) == DEF_FALSE)) {
        ret = WSUTIL_FLOATTOINT_ERROR_NAN;
    }
    else {
        value_float = value * pow(base, decimals);
        value_int   = WSUTIL_FLOAT_TO_INT_ROUNDED(value_float);

        if (value_float >= ((float64_t)INT32_MAX + 0.5) || value_int > max_value) { /* Note 2 */
            *p_int_value = max_value;
            ret          = WSUTIL_FLOATTOINT_ERROR_MAX;
        }
        else if (value_float <= ((float32_t)INT32_MIN - 0.5) || value_int < min_value) { /* Note 2 */
            *p_int_value = min_value;
            ret          = WSUTIL_FLOATTOINT_ERROR_MIN;
        }
        else {
            *p_int_value = value_int;
            ret          = WSUTIL_FLOATTOINT_ERROR_NONE;
        }
    }
    return ret;
}
/**
 * \brief  Converts a float32_t value to uint32_t within the defined limits.
 *         Returns errors defined below.
 *
 * \param  value       Float to get the integer for
 * \param  max_value   Maximum input value allowed to process
 * \param  min_value   Minimum input value allowed to process
 * \param  decimals    Controls where to place the decimal places before converting to integer. Which the input value is multiplied by 10^decimals before conversion.
 *                     Negative values mean that input is divided by multiples of 10. See examples on note #1 
 * \param  p_int_value Pointer to output value.
 *
 * \return Errors in the process:
 *          - WSUTIL_FLOATTOINT_ERROR_NONE: No error. Converted value in p_int_value.
 *          - WSUTIL_FLOATTOINT_ERROR_MAX: Input value too big. Converted max_value in p_int_value.
 *          - WSUTIL_FLOATTOINT_ERROR_MIN: Input value too small. Converted min_value in p_int_value. 
 *          - WSUTIL_FLOATTOINT_ERROR_NAN: Input value is not representable as an integer. p_int_value is not modified. 
 *
 * \note 1) Examples of decimals usage:
 *          Input: 234.56
 *          With decimals = 2, multiply x 100 => output = 23456
 *          With decimals = -2, multiply x 0.01 output => 2
 *
 * \note 2) Closest representable float to UINT32_MAX is 4294967296, which is just outside the margin. The closest inside uint32_t range is 4294967040. 
 *          This means that literals in between will be converted to one or the othes, so passing literals to this function may result in an WSUTIL_FLOATTOINT_ERROR_MAX
 *          when the number could be representable in an int32_t.
 *          The logic left is matematically accurate and if someday it is changed to 64bits it can be reused.
 */
WSUTIL_FLOATTOINT_ERROR_T WSUtil_FloatToUInt32(float32_t value, uint32_t max_value, uint32_t min_value, int8_t decimals, uint32_t *p_int_value) {
    WSUTIL_FLOATTOINT_ERROR_T ret;
    int8_t                    base = 10;
    float64_t                 value_float;
    uint32_t                  value_int;

    if ((isfinite(value) == DEF_FALSE)) {
        ret = WSUTIL_FLOATTOINT_ERROR_NAN;
    }
    else {
        value_float = value * pow(base, decimals);
        value_int   = WSUTIL_FLOAT_TO_UINT_ROUNDED(value_float);

        if (value_float >= ((float64_t)UINT32_MAX + 0.5) || value_int > max_value) { /* Note 2 */
            *p_int_value = max_value;
            ret          = WSUTIL_FLOATTOINT_ERROR_MAX;
        }
        else if (value_float <= ((float32_t)0 - 0.5) || value_int < min_value) { /* Note 2 */
            *p_int_value = min_value;
            ret          = WSUTIL_FLOATTOINT_ERROR_MIN;
        }
        else {
            *p_int_value = value_int;
            ret          = WSUTIL_FLOATTOINT_ERROR_NONE;
        }
    }
    return ret;
}

/**
 * \brief Interpret an array of up to 4 bytes in big endian as an uint32
 *
 *  \Visual example for 2 bytes:
 *    +---------+
 *    |0xAA|0xBB|    2 bytes
 *    +---------+
 *         |
 *         v
 *    +----------+
 *    |0x0000AABB|
 *    +----------+
 * \param  received   Value to be rearranged.
 * \param  num_bytes  Number of bytes to rearrange.
 *
 * \return uint32_t
 */
uint32_t WSUtil_BigEndianArraytoUint32(uint8_t *p_received, uint8_t num_bytes) {
    uint32_t aux = 0;
    WS_ASSERT(num_bytes <= sizeof(aux));
    memcpy(&aux, p_received, num_bytes);
    aux = WSUTIL_ENDIAN_NET_TO_LOCAL_32(aux);
    aux = aux >> ((4 - num_bytes) * 8);
    return aux;
}

/**
 * \brief Initialization of Standard Deviation calculation using the Welford algorithm.
 *        See WSUtil_StDevWelfordStep header for more information.
 *
 * \param  p_handle   Pointer to the handle with the accumulated data.
 *
 */
void WSUtil_StDevWelfordInit(WSUTIL_STDEV_WELFORD_HANDLE_T *p_handle) {
    p_handle->Mean  = 0.0;
    p_handle->M2    = 0.0;
    p_handle->Delta = 0.0;
    p_handle->N     = 0;
}

/**
 * \brief Step for dinamically calculate the standard deviation using the Welford algorithm.
 *        
 *        Call the WSUtil_StDevWelfordInit function before using this function.
 *        Call this function once for every data point in the sample for which the stdev is needed.
 *        Call the WSUtil_StDevWelfordResult to get the final stdev result.
 *
 *        As a side product, the mean of the data can be found on p_handle->Mean.
 *        To allow using the algorithm for big amount of data float64_t are used.
 *
 *        Information on the algorithm used and sample implementation on which this code is based 
 *        can be found in:
 *        https://en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Welford's_online_algorithm
 *
 * \param  p_handle   Pointer to the handle with the accumulated data.
 * \param  value      Current value.
 *
 */
void WSUtil_StDevWelfordStep(WSUTIL_STDEV_WELFORD_HANDLE_T *p_handle, float64_t value) {
    p_handle->N++;

    p_handle->Delta = value - p_handle->Mean;
    p_handle->Mean += p_handle->Delta / (p_handle->N);
    p_handle->M2 += p_handle->Delta * (value - p_handle->Mean);
}

/**
 * \brief Last step of the Standard Deviation calculation using the Welford algorithm.
 *        This gives the Population Standard Deviation.
 *        See WSUtil_StDevWelfordStep header for more information.
 *
 * \param  p_handle   Pointer to the handle with the accumulated data.
 *
 * \return Standard deviation of the data represented in the handle.
 *
 * \note 1) The WSUtil_StDevWelfordStep function must be called at least once before 
 *          calling this function.
 */
float64_t WSUtil_StDevPopulationWelfordResult(WSUTIL_STDEV_WELFORD_HANDLE_T *p_handle) {
    WS_ASSERT(0 != p_handle->N); /* See note #1 */
    return sqrt(p_handle->M2 / (p_handle->N));
}

/**
 * \brief Last step of the Standard Deviation calculation using the Welford algorithm.
 *        This gives the Sample Standard Deviation.
 *        See WSUtil_StDevWelfordStep header for more information.
 *
 * \param  p_handle   Pointer to the handle with the accumulated data.
 *
 * \return Standard deviation of the data represented in the handle.
 *
 * \note 1) The WSUtil_StDevWelfordStep function must be called at least twice before 
 *          calling this function.
 */
float64_t WSUtil_StDevSampleWelfordResult(WSUTIL_STDEV_WELFORD_HANDLE_T *p_handle) {
    WS_ASSERT(1 < p_handle->N); /* See note #1 */
    return sqrt(p_handle->M2 / (p_handle->N - 1));
}

/**
 * \brief Returns the value passed changing the order of magnitude by be exponent
 *        given. So the result is value*10^exponent.
 *        If the exponent is positive, it will add as many zeroes at the right as 
 *        indicated by it, if it is negative, it will truncate as many digits as indicated.
 *
 * \param  value         Value to be corrected.
 * \param  exponent      Number of orders of magnitude to correct.
 * \param  p_overflowed  Return value on whether the magnitude change overflowed the result.
 *                       Optional parameter, use NULL if not interested in the result.
 *
 * \return value multiplied by 10^exponent. If the result overflows an int32_t, the returned
 *         value will be INT32_MAX or INT32_MIN depending on the sign of value.
 *
 * \note 1) Any exponent equal or beyond to the maximum number of digits in an integer will 
 *          overflow any input different from 0, so no need to go beyond this number of 
 *          iterations. Also, any input bigger than ~18 would overflow the int64_t used for
 *          the correction variable, which would result on undefined behaviour.
 *
 * \note 2) Detect the overflow by checking that the value is within the representable 
 *          values. The maximum/minimum value that can have the value is the range limit
 *          divided by the correction to be performed.
 *          If the corresponding check passes, it is safe to perform the correction (else
 *          case).
 *
 */
int32_t WSUtil_ChangeMagnitudeInt32(int32_t value, int8_t exponent, bool_t *p_overflowed) {
    int32_t iterations = WSUTIL_MIN(exponent, WSUTIL_MAX_DIGITS_IN_INT32); // See note #1
    int32_t result;
    bool_t  overflowed = DEF_FALSE;

    if (iterations > 0) {
        int64_t correction = 1;
        for (; iterations > 0; iterations--) {
            correction *= 10;
        }
        if (0 <= value && (INT32_MAX / correction) < value) { // See note #2
            overflowed = DEF_TRUE;
            result     = INT32_MAX;
        }
        else if (0 > value && (INT32_MIN / correction) > value) { // See note #2
            overflowed = DEF_TRUE;
            result     = INT32_MIN;
        }
        else {
            result = value * (int32_t)correction;
        }
    }
    else if (iterations < 0) {
        result = value;
        for (; iterations < 0; iterations++) {
            result /= 10;
        }
    }
    else {
        result = value;
    }

    if (NULL != p_overflowed) {
        *p_overflowed = overflowed;
    }

    return result;
}


/** @} (end addtogroup WS_UTIL) */
/** @} (end addtogroup WS_Libs) */
