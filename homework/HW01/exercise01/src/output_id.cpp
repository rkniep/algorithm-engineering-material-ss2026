#include <cstdio>
#include <cstring>
#include <cstdint>
#include <array>
#include <algorithm>
#include <ranges>
#include <vector>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <iostream>
#include <cstdio>
#include <cerrno>
#include <cstring>
#include <unistd.h>
#include <ctime>

using RawHash = std::array<std::byte, 16>;
using HexHash = std::array<char, 33>;

static auto irange(std::size_t size) {
    return std::ranges::views::iota(std::size_t(0), size);
}

class Hasher {
public:
    /**
     * @brief Construct a Hasher with no input.
     * The hasher is ready to accept data through the update() methods.
     */
    inline Hasher() noexcept;

    /**
     * @brief Update the hash with new data.
     * This can be called multiple times to update the hash with more data.
     * The data can be of any integer or floating-point type,
     * as well as contiguous or non-contiguous ranges of such types.
     * The data is processed as raw bytes, so the same sequence of bytes will produce the
     * same hash regardless of the types used to provide it.
     */
    template<typename T>
    requires (std::is_floating_point_v<T> || std::is_integral_v<T>)
    void update(T value) noexcept {
        const std::byte* bytes = reinterpret_cast<const std::byte*>(&value);
        update(bytes, sizeof(T));
    }

    template<typename T>
    requires std::ranges::contiguous_range<T> && (std::is_floating_point_v<std::ranges::range_value_t<T>> || std::is_integral_v<std::ranges::range_value_t<T>>)
    void update(const T& contiguous_range) noexcept {
        const std::byte* bytes = reinterpret_cast<const std::byte*>(std::data(contiguous_range));
        update(bytes, std::size(contiguous_range) * sizeof(std::ranges::range_value_t<T>));
    }

    template<typename T>
    requires std::ranges::input_range<T> && (!std::ranges::contiguous_range<T>) && (std::is_floating_point_v<std::ranges::range_value_t<T>> || std::is_integral_v<std::ranges::range_value_t<T>>)
    void update(const T& input_range) noexcept {
        for(const auto& element : input_range) {
            update(element);
        }
    }

    template<typename Iterator>
    requires std::input_iterator<Iterator> && (std::is_floating_point_v<std::iter_value_t<Iterator>> || std::is_integral_v<std::iter_value_t<Iterator>>)
    void update(Iterator begin, Iterator end) noexcept {
        for(auto it = begin; it != end; ++it) {
            update(*it);
        }
    }

    /**
     * @brief Update with raw bytes.
     */
    inline void update(const std::byte* data, std::size_t size) noexcept;

    /**
     * @brief Finalize the hash and write the result to the given output.
     * After finalization, the hasher is reset and can be used again to hash new data.
     * The output is a 16-byte array for the raw hash.
     */
    inline void finalize(RawHash& out_hash) noexcept;

    /**
     * @brief Finalize the hash and write the result as a hexadecimal string to the given output.
     * After finalization, the hasher is reset and can be used again to hash new data.
     * The output is a 32-character array for the hexadecimal representation of the hash, plus a null terminator.
     */
    inline void finalize(HexHash& out_hex) noexcept;

private:
    inline void p_block() noexcept;
    inline void p_update_w(std::uint32_t* w, int i) noexcept;

    static inline std::uint32_t p_step1(std::uint32_t e, std::uint32_t f, std::uint32_t g) noexcept;
    static inline std::uint32_t p_step2(std::uint32_t a, std::uint32_t b, std::uint32_t c) noexcept;

    std::uint32_t state[8];
    std::byte buffer[64];
    std::uint64_t n_bits;
    std::uint8_t buffer_counter;
};

Hasher::Hasher() noexcept :
    state{
        UINT32_C(0x6a09e667),
        UINT32_C(0xbb67ae85),
        UINT32_C(0x3c6ef372),
        UINT32_C(0xa54ff53a),
        UINT32_C(0x510e527f),
        UINT32_C(0x9b05688c),
        UINT32_C(0x1f83d9ab),
        UINT32_C(0x5be0cd19)
    },
    n_bits(0),
    buffer_counter(0)
{}

void Hasher::update(const std::byte* data, std::size_t size) noexcept {
    for(std::size_t s : irange(size)) {
        buffer[buffer_counter++] = data[s];
        if(buffer_counter == 64) {
            p_block();
            buffer_counter = 0;
        }
    }
    n_bits += size * 8;
}

void Hasher::p_block() noexcept {
    static const std::uint32_t k[64] = {
        UINT32_C(0x428a2f98), UINT32_C(0x71374491), UINT32_C(0xb5c0fbcf), UINT32_C(0xe9b5dba5),
        UINT32_C(0x3956c25b), UINT32_C(0x59f111f1), UINT32_C(0x923f82a4), UINT32_C(0xab1c5ed5),
        UINT32_C(0xd807aa98), UINT32_C(0x12835b01), UINT32_C(0x243185be), UINT32_C(0x550c7dc3),
        UINT32_C(0x72be5d74), UINT32_C(0x80deb1fe), UINT32_C(0x9bdc06a7), UINT32_C(0xc19bf174),
        UINT32_C(0xe49b69c1), UINT32_C(0xefbe4786), UINT32_C(0x0fc19dc6), UINT32_C(0x240ca1cc),
        UINT32_C(0x2de92c6f), UINT32_C(0x4a7484aa), UINT32_C(0x5cb0a9dc), UINT32_C(0x76f988da),
        UINT32_C(0x983e5152), UINT32_C(0xa831c66d), UINT32_C(0xb00327c8), UINT32_C(0xbf597fc7),
        UINT32_C(0xc6e00bf3), UINT32_C(0xd5a79147), UINT32_C(0x06ca6351), UINT32_C(0x14292967),
        UINT32_C(0x27b70a85), UINT32_C(0x2e1b2138), UINT32_C(0x4d2c6dfc), UINT32_C(0x53380d13),
        UINT32_C(0x650a7354), UINT32_C(0x766a0abb), UINT32_C(0x81c2c92e), UINT32_C(0x92722c85),
        UINT32_C(0xa2bfe8a1), UINT32_C(0xa81a664b), UINT32_C(0xc24b8b70), UINT32_C(0xc76c51a3),
        UINT32_C(0xd192e819), UINT32_C(0xd6990624), UINT32_C(0xf40e3585), UINT32_C(0x106aa070),
        UINT32_C(0x19a4c116), UINT32_C(0x1e376c08), UINT32_C(0x2748774c), UINT32_C(0x34b0bcb5),
        UINT32_C(0x391c0cb3), UINT32_C(0x4ed8aa4a), UINT32_C(0x5b9cca4f), UINT32_C(0x682e6ff3),
        UINT32_C(0x748f82ee), UINT32_C(0x78a5636f), UINT32_C(0x84c87814), UINT32_C(0x8cc70208),
        UINT32_C(0x90befffa), UINT32_C(0xa4506ceb), UINT32_C(0xbef9a3f7), UINT32_C(0xc67178f2),
    };

    std::uint32_t a = state[0];
    std::uint32_t b = state[1];
    std::uint32_t c = state[2];
    std::uint32_t d = state[3];
    std::uint32_t e = state[4];
    std::uint32_t f = state[5];
    std::uint32_t g = state[6];
    std::uint32_t h = state[7];
    std::uint32_t w[16];

    for (int i = 0; i < 80; i += 16) {
        p_update_w(w, i);
        for (int j = 0; j < 16; j += 4) {
            std::uint32_t temp;
            temp = h + p_step1(e, f, g) + k[i + j + 0] + w[j + 0];
            h = temp + d;
            d = temp + p_step2(a, b, c);
            temp = g + p_step1(h, e, f) + k[i + j + 1] + w[j + 1];
            g = temp + c;
            c = temp + p_step2(d, a, b);
            temp = f + p_step1(g, h, e) + k[i + j + 2] + w[j + 2];
            f = temp + b;
            b = temp + p_step2(c, d, a);
            temp = e + p_step1(f, g, h) + k[i + j + 3] + w[j + 3];
            e = temp + a;
            a = temp + p_step2(b, c, d);
        }
    }

    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
    state[4] += e;
    state[5] += f;
    state[6] += g;
    state[7] += h;
}

void Hasher::p_update_w(std::uint32_t* w, int i) noexcept {
    const std::byte* buffer = this->buffer;
    for (int j = 0; j < 16; j++) {
        if (i < 16) {
            w[j] =
                ((std::uint32_t)buffer[0] << 24) |
                ((std::uint32_t)buffer[1] << 16) |
                ((std::uint32_t)buffer[2] <<  8) |
                ((std::uint32_t)buffer[3]);
            buffer += 4;
        } else {
            std::uint32_t a = w[(j + 1) & 15];
            std::uint32_t b = w[(j + 14) & 15];
            std::uint32_t s0 = (std::rotr(a,  7) ^ std::rotr(a, 18) ^ (a >>  3));
            std::uint32_t s1 = (std::rotr(b, 17) ^ std::rotr(b, 19) ^ (b >> 10));
            w[j] += w[(j + 9) & 15] + s0 + s1;
        }
    }
}

std::uint32_t Hasher::p_step1(std::uint32_t e, std::uint32_t f, std::uint32_t g) noexcept {
    return (std::rotr(e, 6) ^ std::rotr(e, 11) ^ std::rotr(e, 25)) + ((e & f) ^ ((~e) & g));
}

std::uint32_t Hasher::p_step2(std::uint32_t a, std::uint32_t b, std::uint32_t c) noexcept {
    return (std::rotr(a, 2) ^ std::rotr(a, 13) ^ std::rotr(a, 22)) + ((a & b) ^ (a & c) ^ (b & c));
}

void Hasher::finalize(RawHash& out_hash) noexcept {
    const std::byte pad = static_cast<std::byte>(UINT8_C(0x80));
    const std::byte zero = static_cast<std::byte>(0);
    auto old_n_bits = n_bits;
    update(&pad, 1);
    while (buffer_counter != 56) {
        update(&zero, 1);
    }
    for (int i = 7; i >= 0; i--){
        std::byte byte = static_cast<std::byte>(static_cast<std::uint8_t>((old_n_bits >> (8 * i)) & 0xff));
        update(&byte, 1);
    }
    std::byte* ptr = out_hash.data();
    for (int i = 0; i < 4; i++) {
        for (int j = 3; j >= 0; j--) {
            *ptr++ = static_cast<std::byte>(std::uint8_t((state[i] >> (j * 8)) & 0xff));
        }
    }

    // reset the hasher state to allow reuse
    state[0] = UINT32_C(0x6a09e667);
    state[1] = UINT32_C(0xbb67ae85);
    state[2] = UINT32_C(0x3c6ef372);
    state[3] = UINT32_C(0xa54ff53a);
    state[4] = UINT32_C(0x510e527f);
    state[5] = UINT32_C(0x9b05688c);
    state[6] = UINT32_C(0x1f83d9ab);
    state[7] = UINT32_C(0x5be0cd19);
    n_bits = 0;
    buffer_counter = 0;
}

void Hasher::finalize(HexHash& out_hex) noexcept {
    RawHash hash;
    finalize(hash);
    for (int i = 0; i < 16; i++) {
        char buf[3];
        std::snprintf(buf, sizeof(buf), "%02x", static_cast<std::uint8_t>(hash[i]));
        out_hex[i * 2] = buf[0];
        out_hex[i * 2 + 1] = buf[1];
    }
    out_hex[32] = '\0';
}

std::vector<char> get_local_ip() {
    int s = ::socket(AF_INET, SOCK_DGRAM, 0);
    if(s == -1) {
        std::cout << "socket: " << std::strerror(errno) << std::endl;
        std::exit(1);
    }
    struct sockaddr_in addr;
    std::memset(static_cast<void*>(&addr), 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(12345);
    ::inet_aton("1.1.1.1", &addr.sin_addr);
    // note that this does not actually establish a connection or send anything
    // since we are using SOCK_DGRAM, but guarantees that we get the local IP
    // that is used to talk to the internet
    int c = ::connect(s, reinterpret_cast<struct sockaddr*>(&addr), sizeof(addr));
    if(c < 0) {
        std::cout << "connect: " << std::strerror(errno) << std::endl;
        std::exit(1);
    }
    sockaddr_in local_addr;
    socklen_t local_addr_len = sizeof(local_addr);
    if(::getsockname(s, reinterpret_cast<struct sockaddr*>(&local_addr), &local_addr_len) < 0) {
        std::cout << "getsockname: " << std::strerror(errno) << std::endl;
        std::exit(1);
    }
    char local_ip_str[INET_ADDRSTRLEN];
    std::memset(local_ip_str, 0, sizeof(local_ip_str));
    if(::inet_ntop(AF_INET, &local_addr.sin_addr, local_ip_str, sizeof(local_ip_str)) == nullptr) {
        std::cout << "inet_ntop: " << std::strerror(errno) << std::endl;
        std::exit(1);
    }
    ::close(s);
    return std::vector<char>(
        +local_ip_str, 
        local_ip_str + std::strlen(local_ip_str)
    );
}

std::vector<char> get_username() {
    const char* user_env = std::getenv("USER");
    if(user_env == nullptr) {
        return {};
    }
    return std::vector<char>(user_env, user_env + std::strlen(user_env));
}

int main() {
    std::vector<char> local_ip = get_local_ip();
    std::vector<char> username = get_username();
    auto pid = static_cast<int>(::getpid());
    auto time = std::time(nullptr);
    std::vector<char> time_str(200);
    time_str.resize(std::strftime(
        time_str.data(), time_str.size(), 
        "%Y-%m-%d %H:%M:%S", std::localtime(&time)
    ));
    Hasher hasher;
    hasher.update(local_ip);
    hasher.update(username);
    hasher.update(pid);
    hasher.update(time_str);
    HexHash hash;
    hasher.finalize(hash);
    HexHash hashhash;
    hasher.update(hash);
    hasher.finalize(hashhash);
    std::cout << "Your unique output is: " 
              << hash.data() << "-" << hashhash.data() << std::endl;
    return 0;
}
