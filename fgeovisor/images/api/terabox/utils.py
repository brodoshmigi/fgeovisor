from base64 import b64encode

def create_sign(sign1: str, sign2: str) -> str:
    """ sign js function(rc4) | Need for api request """
    p = list(range(256))
    a = [ord(sign1[i % len(sign1)]) for i in range(256)]
    result = []

    u = 0
    for q in range(256):
        u = (u + p[q] + a[q]) % 256
        p[q], p[u] = p[u], p[q]

    i = u = 0
    for q in range(len(sign2)):
        i = (i + 1) % 256
        u = (u + p[i]) % 256
        p[i], p[u] = p[u], p[i]
        k = p[(p[i] + p[u]) % 256]
        result.append(ord(sign2[q]) ^ k)
    
    result = b64encode(bytes(result))

    return result.decode()

def main():
    s1 = ''
    s3 = ''
    res = ''

    s1s = create_sign(s3, s1)

    print(s1s == res)

if __name__ == '__main__':
    main()