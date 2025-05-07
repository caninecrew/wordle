from src.ui.app import WordleApp

if __name__ == "__main__":
    try:
        WordleApp().run()
    except Exception as e:
        print(f"An error occurred: {e}")
