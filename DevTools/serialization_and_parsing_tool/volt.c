#include <stdio.h>
#include <stdlib.h>
#include "stream.h"
#include "ws_assert.h"

#define N_BUFF 64
uint32_t RTCA_GetTimeSec() {
    return 1000000000;
}

typedef struct msg_data {
    uint32_t timestamp;
    uint8_t  ChEnBitmap;
    uint8_t  InputType1;
    uint32_t Reading1;
    uint8_t  InputType2;
    uint32_t Reading2;
    uint8_t  InputType3;
    uint32_t Reading3;
    uint8_t  InputType4;
    uint32_t Reading4;
} MSG_DATA_T;


int Msg_Decode(const uint8_t *p_msg, uint16_t msg_size, WS_DATA_UNION_T *p_decoded_msg, uint16_t *p_decoded_size) {

    uint32_t    byte_count  = 0;
    uint16_t    bits_offset = 0;
    MSG_DATA_T *p_data      = malloc(sizeof(MSG_DATA_T));

    uint8_t  am_type;
    uint32_t timestamp;
    uint8_t  ch_en_bitmap;
    uint8_t  ch1_input_type;
    uint32_t ch1_reading;
    uint8_t  ch2_input_type;
    uint32_t ch2_reading;
    uint8_t  ch3_input_type;
    uint32_t ch3_reading;
    uint8_t  ch4_input_type;
    uint32_t ch4_reading;
    byte_count += Stream_GetUint8(&p_msg[byte_count], &am_type);
    byte_count += Stream_GetUint32(&p_msg[byte_count], &timestamp);
    byte_count += Stream_GetUint8(&p_msg[byte_count], &ch_en_bitmap);
    if (ch_en_bitmap & 0x01) {
        byte_count += Stream_GetUint8(&p_msg[byte_count], &ch1_input_type);
    }
    if (ch_en_bitmap & 0x01) {
        byte_count += Stream_GetUint24(&p_msg[byte_count], &ch1_reading);
    }
    if (ch_en_bitmap & 0x02) {
        byte_count += Stream_GetUint8(&p_msg[byte_count], &ch2_input_type);
    }
    if (ch_en_bitmap & 0x02) {
        byte_count += Stream_GetUint24(&p_msg[byte_count], &ch2_reading);
    }
    if (ch_en_bitmap & 0x04) {
        byte_count += Stream_GetUint8(&p_msg[byte_count], &ch3_input_type);
    }
    if (ch_en_bitmap & 0x04) {
        byte_count += Stream_GetUint24(&p_msg[byte_count], &ch3_reading);
    }
    if (ch_en_bitmap & 0x08) {
        byte_count += Stream_GetUint8(&p_msg[byte_count], &ch4_input_type);
    }
    if (ch_en_bitmap & 0x08) {
        byte_count += Stream_GetUint24(&p_msg[byte_count], &ch4_reading);
    }
    p_data->timestamp       = timestamp;
    p_data->ChEnBitmap      = ch_en_bitmap;
    p_data->InputType1      = ch1_input_type;
    p_data->Reading1        = ch1_reading;
    p_data->InputType2      = ch2_input_type;
    p_data->Reading2        = ch2_reading;
    p_data->InputType3      = ch3_input_type;
    p_data->Reading3        = ch3_reading;
    p_data->InputType4      = ch4_input_type;
    p_data->Reading4        = ch4_reading;
    p_decoded_msg->Data_Ptr = (void *)p_data;
    return 0;
}


uint8_t Msg_PayloadSerializeToStream(const void *p, WS_UNUSED uint16_t size, uint8_t *p_buf, WS_UNUSED uint16_t buf_size) {

    uint32_t    byte_count  = 0;
    uint16_t    bits_offset = 0;
    MSG_DATA_T *p_data      = (MSG_DATA_T *)p;

    uint8_t ch_en_bitmap = p_data->ChEnBitmap;
    byte_count += Stream_PutUint8(&p_buf[byte_count], 67);
    byte_count += Stream_PutUint32(&p_buf[byte_count], p_data->timestamp);
    byte_count += Stream_PutUint8(&p_buf[byte_count], p_data->ChEnBitmap);
    if (ch_en_bitmap & 0x01) {
        byte_count += Stream_PutUint8(&p_buf[byte_count], p_data->InputType1);
    }
    if (ch_en_bitmap & 0x01) {
        byte_count += Stream_PutUint24(&p_buf[byte_count], p_data->Reading1);
    }
    if (ch_en_bitmap & 0x02) {
        byte_count += Stream_PutUint8(&p_buf[byte_count], p_data->InputType2);
    }
    if (ch_en_bitmap & 0x02) {
        byte_count += Stream_PutUint24(&p_buf[byte_count], p_data->Reading2);
    }
    if (ch_en_bitmap & 0x04) {
        byte_count += Stream_PutUint8(&p_buf[byte_count], p_data->InputType3);
    }
    if (ch_en_bitmap & 0x04) {
        byte_count += Stream_PutUint24(&p_buf[byte_count], p_data->Reading3);
    }
    if (ch_en_bitmap & 0x08) {
        byte_count += Stream_PutUint8(&p_buf[byte_count], p_data->InputType4);
    }
    if (ch_en_bitmap & 0x08) {
        byte_count += Stream_PutUint24(&p_buf[byte_count], p_data->Reading4);
    }
    return byte_count;
}


int main() {
    uint8_t         p_buf[N_BUFF];
    uint8_t         byte_count;
    uint16_t        decoded_size;
    WS_DATA_UNION_T decoded_msg;
    memset(p_buf, 0, sizeof(p_buf));

    MSG_DATA_T  data;
    MSG_DATA_T *p_data = &data;

    p_data->ChEnBitmap = 0x3;
    p_data->InputType1 = 1;
    p_data->Reading1   = 2;
    p_data->InputType2 = 3;
    p_data->Reading2   = 4;
    p_data->InputType3 = 5;
    p_data->Reading3   = 6;
    p_data->InputType4 = 7;
    p_data->Reading4   = 8;

    byte_count = Msg_PayloadSerializeToStream(p_data, sizeof(MSG_DATA_T), p_buf, N_BUFF);

    memset(p_data, 0, sizeof(data));

    for (int i = 0; i < byte_count; i++) {
        printf("\\x%02x", p_buf[i]);
    }
    printf("\n");

    Msg_Decode(p_buf, byte_count, &decoded_msg, &decoded_size);

    p_data = (MSG_DATA_T *)decoded_msg.Data_Ptr;

    printf("%d %d %d %d %d %d %d %d %d",
           p_data->ChEnBitmap,
           p_data->InputType1,
           p_data->Reading1,
           p_data->InputType2,
           p_data->Reading2,
           p_data->InputType3,
           p_data->Reading3,
           p_data->InputType4,
           p_data->Reading4);


    return 0;
}
