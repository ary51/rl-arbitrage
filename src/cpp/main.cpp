#include <iostream>
#include <string>
#include <ixwebsocket/IXNetSystem.h>
#include <ixwebsocket/IXWebSocket.h>
#include <nlohmann/json.hpp>
#include "order_book.hpp"

using json = nlohmann::json;

OrderBook lob;

void onMessage(const ix::WebSocketMessagePtr& msg) {
    if (msg->type == ix::WebSocketMessageType::Message) {
        try {
            json payload = json::parse(msg->str);

            // Binance depth updates contain "b" (bids) and "a" (asks) arrays
            if (payload.contains("b")) {
                for (const auto& item : payload["b"]) {
                    lob.process_update("bids", std::stod(item[0].get<std::string>()), std::stod(item[1].get<std::string>()));
                }
            }
            if (payload.contains("a")) {
                for (const auto& item : payload["a"]) {
                    lob.process_update("asks", std::stod(item[0].get<std::string>()), std::stod(item[1].get<std::string>()));
                }
            }

            // Print the top of the book to the console to verify processing
            lob.print_top_of_book();

        } catch (json::parse_error& e) {
            std::cerr << "JSON Parse Error: " << e.what() << std::endl;
        }
    } else if (msg->type == ix::WebSocketMessageType::Open) {
        std::cout << "Connected to Binance WebSocket" << std::endl;
    } else if (msg->type == ix::WebSocketMessageType::Error) {
        std::cerr << "WebSocket Error: " << msg->errorInfo.reason << std::endl;
    }
}

int main() {
    ix::initNetSystem();

    ix::WebSocket webSocket;
    
    // Binance Futures L2 Differential Depth Stream
    std::string url = "wss://fstream.binance.com/ws/btcusdt@depth@100ms";
    webSocket.setUrl(url);

    // Setup the callback function
    webSocket.setOnMessageCallback(onMessage);

    std::cout << "Starting WebSocket connection..." << std::endl;
    webSocket.start();

    // Block the main thread so the background WebSocket thread keeps running
    std::cout << "Press ENTER to stop the engine." << std::endl;
    std::cin.get();

    webSocket.stop();
    ix::uninitNetSystem();

    return 0;
}