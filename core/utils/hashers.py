"""
Based on Django 2.2.x
"""
import base64
import random
import hashlib
import warnings
import importlib
from collections import OrderedDict

# This will never be a valid encoded hash
UNUSABLE_PASSWORD_PREFIX = '!'
# number of random chars to add after UNUSABLE_PASSWORD_PREFIX
UNUSABLE_PASSWORD_SUFFIX_LENGTH = 40


try:
    random = random.SystemRandom()
except NotImplementedError:
    RuntimeError('A secure pseudo-random number generator is not available.')


def is_password_usable(encoded):
    if encoded is None or encoded.startswith(UNUSABLE_PASSWORD_PREFIX):
        return False
    return True


def check_password(password, encoded):
    """
    Returns a boolean that indicates whether the raw password matches the three part encoded digest.
    """
    if password is None or not is_password_usable(encoded):
        return False

    hasher = PBKDF2PasswordHasher()
    return hasher.verify(password, encoded)


def make_password(password, salt=None):
    """
    Turn a plain-text password into a hash for database storage

    Same as encode() but generates a new random salt.
    If password is None then a concatenation of
    UNUSABLE_PASSWORD_PREFIX and a random string will be returned
    which disallows logins. Additional random string reduces chances
    of gaining access to staff or superuser accounts.
    See ticket #20079 for more info.
    """
    if password is None:
        return (UNUSABLE_PASSWORD_PREFIX
                + get_random_string(UNUSABLE_PASSWORD_SUFFIX_LENGTH))
    hasher = PBKDF2PasswordHasher()
    salt = salt or hasher.salt()
    return hasher.encode(password, salt)


def mask_hash(hash, show=6, char="*"):
    """
    Returns the given hash, with only the first ``show`` number shown. The
    rest are masked with ``char`` for security reasons.
    """
    masked = hash[:show]
    masked += char * len(hash[show:])
    return masked


def get_random_string(length=12,
                      allowed_chars='abcdefghijklmnopqrstuvwxyz'
                                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
    """
    Returns a securely generated random string.
    The default length of 12 with the a-z, A-Z, 0-9 character set returns
    a 71-bit value. log_2((26+26+10)^12) =~ 71 bits

    Requires operating system provided random number generator.
    """
    return ''.join(random.choice(allowed_chars) for i in range(length))


def constant_time_compare(val1, val2):
    """
    Returns True if the two strings are equal, False otherwise.
    The time taken is independent of the number of characters that match.
    For the sake of simplicity, this function executes in constant time only
    when the two strings have the same length. It short-circuits when they
    have different lengths. Since Django only uses it to compare hashes of
    known expected length, this is acceptable.
    """
    if len(val1) != len(val2):
        return False
    result = 0
    if isinstance(val1, bytes) and isinstance(val2, bytes):
        for x, y in zip(val1, val2):
            result |= x ^ y
    else:
        for x, y in zip(val1, val2):
            result |= ord(x) ^ ord(y)
    return result == 0


class BasePasswordHasher(object):
    """
    Abstract base class for password hashers

    When creating your own hasher, you need to override algorithm,
    verify(), encode() and safe_summary().

    PasswordHasher objects are immutable.
    """
    algorithm = None
    library = None

    def _load_library(self):
        if self.library is not None:
            if isinstance(self.library, (tuple, list)):
                name, mod_path = self.library
            else:
                mod_path = self.library
            try:
                module = importlib.import_module(mod_path)
            except ImportError as e:
                raise ValueError("Couldn't load %r algorithm library: %s" %
                                 (self.__class__.__name__, e))
            return module
        raise ValueError("Hasher %r doesn't specify a library attribute" %
                         self.__class__.__name__)

    def salt(self):
        """
        Generates a cryptographically secure nonce salt in ASCII
        """
        return get_random_string()

    def verify(self, password, encoded):
        """
        Checks if the given password is correct
        """
        raise NotImplementedError(
            'subclasses of BasePasswordHasher must provide a verify() method'
        )

    def encode(self, password, salt):
        """
        Creates an encoded database value

        The result is normally formatted as "algorithm$salt$hash" and
        must be fewer than 128 characters.
        """
        raise NotImplementedError(
            'subclasses of BasePasswordHasher must provide an encode() method'
        )

    def safe_summary(self, encoded):
        """
        Returns a summary of safe values

        The result is a dictionary and will be used where the password field
        must be displayed to construct a safe representation of the password.
        """
        raise NotImplementedError(
            'subclasses of BasePasswordHasher must provide a safe_summary() method'
        )

    def must_update(self, encoded):
        return False

    def harden_runtime(self, password, encoded):
        """
        Bridge the runtime gap between the work factor supplied in `encoded`
        and the work factor suggested by this hasher.

        Taking PBKDF2 as an example, if `encoded` contains 20000 iterations and
        `self.iterations` is 30000, this method should run password through
        another 10000 iterations of PBKDF2. Similar approaches should exist
        for any hasher that has a work factor. If not, this method should be
        defined as a no-op to silence the warning.
        """
        warnings.warn(
            'subclasses of BasePasswordHasher should provide a harden_runtime() method'
        )


class PBKDF2PasswordHasher(BasePasswordHasher):
    """
    Secure password hashing using the PBKDF2 algorithm (recommended)

    Configured to use PBKDF2 + HMAC + SHA256.
    The result is a 64 byte binary string.  Iterations may be changed
    safely but you must rename the algorithm if you change SHA256.
    """
    algorithm = "pbkdf2_sha256"
    iterations = 150000
    digest = hashlib.sha256

    def encode(self, password, salt, iterations=None):
        assert password is not None
        assert salt and '$' not in salt
        iterations = iterations or self.iterations
        hash = pbkdf2(password, salt, iterations, digest=self.digest)
        hash = base64.b64encode(hash).decode('ascii').strip()
        return "%s$%d$%s$%s" % (self.algorithm, iterations, salt, hash)

    def verify(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        encoded_2 = self.encode(password, salt, int(iterations))
        return constant_time_compare(encoded, encoded_2)

    def safe_summary(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        assert algorithm == self.algorithm
        return OrderedDict([
            ('algorithm', algorithm),
            ('iterations', iterations),
            ('salt', mask_hash(salt)),
            ('hash', mask_hash(hash)),
        ])

    def must_update(self, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        return int(iterations) != self.iterations

    def harden_runtime(self, password, encoded):
        algorithm, iterations, salt, hash = encoded.split('$', 3)
        extra_iterations = self.iterations - int(iterations)
        if extra_iterations > 0:
            self.encode(password, salt, extra_iterations)


def force_bytes(s, encoding='utf-8', errors='strict'):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.
    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if isinstance(s, memoryview):
        return bytes(s)
    return str(s).encode(encoding, errors)


def pbkdf2(password, salt, iterations, dklen=0, digest=None):
    """Return the hash of password using pbkdf2."""
    if digest is None:
        digest = hashlib.sha256
    dklen = dklen or None
    password = force_bytes(password)
    salt = force_bytes(salt)
    return hashlib.pbkdf2_hmac(digest().name, password, salt, iterations, dklen)
