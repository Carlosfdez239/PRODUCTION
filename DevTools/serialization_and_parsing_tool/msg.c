
#include <stdio.h>
#include <stdlib.h>
#include "stream.h"
#include "ws_assert.h"

#define N_BUFF 64
uint32_t RTCA_GetTimeSec() {
    return 1000000000;
}

typedef struct msg_data {
    uint32_t  Uptime;
    float32_t Temperature;
    float32_t BatteryVoltage;
} MSG_DATA_T;


int Msg_Decode(const uint8_t *p_msg, uint16_t msg_size, WS_DATA_UNION_T *p_decoded_msg, uint16_t *p_decoded_size) {

    uint32_t    byte_count  = 0;
    uint16_t    bits_offset = 0;
    MSG_DATA_T *p_data      = malloc(sizeof(MSG_DATA_T));

    uint8_t  am_type;
    uint32_t timestamp;
    uint32_t uptime;
    uint16_t battery_voltage;
    int8_t   temperature;
    uint16_t serial_n;
    uint8_t  firmw_msb;
    uint8_t  firmw_lsb;
    uint32_t delta_units;
    uint32_t delta;
    byte_count += Stream_GetUint8(&p_msg[byte_count], &am_type);
    byte_count += Stream_GetUint32(&p_msg[byte_count], &timestamp);
    byte_count += Stream_GetUint32(&p_msg[byte_count], &uptime);
    byte_count += Stream_GetUint16(&p_msg[byte_count], &battery_voltage);
    byte_count += Stream_GetInt8(&p_msg[byte_count], &temperature);
    byte_count += Stream_GetUint16(&p_msg[byte_count], &serial_n);
    byte_count += Stream_GetUint8(&p_msg[byte_count], &firmw_msb);
    byte_count += Stream_GetUint8(&p_msg[byte_count], &firmw_lsb);
    bits_offset += Stream_GetBitsUint32(&p_msg[byte_count], sizeof(p_msg) - byte_count, bits_offset, 1, &delta_units);
    bits_offset += Stream_GetBitsUint32(&p_msg[byte_count], sizeof(p_msg) - byte_count, bits_offset, 15, &delta);
    bits_offset = 0;
    byte_count += 2;
    WS_ASSERT(18 == byte_count)
    p_data->Uptime          = uptime;
    p_data->Temperature     = (float32_t)temperature;
    p_data->BatteryVoltage  = (float32_t)battery_voltage * 10.;
    p_decoded_msg->Data_Ptr = (void *)p_data;
    return 0;
}


uint8_t Msg_PayloadSerializeToStream(const void *p, WS_UNUSED uint16_t size, uint8_t *p_buf, WS_UNUSED uint16_t buf_size) {

    uint32_t    byte_count  = 0;
    uint16_t    bits_offset = 0;
    MSG_DATA_T *p_data      = (MSG_DATA_T *)p;

    byte_count += Stream_PutUint8(&p_buf[byte_count], 70);
    byte_count += Stream_PutUint32(&p_buf[byte_count], RTCA_GetTimeSec());
    byte_count += Stream_PutUint32(&p_buf[byte_count], p_data->Uptime);
    byte_count += Stream_PutUint16(&p_buf[byte_count], (uint16_t)p_data->BatteryVoltage / 10.);
    byte_count += Stream_PutInt8(&p_buf[byte_count], (uint8_t)p_data->Temperature);
    byte_count += Stream_PutUint16(&p_buf[byte_count], 2);
    byte_count += Stream_PutUint8(&p_buf[byte_count], 1);
    byte_count += Stream_PutUint8(&p_buf[byte_count], 2);
    bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, 20, 1);
    bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, 50, 15);
    bits_offset = 0;
    byte_count += 2;
    WS_ASSERT(18 == byte_count)
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

    p_data->BatteryVoltage = 45600;
    p_data->Temperature    = 25.0;
    p_data->Uptime         = 15;

    byte_count = Msg_PayloadSerializeToStream(p_data, sizeof(MSG_DATA_T), p_buf, N_BUFF);

    memset(p_data, 0, sizeof(data));

    for (int i = 0; i < byte_count; i++) {
        printf("\\x%02x", p_buf[i]);
    }
    printf("\n");

    Msg_Decode(p_buf, byte_count, &decoded_msg, &decoded_size);

    p_data = (MSG_DATA_T *)decoded_msg.Data_Ptr;

    printf("%d %f %f", p_data->Uptime, p_data->Temperature, p_data->BatteryVoltage);

    return 0;
}
