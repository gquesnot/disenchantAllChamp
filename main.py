# This is a sample Python script.

# Press Maj+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


# Press the green button in the gutter to run the script.
from api.clientapi import ClientApi

#25452

if __name__ == '__main__':
    cp = ClientApi()
    cp.disenchantAll()
    input("Press Enter to Exit")

