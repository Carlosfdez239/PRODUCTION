/**
  * \file    ws_assert.h
  * 
  * \brief   Assert Functions 
  * \author  Worldsensing  
  *
  * \section License
  *          (C) Copyright 2014 Worldsensing, http://www.worldsensing.com
  */
#ifndef __WS_ASSERT_H__
#define __WS_ASSERT_H__

#include "ws_types.h"
#include <assert.h>

#ifdef __WS_ASSERT_C__
#define WSASST_EXT
#else
#define WSASST_EXT extern
#endif

#define WSASST_ERROR_FILE_STRING_SIZE 30u

void WSAsst_Loop(char *p_file, uint32_t line) __attribute__((__noreturn__));

#ifndef WSASST_UNIT_TEST /* If the unit test symbol is defined,
                           * do not define the WS_ASSERT as it will
                           * be done by the test headers
                           */

#ifndef WSASST_DISABLED
#ifdef SCAN_BUILD
/*Defined so that scan-build tool can understand assert.*/
#define WS_ASSERT(cond) assert(cond); /* NOLINT - avoid tidy check on special name macro */
#else
#define WS_ASSERT(cond) /* NOLINT - avoid tidy check on special name macro */ \
    if (DEF_FALSE == (cond)) {                                                \
        WSAsst_Loop(__FILE__, __LINE__);                                      \
    }
#endif
#else
#define WS_ASSERT(cond) /* NOLINT - avoid tidy check on special name macro */
#endif
#endif

#endif
