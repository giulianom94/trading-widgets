import subprocess
import sys


def install_dependencies():
    for package in ["yfinance", "matplotlib", "mplfinance", "pandas"]:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package]
            )


install_dependencies()

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import yfinance as yf


def generate_chart(timeframe, period, filename):
    ticker = "EURUSD=X"

    if timeframe.lower() in ["1d", "d1"]:
        raw_data = yf.download(
            ticker, period="1y", interval="1h", progress=False, auto_adjust=False
        )
        if hasattr(raw_data.columns, "levels") and len(raw_data.columns.levels) > 1:
            raw_data.columns = raw_data.columns.get_level_values(0)

        data = raw_data.resample("24h").agg(
            {"Open": "first", "High": "max", "Low": "min", "Close": "last"}
        ).dropna()
    else:
        data = yf.download(
            ticker, period=period, interval=timeframe, progress=False, auto_adjust=False
        )
        if hasattr(data.columns, "levels") and len(data.columns.levels) > 1:
            data.columns = data.columns.get_level_values(0)

    if data.index.tz is None:
        data.index = data.index.tz_localize("UTC").tz_convert("Europe/Rome")
    else:
        data.index = data.index.tz_convert("Europe/Rome")

    data["EMA21"] = data["Close"].ewm(span=21, adjust=False).mean()
    data["EMA200"] = data["Close"].ewm(span=200, adjust=False).mean()

    plot_data = data.tail(50)

    apds = [
        mpf.make_addplot(plot_data["EMA21"], color="#fbc02d", width=1.2),
        mpf.make_addplot(plot_data["EMA200"], color="#29b6f6", width=1.2),
    ]

    mc = mpf.make_marketcolors(
        up="#26a69a",
        down="#ef5350",
        edge="white",
        wick="white",
        volume="in",
    )

    s = mpf.make_mpf_style(
        marketcolors=mc,
        figcolor="black",
        facecolor="black",
        rc={
            "text.color": "white",
            "axes.labelcolor": "white",
            "xtick.color": "white",
            "ytick.color": "white",
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "axes.labelsize": 8,
            "axes.edgecolor": "white",
            "axes.linewidth": 1.0,
            "axes.grid": True,
            "axes.grid.axis": "y",
            "grid.color": "#444444",
            "grid.linestyle": "--",
            "grid.linewidth": 0.5,
        },
    )
    
    is_daily = "d" in timeframe.lower()
    dt_fmt = "%b %d" if is_daily else "%b %d %H:%M"

    fig, axes = mpf.plot(
        plot_data,
        type="candle",
        style=s,
        addplot=apds,
        volume=False,
        ylabel="",
        returnfig=True,
        figsize=(6, 3),
        datetime_format=dt_fmt,
        xrotation=0,
    )

    ax = axes[0]
    last_dt = plot_data.index[-1].strftime(dt_fmt)
    
    ax.text(
        len(plot_data) - 1,
        -0.045,
        last_dt,
        transform=ax.get_xaxis_transform(),
        color="white",
        fontsize=6,
        ha="center",
        va="top",
    )
    
    fig.savefig(filename, bbox_inches="tight", dpi=150, facecolor="black")
    plt.close(fig)


if __name__ == "__main__":
    generate_chart("1d", "1y", "eurusd_d1.png")
    generate_chart("4h", "2mo", "eurusd_h4.png")
    generate_chart("1h", "5d", "eurusd_h1.png")
    print("All multi-timeframe charts generated successfully.")
