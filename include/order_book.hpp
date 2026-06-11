#pragma once
#include <map>
#include <string>
#include <iostream>
#include <mutex>

class OrderBook {
private:
    // Bids sorted descending (highest price first)
    std::map<double, double, std::greater<double>> bids;
    // Asks sorted ascending (lowest price first)
    std::map<double, double, std::less<double>> asks;
    
    // Mutex to prevent the WebSocket thread and the ZeroMQ thread from accessing data simultaneously
    std::mutex book_mutex;

public:
    void process_update(const std::string& side, double price, double quantity) {
        std::lock_guard<std::mutex> lock(book_mutex);
        
        if (side == "bids") {
            if (quantity == 0.0) bids.erase(price);
            else bids[price] = quantity;
        } else if (side == "asks") {
            if (quantity == 0.0) asks.erase(price);
            else asks[price] = quantity;
        }
    }

    void print_top_of_book() {
        std::lock_guard<std::mutex> lock(book_mutex);
        if (bids.empty() || asks.empty()) return;

        double best_bid = bids.begin()->first;
        double best_ask = asks.begin()->first;
        double spread = best_ask - best_bid;

        std::cout << "[LOB] Bid: " << best_bid << " | Ask: " << best_ask 
                  << " | Spread: " << spread << std::endl;
    }
};