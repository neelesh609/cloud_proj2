import textwrap
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import pyodbc




driver = '{ODBC Driver 17 for SQL Server}'

server_name = 'nxs0682'
database_name = 'neeldatabase'

server = '{server_name}.database.windows.net,1433'.format(server_name=server_name)

username = "nxs0682"
password = "Aakneel@216"

connection_string = textwrap.dedent('''
    Driver={driver};
    Server={server};
    Database={database};
    Uid={username};
    Pwd={password};
    Encrypt=yes;
    TrustServerCertificate=no;
    Connection Timeout=30;
'''.format(
    driver=driver,
    server=server,
    database=database_name,
    username=username,
    password=password
))

conn = pyodbc.connect(connection_string)
cursor = conn.cursor()

app=Flask(__name__)

@app.route('/', methods=['GET' ,'POST'])
def eq_count1():
    return render_template('index.html')

@app.route('/eq_display5', methods=['GET', 'POST'])
def eq_count():
    quakes = []
    if request.method == 'POST':
        magnitude = request.form.get('count')
    cursor.execute("select Time, Latitude, Longitude, Depth, Mag, Magtype, Place, LocationSource from all_month where Mag > 5",)
    for data in cursor:
        quakes.append(data)
    earthquake_len = len(quakes)
    return render_template('eq_display5.html', earthquakes = quakes, lengths = earthquake_len)

@app.route('/eq_range', methods=['GET', 'POST'])
def range_count():
    quakes=[]
    magnitude=str(request.form.get('startrange'))
    magnitude=magnitude.split(',')
    if request.method == 'POST':
        st_mag = request.form.get('startrange')
        end_mag = request.form.get('stoprange')
        timing = str(request.form.get('timerange'))
        print(st_mag, end_mag, timing)
        
        if timing == "RecentWeek":
            time = '2021-06-05T00:00:00.000Z'
            cursor.execute("select Time, Latitude, Longitude, Depth, Mag, Magtype, Place, LocationSource from all_month where Mag > "+magnitude[0]+" and Mag < "+magnitude[1]+" and  time >= DATEADD(dd,DATEDIFF(dd,0,GETDATE())/7*7-7,-2) AND time < DATEADD(dd,DATEDIFF(dd,0,GETDATE())/7*7-7,5);")
            quakes=cursor.fetchall()
        
        else:
            cursor.execute("select Time, Latitude, Longitude, Depth, Mag, Magtype, Place, LocationSource from all_month where Mag > "+magnitude[0]+" and Mag < "+magnitude[1]+";")
            quakes=cursor.fetchall()
        #earthquake_len = len(quakes)
    return render_template('eq_range.html', quakes1 = quakes, lengths = len(quakes))

@app.route('/eq_night', methods=['GET', 'POST'])
def eq_night():
    quakes = []
    if request.method == 'POST':
        magnitude = request.form.get('night')
        cursor.execute("select  time,mag from all_month where (cast(time as time) not between '08:00:00' and '18:00:00') and mag > 4.0;")
        
    for data in cursor:
        quakes.append(data)
    earthquake_len = len(quakes)
    
    return render_template('eq_night.html', earthquakes = quakes, lengths = earthquake_len)

@app.route('/eq_mag', methods=['GET', 'POST'])
def eq_clusters():
    earthquakes = []
    if request.method == 'POST':
        magnitude = request.form.get('cluster')
    cursor.execute("SELECT  time , place , locationsource , mag from all_month where mag = ? ", magnitude)
    for data in cursor:
        earthquakes.append(data)
    earthquake_len = len(earthquakes)
    return render_template('eq_mag.html', earthquakes = earthquakes, lengths = earthquake_len)

@app.route('/eqlocation', methods=['GET', 'POST'])
def eq_location():
    eq_area = []
    cursor.execute("SELECT Area = right(rtrim([place]),charindex(' ',reverse(rtrim([place]))+' ')-1) From all_month")
    for data in cursor:
        for value in data:
            eq_area.append(value)
    eq_area_list = list(set(eq_area))
    return render_template('eq_location.html', drop_down = eq_area_list)


@app.route('/eqoutput', methods=['GET', 'POST'])
def eq_output():
    earthquakes = []
    eq_area = []
    if request.method == 'POST':
        distance = request.form.get('dist')
        area = request.form.get('areas')
    cursor.execute("SELECT id ,latitude, longitude, place, Area = right(rtrim([place]),charindex(' ',reverse(rtrim([place]))+' ')-1) From all_month where right(rtrim([place]),charindex(' ',reverse(rtrim([place]))+' ')-1)= ? AND SUBSTRING (place,0,PATINDEX('%km%',place)) >=?", area, distance)
    for data in cursor:
        earthquakes.append(data)
    earthquake_len = len(earthquakes)
    cursor.execute("SELECT Area = right(rtrim([place]),charindex(' ',reverse(rtrim([place]))+' ')-1) From all_month")
    for data in cursor:
        for value in data:
            eq_area.append(value)
    eq_area_list = list(set(eq_area))
    return render_template('eq_location.html', earthquakes = earthquakes, lengths = earthquake_len, drop_down = eq_area_list)


if __name__=="__main__":
    app.run(debug=True)
