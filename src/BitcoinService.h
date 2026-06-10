#ifndef _BITCOIN_SERVICE_H
#define _BITCOIN_SERVICE_H

#include <WiFiClientSecure.h>
#include <ConfigItem.h>

class BitcoinService {
public:
    BitcoinService();

    static StringConfigItem& getSource() { static StringConfigItem btc_source("btc_source", 10, "gate"); return btc_source; }
    static IntConfigItem& getInterval() { static IntConfigItem btc_interval("btc_interval", 300); return btc_interval; }

    bool getPrice();
    float getLastPrice() { return lastPrice; }
    unsigned long getLastUpdate() { return lastUpdate; }

private:
    bool tryFetch(WiFiClientSecure &c, const char *host, const char *path);

    float lastPrice;
    unsigned long lastUpdate;
};

#endif
