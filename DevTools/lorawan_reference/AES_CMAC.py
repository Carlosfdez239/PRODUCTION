from struct import pack, unpack

from Crypto.Cipher import AES


class AesCmac:
    def gen_subkey(self, k):
        aes_128 = AES.new(k, AES.MODE_ECB)

        ln = aes_128.encrypt(b"\x00" * 16)

        l_high = unpack(">Q", ln[:8])[0]
        l_low = unpack(">Q", ln[8:])[0]

        k1_high = ((l_high << 1) | (l_low >> 63)) & 0xFFFFFFFFFFFFFFFF
        k1_low = (l_low << 1) & 0xFFFFFFFFFFFFFFFF

        if l_high >> 63:
            k1_low ^= 0x87

        k2_high = ((k1_high << 1) | (k1_low >> 63)) & 0xFFFFFFFFFFFFFFFF
        k2_low = ((k1_low << 1)) & 0xFFFFFFFFFFFFFFFF

        if k1_high >> 63:
            k2_low ^= 0x87

        k1 = pack(">QQ", k1_high, k1_low)
        k2 = pack(">QQ", k2_high, k2_low)

        return k1, k2

    def xor_128(self, n1, n2):
        j = b""
        for i in range(len(n1)):
            j += bytes([n1[i] ^ n2[i]])
        return j

    def pad(self, n):
        pad_len = 16 - len(n)
        return n + b"\x80" + b"\x00" * (pad_len - 1)

    def encode(self, k, m):
        const_b_size = 16
        const_zero = b"\x00" * 16

        aes_128 = AES.new(k, AES.MODE_ECB)
        k1, k2 = self.gen_subkey(k)
        n = int(len(m) / const_b_size)

        if n == 0:
            n = 1
            flag = False
        else:
            if (len(m) % const_b_size) == 0:
                flag = True
            else:
                n += 1
                flag = False

        m_n = m[(n - 1) * const_b_size :]
        if flag is True:
            m_last = self.xor_128(m_n, k1)
        else:
            m_last = self.xor_128(self.pad(m_n), k2)

        x = const_zero
        for i in range(n - 1):
            m_i = m[(i) * const_b_size :][:16]
            y = self.xor_128(x, m_i)
            x = aes_128.encrypt(y)
        y = self.xor_128(m_last, x)
        t = aes_128.encrypt(y)

        return t
