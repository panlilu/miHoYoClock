#include "BitcoinService.h"
#include <ArduinoJson.h>

BitcoinService::BitcoinService() {
    lastPrice = 0;
    lastUpdate = 0;
}

static bool skipHeaders(WiFiClientSecure &client) {
    uint32_t t = millis();
    while (client.connected() && (millis() - t < 10000)) {
        if (client.readStringUntil('\n').length() <= 1) return true;
    }
    return false;
}

struct ApiDef {
    const char *source;
    const char *host;
    const char *path;
};

static const ApiDef apis[] = {
    {"gate",     "api.gateio.ws",     "/api/v4/spot/tickers?currency_pair=BTC_USDT"},
    {"coinex",   "api.coinex.com",    "/api/v1/market/ticker?market=BTCUSDT"},
    {"hotcoin",  "api.hotcoinfin.com","/api/v1/market/ticker?symbol=btc_usdt"},
    {"okx",      "www.okx.com",       "/api/v5/market/ticker?instId=BTC-USDT"},
    {"coingecko","api.coingecko.com", "/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"},
    {"coindesk", "api.coindesk.com",  "/api/v1/bpi/currentprice.json"},
    {"binance",  "api.binance.com",   "/api/v3/ticker/price?symbol=BTCUSDT"},
};

static float parsePrice(const char *s, JsonDocument &doc) {
    switch (s[0]) {
        case 'g': return doc[0]["last"].as<float>();
        case 'h': return doc["ticker"][0]["ticker"][0]["last"].as<float>();
        case 'o': return doc["data"][0]["last"].as<float>();
        case 'b': return doc["price"].as<float>();
        case 'c':
            if (s[1] == 'o' && s[3] == 'n') return doc["data"]["ticker"]["last"].as<float>();
            if (s[1] == 'o' && s[3] == 'd') return doc["bpi"]["USD"]["rate_float"].as<float>();
            return doc["bitcoin"]["usd"].as<float>();
    }
    return 0;
}

bool BitcoinService::getPrice() {
    WiFiClientSecure client;
    client.setInsecure();
    client.setTimeout(10000);

    const char *source = getSource().value.c_str();

    const ApiDef *api = nullptr;
    for (auto &a : apis) {
        if (strcmp(source, a.source) == 0) { api = &a; break; }
    }
    if (!api) api = &apis[0];

    if (!client.connect(api->host, 443)) {
        return false;
    }
    client.print("GET "); client.print(api->path); client.println(" HTTP/1.1");
    client.print("Host: "); client.println(api->host);
    client.println("Connection: close");
    client.println();

    if (!skipHeaders(client)) {
        return false;
    }

    // Read body, strip chunked encoding in-place
    char buf[512];
    int len = 0;
    uint32_t t = millis();
    while (client.connected() && (millis() - t < 5000) && len < 511) {
        while (client.available() && len < 511) {
            buf[len++] = client.read();
            t = millis();
        }
    }
    buf[len] = 0;

    // Strip chunked encoding markers (hex-only lines) in-place
    int w = 0, i = 0;
    while (i < len) {
        int start = i;
        while (i < len && buf[i] != '\n') i++;
        int lineLen = i - start;
        bool hex = (lineLen > 0 && lineLen <= 4);
        for (int j = start; j < i && hex; j++) {
            char c = buf[j];
            if (c == '\r') { lineLen--; continue; }
            if (!((c>='0'&&c<='9')||(c>='a'&&c<='f')||(c>='A'&&c<='F'))) hex = false;
        }
        if (!hex && lineLen > 0) {
            for (int j = start; j < i; j++)
                if (buf[j] != '\r') buf[w++] = buf[j];
        }
        i++;
    }
    buf[w] = 0;

    JsonDocument doc;
    DeserializationError err = deserializeJson(doc, buf);
    if (err) return false;

    lastPrice = parsePrice(source, doc);
    lastUpdate = millis();
    return lastPrice > 0;
}
