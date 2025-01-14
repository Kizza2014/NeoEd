import uuid
import zlib

BASE62_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

async def encode_base62(number, alphabet=BASE62_ALPHABET):
    base = len(alphabet)
    encoded = []
    while number:
        number, rem = divmod(number, base)
        encoded.append(alphabet[rem])
    return ''.join(reversed(encoded))

async def crc32_encode(unique_id):
    # Compute CRC32 checksum of the UUID
    checksum = zlib.crc32(unique_id.bytes) & 0xffffffff
    return await encode_base62(checksum)

async def generate_invitation_code(class_id: str) -> str:
    uid = '-'.join(class_id.split('-')[1:])
    unique_id = uuid.UUID(uid)
    encoded_id = await crc32_encode(unique_id)
    return encoded_id
