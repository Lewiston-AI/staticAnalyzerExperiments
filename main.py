# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
import matplotlib.pyplot as plt

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.

def simple_histogram():
    # Create a sample DataFrame
    data = {
        'values': [18, 21, 22, 25, 28, 30, 32, 34, 35, 36, 38, 40, 42, 45, 50, 55, 60, 65, 70],
        'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7', 'tag8', 'tag9', 'tag10', 'tag11', 'tag12',
                  'tag13', 'tag14', 'tag15', 'tag16', 'tag17', 'tag18', 'tag19']
    }
    df = pd.DataFrame(data)
    print(df)
    plt.hist(df['values'], bins=10, color='orange', alpha=0.7, edgecolor='black', range=(15, 70), cumulative=True, density=True)
    plt.title('Histogram of Values')
    plt.xlabel('Value')
    plt.ylabel('Frequency')
    plt.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('Starting Static Analyzer Experiments')
    simple_histogram()

    print("done")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
