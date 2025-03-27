#include <stdio.h>
#include "stream.h"
#include "ws_assert.h"

#define N_BUFF 64

typedef struct health_info {
    uint32_t  Uptime;         /**< Uptime of node            */
    float32_t Temperature;    /**< Temperature of the node   */
    float32_t BatteryVoltage; /**< Battery of node in mV     */
} HEALTH_INFO_T;

uint32_t RTCA_GetTimeSec() {
    return 1000000000;
}


int main() {
    uint8_t  p_buf[N_BUFF];
    uint32_t byte_count  = 0;
    uint16_t bits_offset = 0;
    memset(p_buf, 0, sizeof(p_buf));


#if 0
uint8_t h_version = 4;
uint8_t h_id_high = 0;
uint8_t h_pr_code = 2;
uint16_t h_id_low = 5;
uint8_t h_seq_num = 1;
uint8_t am_type = 70;
uint32_t timestamp = 540475440;
uint32_t uptime = 5000;
uint16_t battery_voltage = 4500;
int8_t temperature = 25;
uint16_t serial_n = 2;
uint8_t firmw_msb = 1;
uint8_t firmw_lsb = 2;
uint8_t delta_units = 0;
uint16_t delta = 32767;


bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, h_version, 4);
bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, h_id_high, 4);
bits_offset = 0;
byte_count += 1;
byte_count += Stream_PutUint8(&p_buf[byte_count], h_pr_code);
byte_count += Stream_PutUint16(&p_buf[byte_count], h_id_low);
byte_count += Stream_PutUint8(&p_buf[byte_count], h_seq_num);
byte_count += Stream_PutUint8(&p_buf[byte_count], am_type);
byte_count += Stream_PutUint32(&p_buf[byte_count], timestamp);
byte_count += Stream_PutUint32(&p_buf[byte_count], uptime);
byte_count += Stream_PutUint16(&p_buf[byte_count], battery_voltage);
byte_count += Stream_PutInt8(&p_buf[byte_count], temperature);
byte_count += Stream_PutUint16(&p_buf[byte_count], serial_n);
byte_count += Stream_PutUint8(&p_buf[byte_count], firmw_msb);
byte_count += Stream_PutUint8(&p_buf[byte_count], firmw_lsb);
bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, delta_units, 1);
bits_offset += Stream_PutBits(&p_buf[byte_count], sizeof(p_buf) - byte_count, bits_offset, delta, 15);
bits_offset = 0;
byte_count += 2;
WS_ASSERT(23 == byte_count)
#endif
    HEALTH_INFO_T  data;
    HEALTH_INFO_T *p_data = &data;

    p_data->BatteryVoltage = 45600;
    p_data->Temperature    = 25.0;
    p_data->Uptime         = 15;

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

    memset(p_data, 0, sizeof(data));

    for (int i = 0; i < byte_count; i++) {
        printf("\\x%02x", p_buf[i]);
    }
    printf("\n");
    byte_count     = 0;
    uint8_t *p_msg = p_buf;

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
    p_data->Uptime         = uptime;
    p_data->Temperature    = (float32_t)temperature;
    p_data->BatteryVoltage = (float32_t)battery_voltage * 10.;


    printf("%d %f %f", p_data->Uptime, p_data->Temperature, p_data->BatteryVoltage);


    return 0;
}
