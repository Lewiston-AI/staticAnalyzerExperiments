# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import pandas as pd
import PIthon
import saDefs
import saDF
import saArcSummary
import plotly.express as px

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'{name}')  # Press Ctrl+F8 to toggle the breakpoint.

def simple_histogram():
    # Create a sample DataFrame
    data = {
        'values': [18, 21, 22, 25, 28, 30, 32, 34, 35, 36, 38, 40, 42, 45, 50, 55, 60, 65, 70],
        'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6', 'tag7', 'tag8', 'tag9', 'tag10', 'tag11', 'tag12',
                  'tag13', 'tag14', 'tag15', 'tag16', 'tag17', 'tag18', 'tag19']
    }
    fig = px.histogram(data,x='values')
    fig.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('Starting Static Analyzer Experiments')
    #simple_histogram()

    PIthon.connect_to_Server('ec2-54-200-148-162.us-west-2.compute.amazonaws.com')
    #PIthon.get_tag_snapshot('sinusoid')
    #defPoint = PIthon.get_def_point()
    #print(defPoint)
    reports = PIthon.get_reports1()
    for pt in reports[0]:
        saDefs.update_defaults(pt)
    i = 0
    for key,value in reports[1].items():
        print(key)
        if len(value) <= 0:
            print("no data")
            continue
        df = pd.DataFrame(value)
        saArcSummary.add_arc_summary(df, reports[0][i])
        i = i + 1
    df = pd.DataFrame(reports[0])
    print(df)
    saDF.sa_histogram(df, 'snapshot ln(DT)', 25)
    saDF.sa_histogram(df, 'normalized minDV', 50)
    saDF.sa_histogram(df, 'ln(minDT)', 50)
    saDF.sa_histogram(df, 'minDV', 200)
    saDF.sa_histogram(df, 'minDT', 200)
    saDF.sa_save_csv(df, '.\channels.csv')

    print("done")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/