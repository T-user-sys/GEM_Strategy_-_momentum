import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import flet as ft
from io import BytesIO
import base64

def main(page: ft.Page):
    page.title = "Momentum checker"
    page.scroll = ft.ScrollMode.AUTO
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    chart_container = ft.Column()
    tickers_field = ft.TextField(
        label="Add tickers separated with comma",
        text_align=ft.TextAlign.CENTER,
    )
    output_text = ft.Text(value="", size=16)

    def button_clicked(e):
        tickers_input = tickers_field.value.strip()
        output_text.value = ""
        chart_container.controls.clear()

        if not tickers_input:
            output_text.value = "You didn't input any tickers"
        else:
            tickers_list = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
            data = {}

            for ticker in tickers_list:
                try:
                    df = yf.download(ticker, period='13mo')['Close']
                    if df.empty:
                        output_text.value += f"\nBrak danych dla: {ticker}"
                    else:
                        data[ticker] = df
                except Exception as ex:
                    output_text.value += f"\nBłąd dla {ticker}: {str(ex)}"

            if not data:
                output_text.value += "\nNie udało się pobrać danych dla żadnego tickera."
            else:
                lookback = 252
                momentum_data = pd.DataFrame()

                for ticker, df in data.items():
                    momentum = df.pct_change(periods=lookback)
                    momentum_data[ticker] = momentum

                momentum_data.dropna(inplace=True)

                if momentum_data.empty:
                    output_text.value += "\nBrak wystarczających danych do obliczeń momentum."
                else:
                    plt.figure(figsize=(10, 5))
                    for ticker in momentum_data.columns:
                        plt.plot(momentum_data.index, momentum_data[ticker], label=ticker)
                    plt.title("Momentum (252-dniowe zmiany procentowe)")
                    plt.xlabel("Data")
                    plt.ylabel("Momentum (zmiana %)")
                    plt.legend()
                    plt.grid(True)

                    # Zapisz wykres do pamięci RAM jako PNG
                    buf = BytesIO()
                    plt.tight_layout()
                    plt.savefig(buf, format="png")
                    plt.close()
                    buf.seek(0)

                    # Zakoduj obraz do base64
                    img_base64 = base64.b64encode(buf.read()).decode("utf-8")
                    img_control = ft.Image(src_base64=img_base64, expand=True)

                    chart_container.controls.append(img_control)

        page.update()

    calculate_button = ft.ElevatedButton(
        text="Submit",
        width=250,
        on_click=button_clicked
    )

    container = ft.Container(
        content=ft.Column(
            controls=[
                chart_container,  # Wykres na górze
                ft.ResponsiveRow(
                    controls=[tickers_field],
                    alignment=ft.MainAxisAlignment.CENTER,
                    width=600
                ),
                ft.ResponsiveRow(
                    controls=[calculate_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                    width=350
                ),
                output_text,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        padding=20,
    )

    page.add(container)

ft.app(target=main)
