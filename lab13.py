import requests
import json
import sqlite3
from tkinter import *
from tkinter.ttk import *
from tkinter import scrolledtext
import matplotlib.pyplot as plt


def get_chuck_norris_fact():
    response = requests.get('https://api.chucknorris.io/jokes/random')
    return json.loads(response.text)


def db_create_connection(db_file='app.db'):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)
    return conn


def db_execute(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Exception as e:
        print(e)


def init_db():
    sql_create_facts_table = """ CREATE TABLE IF NOT EXISTS CNFacts (
                                            txt text NOT NULL,
                                            begin_date text,
                                            last_update text,
                                            url text
                                        ); """
    conn = db_create_connection()

    if conn is not None:
        db_execute(conn, sql_create_facts_table)
    else:
        print("Error! Could not create the database connection")
    return conn


def db_get_all_facts(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT txt FROM CNFacts")
    rows = cur.fetchall()
    return rows


def db_add_chucknorrisfact(conn):
    fact = get_chuck_norris_fact()
    sql_query = 'INSERT INTO CNFacts (txt, begin_date, last_update, url) VALUES (?,?,?,?)'
    conn.execute(sql_query, (fact["value"], fact["created_at"], fact["updated_at"], fact["url"]))
    conn.commit()


def get_numeric(txt):
    if len(txt) > 0:
        for c in txt:
            if c < '0' or c > '9':
                return 0
        return int(txt)
    return 0


def create_app(conn):

    def opennewwindow():

        newwindow = Toplevel(window)
        text = Text(newwindow, width=10, height=5)
        facts = db_get_all_facts(conn)
        def get_avg():
            summ = 0
            for fact in facts:
                summ += len(fact[0])
            text.insert(INSERT, str(summ/len(facts)))

        # sets the title of the
        # Toplevel widget
        newwindow.title("Database")
        # A Label widget to show in toplevel
        Label(newwindow, text="DB Output").pack()
        txt = scrolledtext.ScrolledText(newwindow)
        txt.pack()
        for fact in facts:
            txt.insert(END, ("- " + fact[0] + "\n\n"))
        btn_avglen = Button(newwindow, text="Avg Quote Length", command=get_avg)
        btn_avglen.pack()
        text.pack()

    window = Tk()
    window.title("Chuck Norris Facts")
    var = IntVar()
    colors = {1: '#999', 2: '#ddd', 3: 'red', 4: 'blue'}
    title = Label(window, text="Welcome to Chuck Norris Facts")
    title.configure(anchor="center")
    window.configure(bg='#ddd')

    def bgcolor():
        window.configure(bg=colors[var.get()])
    rad1 = Radiobutton(window, text='Dark', value=1, variable=var, command=bgcolor)
    rad2 = Radiobutton(window, text='Light', value=2, variable=var, command=bgcolor)
    rad3 = Radiobutton(window, text='Red', value=3, variable=var, command=bgcolor)
    rad4 = Radiobutton(window, text='Blue', value=4, variable=var, command=bgcolor)

    btn_newwindow = Button(window, text="Database Output", command=opennewwindow)

    def clicked_btn_getfact():
        db_add_chucknorrisfact(conn)
    btn_getfact = Button(window, text="One Fact", command=clicked_btn_getfact)

    def clicked_btn_getfacts():
        for i in range(get_numeric(txt_factcount.get())):
            db_add_chucknorrisfact(conn)
    btn_getfacts = Button(window, text="Many Facts", command=clicked_btn_getfacts)
    txt_factcount = Entry(window, width=10)

    def clicked_btn_clear_db():
        sql = 'DELETE FROM CNFacts'
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
    btn_clear_db = Button(window, text="Clear", command=clicked_btn_clear_db)
    sep = Separator(window, orient=HORIZONTAL)
    sep2 = Separator(window, orient=HORIZONTAL)
    sep3 = Separator(window, orient=VERTICAL)

    def plot():
        facts = db_get_all_facts(conn)
        lengths = []
        for fact in facts:
            lengths.append(len(fact[0]))
        plt.plot(lengths)
        plt.savefig('plot.png')
        render = PhotoImage(file="plot.png")
        img = Label(window, image=render)
        img.image = render
        img.grid(row=1, column=1, columnspan=3, pady=10, ipady=10)
    btn_plot = Button(window, text="Plot Quote Lengths", command=plot)

    title.grid(row=0, column=1, pady=10, ipady=10)
    btn_newwindow.grid(row=0, column=2, padx=10, pady=10, ipady=10)
    btn_plot.grid(row=0, column=3, padx=10, pady=10, ipady=10)
    txt_factcount.grid(column=0, row=3)
    btn_getfacts.grid(column=0, row=4)
    btn_getfact.grid(column=1, row=3, padx=5)
    btn_clear_db.grid(column=1, row=4, padx=5)
    sep3.grid(column=2, row=3, rowspan=2, padx=5, pady=10, sticky="ns")
    rad1.grid(column=3, row=3, padx=5)
    rad2.grid(column=3, row=4, padx=5)
    rad3.grid(column=4, row=3, padx=5)
    rad4.grid(column=4, row=4, padx=5)
    sep.grid(column=0, row=2, columnspan=5, padx=5, pady=10, sticky="ew")
    sep2.grid(column=0, row=5, columnspan=5, padx=5, pady=10, sticky="ew")

    title.focus()
    window.resizable(0, 0)
    window.mainloop()


def run():
    conn = init_db()
    create_app(conn)


if __name__ == "__main__":
    run()
