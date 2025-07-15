import threading, tkinter
import tkinter.ttk as ttk

import utils

# window settings
root = tkinter.Tk()
root.title("Stock Trading Algorithm")
root.iconbitmap("icon.ico")
root.geometry("400x400")
root.resizable(False, False)
root.configure(bg="#ffffff")

# loading frame and label
loading_frame = tkinter.Frame(root, bg="#ffffff")
loading_label = tkinter.Label(
    loading_frame,
    anchor="center",
    text="Please wait while we start the program...",
    font=("Consolas", 11, "italic"),
    bg="#ffffff"
)
loading_frame.pack(fill="both", expand=True)
loading_label.pack(expand=True)

# upper frame | slaves: portfolio frame, reset buttons frame
upper_frame = tkinter.Frame(root, bg="#ffffff")

# portfolio frame | slaves: portfolio labels, portfolio values
portfolio_frame = tkinter.Frame(upper_frame)

# portfolio labels
balance_label = tkinter.Label(
    portfolio_frame,
    anchor='w',
    text="Balance: ",
    font=("Consolas", 11, "bold"),
    width=9
)
initialBalance_label = tkinter.Label(
    portfolio_frame,
    anchor='w',
    text="Initial Balance: ",
    font=("Consolas", 11, "bold"),
    width=17
)
netChange_label = tkinter.Label(
    portfolio_frame,
    anchor='w',
    text="Net (%): ",
    font=("Consolas", 11, "bold"),
    width=9
)

# portfolio values (initially empty)
balanceVal_label = tkinter.Label(
    portfolio_frame,
    anchor='e',
    font=("Consolas", 11),
    width=15,
    fg="#0062ff"
)
initialBalanceVal_label = tkinter.Label(
    portfolio_frame,
    anchor='e',
    font=("Consolas", 11),
    width=15,
    fg="#0062ff"
)
netChangeVal_label = tkinter.Label(
    portfolio_frame,
    anchor='e',
    font=("Consolas", 11),
    width=15,
    fg=("#04c314" or "#CB1313")
) # This is just a placeholder for consistency -- fg is dependent on netChange which will be defined later.

# grid of labels and values formed by portfolio frame
balance_label.grid(row=0, column=0, sticky='w')
balanceVal_label.grid(row=0, column=1, sticky='e')
initialBalance_label.grid(row=1, column=0, sticky='w')
initialBalanceVal_label.grid(row=1, column=1, sticky='e')
netChange_label.grid(row=2, column=0, sticky='w')
netChangeVal_label.grid(row=2, column=1, sticky='e')

# reset button function (resets initial balance, deletes all tickers)
def reset_portfolio_gui():
    utils.reset_portfolio()
    tickerVar.set("") # a selected ticker from dropdown menu defined later needs to be de-selected
    updateGUI()

# hard reset button function (prompts user for new balance, deletes all tickers)
def new_balance_popup():

    popup = tkinter.Toplevel(root)
    popup.grab_set()
    popup.title("Set New Balance")
    popup.geometry("350x140")
    popup.resizable(False, False)
    popup.iconbitmap("icon.ico")

    new_balance_label = tkinter.Label(popup, text="Enter new balance between $10,000 and $1,000,000:")
    new_balance_label.pack(pady=10)

    newBalanceVal = tkinter.StringVar()
    new_balance_entry = tkinter.Entry(popup, justify="center", textvariable=newBalanceVal)
    new_balance_entry.pack()

    def on_enter():
        newBalance = round(float(newBalanceVal.get()), 2)
        utils.reset_portfolio(newBalance)
        tickerVar.set("") # a selected ticker from dropdown menu defined later needs to be de-selected
        updateGUI()
        popup.destroy()

    enter_button = tkinter.Button(
        popup,
        text="ENTER",
        command=on_enter,
        state="disabled",
        font=("Consolas", 11)
    )
    enter_button.pack(pady=10)

    warning_label = tkinter.Label(popup, text="WARNING: All ticker data will be discarded.", fg="#DD0F0F")
    warning_label.pack()

    # runtime input validation
    def validate_input(*args):
        val = newBalanceVal.get()
        try:
            val = float(val)
            if 10000 <= val <= 1000000:
                enter_button.config(state="normal")
            else:
                enter_button.config(state="disabled")
        except ValueError:
            enter_button.config(state="disabled")

    newBalanceVal.trace_add("write", validate_input)

# reset buttons frame | slaves: reset and hard reset buttons
reset_frame = tkinter.Frame(upper_frame, bg="#ffffff")

# reset button
reset_button = tkinter.Button(
    reset_frame,
    text="RESET",
    command=reset_portfolio_gui,
    font=("Consolas", 11),
    relief="raised"
)

# hard reset button
reset_hard_button = tkinter.Button(
    reset_frame,
    text="NEW BALANCE",
    command=new_balance_popup,
    font=("Consolas", 11),
    relief="raised"
)

# no grid -- just pack the buttons
reset_button.pack()
reset_hard_button.pack(pady=7)

# grid of portfolio_frame and reset_frame formed by upper_frame
portfolio_frame.grid(row=0, column=0, sticky="nw", padx=10, pady=10)
reset_frame.grid(row=0, column=1, sticky="ne", padx=2, pady=10)

# entry frame | slaves: ticker entry frame, error message label
entry_frame = tkinter.Frame(root, bg="#ffffff")

# ticker entry frame | slaves: ticker entry widget and add ticker button
ticker_entry_frame = tkinter.Frame(entry_frame, bg="#ffffff")

# add ticker button function
def on_add_ticker():
    ticker = tickerEntered.get()
    try:
        utils.ticker_add(ticker)
        updateGUI()
        error_label.config(text="TICKER HAS BEEN ADDED", fg="#0CB40F")
    except Exception as e:
        error_label.config(text=str(e), fg="#DD0F0F")

    root.after(3000, lambda: error_label.config(text=''))

# ticker entry widget
tickerEntered = tkinter.StringVar()
ticker_entry = tkinter.Entry(
    ticker_entry_frame,
    textvariable=tickerEntered,
    font=("Consolas", 11),
    width=10,
    relief="solid",
    justify="center"
)

# add ticker button
add_ticker_button = tkinter.Button(
    ticker_entry_frame,
    text="ADD TICKER",
    command=on_add_ticker,
    font=("Consolas", 11)
)

# grid of ticker_entry and add_ticker_button formed by ticker_entry_frame
ticker_entry.grid(row=0, column=0, padx=10)
add_ticker_button.grid(row=0, column=1)

# error message label (also displays success message)
error_label = tkinter.Label(
    entry_frame,
    font=("Consolas", 11),
    bg="#ffffff"
)

# grid of ticker_entry_frame and error_label formed by entry_frame
ticker_entry_frame.grid(row=0, column=0, sticky="w")
error_label.grid(row=0, column=1, padx=10)

# dropmenu frame | slaves: ticker dropmenu label and widget
dropmenu_frame = tkinter.Frame(root, bg="#ffffff")

# ticker dropmenu label
dropmenu_label = tkinter.Label(
    dropmenu_frame,
    text="List of added tickers:",
    font=("Consolas", 11),
)

# ticker dropmenu widget
tickerVar = tkinter.StringVar()
ticker_dropmenu = ttk.Combobox(
    dropmenu_frame,
    textvariable=tickerVar,
    state="readonly",
    width=10)

# grid of ticker dropmenu label and widget formed by dropmenu_frame
dropmenu_label.grid(row=0, column=0, padx=8, pady=10)
ticker_dropmenu.grid(row=0, column=1)

# interact frame | slaves: backtest ticker button, remove ticker button
interact_frame = tkinter.Frame(root, bg="#ffffff")

# function to trace selected ticker and enable/disable interact-buttons
def on_ticker_change(*args):
    ticker = tickerVar.get()

    if not ticker or ticker == '': 
        remove_ticker_button.config(state="disabled")
        backtest_ticker_button.config(state="disabled")
        results_frame.pack_forget()

    elif utils.tickerData[ticker]["backtested"]:
        remove_ticker_button.config(state="normal")
        backtest_ticker_button.config(state="disabled")

        # reconfigure results_frame's slaves and pack it
        tickerData = utils.tickerData[ticker]
        companyName = tickerData["company-name"]
        term = tickerData["term"]
        riskControl = tickerData["risk-control"]
        balanceAllocated = tickerData["balance-allocated"]
        finalBalance = tickerData["final-balance"]
        netChange = tickerData["net-change"]
        highestWin = tickerData["highest-win"]
        highestLoss = tickerData["highest-loss"]

        company_name_label_var.config(text=companyName)
        backtest_settings_label_var.config(
            text=f"{term.lower()}-term, {("no risk control" if not riskControl else "risk-controlled")}")
        balance_allocated_label_var.config(text=f"${balanceAllocated:,.2f}")
        final_balance_label_var.config(text=f"${finalBalance:,.2f}")
        backtest_net_change_label_var.config(
            text=f"{netChange:+.2f}%",
            fg=("#04c314" if netChange >= 0 else "#CB1313")
        )
        highest_win_label_var.config(text=f"${highestWin:+.2f}%")
        highest_loss_label_var.config(text=f"${highestLoss:+.2f}%")

        results_frame.pack(pady=10)

    else:
        remove_ticker_button.config(state="normal")
        backtest_ticker_button.config(state="normal")
        results_frame.pack_forget()

# backtest ticker button function
def on_backtest_ticker():
    popup = tkinter.Toplevel(root, bg="#ffffff")
    popup.grab_set()
    popup.title("Backtest Settings")
    popup.iconbitmap("icon.ico")
    popup.geometry("300x280")
    popup.resizable(False, False)

    # allocated balance slider (in %)
    allocated_balance_label = tkinter.Label(
        popup,
        text="Allocated balance (5% - 40%)",
        font=("Consolas", 11),
        bg="#ffffff"
    )
    allocated_balance_label.pack(pady=(10, 0))
    allocatedBalanceVar = tkinter.IntVar(value=10)
    allocated_balance_slider = tkinter.Scale(
        popup,
        from_=0.05*utils.portfolio["balance"],
        to=0.4*utils.portfolio["balance"],
        orient="horizontal",
        variable=allocatedBalanceVar
    )
    allocated_balance_slider.pack(fill="x", padx=20, pady=10)

    # risk control toggle (YES / NO)
    risk_control_label = tkinter.Label(
        popup,
        text="Apply risk control?",
        font=("Consolas", 11),
        bg="#ffffff"
    )
    risk_control_label.pack(pady=(5, 0))
    riskControlVar = tkinter.StringVar(value="YES")

    # turn YES / NO to switch
    def toggle_risk(boolean):
        riskControlVar.set(boolean)
        if boolean == "YES":
            yes_button.config(relief="sunken", state="disabled")
            no_button.config(relief="raised", state="normal")
        else:
            yes_button.config(relief="raised", state="normal")
            no_button.config(relief="sunken", state="disabled")

    # 1st button frame
    button_frame1 = tkinter.Frame(popup, bg="#ffffff")
    button_frame1.pack()

    # YES / NO buttons
    yes_button = tkinter.Button( # default ON
        button_frame1,
        text="YES",
        font=("Consolas", 11),
        width=6,
        relief="sunken",
        state="disabled",
        command=lambda: toggle_risk("YES")
    )
    no_button = tkinter.Button(
        button_frame1,
        text="NO",
        font=("Consolas", 11),
        width=6,
        relief="raised",
        state="normal",
        command=lambda: toggle_risk("NO")
    )

    yes_button.pack(side="left", padx=5)
    no_button.pack(side="left", padx=5)

    # term toggle (LONG / SHORT)
    term_label = tkinter.Label(
        popup,
        text="Short-term or long-term method?",
        font=("Consolas", 11),
        bg="#ffffff")
    term_label.pack(pady=(10, 0))
    termVar = tkinter.StringVar(value="LONG")

    # turn LONG / SHORT to switch
    def toggle_term(boolean):
        termVar.set(boolean)
        if boolean == "LONG":
            long_button.config(relief="sunken", state="disabled")
            short_button.config(relief="raised", state="normal")
        else:
            long_button.config(relief="raised", state="normal")
            short_button.config(relief="sunken", state="disabled")

    # 2nd button frame
    button_frame2 = tkinter.Frame(popup, bg="#ffffff")
    button_frame2.pack()

    # LONG / SHORT buttons
    long_button = tkinter.Button( # default ON
        button_frame2,
        text="LONG",
        font=("Consolas", 11),
        width=6,
        relief="sunken",
        state="disabled",
        command=lambda: toggle_term("LONG")
    )
    short_button = tkinter.Button(
        button_frame2,
        text="SHORT",
        font=("Consolas", 11),
        width=6,
        relief="raised",
        state="normal",
        command=lambda: toggle_term("SHORT")
    )

    long_button.pack(side="left", padx=5)
    short_button.pack(side="left", padx=5)

    # enter button function
    def on_enter():
        ticker = tickerVar.get()
        balanceAllocated = allocatedBalanceVar.get()
        term = termVar.get()
        riskControl = riskControlVar.get()
        riskControl = True if riskControl == "YES" else False

        utils.ticker_backtest(ticker, balanceAllocated, term, riskControl)
        updateGUI()
        tickerVar.set(ticker)
        popup.destroy()

    # enter button
    enter_button = tkinter.Button(
        popup,
        text="ENTER",
        font=("Consolas", 11),
        command=on_enter)
    enter_button.pack(pady=15)

# backtest ticker button
backtest_ticker_button = tkinter.Button(
    interact_frame,
    text="BACKTEST TICKER",
    state="disabled",
    command=on_backtest_ticker,
    font=("Consolas", 11)
)

# remove ticker button function
def on_remove_ticker():
    ticker = tickerVar.get()
    utils.ticker_remove(ticker)
    tickerVar.set("")
    updateGUI()

# remove ticker button
remove_ticker_button = tkinter.Button(
    interact_frame,
    text="REMOVE TICKER",
    command=on_remove_ticker,
    state="disabled",
    font=("Consolas", 11)
)

tickerVar.trace_add("write", on_ticker_change)

# grid of backtest/remove ticker buttons formed by interact_frame
backtest_ticker_button.grid(row=0, column=0)
remove_ticker_button.grid(row=0, column=1, padx=10)


# results frame for backtested tickers
results_frame = tkinter.Frame(root)

# results labels
company_name_label = tkinter.Label(
    results_frame,
    anchor='w',
    text="Company: ",
    font=("Consolas", 11, "bold")
)
backtest_settings_label = tkinter.Label(
    results_frame,
    anchor='w',
    text="Settings: ",
    font=("Consolas", 11, "bold")
)
balance_allocated_label = tkinter.Label(
    results_frame,
    anchor='w',
    text="Balance Allocated: ",
    font=("Consolas", 11, "bold")
)
final_balance_label = tkinter.Label(
    results_frame,
    anchor='w',
    text="Final Balance: ",
    font=("Consolas", 11, "bold")
)
backtest_net_change_label = tkinter.Label(
    results_frame,
    anchor='w',
    text="Net Change: ",
    font=("Consolas", 11, "bold")
)
highest_win_label = tkinter.Label(
    results_frame,
    anchor='w',
    text="Highest Win: ",
    font=("Consolas", 11, "bold")
)
highest_loss_label = tkinter.Label(
    results_frame,
    anchor='w',
    text="Highest Loss: ",
    font=("Consolas", 11, "bold")
)

# results values (initially empty)
company_name_label_var = tkinter.Label(
    results_frame,
    anchor='e',
    font=("Consolas", 11),
    fg="#ff7b00"
)
backtest_settings_label_var = tkinter.Label(
    results_frame,
    anchor='e',
    font=("Consolas", 11),
    fg="#ffd500"
)
balance_allocated_label_var = tkinter.Label(
    results_frame,
    anchor='e',
    font=("Consolas", 11),
    fg="#0062ff"
)
final_balance_label_var = tkinter.Label(
    results_frame,
    anchor='e',
    font=("Consolas", 11),
    fg="#0062ff"
)
backtest_net_change_label_var = tkinter.Label(
    results_frame,
    anchor='e',
    font=("Consolas", 11),
    fg=("#04c314" or "#CB1313") # placeholder
)
highest_win_label_var = tkinter.Label(
    results_frame,
    anchor='e',
    font=("Consolas", 11),
    fg="#04c314"
)
highest_loss_label_var = tkinter.Label(
    results_frame,
    anchor='e',
    font=("Consolas", 11),
    fg="#CB1313"
)

# grid of results' labels and values formed by results_frame
company_name_label.grid(row=0, column=0, sticky='w')
company_name_label_var.grid(row=0, column=1, sticky='e')
backtest_settings_label.grid(row=1, column=0, sticky='w')
backtest_settings_label_var.grid(row=1, column=1, sticky='e')
balance_allocated_label.grid(row=2, column=0, sticky='w')
balance_allocated_label_var.grid(row=2, column=1, sticky='e')
final_balance_label.grid(row=3, column=0, sticky='w')
final_balance_label_var.grid(row=3, column=1, sticky='e')
backtest_net_change_label.grid(row=4, column=0, sticky='w')
backtest_net_change_label_var.grid(row=4, column=1, sticky='e')
highest_win_label.grid(row=5, column=0, sticky='w')
highest_win_label_var.grid(row=5, column=1, sticky='e')
highest_loss_label.grid(row=6, column=0, sticky='w')
highest_loss_label_var.grid(row=6, column=1, sticky='e')

def updateGUI():
    balance = utils.portfolio["balance"]
    initialBalance = utils.portfolio["initial-balance"]
    netChange = (balance / initialBalance - 1) * 100

    balanceVal_label.config(text=f"${balance:,.2f}")
    initialBalanceVal_label.config(text=f"${initialBalance:,.2f}")
    netChangeVal_label.config(
        text=f"{netChange:+.2f}%",
        fg=("#04c314" if netChange >= 0 else "#CB1313")
    )

    ticker_dropmenu['values'] = list(utils.tickerData.keys())

def show_main_frame():
    loading_frame.pack_forget()
    upper_frame.pack(fill="x")
    entry_frame.pack(fill="x")
    dropmenu_frame.pack(fill="x")
    interact_frame.pack()

def start_program():

    def threaded_init():
        utils.init()
        updateGUI()
        loading_label.config(text="Done!") # may not be thread-safe
        root.after(800, show_main_frame) # may not be thread-safe

    threading.Thread(target=threaded_init, daemon=True).start()

root.after(1000, start_program)
root.mainloop()