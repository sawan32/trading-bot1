// ✅ Include the Trade Library for Order Execution
#include <Trade/Trade.mqh>

CTrade trade;

// ✅ Input Parameters
input string Trading_Symbol = "EURUSD";  
input double Lot_Size = 0.02;  
input double Stop_Loss = 50;  
input double Take_Profit = 100;  
input double Spread_Adjustment = 2;  

void OnTick()
{
    double Ask = SymbolInfoDouble(Trading_Symbol, SYMBOL_ASK);
    double Bid = SymbolInfoDouble(Trading_Symbol, SYMBOL_BID);
    
    if (Ask == 0 || Bid == 0)  
    {
        Print("⚠ Error: Unable to get market prices for ", Trading_Symbol);
        return;
    }

    double sl = Ask - (Stop_Loss * Point) - (Spread_Adjustment * Point);
    double tp = Ask + (Take_Profit * Point);

    if (PositionsTotal() == 0)
    {
        bool buyResult = trade.PositionOpen(Trading_Symbol, ORDER_TYPE_BUY, Lot_Size, Ask, sl, tp, "AI Trade Execution");

        if (buyResult)
        {
            Print("✅ Trade Executed: BUY Order Sent for ", Trading_Symbol);
        }
        else
        {
            Print("⚠ Trade Execution Failed: BUY Order for ", Trading_Symbol);
        }
    }
}
