from PIL import Image, ImageTk
from tkinter.ttk import Treeview
import teradatasql
import tkinter as tk


class TDskewApp(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # self.geometry("650x450")
        self.resizable(0,0)
        self.title("Teradata table size analyzer")

        self.upper_frame = tk.Frame(self, width=650, height=200)
        self.upper_frame.grid(row=0)

        self.lower_frame = tk.Frame(self, width=650, height=300)
        self.lower_frame.grid(row=1)

        self.image = Image.open("img/Teradata_logo_2018.png")
        self.MAX_SIZE = (300, 300)
        self.image.thumbnail(self.MAX_SIZE)
        self.photo = ImageTk.PhotoImage(self.image)
        self.label = tk.Label(self.upper_frame, image=self.photo)
        self.label.image = self.photo  # keep a reference!
        self.label.grid(row=0, column=0, columnspan=6)

        self.dbcname_label = tk.Label(self.upper_frame, text="dbcname:", font="Helvetica 9 bold", width=20).grid(row=1, column=0)
        self.db_username_label = tk.Label(self.upper_frame, text="username:", font="Helvetica 9 bold", width=20).grid(row=2, column=0)
        self.password_label = tk.Label(self.upper_frame, text="password:", font="Helvetica 9 bold", width=20).grid(row=3, column=0)

        self.dbcname = tk.Entry(self.upper_frame, width=20)
        self.dbcname.grid(row=1, column=1)
        self.db_username = tk.Entry(self.upper_frame, width=20)
        self.db_username.grid(row=2, column=1)
        self.password = tk.Entry(self.upper_frame, width=20)
        self.password.grid(row=3, column=1)

        self.database_label = tk.Label(self.upper_frame, text="database:", font="Helvetica 9 bold", width=20).grid(row=1, column=2)
        self.table_label = tk.Label(self.upper_frame, text="table:", font="Helvetica 9 bold", width=20).grid(row=2, column=2)

        self.database = tk.Entry(self.upper_frame, width=20)
        self.database.grid(row=1, column=3)
        self.table = tk.Entry(self.upper_frame, width=20)
        self.table.grid(row=2, column=3)

        self.run_qry_btn = tk.Button(self.upper_frame, width=20, text="run query", command=self.execute_sql).grid(row=4, column=1)

        self.columns = ("DataBaseName", "TableName", "Type", "CurrentPermMB", "PeakPermMB", "SkewFactor", "CreatorName")
        self.tree = Treeview(self.lower_frame, columns=self.columns, show='headings')
        self.tree.grid(row=0, column=0)
        self.tree.heading("DataBaseName", text="DataBaseName")
        self.tree.column("DataBaseName", minwidth=0, width=100)
        self.tree.heading("TableName", text="TableName")
        self.tree.column("TableName", minwidth=0, width=100)
        self.tree.heading("Type", text="Type")
        self.tree.column("Type", minwidth=0, width=100)
        self.tree.heading("CurrentPermMB", text="CurrentPermMB")
        self.tree.column("CurrentPermMB", minwidth=0, width=100)
        self.tree.heading("PeakPermMB", text="PeakPermMB")
        self.tree.column("PeakPermMB", minwidth=0, width=100)
        self.tree.heading("SkewFactor", text="SkewFactor")
        self.tree.column("SkewFactor", minwidth=0, width=100)
        self.tree.heading("CreatorName", text="CreatorName")
        self.tree.column("CreatorName", minwidth=0, width=100)

        self.vsb = tk.Scrollbar(self.lower_frame, orient="vertical", command=self.tree.yview)
        self.vsb.grid(row=0, column=1, sticky="NS")
        self.tree.configure(yscrollcommand=self.vsb.set)


    def execute_sql(self):
        with teradatasql.connect (host="192.168.179.128", user='dbc', password='dbc') as con:
        # with teradatasql.connect (host=self.dbcname.get(), user=self.db_username.get(), password=self.password.get()) as con:
            with con.cursor() as cur:
                cur.execute("SELECT S.DataBaseName,S.TableName AS Name, CASE   TableKind WHEN   'O' THEN 'T' WHEN   'D' THEN 'P' WHEN   'E' THEN 'P' WHEN   'A' THEN 'F' WHEN   'S' THEN 'F' WHEN   'R' THEN 'F' WHEN   'B' THEN 'F'  ELSE   TableKind END    AS Typ ,SUM(CurrentPerm)/1024/1024 AS CurrentPermMB,SUM(PeakPerm)/1024/1024 AS PeakPermMB,             (100 - (AVG(CurrentPerm)/NULLIFZERO(MAX(CurrentPerm))*100)) AS SkewFactor,CreatorName,CommentString FROM   Dbc.TableSizeV S,dbc.TablesV T "
                            "WHERE  1=1       AND S.DataBaseName in  ('" + self.database.get() + "')   AND    S.DataBaseName=T.DataBaseName        AND    S.TableName=T.TableName GROUP  BY 1,2,3,7,8 ORDER  BY 1,4 desc;")
                _rs = cur.fetchall()
        # for row in _rs:
        #     print(row)
        self.tree.delete(*self.tree.get_children())
        for row in _rs:
            self.tree.insert('', 'end', values=row)

def main():

    w = TDskewApp()
    w.mainloop()

if __name__ == "__main__":
    main()