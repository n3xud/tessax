from .html_reader import HTMLReader

if __name__ == "__main__":
    print("Starting the application...")
    html_reader = HTMLReader(
        sources=[
            "https://www.hochschule-rhein-waal.de/de/fakultaeten/kommunikation-und-umwelt/studienangebot/bachelorstudiengaenge/medieninformatik-bsc"
        ]
    )
    html_reader.run()
    # run_app()
