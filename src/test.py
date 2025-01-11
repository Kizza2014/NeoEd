import uuid
import zlib

BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def encode_base62(number, alphabet=BASE62_ALPHABET):
    base = len(alphabet)
    encoded = []
    while number:
        number, rem = divmod(number, base)
        encoded.append(alphabet[rem])
    return ''.join(reversed(encoded))

def crc32_encode(unique_id):
    # Compute CRC32 checksum of the UUID
    checksum = zlib.crc32(unique_id.bytes) & 0xffffffff
    return encode_base62(checksum)

class_id = 'classroom-b620573c-7c3f-43cf-956a-62b667811394'
unique_id = uuid.UUID('-'.join(class_id.split('-')[1:]))

# Encode
encoded_id = crc32_encode(unique_id)

print("Original UUID:", unique_id)
print("CRC32 Encoded ID:", encoded_id)
