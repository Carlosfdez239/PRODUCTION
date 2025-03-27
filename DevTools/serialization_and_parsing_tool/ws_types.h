/**
  * \file    ws_types.h
  * 
  * \brief   Internal worldsensing types definitions 
  * \author  Worldsensing  
  *
  * \section License
  *          (C) Copyright 2013 Worldsensing, http://www.worldsensing.com
  */
#ifndef __WS_TYPES_H__
#define __WS_TYPES_H__

#define __STDC_FORMAT_MACROS
#include <inttypes.h>
#include <stdint.h>


/** Floating point types */
typedef float  float32_t;
typedef double float64_t;

/** Bool type    */
typedef uint8_t bool_t;

/** Bool defines */
#define DEF_TRUE  1u
#define DEF_FALSE 0u

#define DEF_OK   1u
#define DEF_FAIL 0u

#define DEF_YES 1u
#define DEF_NO  0u

/** WS Union Data types */
typedef union {
    void     *Data_Ptr;
    uint8_t   UData8[4u];
    uint16_t  UData16[2u];
    uint32_t  UData32;
    int8_t    Data8[4u];
    int16_t   Data16[2u];
    int32_t   Data32;
    float32_t DataFloat;
} WS_DATA_UNION_T;

/** WS Inline */
#define WS_INLINE        inline
#define WS_STATIC_INLINE static inline

/** Unused parameter */
#define WS_UNUSED __attribute__((unused))


#ifndef WSASST_UNIT_TEST /* If the unit test symbol is defined,
                           * do not define the WS_ASSERT as it will
                           * be done by the test headers
                           */
/**
 * \brief Renames a function to allow the original name to be mocked in a UT file
 *
 * Important: the function cannot be declared as static
 *
 * \param name of the function
 */
#define WS_UNIT_TEST_MOCKABLE(_f) _f
#endif

#endif
